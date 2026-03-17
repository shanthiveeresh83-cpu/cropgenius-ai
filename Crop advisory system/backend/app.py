# CropGenius AI: A Multilingual Intelligent Crop Advisory and Recommendation System
# Backend Flask Application

import os
import hashlib
from datetime import datetime

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_bcrypt import Bcrypt
import sqlite3
import pickle
import numpy as np

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    from yield_prediction import YieldPredictionModel
    yield_model_available = True
except Exception as e:
    print(f"YieldPredictionModel unavailable: {e}")
    YieldPredictionModel = None
    yield_model_available = False

try:
    from fertilizer_recommendation import FertilizerRecommendation
    fertilizer_available = True
except Exception as e:
    print(f"FertilizerRecommendation unavailable: {e}")
    FertilizerRecommendation = None
    fertilizer_available = False

try:
    from soil_health import SoilHealthClassifier
    soil_available = True
except Exception as e:
    print(f"SoilHealthClassifier unavailable: {e}")
    SoilHealthClassifier = None
    soil_available = False

try:
    from weather_prediction import WeatherBasedPrediction
    weather_available = True
except Exception as e:
    print(f"WeatherBasedPrediction unavailable: {e}")
    WeatherBasedPrediction = None
    weather_available = False

try:
    from price_prediction import CropPricePrediction
    price_available = True
except Exception as e:
    print(f"CropPricePrediction unavailable: {e}")
    CropPricePrediction = None
    price_available = False

try:
    from cv_image_model import CropImageCVModel
    cv_model_available = True
except Exception:
    CropImageCVModel = None
    cv_model_available = False

try:
    from translation import translate_text
    translation_available = True
except Exception:
    translation_available = False

try:
    from disease_detection import CropDiseaseDetector, SimpleDiseaseDetector
    disease_detector = None
    try:
        disease_detector = CropDiseaseDetector.load()
        print("CNN Disease Detector loaded")
    except:
        disease_detector = SimpleDiseaseDetector()
        print("Using fallback disease detector")
except Exception as e:
    disease_detector = None
    print(f"Disease detection unavailable: {e}")

try:
    from llm_advisor import get_llm_instance
    llm_advisor = get_llm_instance()
    print(f"LLM Advisor initialized: {llm_advisor.provider}")
except Exception as e:
    llm_advisor = None
    print(f"LLM unavailable: {e}")

try:
    from rag_chatbot import get_rag_chatbot
    rag_chatbot = get_rag_chatbot()
    print("RAG Chatbot initialized")
except Exception as e:
    rag_chatbot = None
    print(f"RAG unavailable: {e}")

from routes.predict import predict_bp
from routes.analytics import analytics_bp
from routes.chat import chat_bp
from routes.auth import auth_bp
from routes.location import location_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(predict_bp, url_prefix="/predict")
app.register_blueprint(analytics_bp, url_prefix="/analytics")
app.register_blueprint(chat_bp, url_prefix="/chat")
app.register_blueprint(location_bp, url_prefix="/location")

app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "supersecretkey")
jwt = JWTManager(app)

backend_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(backend_dir, "model.pkl")
db_path = os.path.join(backend_dir, "crop.db")
print(f"Loading model from: {model_path}")
model = pickle.load(open(model_path, "rb"))
bcrypt = Bcrypt(app)

FEATURE_KEYS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

def get_db_connection():
    return sqlite3.connect(db_path)

def parse_feature_payload(data):
    if not isinstance(data, dict):
        raise ValueError("Request body must be a JSON object")

    missing = [k for k in FEATURE_KEYS if k not in data]
    if missing:
        raise ValueError(f"Missing required fields: {', '.join(missing)}")

    try:
        values = [float(data[k]) for k in FEATURE_KEYS]
    except (TypeError, ValueError):
        raise ValueError("All feature fields must be numeric")

    n, p, k, temperature, humidity, ph, rainfall = values
    if not (0 <= humidity <= 100):
        raise ValueError("humidity must be between 0 and 100")
    if not (0 <= ph <= 14):
        raise ValueError("ph must be between 0 and 14")
    if rainfall < 0:
        raise ValueError("rainfall must be >= 0")

    return values

