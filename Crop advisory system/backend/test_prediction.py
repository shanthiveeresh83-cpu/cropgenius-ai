import os
import sys

os.chdir(os.path.dirname(os.path.abspath(__file__)))

sys.path.insert(0, os.getcwd())

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import pickle
import numpy as np
from datetime import datetime

model = pickle.load(open("model.pkl", "rb"))

try:
    from yield_prediction import YieldPredictionModel
    yield_model = YieldPredictionModel()
    try:
        yield_model.model = pickle.load(open("yield_model.pkl", "rb"))
    except:
        yield_model.model = None
except:
    yield_model = None

try:
    from fertilizer_recommendation import FertilizerRecommendation
    fertilizer_system = FertilizerRecommendation()
except:
    fertilizer_system = None

try:
    from soil_health import SoilHealthClassifier
    soil_classifier = SoilHealthClassifier()
except:
    soil_classifier = None

try:
    from weather_prediction import WeatherBasedPrediction
    weather_predictor = WeatherBasedPrediction()
except:
    weather_predictor = None

try:
    from price_prediction import CropPricePrediction
    price_predictor = CropPricePrediction()
    try:
        price_predictor.model = pickle.load(open("price_model.pkl", "rb"))
    except:
        price_predictor.model = None
except:
    price_predictor = None

sample_data = {
    'N': 90,       # Nitrogen
    'P': 42,       # Phosphorus
    'K': 43,       # Potassium
    'temperature': 20.8,  # Temperature in Celsius
    'humidity': 82.0,     # Humidity %
    'ph': 6.5,           # pH level
    'rainfall': 250.0    # Rainfall in mm
}

n = float(sample_data['N'])
p = float(sample_data['P'])
k = float(sample_data['K'])
temperature = float(sample_data['temperature'])
humidity = float(sample_data['humidity'])
ph = float(sample_data['ph'])
rainfall = float(sample_data['rainfall'])

features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
crop_pred = model.predict(features)[0]

print(f"\n{'='*60}")
print(f"🌾 FARM ANALYSIS PREDICTION RESULTS")
print(f"{'='*60}")
print(f"\n📊 INPUT PARAMETERS:")
print(f"   Nitrogen (N): {n}")
print(f"   Phosphorus (P): {p}")
print(f"   Potassium (K): {k}")
print(f"   Temperature: {temperature}°C")
print(f"   Humidity: {humidity}%")
print(f"   pH Level: {ph}")
print(f"   Rainfall: {rainfall}mm")

print(f"\n{'='*60}")
print(f"🌾 RECOMMENDED CROP: {crop_pred.upper()}")
print(f"{'='*60}")

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
        'component_scores': {'nitrogen': n_score, 'phosphorus': p_score, 'potassium': k_score}
    }

print(f"\n🌍 SOIL HEALTH ANALYSIS:")
print(f"   Health Class: {soil_health_result['health_class']}")
print(f"   Health Score: {soil_health_result['health_score']}/100")
print(f"   Component Scores:")
for key, value in soil_health_result['component_scores'].items():
    print(f"      - {key}: {value:.2f}")

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

print(f"\n🧪 FERTILIZER RECOMMENDATIONS:")
for rec in fertilizer_rec:
    print(f"   - {rec['nutrient']}: {rec['fertilizer']} ({rec['quantity']})")

if yield_model and hasattr(yield_model, 'model') and yield_model.model is not None:
    try:
        predicted_yield = yield_model.model.predict(features)[0]
        print(f"\n📊 YIELD PREDICTION:")
        print(f"   Estimated Yield: {predicted_yield} tons/hectare")
    except:
        print(f"\n📊 YIELD PREDICTION: Model not available")
else:

    base_yields = {'rice': 3.5, 'wheat': 3.0, 'maize': 4.0, 'cotton': 2.0, 'sugarcane': 70.0}
    estimated_yield = base_yields.get(crop_pred.lower(), 3.0)
    print(f"\n📊 YIELD PREDICTION (Estimated):")
    print(f"   Estimated Yield: ~{estimated_yield} tons/hectare")

if weather_predictor:
    weather_suitability = weather_predictor.assess_suitability(crop_pred, {'temperature': temperature, 'humidity': humidity, 'rainfall': rainfall})
else:
    weather_suitability = 'Good' if 15 <= temperature <= 35 and 50 <= humidity <= 90 else 'Fair'

print(f"\n🌤️ WEATHER SUITABILITY: {weather_suitability}")

if price_predictor:
    base_prices = {'rice': 2500, 'wheat': 2000, 'maize': 1800, 'cotton': 6000, 'sugarcane': 3500, 'potato': 1200, 'onion': 1500, 'tomato': 2000}
    base_price = base_prices.get(crop_pred.lower(), 2000)
    price_history = np.array([base_price + np.random.randint(-200, 200) for _ in range(40)])
    try:
        trend_analysis = price_predictor.analyze_price_trend(price_history)
        future_prices = price_predictor.predict_future_prices(price_history, days=7)
        print(f"\n💰 MARKET PRICE ANALYSIS:")
        print(f"   Current Price: ₹{trend_analysis.get('current_price', base_price)}/quintal")
        print(f"   Trend: {trend_analysis.get('trend', 'Stable')}")
        print(f"   Change: {trend_analysis.get('change_percentage', 0)}%")
        print(f"   Recommendation: {trend_analysis.get('recommendation', 'Market stable')}")
        print(f"   Future Prices (Next 5 days): {[round(float(p), 2) for p in future_prices[:5]]}")
    except Exception as e:
        print(f"\n💰 MARKET PRICE ANALYSIS: Unable to analyze")
else:
    base_prices = {'rice': 2500, 'wheat': 2000, 'maize': 1800, 'cotton': 6000, 'sugarcane': 3500, 'potato': 1200, 'onion': 1500, 'tomato': 2000}
    base_price = base_prices.get(crop_pred.lower(), 2000)
    print(f"\n💰 MARKET PRICE ANALYSIS:")
    print(f"   Current Price: ₹{base_price}/quintal (estimated)")
    print(f"   Trend: Stable")
    print(f"   Recommendation: Monitor market prices")

if fertilizer_system:
    crop_specific_rec = fertilizer_system.get_crop_specific_recommendation(crop_pred, n, p, k)
    print(f"\n🎯 CROP-SPECIFIC RECOMMENDATIONS:")
    if crop_specific_rec and crop_specific_rec.get('deficit'):
        for key, value in crop_specific_rec['deficit'].items():
            if value > 0:
                print(f"   - {key}: {value} kg/hectare deficit")

print(f"\n💡 OVERALL RECOMMENDATIONS:")
overall_recommendations = []
if soil_health_result.get('health_class') in ['Poor', 'Fair']:
    if soil_health_result.get('recommendations'):
        overall_recommendations.extend(soil_health_result.get('recommendations', [])[:2])
    else:
        overall_recommendations.append('Improve soil health with organic matter')
if weather_suitability in ['Fair', 'Poor']:
    overall_recommendations.append(f"Weather conditions are {weather_suitability.lower()} for {crop_pred}. Consider alternative crops.")
if not overall_recommendations:
    overall_recommendations.append(f"Excellent conditions for {crop_pred} cultivation!")

for rec in overall_recommendations:
    print(f"   ✓ {rec}")

print(f"\n{'='*60}")
print(f"Analysis completed: {datetime.now()}")
print(f"{'='*60}\n")