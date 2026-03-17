import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import pickle

class SoilHealthClassifier:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()

    def classify_soil_health(self, N, P, K, ph, organic_matter=None):

        scores = []

        if N < 30:
            n_score = 25
        elif N < 50:
            n_score = 50
        elif N < 80:
            n_score = 75
        else:
            n_score = 100
        scores.append(n_score)

        if P < 20:
            p_score = 25
        elif P < 40:
            p_score = 50
        elif P < 60:
            p_score = 75
        else:
            p_score = 100
        scores.append(p_score)

        if K < 20:
            k_score = 25
        elif K < 40:
            k_score = 50
        elif K < 60:
            k_score = 75
        else:
            k_score = 100
        scores.append(k_score)

        if ph < 5.5 or ph > 8.0:
            ph_score = 25
        elif ph < 6.0 or ph > 7.5:
            ph_score = 50
        elif ph < 6.5 or ph > 7.0:
            ph_score = 75
        else:
            ph_score = 100
        scores.append(ph_score)

        health_score = np.mean(scores)

        if health_score >= 80:
            health_class = 'Excellent'
            color = 'green'
        elif health_score >= 60:
            health_class = 'Good'
            color = 'lightgreen'
        elif health_score >= 40:
            health_class = 'Fair'
            color = 'yellow'
        else:
            health_class = 'Poor'
            color = 'red'

        return {
            'health_class': health_class,
            'health_score': round(health_score, 2),
            'color': color,
            'component_scores': {
                'nitrogen': n_score,
                'phosphorus': p_score,
                'potassium': k_score,
                'ph': ph_score
            },
            'recommendations': self.get_improvement_recommendations(health_class, N, P, K, ph)
        }

    def get_improvement_recommendations(self, health_class, N, P, K, ph):
        recommendations = []

        if health_class in ['Poor', 'Fair']:
            recommendations.append("Add organic compost (5-10 tons/hectare)")
            recommendations.append("Practice crop rotation")
            recommendations.append("Use cover crops during off-season")

        if N < 40:
            recommendations.append("Apply nitrogen-rich fertilizers")
        if P < 30:
            recommendations.append("Add phosphate fertilizers")
        if K < 30:
            recommendations.append("Apply potassium supplements")
        if ph < 6.0:
            recommendations.append("Apply lime to increase pH")
        elif ph > 7.5:
            recommendations.append("Apply sulfur to decrease pH")

        return recommendations

if __name__ == '__main__':
    soil_classifier = SoilHealthClassifier()

    test_soils = [
        {'N': 85, 'P': 55, 'K': 45, 'ph': 6.8},  # Excellent
        {'N': 60, 'P': 40, 'K': 35, 'ph': 6.5},  # Good
        {'N': 35, 'P': 25, 'K': 20, 'ph': 5.5},  # Poor
    ]

    for i, soil in enumerate(test_soils, 1):
        result = soil_classifier.classify_soil_health(**soil)
        print(f"\nSoil Sample {i}:")
        print(f"Health: {result['health_class']} ({result['health_score']}/100)")
        print(f"Recommendations: {', '.join(result['recommendations'][:2])}")