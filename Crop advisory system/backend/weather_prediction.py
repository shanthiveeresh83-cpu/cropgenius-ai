import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

try:
    import requests
except Exception:
    requests = None

class WeatherBasedPrediction:
    def __init__(self, api_key=None):
        self.api_key = api_key
        self.base_url = "https://api.openweathermap.org/data/2.5"

    def fetch_weather_data(self, lat, lon):
        if not self.api_key or requests is None:

            return {
                'temperature': 25.0,
                'humidity': 75.0,
                'rainfall': 150.0
            }

        url = f"{self.base_url}/weather"
        params = {'lat': lat, 'lon': lon, 'appid': self.api_key, 'units': 'metric'}
        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
        except Exception:
            return {
                'temperature': 25.0,
                'humidity': 75.0,
                'rainfall': 150.0
            }

        return {
            'temperature': data['main']['temp'],
            'humidity': data['main']['humidity'],
            'rainfall': data.get('rain', {}).get('1h', 0) * 30  # Convert to monthly
        }

    def predict_with_weather(self, N, P, K, ph, lat, lon, model):
        weather = self.fetch_weather_data(lat, lon)

        features = [[
            N, P, K,
            weather['temperature'],
            weather['humidity'],
            ph,
            weather['rainfall']
        ]]

        prediction = model.predict(features)[0]
        probability = model.predict_proba(features)[0]

        return {
            'predicted_crop': prediction,
            'confidence': round(max(probability) * 100, 2),
            'weather_data': weather,
            'suitability': self.assess_suitability(prediction, weather)
        }

    def assess_suitability(self, crop, weather):
        crop_weather_req = {
            'rice': {'temp': (20, 27), 'humidity': (80, 85), 'rainfall': (200, 300)},
            'wheat': {'temp': (12, 25), 'humidity': (50, 70), 'rainfall': (50, 75)},
            'maize': {'temp': (21, 27), 'humidity': (65, 75), 'rainfall': (90, 120)},
            'cotton': {'temp': (21, 30), 'humidity': (60, 70), 'rainfall': (50, 100)}
        }

        if crop not in crop_weather_req:
            return 'Unknown'

        req = crop_weather_req[crop]
        temp_ok = req['temp'][0] <= weather['temperature'] <= req['temp'][1]
        humidity_ok = req['humidity'][0] <= weather['humidity'] <= req['humidity'][1]
        rainfall_ok = req['rainfall'][0] <= weather['rainfall'] <= req['rainfall'][1]

        if temp_ok and humidity_ok and rainfall_ok:
            return 'Excellent'
        elif temp_ok and (humidity_ok or rainfall_ok):
            return 'Good'
        elif temp_ok or humidity_ok:
            return 'Fair'
        else:
            return 'Poor'

if __name__ == '__main__':
    weather_predictor = WeatherBasedPrediction()

    model = pickle.load(open('model.pkl', 'rb'))

    result = weather_predictor.predict_with_weather(
        N=80, P=40, K=40, ph=6.5,
        lat=28.6139, lon=77.2090,
        model=model
    )

    print(f"Predicted Crop: {result['predicted_crop']}")
    print(f"Confidence: {result['confidence']}%")
    print(f"Weather Suitability: {result['suitability']}")
    print(f"Current Weather: {result['weather_data']}")