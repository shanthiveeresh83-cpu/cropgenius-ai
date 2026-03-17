from flask import Flask, request, jsonify
from flask_cors import CORS
import pickle
import numpy as np
import os
from datetime import datetime
from yield_prediction import YieldPredictionModel
from fertilizer_recommendation import FertilizerRecommendation
from soil_health import SoilHealthClassifier
from weather_prediction import WeatherBasedPrediction
from price_prediction import CropPricePrediction

app = Flask(__name__)
CORS(app)

backend_dir = os.path.dirname(os.path.abspath(__file__))
advanced_model_path = os.path.join(backend_dir, 'advanced_model.pkl')
base_model_path = os.path.join(backend_dir, 'model.pkl')

if os.path.exists(advanced_model_path):
    crop_model = pickle.load(open(advanced_model_path, 'rb'))
else:
    crop_model = pickle.load(open(base_model_path, 'rb'))

fertilizer_system = FertilizerRecommendation()
soil_classifier = SoilHealthClassifier()
weather_predictor = WeatherBasedPrediction()

@app.route('/api/predict-crop', methods=['POST'])
def predict_crop():
    data = request.json
    features = [[
        data['N'], data['P'], data['K'],
        data['temperature'], data['humidity'],
        data['ph'], data['rainfall']
    ]]

    prediction = crop_model.predict(features)[0]
    probability = crop_model.predict_proba(features)[0]

    return jsonify({
        'crop': prediction,
        'confidence': round(max(probability) * 100, 2),
        'model': 'XGBoost Ensemble'
    })

@app.route('/api/predict-yield', methods=['POST'])
def predict_yield():
    data = request.json
    yield_model_path = os.path.join(backend_dir, 'yield_model.pkl')
    if not os.path.exists(yield_model_path):
        return jsonify({'error': 'yield_model.pkl not found'}), 404
    yield_model = pickle.load(open(yield_model_path, 'rb'))

    features = [[
        data['N'], data['P'], data['K'],
        data['temperature'], data['humidity'],
        data['ph'], data['rainfall']
    ]]

    predicted_yield = yield_model.model.predict(features)[0]

    return jsonify({
        'predicted_yield': round(predicted_yield, 2),
        'unit': 'tons/hectare'
    })

@app.route('/api/fertilizer-recommendation', methods=['POST'])
def fertilizer_recommendation():
    data = request.json
    recommendations = fertilizer_system.analyze_soil(
        data['N'], data['P'], data['K'], data['ph']
    )

    crop_specific = None
    if 'crop' in data:
        crop_specific = fertilizer_system.get_crop_specific_recommendation(
            data['crop'], data['N'], data['P'], data['K']
        )

    return jsonify({
        'general_recommendations': recommendations,
        'crop_specific': crop_specific
    })

@app.route('/api/soil-health', methods=['POST'])
def soil_health():
    data = request.json
    health_result = soil_classifier.classify_soil_health(
        data['N'], data['P'], data['K'], data['ph']
    )

    return jsonify(health_result)

@app.route('/api/weather-prediction', methods=['POST'])
def weather_prediction():
    data = request.json
    result = weather_predictor.predict_with_weather(
        data['N'], data['P'], data['K'], data['ph'],
        data['lat'], data['lon'],
        crop_model
    )

    return jsonify(result)

@app.route('/api/price-prediction', methods=['POST'])
def price_prediction():
    data = request.json
    price_model_path = os.path.join(backend_dir, 'price_model.pkl')
    if os.path.exists(price_model_path):
        price_model = pickle.load(open(price_model_path, 'rb'))
    else:
        price_model = CropPricePrediction()

    recent_prices = np.array(data['price_history'])
    if getattr(price_model, 'model', None) is None:
        price_model.train_price_model(recent_prices)
    future_prices = price_model.predict_future_prices(recent_prices, days=7)
    trend = price_model.analyze_price_trend(recent_prices)

    return jsonify({
        'future_prices': [round(p, 2) for p in future_prices],
        'trend_analysis': trend
    })

@app.route('/api/comprehensive-analysis', methods=['POST'])
def comprehensive_analysis():
    data = request.json

    crop_pred = crop_model.predict([[
        data['N'], data['P'], data['K'],
        data['temperature'], data['humidity'],
        data['ph'], data['rainfall']
    ]])[0]

    soil_health_result = soil_classifier.classify_soil_health(
        data['N'], data['P'], data['K'], data['ph']
    )

    fertilizer_rec = fertilizer_system.analyze_soil(
        data['N'], data['P'], data['K'], data['ph']
    )

    return jsonify({
        'recommended_crop': crop_pred,
        'soil_health': soil_health_result,
        'fertilizer_recommendations': fertilizer_rec,
        'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)