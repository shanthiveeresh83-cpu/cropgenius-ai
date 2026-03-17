"""
Profit Analysis Module with Cultivation Cost and Historical Comparison
"""
import numpy as np
from datetime import datetime

class ProfitAnalyzer:
    def __init__(self):
        self.cultivation_costs = {
            'rice': {'seed': 3000, 'fertilizer': 8000, 'pesticide': 4000, 'labor': 15000, 'irrigation': 5000, 'total': 35000},
            'wheat': {'seed': 2500, 'fertilizer': 7000, 'pesticide': 3000, 'labor': 12000, 'irrigation': 4000, 'total': 28500},
            'maize': {'seed': 2000, 'fertilizer': 6000, 'pesticide': 3500, 'labor': 10000, 'irrigation': 3500, 'total': 25000},
            'cotton': {'seed': 4000, 'fertilizer': 10000, 'pesticide': 8000, 'labor': 20000, 'irrigation': 6000, 'total': 48000},
            'chickpea': {'seed': 3500, 'fertilizer': 5000, 'pesticide': 3000, 'labor': 8000, 'irrigation': 2500, 'total': 22000},
            'kidneybeans': {'seed': 4000, 'fertilizer': 6000, 'pesticide': 4000, 'labor': 12000, 'irrigation': 4000, 'total': 30000},
            'pigeonpeas': {'seed': 3000, 'fertilizer': 5000, 'pesticide': 3500, 'labor': 9000, 'irrigation': 3000, 'total': 23500},
            'mungbean': {'seed': 3500, 'fertilizer': 5500, 'pesticide': 3000, 'labor': 10000, 'irrigation': 3000, 'total': 25000},
            'blackgram': {'seed': 3200, 'fertilizer': 5000, 'pesticide': 3200, 'labor': 9500, 'irrigation': 2800, 'total': 23700},
            'lentil': {'seed': 3000, 'fertilizer': 5200, 'pesticide': 3000, 'labor': 9000, 'irrigation': 2800, 'total': 23000}
        }
        
        self.historical_data = self._load_historical_data()
        self.season_crops = {
            'kharif': ['rice', 'maize', 'cotton', 'kidneybeans', 'pigeonpeas', 'mungbean', 'blackgram'],
            'rabi': ['wheat', 'chickpea', 'lentil'],
            'zaid': ['watermelon', 'muskmelon']
        }
    
    def _load_historical_data(self):
        """Load 2-year historical profit/loss data"""
        return {
            'rice': {
                '2023': {'yield': 4.8, 'price': 2450, 'revenue': 11760, 'cost': 35000, 'profit': -23240},
                '2024': {'yield': 5.2, 'price': 2530, 'revenue': 13156, 'cost': 35000, 'profit': -21844}
            },
            'wheat': {
                '2023': {'yield': 4.3, 'price': 2000, 'revenue': 8600, 'cost': 28500, 'profit': -19900},
                '2024': {'yield': 4.7, 'price': 2120, 'revenue': 9964, 'cost': 28500, 'profit': -18536}
            },
            'maize': {
                '2023': {'yield': 5.8, 'price': 1800, 'revenue': 10440, 'cost': 25000, 'profit': -14560},
                '2024': {'yield': 6.2, 'price': 1870, 'revenue': 11594, 'cost': 25000, 'profit': -13406}
            },
            'cotton': {
                '2023': {'yield': 2.3, 'price': 5900, 'revenue': 13570, 'cost': 48000, 'profit': -34430},
                '2024': {'yield': 2.7, 'price': 6250, 'revenue': 16875, 'cost': 48000, 'profit': -31125}
            },
            'chickpea': {
                '2023': {'yield': 2.3, 'price': 4400, 'revenue': 10120, 'cost': 22000, 'profit': -11880},
                '2024': {'yield': 2.7, 'price': 4750, 'revenue': 12825, 'cost': 22000, 'profit': -9175}
            },
            'kidneybeans': {
                '2023': {'yield': 1.8, 'price': 5900, 'revenue': 10620, 'cost': 30000, 'profit': -19380},
                '2024': {'yield': 2.2, 'price': 6200, 'revenue': 13640, 'cost': 30000, 'profit': -16360}
            },
            'pigeonpeas': {
                '2023': {'yield': 1.6, 'price': 4900, 'revenue': 7840, 'cost': 23500, 'profit': -15660},
                '2024': {'yield': 2.0, 'price': 5200, 'revenue': 10400, 'cost': 23500, 'profit': -13100}
            },
            'mungbean': {
                '2023': {'yield': 1.0, 'price': 5900, 'revenue': 5900, 'cost': 25000, 'profit': -19100},
                '2024': {'yield': 1.4, 'price': 6200, 'revenue': 8680, 'cost': 25000, 'profit': -16320}
            },
            'blackgram': {
                '2023': {'yield': 0.9, 'price': 5400, 'revenue': 4860, 'cost': 23700, 'profit': -18840},
                '2024': {'yield': 1.1, 'price': 5700, 'revenue': 6270, 'cost': 23700, 'profit': -17430}
            },
            'lentil': {
                '2023': {'yield': 1.3, 'price': 4700, 'revenue': 6110, 'cost': 23000, 'profit': -16890},
                '2024': {'yield': 1.7, 'price': 5000, 'revenue': 8500, 'cost': 23000, 'profit': -14500}
            }
        }
    
    def get_current_season(self):
        """Determine current agricultural season"""
        month = datetime.now().month
        if 6 <= month <= 10:
            return 'kharif'
        elif 11 <= month or month <= 3:
            return 'rabi'
        else:
            return 'zaid'
    
    def analyze_top_3_crops(self, crop_probabilities, current_price_data):
        """Analyze top 3 crops with profit comparison"""
        current_season = self.get_current_season()
        
        # Filter by season
        seasonal_crops = []
        for crop, prob in crop_probabilities:
            if crop in self.season_crops.get(current_season, []):
                seasonal_crops.append((crop, prob))
        
        # Get top 3
        top_3 = sorted(seasonal_crops, key=lambda x: x[1], reverse=True)[:3]
        
        results = []
        for crop, suitability in top_3:
            cost_data = self.cultivation_costs.get(crop, {})
            hist_data = self.historical_data.get(crop, {})
            price_info = current_price_data.get(crop, {})
            
            # Calculate expected profit
            expected_yield = price_info.get('avg_yield', 3.0)
            current_price = price_info.get('avg_price', 2000)
            cultivation_cost = cost_data.get('total', 25000)
            
            expected_revenue = expected_yield * current_price * 10  # Convert to quintals
            expected_profit = expected_revenue - cultivation_cost
            profit_margin = (expected_profit / cultivation_cost) * 100 if cultivation_cost > 0 else 0
            
            # Historical comparison
            hist_2023 = hist_data.get('2023', {})
            hist_2024 = hist_data.get('2024', {})
            
            profit_trend = 'improving' if hist_2024.get('profit', 0) > hist_2023.get('profit', 0) else 'declining'
            avg_historical_profit = (hist_2023.get('profit', 0) + hist_2024.get('profit', 0)) / 2
            
            results.append({
                'crop': crop,
                'suitability_score': round(suitability * 100, 2),
                'season': current_season,
                'cultivation_cost': {
                    'seed': cost_data.get('seed', 0),
                    'fertilizer': cost_data.get('fertilizer', 0),
                    'pesticide': cost_data.get('pesticide', 0),
                    'labor': cost_data.get('labor', 0),
                    'irrigation': cost_data.get('irrigation', 0),
                    'total': cultivation_cost
                },
                'expected_yield': expected_yield,
                'current_price': current_price,
                'expected_revenue': round(expected_revenue, 2),
                'expected_profit': round(expected_profit, 2),
                'profit_margin': round(profit_margin, 2),
                'historical_data': {
                    '2023': hist_2023,
                    '2024': hist_2024,
                    'avg_profit': round(avg_historical_profit, 2),
                    'trend': profit_trend
                },
                'recommendation_rank': len(results) + 1
            })
        
        return {
            'season': current_season,
            'top_3_crops': results,
            'comparison_summary': self._generate_comparison(results)
        }
    
    def _generate_comparison(self, results):
        """Generate comparison summary"""
        if not results:
            return "No suitable crops found for current season"
        
        best_profit = max(results, key=lambda x: x['expected_profit'])
        lowest_cost = min(results, key=lambda x: x['cultivation_cost']['total'])
        best_margin = max(results, key=lambda x: x['profit_margin'])
        
        return {
            'most_profitable': best_profit['crop'],
            'lowest_cost': lowest_cost['crop'],
            'best_margin': best_margin['crop'],
            'recommendation': f"Based on analysis, {best_profit['crop']} offers highest profit (₹{best_profit['expected_profit']:,.0f}), "
                            f"while {lowest_cost['crop']} has lowest cultivation cost (₹{lowest_cost['cultivation_cost']['total']:,.0f})"
        }

def get_profit_analyzer():
    """Get profit analyzer instance"""
    return ProfitAnalyzer()
