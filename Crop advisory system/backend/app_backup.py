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
except Exception:
    YieldPredictionModel = None
    yield_model_available = False

try:
    from fertilizer_recommendation import FertilizerRecommendation
    fertilizer_available = True
except Exception:
    FertilizerRecommendation = None
    fertilizer_available = False

try:
    from soil_health import SoilHealthClassifier
    soil_available = True
except Exception:
    SoilHealthClassifier = None
    soil_available = False

try:
    from weather_prediction import WeatherBasedPrediction
    weather_available = True
except Exception:
    WeatherBasedPrediction = None
    weather_available = False

try:
    from price_prediction import CropPricePrediction
    price_available = True
except Exception:
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
        print("✅ CNN Disease Detector loaded")
    except:
        disease_detector = SimpleDiseaseDetector()
        print("⚠️ Using fallback disease detector")
except Exception as e:
    disease_detector = None
    print(f"❌ Disease detection unavailable: {e}")

try:
    from llm_advisor import get_llm_instance
    llm_advisor = get_llm_instance()
    print(f"✅ LLM Advisor initialized: {llm_advisor.provider}")
except Exception as e:
    llm_advisor = None
    print(f"❌ LLM unavailable: {e}")

try:
    from rag_chatbot import get_rag_chatbot
    rag_chatbot = get_rag_chatbot()
    print("✅ RAG Chatbot initialized")
except Exception as e:
    rag_chatbot = None
    print(f"⚠️ RAG unavailable: {e}")

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
            "rice": {"fertilizer": "Apply balanced NPK with higher nitrogen.", "irrigation": "Maintain moist field conditions.", "season": "Kharif (monsoon) is optimal.", "advice": "Use disease-resistant varieties."},
            "wheat": {"fertilizer": "Use nitrogen split doses; apply phosphorus at sowing.", "irrigation": "Irrigate at crown-root initiation.", "season": "Rabi season is suitable.", "advice": "Monitor rust and aphids."},
            "maize": {"fertilizer": "Apply starter phosphorus and nitrogen.", "irrigation": "Critical at tasseling.", "season": "Kharif and Rabi.", "advice": "Keep field weed-free."},
            "cotton": {"fertilizer": "Use balanced NPK.", "irrigation": "Irrigate at flowering.", "season": "Warm season best.", "advice": "Scout for bollworms."},
            "sugarcane": {"fertilizer": "Heavy nitrogen with P and K.", "irrigation": "Frequent irrigation needed.", "season": "Spring or autumn.", "advice": "Harvest at proper maturity."},
            "chickpea": {"fertilizer": "Apply phosphorus and potassium.", "irrigation": "Light irrigation needed.", "season": "Rabi season.", "advice": "Control pod borer."},
            "kidneybeans": {"fertilizer": "Moderate NPK application.", "irrigation": "Regular watering.", "season": "Kharif season.", "advice": "Provide support for climbing."},
            "pigeonpeas": {"fertilizer": "Low nitrogen, high phosphorus.", "irrigation": "Drought tolerant.", "season": "Kharif season.", "advice": "Intercrop with cereals."},
            "mothbeans": {"fertilizer": "Minimal fertilizer needed.", "irrigation": "Drought resistant.", "season": "Kharif season.", "advice": "Good for arid regions."},
            "mungbean": {"fertilizer": "Phosphorus and potassium.", "irrigation": "Moderate watering.", "season": "Kharif and summer.", "advice": "Short duration crop."},
            "blackgram": {"fertilizer": "Phosphorus rich fertilizer.", "irrigation": "Light irrigation.", "season": "Kharif and Rabi.", "advice": "Suitable for intercropping."},
            "lentil": {"fertilizer": "Phosphorus and potassium.", "irrigation": "Minimal irrigation.", "season": "Rabi season.", "advice": "Cold tolerant crop."},
            "pomegranate": {"fertilizer": "Balanced NPK with micronutrients.", "irrigation": "Drip irrigation ideal.", "season": "Year-round.", "advice": "Prune regularly."},
            "banana": {"fertilizer": "High potassium requirement.", "irrigation": "Heavy watering needed.", "season": "Year-round.", "advice": "Protect from wind."},
            "mango": {"fertilizer": "NPK with zinc and boron.", "irrigation": "Moderate watering.", "season": "Year-round.", "advice": "Control fruit fly."},
            "grapes": {"fertilizer": "Potassium and calcium rich.", "irrigation": "Drip irrigation.", "season": "Year-round.", "advice": "Trellising required."},
            "watermelon": {"fertilizer": "High nitrogen initially.", "irrigation": "Regular watering.", "season": "Summer.", "advice": "Mulching recommended."},
            "muskmelon": {"fertilizer": "Balanced NPK.", "irrigation": "Consistent moisture.", "season": "Summer.", "advice": "Good drainage needed."},
            "apple": {"fertilizer": "Nitrogen and potassium.", "irrigation": "Regular watering.", "season": "Temperate climate.", "advice": "Requires chilling hours."},
            "orange": {"fertilizer": "Nitrogen rich fertilizer.", "irrigation": "Regular irrigation.", "season": "Year-round.", "advice": "Control citrus canker."},
            "papaya": {"fertilizer": "High nitrogen and potassium.", "irrigation": "Frequent watering.", "season": "Year-round.", "advice": "Protect from frost."},
            "coconut": {"fertilizer": "High potassium and chlorine.", "irrigation": "Regular watering.", "season": "Year-round.", "advice": "Coastal areas ideal."},
            "jute": {"fertilizer": "Nitrogen and phosphorus.", "irrigation": "High water requirement.", "season": "Kharif season.", "advice": "Waterlogged conditions."},
            "coffee": {"fertilizer": "Organic matter rich.", "irrigation": "Moderate watering.", "season": "Year-round.", "advice": "Shade required."},
        },
    }

    lang_advice = advice_map.get(language, advice_map["en"])
    return lang_advice.get(crop, {"fertilizer": "Apply nutrients based on soil test.", "irrigation": "Use crop-stage irrigation.", "season": "Follow local advisories.", "advice": "Monitor pests."})