def get_crop_advice(crop_name, language="en"):
    crop = str(crop_name).lower()

    advice_map = {
        "en": {
            "rice": {
                "fertilizer": "Apply balanced NPK fertilizer with higher nitrogen content. Use 120-150 kg N, 60-80 kg P2O5, and 40-60 kg K2O per hectare. Split nitrogen application: 50% at transplanting, 25% at tillering, and 25% at panicle initiation stage.",
                "irrigation": "Maintain 2-5 cm standing water throughout the growing season. Drain field 10-15 days before harvest. Critical irrigation stages: transplanting, tillering, flowering, and grain filling. Avoid water stress during flowering.",
                "season": "Kharif (June-November) is optimal for monsoon rice. Rabi season (November-April) suitable for irrigated areas. Summer rice (March-June) possible with assured irrigation.",
                "advice": "Use disease-resistant varieties like Swarna, IR64, or MTU1010. Maintain 20x15 cm spacing. Control weeds within first 30 days. Watch for blast disease, stem borer, and leaf folder. Apply zinc sulfate if leaves turn yellow. Harvest when 80% grains turn golden yellow."
            },
            "wheat": {
                "fertilizer": "Apply 120 kg N, 60 kg P2O5, and 40 kg K2O per hectare. Use full dose of P and K at sowing. Split nitrogen: 50% at sowing, 25% at first irrigation (21 days), 25% at second irrigation (40 days). Add 25 kg zinc sulfate per hectare if deficient.",
                "irrigation": "Requires 4-6 irrigations. Critical stages: crown root initiation (21 days), tillering (40 days), jointing (60 days), flowering (80 days), milk stage (100 days), and dough stage (115 days). Each irrigation should be 5-7 cm depth.",
                "season": "Rabi season (November-April) is ideal. Sow between November 1-30 for optimal yield. Late sowing reduces yield by 1% per day after November 30. Requires cool weather during vegetative growth and warm weather during grain filling.",
                "advice": "Use certified seeds of varieties like HD2967, PBW343, or DBW17. Seed rate: 100 kg/ha for timely sowing, 125 kg/ha for late sowing. Maintain row spacing of 20-23 cm. Control weeds at 30-35 days. Monitor for rust diseases, aphids, and termites. Harvest when moisture content is 20-25%."
            },
            "maize": {
                "fertilizer": "Apply 150 kg N, 60 kg P2O5, and 40 kg K2O per hectare. Full P and K at sowing. Split nitrogen: 50% at sowing, 25% at knee-high stage (30 days), 25% at tasseling (45 days). Apply 25 kg ZnSO4 and 12 kg FeSO4 per hectare.",
                "irrigation": "Critical irrigation at knee-high stage, tasseling, silking, and grain filling. Requires 500-800 mm water throughout season. Avoid water stress during flowering as it severely affects pollination and grain formation. Irrigate every 10-12 days in absence of rain.",
                "season": "Kharif (June-October) and Rabi (November-March) seasons. Spring maize (February-May) in hills. Requires 21-27°C temperature and 50-75 cm rainfall. Frost sensitive, avoid areas with temperature below 10°C.",
                "advice": "Use hybrid varieties like DHM117, HQPM1, or Vivek Maize Hybrid 9. Maintain 60x20 cm spacing. Keep field weed-free for first 40 days. Control fall armyworm, stem borer, and shoot fly. Apply earthing up at 30 days. Harvest when grain moisture is 20-22%. Dry to 14% moisture for storage."
            },
            "cotton": {
                "fertilizer": "Apply 120 kg N, 60 kg P2O5, and 60 kg K2O per hectare. Full P and K at sowing. Split nitrogen: 25% at sowing, 25% at square formation (45 days), 25% at flowering (75 days), 25% at boll development (105 days). Foliar spray of micronutrients at flowering.",
                "irrigation": "Requires 8-10 irrigations. Critical stages: square formation, flowering, and boll development. Avoid water stress during flowering and boll formation. Each irrigation 6-8 cm depth. Stop irrigation 15-20 days before final picking.",
                "season": "Warm season crop requiring 180-200 frost-free days. Sow in April-May in North India, June-July in South India. Requires 21-27°C temperature and 50-100 cm rainfall. Sensitive to frost and waterlogging.",
                "advice": "Use Bt cotton varieties for bollworm resistance. Maintain 90x60 cm spacing for hybrids, 60x30 cm for varieties. Scout regularly for pink bollworm, whitefly, and jassids. Remove and destroy infected plant parts. Apply growth regulators if excessive vegetative growth. Pick bolls when fully opened. Multiple pickings at 15-day intervals."
            },
            "sugarcane": {
                "fertilizer": "Apply 250-300 kg N, 100-125 kg P2O5, and 100-125 kg K2O per hectare. Full P and K at planting. Split nitrogen: 25% at planting, 25% at 45 days, 25% at 90 days, 25% at 120 days. Apply 25 kg ZnSO4 and 50 kg FeSO4 per hectare.",
                "irrigation": "Requires 20-25 irrigations throughout 12-month crop period. Critical stages: germination, tillering, grand growth, and maturity. Irrigate every 7-10 days in summer, 12-15 days in winter. Avoid water stress during grand growth phase (4-7 months). Stop irrigation 3-4 weeks before harvest.",
                "season": "Plant in spring (February-March) or autumn (September-October). Spring planting gives higher yield. Requires 20-26°C temperature and 150-250 cm rainfall. Frost damages crop, waterlogging reduces yield.",
                "advice": "Use disease-free seed cane of varieties like Co0238, Co86032, or CoLk94184. Plant 3-bud setts at 75-90 cm row spacing. Earthing up at 90-120 days. Control early shoot borer, top borer, and red rot disease. Trash mulching conserves moisture. Harvest at 10-12 months when Brix reaches 18-20%. Ratooning possible for 3-4 crops."
            },
        },
    }

    lang_advice = advice_map.get(language, advice_map["en"])
    return lang_advice.get(crop, {"fertilizer": "Apply nutrients based on soil test.", "irrigation": "Use crop-stage irrigation.", "season": "Follow local advisories.", "advice": "Monitor pests."})

