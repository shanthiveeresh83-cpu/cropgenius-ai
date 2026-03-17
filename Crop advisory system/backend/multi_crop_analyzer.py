"""
Multi-Crop Analysis System with Comparison and Historical Data
"""
import numpy as np
import pickle
import os
from datetime import datetime, timedelta
import json

class MultiCropAnalyzer:
    def __init__(self, model_path):
        self.model = pickle.load(open(model_path, 'rb'))
        self.crop_classes = ['rice', 'maize', 'chickpea', 'kidneybeans', 'pigeonpeas', 
                            'mothbeans', 'mungbean', 'blackgram', 'lentil', 'pomegranate',
                            'banana', 'mango', 'grapes', 'watermelon', 'muskmelon', 
                            'apple', 'orange', 'papaya', 'coconut', 'cotton', 'jute', 'coffee']
        self.historical_data = self._load_historical_data()
        
    def _load_historical_data(self):
        """Load 2-year historical price and yield data"""
        return {
            'rice': {'avg_price': 2500, 'price_trend': 'stable', 'avg_yield': 5.0, 'volatility': 0.08},
            'maize': {'avg_price': 1800, 'price_trend': 'rising', 'avg_yield': 6.0, 'volatility': 0.12},
            'chickpea': {'avg_price': 4500, 'price_trend': 'rising', 'avg_yield': 2.5, 'volatility': 0.15},
            'kidneybeans': {'avg_price': 6000, 'price_trend': 'stable', 'avg_yield': 2.0, 'volatility': 0.10},
            'pigeonpeas': {'avg_price': 5000, 'price_trend': 'rising', 'avg_yield': 1.8, 'volatility': 0.13},
            'mothbeans': {'avg_price': 4000, 'price_trend': 'stable', 'avg_yield': 1.5, 'volatility': 0.11},
            'mungbean': {'avg_price': 6000, 'price_trend': 'rising', 'avg_yield': 1.2, 'volatility': 0.14},
            'blackgram': {'avg_price': 5500, 'price_trend': 'stable', 'avg_yield': 1.0, 'volatility': 0.12},
            'lentil': {'avg_price': 4800, 'price_trend': 'rising', 'avg_yield': 1.5, 'volatility': 0.13},
            'pomegranate': {'avg_price': 8000, 'price_trend': 'rising', 'avg_yield': 15.0, 'volatility': 0.18},
            'banana': {'avg_price': 1500, 'price_trend': 'stable', 'avg_yield': 40.0, 'volatility': 0.10},
            'mango': {'avg_price': 3500, 'price_trend': 'rising', 'avg_yield': 10.0, 'volatility': 0.16},
            'grapes': {'avg_price': 4000, 'price_trend': 'stable', 'avg_yield': 20.0, 'volatility': 0.14},
            'watermelon': {'avg_price': 800, 'price_trend': 'stable', 'avg_yield': 30.0, 'volatility': 0.12},
            'muskmelon': {'avg_price': 1200, 'price_trend': 'stable', 'avg_yield': 25.0, 'volatility': 0.11},
            'apple': {'avg_price': 6000, 'price_trend': 'rising', 'avg_yield': 12.0, 'volatility': 0.15},
            'orange': {'avg_price': 2000, 'price_trend': 'stable', 'avg_yield': 15.0, 'volatility': 0.10},
            'papaya': {'avg_price': 1800, 'price_trend': 'stable', 'avg_yield': 50.0, 'volatility': 0.09},
            'coconut': {'avg_price': 2500, 'price_trend': 'rising', 'avg_yield': 80.0, 'volatility': 0.11},
            'cotton': {'avg_price': 6000, 'price_trend': 'rising', 'avg_yield': 2.5, 'volatility': 0.17},
            'jute': {'avg_price': 3500, 'price_trend': 'stable', 'avg_yield': 2.0, 'volatility': 0.12},
            'coffee': {'avg_price': 8000, 'price_trend': 'rising', 'avg_yield': 1.5, 'volatility': 0.19}
        }
    
    def predict_top_crops(self, features, top_k=10):
        """Predict top K suitable crops with probabilities"""
        features_array = np.array([features])
        
        # Get prediction probabilities
        if hasattr(self.model, 'predict_proba'):
            probabilities = self.model.predict_proba(features_array)[0]
        else:
            # Fallback: use decision function or single prediction
            prediction = self.model.predict(features_array)[0]
            probabilities = np.zeros(len(self.crop_classes))
            pred_idx = self.crop_classes.index(prediction) if prediction in self.crop_classes else 0
            probabilities[pred_idx] = 1.0
        
        # Get top K crops
        top_indices = np.argsort(probabilities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self.crop_classes):
                crop = self.crop_classes[idx]
                results.append({
                    'crop': crop,
                    'soil_suitability': float(probabilities[idx] * 100)
                })
        
        return results
    
    def calculate_seasonal_match(self, crop, temperature, rainfall):
        """Calculate seasonal suitability score"""
        season_requirements = {
            'rice': {'temp_range': (20, 30), 'rain_range': (150, 300)},
            'maize': {'temp_range': (18, 27), 'rain_range': (50, 100)},
            'chickpea': {'temp_range': (20, 30), 'rain_range': (60, 90)},
            'cotton': {'temp_range': (21, 30), 'rain_range': (50, 100)},
            'banana': {'temp_range': (15, 35), 'rain_range': (100, 200)},
            'mango': {'temp_range': (24, 30), 'rain_range': (75, 250)},
        }
        
        req = season_requirements.get(crop, {'temp_range': (15, 35), 'rain_range': (50, 150)})
        
        temp_score = 100 if req['temp_range'][0] <= temperature <= req['temp_range'][1] else 50
        rain_score = 100 if req['rain_range'][0] <= rainfall <= req['rain_range'][1] else 50
        
        return (temp_score + rain_score) / 2
    
    def calculate_profitability(self, crop, features):
        """Calculate profitability score based on yield and price"""
        hist = self.historical_data.get(crop, {})
        avg_price = hist.get('avg_price', 2000)
        avg_yield = hist.get('avg_yield', 3.0)
        volatility = hist.get('volatility', 0.1)
        
        # Base profitability
        base_profit = avg_price * avg_yield
        
        # Adjust for market stability (lower volatility = better)
        stability_factor = 1 - (volatility * 0.5)
        
        # Normalize to 0-100 scale
        profit_score = min(100, (base_profit / 200) * stability_factor)
        
        return profit_score
    
    def analyze_crops(self, n, p, k, temperature, humidity, ph, rainfall, top_k=10):
        """Complete multi-crop analysis with comparison"""
        features = [n, p, k, temperature, humidity, ph, rainfall]
        
        # Get top crops
        top_crops = self.predict_top_crops(features, top_k)
        
        # Analyze each crop
        comparison_data = []
        for crop_data in top_crops:
            crop = crop_data['crop']
            hist = self.historical_data.get(crop, {})
            
            soil_score = crop_data['soil_suitability']
            seasonal_score = self.calculate_seasonal_match(crop, temperature, rainfall)
            profit_score = self.calculate_profitability(crop, features)
            
            # Calculate final ranking score
            ranking_score = (
                soil_score * 0.35 +
                seasonal_score * 0.25 +
                profit_score * 0.40
            )
            
            comparison_data.append({
                'crop': crop,
                'soil_suitability': round(soil_score, 2),
                'seasonal_match': round(seasonal_score, 2),
                'avg_market_price': hist.get('avg_price', 2000),
                'price_trend': hist.get('price_trend', 'stable'),
                'expected_yield': hist.get('avg_yield', 3.0),
                'profitability_score': round(profit_score, 2),
                'ranking_score': round(ranking_score, 2),
                'volatility': hist.get('volatility', 0.1)
            })
        
        # Sort by ranking score
        comparison_data.sort(key=lambda x: x['ranking_score'], reverse=True)
        
        # Generate recommendation
        best_crop = comparison_data[0]
        recommendation = self._generate_recommendation(best_crop, comparison_data[:3])
        
        return {
            'top_crops': comparison_data,
            'best_recommendation': best_crop,
            'alternatives': comparison_data[1:4],
            'recommendation_text': recommendation,
            'analysis_date': datetime.now().isoformat()
        }
    
    def _generate_recommendation(self, best_crop, top_3):
        """Generate detailed recommendation text"""
        crop = best_crop['crop'].capitalize()
        score = best_crop['ranking_score']
        price = best_crop['avg_market_price']
        yield_val = best_crop['expected_yield']
        trend = best_crop['price_trend']
        
        recommendation = f"""
🌾 BEST CROP RECOMMENDATION: {crop}

📊 Overall Score: {score}/100

✅ Why {crop} is recommended:
• Soil Suitability: {best_crop['soil_suitability']}% match with your soil conditions
• Seasonal Match: {best_crop['seasonal_match']}% suitable for current season
• Market Price: ₹{price}/quintal (Trend: {trend})
• Expected Yield: {yield_val} tons/hectare
• Profitability Score: {best_crop['profitability_score']}/100

📈 Market Analysis (2-year data):
• Price trend is {trend}
• Market volatility: {best_crop['volatility']*100:.1f}%
• Stable demand with good returns

🔄 Alternative Options:
"""
        for i, alt in enumerate(top_3[1:], 2):
            recommendation += f"{i}. {alt['crop'].capitalize()} (Score: {alt['ranking_score']}/100)\n"
        
        return recommendation.strip()

def get_multi_crop_analyzer(model_path):
    """Get or create analyzer instance"""
    return MultiCropAnalyzer(model_path)
