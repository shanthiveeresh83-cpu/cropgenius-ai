import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pickle

class FertilizerRecommendation:
    def __init__(self):
        self.model = None
        self.fertilizer_map = {
            'high_n': 'Urea (46-0-0)',
            'high_p': 'DAP (18-46-0)',
            'high_k': 'MOP (0-0-60)',
            'balanced': 'NPK (20-20-20)',
            'organic': 'Compost/Manure'
        }

    def analyze_soil(self, N, P, K, ph):
        recommendations = []

        if N < 40:
            recommendations.append({
                'nutrient': 'Nitrogen',
                'status': 'Low',
                'fertilizer': self.fertilizer_map['high_n'],
                'quantity': '50-60 kg/hectare'
            })
        elif N > 80:
            recommendations.append({
                'nutrient': 'Nitrogen',
                'status': 'High',
                'fertilizer': 'Reduce nitrogen application',
                'quantity': 'Skip this season'
            })

        if P < 30:
            recommendations.append({
                'nutrient': 'Phosphorus',
                'status': 'Low',
                'fertilizer': self.fertilizer_map['high_p'],
                'quantity': '40-50 kg/hectare'
            })

        if K < 30:
            recommendations.append({
                'nutrient': 'Potassium',
                'status': 'Low',
                'fertilizer': self.fertilizer_map['high_k'],
                'quantity': '30-40 kg/hectare'
            })

        if ph < 6.0:
            recommendations.append({
                'nutrient': 'pH',
                'status': 'Acidic',
                'fertilizer': 'Lime (CaCO3)',
                'quantity': '200-300 kg/hectare'
            })
        elif ph > 7.5:
            recommendations.append({
                'nutrient': 'pH',
                'status': 'Alkaline',
                'fertilizer': 'Sulfur',
                'quantity': '50-100 kg/hectare'
            })

        if not recommendations:
            recommendations.append({
                'nutrient': 'All',
                'status': 'Optimal',
                'fertilizer': self.fertilizer_map['balanced'],
                'quantity': '100 kg/hectare (maintenance)'
            })

        return recommendations

    def get_crop_specific_recommendation(self, crop, N, P, K):
        crop_requirements = {
            'rice': {'N': 80, 'P': 40, 'K': 40},
            'wheat': {'N': 50, 'P': 30, 'K': 20},
            'maize': {'N': 60, 'P': 40, 'K': 40},
            'cotton': {'N': 60, 'P': 30, 'K': 30}
        }

        if crop not in crop_requirements:
            return None

        req = crop_requirements[crop]
        deficit = {
            'N': max(0, req['N'] - N),
            'P': max(0, req['P'] - P),
            'K': max(0, req['K'] - K)
        }

        return {
            'crop': crop,
            'current': {'N': N, 'P': P, 'K': K},
            'required': req,
            'deficit': deficit,
            'recommendation': f"Apply N:{deficit['N']}, P:{deficit['P']}, K:{deficit['K']} kg/hectare"
        }

if __name__ == '__main__':
    fertilizer_system = FertilizerRecommendation()

    recommendations = fertilizer_system.analyze_soil(N=35, P=25, K=28, ph=5.8)
    print("Fertilizer Recommendations:")
    for rec in recommendations:
        print(f"- {rec['nutrient']}: {rec['status']} → {rec['fertilizer']} ({rec['quantity']})")

    crop_rec = fertilizer_system.get_crop_specific_recommendation('rice', N=50, P=30, K=25)
    print(f"\nCrop-specific: {crop_rec['recommendation']}")