yield_model = None
fertilizer_system = None
soil_classifier = None
weather_predictor = None
price_predictor = None

try:
    yield_model = YieldPredictionModel() if YieldPredictionModel else None
    if yield_model:
        try:
            yield_model_path = os.path.join(backend_dir, "yield_model.pkl")
            yield_model.model = pickle.load(open(yield_model_path, "rb"))
        except:
            pass
except:
    pass

try:
    fertilizer_system = FertilizerRecommendation() if FertilizerRecommendation else None
except:
    pass

try:
    soil_classifier = SoilHealthClassifier() if SoilHealthClassifier else None
except:
    pass

try:
    weather_predictor = WeatherBasedPrediction() if WeatherBasedPrediction else None
except:
    pass

try:
    price_predictor = CropPricePrediction() if CropPricePrediction else None
    if price_predictor:
        try:
            price_model_path = os.path.join(backend_dir, "price_model.pkl")
            loaded_price_obj = pickle.load(open(price_model_path, "rb"))
            if hasattr(loaded_price_obj, "predict_future_prices") and hasattr(loaded_price_obj, "analyze_price_trend"):
                price_predictor = loaded_price_obj
            else:
                price_predictor.model = loaded_price_obj
        except:
            pass
except:
    pass

cv_image_model = None
cv_model_error = None
if cv_model_available and CropImageCVModel:
    try:
        cv_model_path = os.path.join(backend_dir, "crop_image_model.pkl")
        if os.path.exists(cv_model_path):
            cv_image_model = CropImageCVModel.load(cv_model_path)
            print(f"Successfully loaded CV model from: {cv_model_path}")
        else:
            cv_model_error = f"CV model file not found at: {cv_model_path}. Run: python train_cv_model.py --dataset-dir backend/image_dataset"
            print(f"ERROR: {cv_model_error}")
    except Exception as e:
        cv_model_error = f"Failed to load CV model: {str(e)}"
        print(f"ERROR: {cv_model_error}")
        cv_image_model = None

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
    """)
    
    cursor.execute("PRAGMA table_info(users)")
    existing_user_columns = {row[1] for row in cursor.fetchall()}
    
    location_columns = {
        "latitude": "REAL",
        "longitude": "REAL",
        "district": "TEXT",
        "state": "TEXT",
        "city": "TEXT",
        "formatted_address": "TEXT",
        "location_updated_at": "DATETIME"
    }
    
    for column_name, column_type in location_columns.items():
        if column_name not in existing_user_columns:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {column_name} {column_type}")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            crop TEXT,
            n REAL,
            p REAL,
            k REAL,
            temperature REAL,
            humidity REAL,
            ph REAL,
            rainfall REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS price_analysis (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            crop TEXT,
            current_price REAL,
            trend TEXT,
            change_percentage REAL,
            recommendation TEXT,
            future_prices TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("PRAGMA table_info(predictions)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    required_columns = {
        "n": "REAL",
        "p": "REAL",
        "k": "REAL",
        "temperature": "REAL",
        "humidity": "REAL",
        "ph": "REAL",
        "rainfall": "REAL",
    }
    for column_name, column_type in required_columns.items():
        if column_name not in existing_columns:
            cursor.execute(f"ALTER TABLE predictions ADD COLUMN {column_name} {column_type}")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            message TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    conn.commit()
    conn.close()

init_db()

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "email and password are required"}), 400
    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (email, password) VALUES (?,?)", (email, hashed))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({"msg": "User already exists"}), 409
    conn.close()

    return jsonify({"msg": "User registered successfully"})

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = data.get("email")
    password = data.get("password")
    if not email or not password:
        return jsonify({"msg": "email and password are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE email=?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user and bcrypt.check_password_hash(user[2], password):
        access_token = create_access_token(identity=email)
        return jsonify(access_token=access_token)

    return jsonify({"msg": "Invalid credentials"}), 401

@app.route("/api/translate", methods=["POST"])
@jwt_required()
def translate():
    data = request.get_json(silent=True) or {}
    text = data.get("text", "")
    from_lang = data.get("from", "en")
    to_lang = data.get("to", "hi")

    if not text:
        return jsonify({"error": "text is required"}), 400

    if from_lang not in ["en", "hi", "te", "ta"]:
        return jsonify({"error": "Unsupported source language. Supported: en, hi, te, ta"}), 400

    if to_lang not in ["en", "hi", "te", "ta"]:
        return jsonify({"error": "Unsupported target language. Supported: en, hi, te, ta"}), 400

    try:
        if translation_available:
            translated_text = translate_text(text, from_lang, to_lang)
        else:
            translated_text = text
        return jsonify({
            "original_text": text,
            "translated_text": translated_text,
            "from_language": from_lang,
            "to_language": to_lang
        })
    except Exception as e:
        return jsonify({"error": f"Translation failed: {str(e)}"}), 500

@app.route("/api/analyze-crop", methods=["POST"])
@jwt_required(optional=True)
def analyze_crop_image():
    try:
        print("\n=== ANALYZE-CROP REQUEST ===")
        print(f"Content-Type: {request.content_type}")
        print(f"Method: {request.method}")

        try:
            data = request.get_json(force=True)
        except Exception as json_error:
            print(f"JSON parsing error: {json_error}")
            return jsonify({"error": f"Invalid JSON: {str(json_error)}"}), 400

        if not data:
            print("Error: No JSON data received")
            return jsonify({"error": "No data received. Please send JSON with 'image' field."}), 400

        print(f"Received data keys: {list(data.keys())}")

        image_data = data.get("image")
        language = data.get("language", "en")

        if not image_data:
            print("Error: No image field in request")
            return jsonify({"error": "'image' field is required in request body"}), 400

        if not isinstance(image_data, str):
            print(f"Error: Image data is not a string, type: {type(image_data)}")
            return jsonify({"error": "Image data must be a base64 string"}), 400

        if len(image_data) < 100:
            print(f"Error: Image data too short: {len(image_data)} characters")
            return jsonify({"error": "Image data is too short. Please provide a valid base64 encoded image."}), 400

        print(f"Image data length: {len(image_data)} characters")
        print(f"Image data starts with: {image_data[:50]}...")
        print(f"Language: {language}")

        # STEP 1: Validate if image is a crop image
        from modern_crop_validator import get_validator
        validator = get_validator()
        validation_result = validator.validate_from_base64(image_data)
        
        print(f"Validation result: {validation_result}")
        
        if not validation_result.get('valid', False):
            print(f"REJECTED: {validation_result.get('reason', 'Invalid image')}")
            return jsonify({
                "error": validation_result.get('message', 'Invalid input: Please upload only crop or plant images.'),
                "reason": validation_result.get('reason', 'Non-crop image detected'),
                "confidence": validation_result.get('confidence', 0)
            }), 400

        # STEP 2: Proceed with crop classification
        if cv_image_model is None:
            print("Error: CV model is None")
            error_msg = cv_model_error if cv_model_error else "Image model not loaded. Please contact administrator."
            return jsonify({
                "error": error_msg,
                "model_loaded": False
            }), 503

        print("Image validated as crop. Calling cv_image_model.predict_from_base64...")
        pred = cv_image_model.predict_from_base64(image_data)
        print(f"Prediction result: {pred}")

        crop_name = pred["label"]
        confidence = pred["confidence"]

        print(f"Detected: {crop_name} with confidence: {confidence}%")

        if confidence < 20:
            print(f"REJECTED: Confidence {confidence}% is below 20% threshold")
            return jsonify({
                "error": "⚠️ Image quality too low. Please upload a clear photo.",
                "detected": crop_name,
                "confidence": confidence
            }), 400

        valid_crops = ['rice', 'wheat', 'maize', 'corn', 'cotton', 'sugarcane', 'chickpea', 
                      'kidneybeans', 'pigeonpeas', 'mothbeans', 'mungbean', 'blackgram', 
                      'lentil', 'pomegranate', 'banana', 'mango', 'grapes', 'watermelon', 
                      'muskmelon', 'apple', 'orange', 'papaya', 'coconut', 'jute', 'coffee']

        if crop_name.lower() not in valid_crops:
            return jsonify({
                "error": f"Detected '{crop_name}' is not a supported crop. Please upload images of crops like rice, wheat, maize, cotton, fruits, or vegetables.",
                "detected": crop_name,
                "confidence": confidence,
                "supported_crops": "rice, wheat, maize, cotton, sugarcane, chickpea, beans, lentils, fruits"
            }), 400

        info = get_crop_advice(crop_name, language)

        result = {
            "detected_crop": crop_name,
            "confidence": confidence,
            "fertilizer": info["fertilizer"],
            "irrigation": info["irrigation"],
            "season": info["season"],
            "advice": info["advice"],
            "model_loaded": True
        }
        print(f"Success! Returning result for: {crop_name}")
        print("=== END REQUEST ===\n")

        return jsonify(result)

    except Exception as e:
        print(f"\n!!! EXCEPTION in analyze_crop_image !!!")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        print("=== END REQUEST ===\n")
        return jsonify({
            "error": f"Unable to process image: {str(e)}",
            "hint": "Make sure the image is a valid crop photo"
        }), 500

@app.route('/api/comprehensive-analysis', methods=['POST'])
@jwt_required(optional=True)
def comprehensive_analysis():
    try:
        data = request.get_json(silent=True) or {}
        
        if not data or not any(k in data for k in FEATURE_KEYS):
            from routes.predict import predict_fully_auto
            return predict_fully_auto()
        
        n, p, k, temperature, humidity, ph, rainfall = parse_feature_payload(data)
        
        from multi_crop_analyzer import get_multi_crop_analyzer
        from profit_analyzer import get_profit_analyzer
        
        analyzer = get_multi_crop_analyzer(model_path)
        profit_analyzer = get_profit_analyzer()
        
        # Get multi-crop analysis
        result = analyzer.analyze_crops(n, p, k, temperature, humidity, ph, rainfall, top_k=10)
        
        # Prepare crop probabilities for profit analysis
        crop_probs = [(crop['crop'], crop['soil_suitability']/100) for crop in result['top_crops']]
        
        # Get current price data
        price_data = {
            'rice': {'avg_price': 2530, 'avg_yield': 5.0},
            'wheat': {'avg_price': 2120, 'avg_yield': 4.5},
            'maize': {'avg_price': 1870, 'avg_yield': 6.0},
            'cotton': {'avg_price': 6250, 'avg_yield': 2.5},
            'chickpea': {'avg_price': 4750, 'avg_yield': 2.5},
            'kidneybeans': {'avg_price': 6200, 'avg_yield': 2.0},
            'pigeonpeas': {'avg_price': 5200, 'avg_yield': 1.8},
            'mungbean': {'avg_price': 6200, 'avg_yield': 1.2},
            'blackgram': {'avg_price': 5700, 'avg_yield': 1.0},
            'lentil': {'avg_price': 5000, 'avg_yield': 1.5}
        }
        
        # Get profit analysis for top 3 seasonal crops
        profit_analysis = profit_analyzer.analyze_top_3_crops(crop_probs, price_data)
        
        # Store best crop
        best_crop = profit_analysis['top_3_crops'][0]['crop'] if profit_analysis['top_3_crops'] else 'rice'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) VALUES (?,?,?,?,?,?,?,?,?)",
            ("guest", best_crop, n, p, k, temperature, humidity, ph, rainfall)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'analysis_type': 'profit_comparison',
            'season': profit_analysis['season'],
            'top_3_recommendations': profit_analysis['top_3_crops'],
            'comparison_summary': profit_analysis['comparison_summary'],
            'all_crops': result['top_crops'],
            'analysis_date': result['analysis_date']
        })
        
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history', methods=['GET'])
@jwt_required()
def get_history():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT crop, n, p, k, temperature, humidity, ph, rainfall, timestamp FROM predictions ORDER BY timestamp DESC LIMIT 50")
    rows = cursor.fetchall()
    conn.close()

    predictions = [{
        'crop': row[0],
        'n': row[1],
        'p': row[2],
        'k': row[3],
        'temperature': row[4],
        'humidity': row[5],
        'ph': row[6],
        'rainfall': row[7],
        'timestamp': row[8]
    } for row in rows]

    return jsonify({'predictions': predictions})

@app.route('/api/detect-disease', methods=['POST'])
@jwt_required(optional=True)
def detect_disease():
    if not disease_detector:
        return jsonify({'error': 'Disease detection not available'}), 503

    try:
        data = request.get_json(force=True)
        image_data = data.get('image')

        if not image_data:
            return jsonify({'error': 'Image required'}), 400

        result = disease_detector.predict_from_base64(image_data)

        if 'error' in result:
            return jsonify(result), 400

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/llm-advice', methods=['POST'])
@jwt_required(optional=True)
def llm_advice():
    if not llm_advisor:
        return jsonify({'error': 'LLM advisor not available'}), 503

    try:
        data = request.get_json()
        crop = data.get('crop')
        soil_data = data.get('soil_data', {})
        weather_data = data.get('weather_data', {})
        language = data.get('language', 'en')

        advice = llm_advisor.get_farming_advice(crop, soil_data, weather_data, language)

        return jsonify({
            'advice': advice,
            'provider': llm_advisor.provider,
            'crop': crop
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/explain-fertilizer', methods=['POST'])
@jwt_required(optional=True)
def explain_fertilizer():
    if not llm_advisor:
        return jsonify({'error': 'LLM advisor not available'}), 503

    try:
        data = request.get_json()
        npk_values = data.get('npk', {})
        crop = data.get('crop', 'crops')
        language = data.get('language', 'en')

        explanation = llm_advisor.explain_fertilizer(npk_values, crop, language)

        return jsonify({
            'explanation': explanation,
            'provider': llm_advisor.provider
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ask-question', methods=['POST'])
@jwt_required(optional=True)
def ask_question():
    if not llm_advisor:
        return jsonify({'error': 'LLM advisor not available'}), 503

    try:
        data = request.get_json()
        question = data.get('question')
        context = data.get('context', {})
        language = data.get('language', 'en')

        if not question:
            return jsonify({'error': 'Question required'}), 400

        answer = llm_advisor.answer_question(question, context, language)

        return jsonify({
            'answer': answer,
            'question': question,
            'provider': llm_advisor.provider
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rag-chat', methods=['POST'])
@jwt_required(optional=True)
def rag_chat():
    if not rag_chatbot:
        return jsonify({'error': 'RAG chatbot not available'}), 503

    try:
        data = request.get_json()
        question = data.get('question')
        language = data.get('language', 'en')

        if not question:
            return jsonify({'error': 'Question required'}), 400

        result = rag_chatbot.chat(question, language)

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/detect-location', methods=['POST'])
@jwt_required()
def api_detect_location():
    from routes.location import detect_location
    return detect_location()

@app.route('/api/update-location', methods=['PUT'])
@jwt_required()
def api_update_location():
    from routes.location import update_location
    return update_location()

@app.route('/api/get-location', methods=['GET'])
@jwt_required()
def api_get_location():
    from routes.location import get_current_location
    return get_current_location()

@app.route('/api/search-location', methods=['POST'])
def api_search_location():
    from routes.location import search_location
    return search_location()

if __name__ == "__main__":
    app.run(debug=True)

@app.route('/api/price-analysis', methods=['GET'])
@jwt_required(optional=True)
def get_price_analysis():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT crop, current_price, trend, change_percentage, recommendation, future_prices, timestamp FROM price_analysis ORDER BY timestamp DESC LIMIT 10")
    rows = cursor.fetchall()
    conn.close()

    import json
    analyses = [{
        'crop': row[0],
        'current_price': row[1],
        'trend': row[2],
        'change_percentage': row[3],
        'recommendation': row[4],
        'future_prices': json.loads(row[5]) if row[5] else [],
        'timestamp': row[6]
    } for row in rows]

    return jsonify({'price_analyses': analyses})

@app.route('/api/chat-history', methods=['GET'])
@jwt_required()
def get_chat_history():
    user_email = get_jwt_identity()
    language = request.args.get('language', 'en')
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT message, response FROM chat_messages WHERE user_email = ? ORDER BY timestamp ASC",
            (user_email,)
        )
        rows = cursor.fetchall()
        conn.close()
        
        history = []
        for row in rows:
            history.append({"text": row[0], "sender": "user"})
            history.append({"text": row[1], "sender": "bot"})
        
        return jsonify({"history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/chat-history', methods=['DELETE'])
@jwt_required()
def delete_chat_history():
    user_email = get_jwt_identity()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM chat_messages WHERE user_email = ?", (user_email,))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/multi-crop-analysis', methods=['POST'])
@jwt_required(optional=True)
def multi_crop_analysis():
    """Multi-crop analysis with comparison and ranking"""
    try:
        data = request.get_json(silent=True) or {}
        n, p, k, temperature, humidity, ph, rainfall = parse_feature_payload(data)
        
        from multi_crop_analyzer import get_multi_crop_analyzer
        analyzer = get_multi_crop_analyzer(model_path)
        
        result = analyzer.analyze_crops(n, p, k, temperature, humidity, ph, rainfall, top_k=10)
        
        return jsonify({
            'success': True,
            'best_crop': result['best_recommendation'],
            'top_crops': result['top_crops'],
            'alternatives': result['alternatives'],
            'recommendation': result['recommendation_text'],
            'analysis_date': result['analysis_date']
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics-data', methods=['GET'])
@jwt_required(optional=True)
def get_analytics_data():
    """Get 2-year historical analytics data with seasonal analysis"""
    try:
        from datetime import datetime
        current_month = datetime.now().month
        
        # Determine current season
        if 6 <= current_month <= 10:
            season = 'kharif'
        elif 11 <= current_month or current_month <= 3:
            season = 'rabi'
        else:
            season = 'zaid'
        
        months = ['Jan 23', 'Apr 23', 'Jul 23', 'Oct 23', 'Jan 24', 'Apr 24', 'Jul 24', 'Oct 24']
        
        # Expanded crop data with seasonal information
        all_crops_data = {
            'rice': {'prices': [2400, 2450, 2500, 2480, 2520, 2550, 2500, 2530], 'season': 'kharif', 'yield': 5.0},
            'wheat': {'prices': [1950, 2000, 1980, 2020, 2050, 2100, 2080, 2120], 'season': 'rabi', 'yield': 4.5},
            'maize': {'prices': [1750, 1800, 1820, 1850, 1880, 1900, 1850, 1870], 'season': 'kharif', 'yield': 6.0},
            'cotton': {'prices': [5800, 5900, 6000, 6100, 6050, 6200, 6150, 6250], 'season': 'kharif', 'yield': 2.5},
            'chickpea': {'prices': [4300, 4400, 4500, 4550, 4600, 4650, 4700, 4750], 'season': 'rabi', 'yield': 2.5},
            'kidneybeans': {'prices': [5800, 5900, 6000, 6050, 6100, 6150, 6100, 6200], 'season': 'kharif', 'yield': 2.0},
            'pigeonpeas': {'prices': [4800, 4900, 5000, 5050, 5100, 5150, 5100, 5200], 'season': 'kharif', 'yield': 1.8},
            'mungbean': {'prices': [5800, 5900, 6000, 6050, 6100, 6150, 6100, 6200], 'season': 'kharif', 'yield': 1.2},
            'blackgram': {'prices': [5300, 5400, 5500, 5550, 5600, 5650, 5600, 5700], 'season': 'kharif', 'yield': 1.0},
            'lentil': {'prices': [4600, 4700, 4800, 4850, 4900, 4950, 4900, 5000], 'season': 'rabi', 'yield': 1.5},
            'banana': {'prices': [1400, 1450, 1500, 1480, 1520, 1550, 1500, 1530], 'season': 'perennial', 'yield': 40.0},
            'mango': {'prices': [3300, 3400, 3500, 3550, 3600, 3650, 3600, 3700], 'season': 'perennial', 'yield': 10.0},
            'grapes': {'prices': [3800, 3900, 4000, 4050, 4100, 4150, 4100, 4200], 'season': 'perennial', 'yield': 20.0},
            'watermelon': {'prices': [750, 800, 820, 800, 850, 880, 850, 900], 'season': 'zaid', 'yield': 30.0},
            'muskmelon': {'prices': [1100, 1150, 1200, 1180, 1220, 1250, 1200, 1280], 'season': 'zaid', 'yield': 25.0},
            'apple': {'prices': [5800, 5900, 6000, 6050, 6100, 6150, 6100, 6200], 'season': 'perennial', 'yield': 12.0},
            'orange': {'prices': [1900, 1950, 2000, 1980, 2020, 2050, 2000, 2080], 'season': 'perennial', 'yield': 15.0},
            'papaya': {'prices': [1700, 1750, 1800, 1780, 1820, 1850, 1800, 1880], 'season': 'perennial', 'yield': 50.0},
            'coconut': {'prices': [2400, 2450, 2500, 2480, 2520, 2550, 2500, 2600], 'season': 'perennial', 'yield': 80.0},
            'jute': {'prices': [3400, 3450, 3500, 3480, 3520, 3550, 3500, 3580], 'season': 'kharif', 'yield': 2.0},
            'coffee': {'prices': [7800, 7900, 8000, 8050, 8100, 8150, 8100, 8200], 'season': 'perennial', 'yield': 1.5}
        }
        
        # Build price trends
        price_trends = []
        for i, month in enumerate(months):
            trend_data = {'month': month}
            for crop, data in all_crops_data.items():
                trend_data[crop] = data['prices'][i]
            price_trends.append(trend_data)
        
        # Build crop comparison with seasonal filtering
        crop_comparison = []
        for crop, data in all_crops_data.items():
            current_price = data['prices'][-1]
            crop_yield = data['yield']
            profit = current_price * crop_yield
            
            # Calculate trend
            price_change = ((data['prices'][-1] - data['prices'][0]) / data['prices'][0]) * 100
            if price_change > 5:
                trend = 'rising'
            elif price_change < -5:
                trend = 'falling'
            else:
                trend = 'stable'
            
            crop_comparison.append({
                'crop': crop.capitalize(),
                'price': current_price,
                'yield': crop_yield,
                'profit': int(profit),
                'trend': trend,
                'season': data['season'],
                'suitable_now': data['season'] == season or data['season'] == 'perennial'
            })
        
        # Sort by profitability
        crop_comparison.sort(key=lambda x: x['profit'], reverse=True)
        
        return jsonify({
            'price_trends': price_trends,
            'crop_comparison': crop_comparison,
            'current_season': season,
            'total_crops': len(crop_comparison)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500