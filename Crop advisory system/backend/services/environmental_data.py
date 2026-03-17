"""
Environmental Data Service - Automated Data Collection

This service provides:
- Automatic collection of all parameters needed for crop prediction
- Weather data from OpenWeatherMap API
- Soil parameters from dataset or simulated IoT sensors

Usage:
    from services.environmental_data import EnvironmentalDataCollector
    
    collector = EnvironmentalDataCollector()
    data = collector.get_all_data()
"""

import os
import logging
import random
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class EnvironmentalDataCollector:
    """
    Service for automatically collecting all environmental data needed for crop prediction.
    
    Data sources:
    - Weather: OpenWeatherMap API (temperature, humidity, rainfall)
    - Soil: Dataset row OR simulated IoT sensors (N, P, K, pH)
    """
    
    def __init__(self):
        """Initialize the environmental data collector."""
        self._weather_service = None
        self._nutrient_estimator = None
        self._data_cache = {}
        
        # Default location - will be overridden by user's actual location
        self.default_location = None
        
        # IoT simulation parameters
        self.enable_iot_simulation = os.getenv("ENABLE_IOT_SIMULATION", "true").lower() == "true"
        self.use_dataset_fallback = os.getenv("USE_DATASET_FALLBACK", "true").lower() == "true"
        
        # Dataset path
        self.dataset_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "crop_data.csv"
        )
        
        logger.info("EnvironmentalDataCollector initialized")
    
    def _get_weather_service(self):
        """Lazy load weather service."""
        if self._weather_service is None:
            try:
                from services.weather_service import WeatherService, WeatherServiceError
                self._weather_service = WeatherService()
                self._weather_service.WeatherServiceError = WeatherServiceError
            except ImportError as e:
                logger.error(f"Failed to import weather service: {e}")
                self._weather_service = None
        return self._weather_service
    
    def _get_nutrient_estimator(self):
        """Lazy load nutrient estimator."""
        if self._nutrient_estimator is None:
            try:
                from services.nutrient_estimator import NutrientEstimator, NutrientEstimatorError
                self._nutrient_estimator = NutrientEstimator()
                self._nutrient_estimator.NutrientEstimatorError = NutrientEstimatorError
            except ImportError as e:
                logger.error(f"Failed to import nutrient estimator: {e}")
                self._nutrient_estimator = None
        return self._nutrient_estimator
    
    def _get_weather_data(self, location: Optional[Dict[str, Any]] = None) -> Dict[str, float]:
        """
        Fetch weather data from API or use defaults.
        
        Args:
            location: Optional location dict with city, lat/lon
            
        Returns:
            Dict with temperature, humidity, rainfall
        """
        weather_service = self._get_weather_service()
        
        if weather_service is None:
            logger.warning("Weather service unavailable, using defaults")
            city_name = 'Unknown'
            if location:
                city_name = location.get('city') or f"Lat:{location.get('lat', 'N/A')}, Lon:{location.get('lon', 'N/A')}"
            return {
                'temperature': 25.0,
                'humidity': 75.0,
                'rainfall': 150.0,
                'source': 'default',
                'city': city_name
            }
        
        try:
            if not location:
                raise Exception("No location provided")
            weather_data = weather_service.get_weather(location)
            
            return {
                'temperature': weather_data.get('temperature', 25.0),
                'humidity': weather_data.get('humidity', 75.0),
                'rainfall': weather_data.get('rainfall', 150.0),
                'source': weather_data.get('source', 'api'),
                'city': weather_data.get('city', location.get('city', 'Unknown'))
            }
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}, using defaults")
            city_name = 'Unknown'
            if location:
                city_name = location.get('city') or f"Lat:{location.get('lat', 'N/A')}, Lon:{location.get('lon', 'N/A')}"
            return {
                'temperature': 25.0,
                'humidity': 75.0,
                'rainfall': 150.0,
                'source': 'default',
                'city': city_name
            }
    
    def _get_soil_from_dataset(self) -> Dict[str, float]:
        """
        Get random soil parameters from dataset.
        
        Returns:
            Dict with N, P, K, ph values from random dataset row
        """
        if not os.path.exists(self.dataset_path):
            logger.warning(f"Dataset not found: {self.dataset_path}")
            return self._get_iot_sensor_data()
        
        try:
            import pandas as pd
            df = pd.read_csv(self.dataset_path)
            
            if df.empty:
                logger.warning("Dataset is empty")
                return self._get_iot_sensor_data()
            
            # Select random row
            random_row = df.sample(n=1).iloc[0]
            
            return {
                'N': float(random_row['N']),
                'P': float(random_row['P']),
                'K': float(random_row['K']),
                'ph': float(random_row['ph']),
                'source': 'dataset',
                'crop_from_dataset': random_row.get('label', 'unknown')
            }
        except Exception as e:
            logger.warning(f"Failed to read dataset: {e}")
            return self._get_iot_sensor_data()
    
    def _get_iot_sensor_data(self) -> Dict[str, float]:
        """
        Simulate IoT sensor data with realistic values for maximum crop diversity.
        
        Returns:
            Dict with N, P, K, ph values simulating IoT sensors
        """
        # Maximum diversity ranges covering all crop types in dataset
        n_range = (20, 140)    # Nitrogen ppm - very wide range
        p_range = (28, 145)    # Phosphorus ppm - very wide range
        k_range = (30, 205)    # Potassium ppm - very wide range  
        ph_range = (5.5, 9.5)  # pH scale - very wide range
        
        # Generate highly varied values for diverse crop predictions
        n_value = round(random.uniform(*n_range), 2)
        p_value = round(random.uniform(*p_range), 2)
        k_value = round(random.uniform(*k_range), 2)
        ph_value = round(random.uniform(*ph_range), 2)
        
        logger.info(f"IoT sensor simulation: N={n_value}, P={p_value}, K={k_value}, pH={ph_value}")
        
        return {
            'N': n_value,
            'P': p_value,
            'K': k_value,
            'ph': ph_value,
            'source': 'iot_sensor'
        }
    
    def _get_soil_parameters(self) -> Dict[str, float]:
        """
        Get soil parameters from dataset or IoT sensors.
        
        Tries dataset first, falls back to IoT simulation.
        
        Returns:
            Dict with N, P, K, ph values
        """
        if self.use_dataset_fallback:
            soil_data = self._get_soil_from_dataset()
            if soil_data.get('source') == 'dataset':
                return soil_data
        
        # Fallback to IoT simulation
        return self._get_iot_sensor_data()
    
    def get_all_data(self, location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Collect all environmental data automatically.
        
        This is the main method that collects:
        - Weather: temperature, humidity, rainfall
        - Soil: N, P, K, pH
        
        Args:
            location: Optional location dict
            
        Returns:
            Dict with all parameters needed for crop prediction
        """
        logger.info("Collecting all environmental data automatically...")
        
        # Get weather data
        weather_data = self._get_weather_data(location)
        
        # Get soil parameters
        soil_data = self._get_soil_parameters()
        
        # Combine all data
        result = {
            'N': soil_data.get('N', 50.0),
            'P': soil_data.get('P', 30.0),
            'K': soil_data.get('K', 40.0),
            'temperature': weather_data.get('temperature', 25.0),
            'humidity': weather_data.get('humidity', 75.0),
            'ph': soil_data.get('ph', 7.0),
            'rainfall': weather_data.get('rainfall', 150.0),
            'sources': {
                'N': soil_data.get('source', 'iot_sensor'),
                'P': soil_data.get('source', 'iot_sensor'),
                'K': soil_data.get('source', 'iot_sensor'),
                'ph': soil_data.get('source', 'iot_sensor'),
                'temperature': weather_data.get('source', 'default'),
                'humidity': weather_data.get('source', 'default'),
                'rainfall': weather_data.get('source', 'default')
            },
            'location': {
                'city': weather_data.get('city') or (location.get('city') if location else 'Unknown'),
                'coordinates': location if location else None
            }
        }
        
        logger.info(f"Environmental data collected: N={result['N']}, P={result['P']}, "
                   f"K={result['K']}, temp={result['temperature']}, "
                   f"humidity={result['humidity']}, pH={result['ph']}, "
                   f"rainfall={result['rainfall']}")
        
        return result
    
    def get_data_with_estimator(self, location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Collect data using ML nutrient estimator for better accuracy.
        
        Uses NutrientEstimator service instead of random dataset/IoT values.
        
        Args:
            location: Optional location dict
            
        Returns:
            Dict with all parameters using ML-based estimation
        """
        logger.info("Collecting environmental data with ML nutrient estimation...")
        
        # Get weather data first
        weather_data = self._get_weather_data(location)
        
        # Get nutrient estimator
        nutrient_estimator = self._get_nutrient_estimator()
        
        if nutrient_estimator is not None:
            try:
                # Estimate N and P using ML model
                n_value, p_value = nutrient_estimator.estimate_nutrients(
                    soil_type=None,
                    region=None,
                    crop=None,
                    ph=7.0,
                    rainfall=weather_data.get('rainfall', 100.0),
                    temperature=weather_data.get('temperature', 25.0),
                    humidity=weather_data.get('humidity', 75.0),
                    k=40.0
                )
                
                logger.info(f"ML estimated: N={n_value}, P={p_value}")
                
                return {
                    'N': n_value,
                    'P': p_value,
                    'K': 40.0,  # Default K value
                    'temperature': weather_data.get('temperature', 25.0),
                    'humidity': weather_data.get('humidity', 75.0),
                    'ph': 7.0,  # Default pH
                    'rainfall': weather_data.get('rainfall', 150.0),
                    'sources': {
                        'N': 'ml_estimator',
                        'P': 'ml_estimator',
                        'K': 'default',
                        'ph': 'default',
                        'temperature': weather_data.get('source', 'default'),
                        'humidity': weather_data.get('source', 'default'),
                        'rainfall': weather_data.get('source', 'default')
                    },
                    'location': {
                        'city': weather_data.get('city', 'Unknown'),
                        'coordinates': location if location else None
                    }
                }
            except Exception as e:
                logger.warning(f"ML estimation failed: {e}, using fallback")
        
        # Fallback to basic method
        return self.get_all_data(location)


class EnvironmentalDataError(Exception):
    """Custom exception for EnvironmentalDataCollector errors."""
    pass


# Convenience function
def get_environmental_data(location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Quick function to get all environmental data.
    
    Args:
        location: Optional location dict
        
    Returns:
        Dict with all parameters for crop prediction
    """
    collector = EnvironmentalDataCollector()
    return collector.get_all_data(location)


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    collector = EnvironmentalDataCollector()
    
    print("=== Test: Get all environmental data ===")
    data = collector.get_all_data()
    print(f"N: {data['N']}")
    print(f"P: {data['P']}")
    print(f"K: {data['K']}")
    print(f"pH: {data['ph']}")
    print(f"Temperature: {data['temperature']}")
    print(f"Humidity: {data['humidity']}")
    print(f"Rainfall: {data['rainfall']}")
    print(f"Sources: {data['sources']}")
    print(f"Location: {data['location']}")
