from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from flask_bcrypt import Bcrypt
import sqlite3
import pickle
import numpy as np
import os
from datetime import datetime

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

app = Flask(__name__)
CORS(app)

app.config["JWT_TOKEN_LOCATION"] = ["headers"]
app.config["JWT_HEADER_NAME"] = "Authorization"
app.config["JWT_HEADER_TYPE"] = "Bearer"
app.config["JWT_SECRET_KEY"] = "supersecretkey"
jwt = JWTManager(app)
bcrypt = Bcrypt(app)

# Load ML model - use absolute path based on this file's location
backend_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(backend_dir, "model.pkl")
print(f"Loading model from: {model_path}")
model = pickle.load(open(model_path, "rb"))

yield_model = YieldPredictionModel() if YieldPredictionModel else None
fertilizer_system = FertilizerRecommendation() if FertilizerRecommendation else None
soil_classifier = SoilHealthClassifier() if SoilHealthClassifier else None
weather_predictor = WeatherBasedPrediction() if WeatherBasedPrediction else None
price_predictor = CropPricePrediction() if CropPricePrediction else None

if yield_model:
    try:
        yield_model.model = pickle.load(open(os.path.join(backend_dir, "yield_model.pkl"), "rb"))
    except:
        pass

if price_predictor:
    try:
        price_predictor.model = pickle.load(open(os.path.join(backend_dir, "price_model.pkl"), "rb"))
    except:
        pass

def init_db():
    db_path = os.path.join(backend_dir, "crop.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            password TEXT
        )
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
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_email TEXT,
            message TEXT,
            response TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    try:
        data = request.json

        n = float(data['N'])
        p = float(data['P'])
        k = float(data['K'])
        temperature = float(data['temperature'])
        humidity = float(data['humidity'])
        ph = float(data['ph'])
        rainfall = float(data['rainfall'])

        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        crop_pred = model.predict(features)[0]

        db_path = os.path.join(backend_dir, "crop.db")
        conn = sqlite3.connect(db_path)
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

        price_analysis = None
        if price_predictor and hasattr(price_predictor, 'model') and price_predictor.model is not None and hasattr(price_predictor, 'scaler'):
            base_prices = {'rice': 2500, 'wheat': 2000, 'maize': 1800, 'cotton': 6000, 'sugarcane': 3500, 'potato': 1200, 'onion': 1500, 'tomato': 2000}
            base_price = base_prices.get(crop_pred.lower(), 2000)
            price_history = np.array([base_price + np.random.randint(-200, 200) for _ in range(40)])
            try:
                trend_analysis = price_predictor.analyze_price_trend(price_history)
                future_prices = price_predictor.predict_future_prices(price_history, days=7)
                price_analysis = {
                    'current_price': trend_analysis.get('current_price', base_price),
                    'trend': trend_analysis.get('trend', 'Stable'),
                    'change_percentage': trend_analysis.get('change_percentage', 0),
                    'recommendation': trend_analysis.get('recommendation', 'Market stable'),
                    'future_prices': [round(float(p), 2) for p in future_prices[:5]]
                }
            except:
                price_analysis = {'current_price': base_price, 'trend': 'Stable', 'change_percentage': 0, 'recommendation': 'Unable to analyze market trends', 'future_prices': []}

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
    except Exception as e:
        import traceback
        return jsonify({'error': str(e), 'trace': traceback.format_exc()}), 500

@app.route('/history', methods=['GET'])
@jwt_required()
def get_history():
    db_path = os.path.join(backend_dir, "crop.db")
    conn = sqlite3.connect(db_path)
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

if __name__ == "__main__":
    app.run(debug=True)