yield_model = YieldPredictionModel() if YieldPredictionModel else None
fertilizer_system = FertilizerRecommendation() if FertilizerRecommendation else None
soil_classifier = SoilHealthClassifier() if SoilHealthClassifier else None
weather_predictor = WeatherBasedPrediction() if WeatherBasedPrediction else None
price_predictor = CropPricePrediction() if CropPricePrediction else None

if yield_model:
    try:
        yield_model_path = os.path.join(backend_dir, "yield_model.pkl")
        yield_model.model = pickle.load(open(yield_model_path, "rb"))
    except:
        pass

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

@app.route("/register", methods=["POST"])
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

@app.route("/login", methods=["POST"])
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

@app.route("/translate", methods=["POST"])
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

@app.route("/analyze-crop", methods=["POST"])
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

        if cv_image_model is None:
            print("Error: CV model is None")
            error_msg = cv_model_error if cv_model_error else "Image model not loaded. Please contact administrator."
            return jsonify({
                "error": error_msg,
                "model_loaded": False
            }), 503

        print("Calling cv_image_model.predict_from_base64...")
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
def comprehensive_analysis():
    try:
        data = request.get_json(silent=True) or {}
        n, p, k, temperature, humidity, ph, rainfall = parse_feature_payload(data)

        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        crop_pred = model.predict(features)[0]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO predictions (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) VALUES (?,?,?,?,?,?,?,?,?)",
            ("guest", crop_pred, n, p, k, temperature, humidity, ph, rainfall)
        )
        conn.commit()
        conn.close()

        if soil_classifier:
            soil_health_result = soil_classifier.classify_soil_health(n, p, k, ph)
        else:

            n_score = min(100, (n / 100) * 100)
            p_score = min(100, (p / 60) * 100)
            k_score = min(100, (k / 60) * 100)
            ph_score = 100 if 6.0 <= ph <= 7.5 else max(0, 100 - abs(ph - 6.75) * 20)
            health_score = (n_score + p_score + k_score + ph_score) / 4
            health_class = "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair" if health_score >= 40 else "Poor"
            soil_health_result = {
                'health_class': health_class,
                'health_score': round(health_score, 2),
                'component_scores': {'nitrogen': n_score, 'phosphorus': p_score, 'potassium': k_score},
                'recommendations': ['Improve soil health with organic matter'] if health_score < 60 else ['Maintain current practices']
            }

        if fertilizer_system:
            fertilizer_rec = fertilizer_system.analyze_soil(n, p, k, ph)
        else:

            fertilizer_rec = []
            if n < 50:
                fertilizer_rec.append({'nutrient': 'Nitrogen', 'fertilizer': 'Urea', 'quantity': '50-100 kg/hectare'})
            if p < 30:
                fertilizer_rec.append({'nutrient': 'Phosphorus', 'fertilizer': 'DAP', 'quantity': '40-80 kg/hectare'})
            if k < 30:
                fertilizer_rec.append({'nutrient': 'Potassium', 'fertilizer': 'MOP', 'quantity': '30-60 kg/hectare'})
            if not fertilizer_rec:
                fertilizer_rec.append({'nutrient': 'Balanced', 'fertilizer': 'NPK 10:10:10', 'quantity': 'Maintenance dose'})

        yield_prediction = None
        if yield_model and hasattr(yield_model, 'model') and yield_model.model is not None:
            try:
                predicted_yield = yield_model.model.predict(features)[0]
                yield_prediction = {
                    'estimated_yield': round(float(predicted_yield), 2),
                    'unit': 'tons/hectare',
                    'confidence': 'Based on soil and weather conditions'
                }
            except:
                yield_prediction = {'estimated_yield': 'N/A', 'unit': 'tons/hectare', 'confidence': 'Model not available'}

        base_prices = {'rice': 2500, 'wheat': 2000, 'maize': 1800, 'cotton': 6000, 'sugarcane': 3500, 'potato': 1200, 'onion': 1500, 'tomato': 2000, 'chickpea': 4500, 'kidneybeans': 3000, 'pigeonpeas': 5000, 'mothbeans': 4000, 'mungbean': 6000, 'blackgram': 5500, 'lentil': 4800, 'pomegranate': 3500, 'banana': 1500, 'mango': 2500, 'grapes': 4000, 'watermelon': 800, 'muskmelon': 1200, 'apple': 6000, 'orange': 2000, 'papaya': 1800, 'coconut': 2500, 'jute': 3500, 'coffee': 8000}
        base_price = base_prices.get(crop_pred.lower(), 2000)
        seed_source = f"{crop_pred}|{n:.2f}|{p:.2f}|{k:.2f}|{temperature:.2f}|{humidity:.2f}|{ph:.2f}|{rainfall:.2f}"
        seed = int(hashlib.md5(seed_source.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        price_history = np.array([base_price + int(rng.integers(-200, 201)) for _ in range(40)])
        price_analysis = None

        if price_predictor and hasattr(price_predictor, 'analyze_price_trend') and hasattr(price_predictor, 'predict_future_prices'):
            try:
                if not hasattr(price_predictor, 'model') or price_predictor.model is None:
                    price_predictor.train_price_model(price_history)

                trend_analysis = price_predictor.analyze_price_trend(price_history)
                future_prices = price_predictor.predict_future_prices(price_history, days=7)
                price_analysis = {
                    'current_price': trend_analysis.get('current_price', base_price),
                    'trend': trend_analysis.get('trend', 'Stable'),
                    'change_percentage': trend_analysis.get('change_percentage', 0),
                    'recommendation': trend_analysis.get('recommendation', 'Market stable'),
                    'future_prices': [round(float(p), 2) for p in future_prices[:5]]
                }

                import json
                cursor.execute(
                    "INSERT INTO price_analysis (user_email, crop, current_price, trend, change_percentage, recommendation, future_prices) VALUES (?,?,?,?,?,?,?)",
                    ("guest", crop_pred, price_analysis['current_price'], price_analysis['trend'], price_analysis['change_percentage'], price_analysis['recommendation'], json.dumps(price_analysis['future_prices']))
                )
                conn.commit()
            except Exception:
                price_analysis = {
                    'current_price': base_price,
                    'trend': 'Stable',
                    'change_percentage': 0,
                    'recommendation': 'Unable to analyze market trends',
                    'future_prices': []
                }

        if weather_predictor:
            weather_suitability = weather_predictor.assess_suitability(crop_pred, {'temperature': temperature, 'humidity': humidity, 'rainfall': rainfall})
        else:

            weather_suitability = 'Good' if 15 <= temperature <= 35 and 50 <= humidity <= 90 else 'Fair'

        if fertilizer_system:
            crop_specific_rec = fertilizer_system.get_crop_specific_recommendation(crop_pred, n, p, k)
        else:
            crop_specific_rec = None

        overall_recommendations = []
        if soil_health_result.get('health_class') in ['Poor', 'Fair']:
            overall_recommendations.extend(soil_health_result.get('recommendations', [])[:2])
        if weather_suitability in ['Fair', 'Poor']:
            overall_recommendations.append(f"Weather conditions are {weather_suitability.lower()} for {crop_pred}. Consider alternative crops.")
        if not overall_recommendations:
            overall_recommendations.append(f"Excellent conditions for {crop_pred} cultivation!")

        return jsonify({
            'recommended_crop': crop_pred,
            'soil_health': soil_health_result,
            'fertilizer_recommendations': fertilizer_rec,
            'yield_prediction': yield_prediction,
            'price_analysis': price_analysis,
            'weather_suitability': weather_suitability,
            'crop_specific': crop_specific_rec,
            'overall_recommendations': overall_recommendations,
            'analysis_timestamp': str(datetime.now())
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/history', methods=['GET'])
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