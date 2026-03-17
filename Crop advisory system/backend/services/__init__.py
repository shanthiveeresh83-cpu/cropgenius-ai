"""
Services Package for Crop Advisory System

This package contains business logic services:
- weather_service: Integration with OpenWeatherMap API
- nutrient_estimator: ML models to estimate N and P values
- environmental_data: Automated data collection for predictions
"""

# Lazy imports to avoid import errors when pandas is not installed
def get_weather_service():
    """Get WeatherService class lazily."""
    from .weather_service import WeatherService
    return WeatherService

def get_nutrient_estimator():
    """Get NutrientEstimator class lazily."""
    from .nutrient_estimator import NutrientEstimator
    return NutrientEstimator

def get_environmental_data_collector():
    """Get EnvironmentalDataCollector class lazily."""
    from .environmental_data import EnvironmentalDataCollector
    return EnvironmentalDataCollector

__all__ = ['get_weather_service', 'get_nutrient_estimator', 'get_environmental_data_collector']
