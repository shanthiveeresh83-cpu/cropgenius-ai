"""
Weather Service - Integration with OpenWeatherMap API

This service provides:
- Current weather data fetching by coordinates or city name
- Temperature, humidity, and rainfall data
- Fallback to mock data when API is unavailable

Usage:
    weather_service = WeatherService()
    weather_data = weather_service.get_weather_by_coords(lat=28.6139, lon=77.2090)
    weather_data = weather_service.get_weather_by_city("Delhi")
"""

import os
import logging
from typing import Optional, Dict, Any, Tuple

# Try to import requests, fall back to mock if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    logging.warning("requests library not available, using mock weather data")

logger = logging.getLogger(__name__)


class WeatherService:
    """
    Service for fetching weather data from OpenWeatherMap API.
    
    Supports fetching by:
    - Latitude/Longitude coordinates
    - City name
    
    Includes fallback to mock data when API is unavailable.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize WeatherService with API key.
        
        Args:
            api_key: OpenWeatherMap API key. If None, reads from environment variable.
        """
        self.api_key = api_key or os.getenv("OPENWEATHERMAP_API_KEY")
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.timeout = int(os.getenv("WEATHER_API_TIMEOUT", "10"))
        self.units = os.getenv("WEATHER_API_UNITS", "metric")
        
        # Enable/disable features
        self.enable_fallback = os.getenv("ENABLE_FALLBACK_MOCK_DATA", "True").lower() == "true"
        
        # Default location for fallback - will be overridden by user location
        self.default_lat = None
        self.default_lon = None
        self.default_city = None
        
        logger.info(f"WeatherService initialized with API key: {'set' if self.api_key else 'NOT SET (will use fallback)'}")
    
    def _get_mock_weather_data(self, city=None) -> Dict[str, Any]:
        """
        Return mock weather data for testing when API is unavailable.
        
        Returns:
            Dictionary with temperature, humidity, and rainfall values
        """
        return {
            'temperature': 25.0,
            'humidity': 75.0,
            'rainfall': 150.0,
            'description': 'clear sky',
            'city': city or 'Unknown',
            'source': 'mock'
        }
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Make API request to OpenWeatherMap with error handling.
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response data or None on error
        """
        if not REQUESTS_AVAILABLE or not self.api_key:
            logger.warning("API request skipped: requests unavailable or no API key")
            return None
        
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.get(url, params=params, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            logger.error(f"API request timeout after {self.timeout} seconds")
            return None
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e.response.status_code} - {e.response.text}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return None
        except ValueError as e:
            logger.error(f"Invalid JSON response: {str(e)}")
            return None
    
    def get_weather_by_coords(self, lat: float, lon: float) -> Dict[str, Any]:
        """
        Fetch current weather data by geographic coordinates.
        
        Args:
            lat: Latitude (-90 to 90)
            lon: Longitude (-180 to 180)
            
        Returns:
            Dictionary containing:
            - temperature: Temperature in Celsius
            - humidity: Humidity percentage (0-100)
            - rainfall: Estimated monthly rainfall in mm
            - description: Weather description
            - city: City name
            - source: 'api' or 'mock'
        """
        logger.info(f"Fetching weather for coordinates: lat={lat}, lon={lon}")
        
        params = {
            'lat': lat,
            'lon': lon,
            'appid': self.api_key,
            'units': self.units
        }
        
        data = self._make_api_request('/weather', params)
        
        if data is None:
            if self.enable_fallback:
                logger.warning("Using fallback mock weather data")
                return self._get_mock_weather_data(city=f"Lat:{lat}, Lon:{lon}")
            else:
                raise WeatherServiceError("Weather API unavailable and fallback disabled")
        
        try:
            # Extract relevant data from OpenWeatherMap response
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            rain = data.get('rain', {})
            
            # Convert rainfall from mm/h to estimated monthly mm
            hourly_rain = rain.get('1h', 0)
            monthly_rain_estimate = hourly_rain * 24 * 30  # Approximate monthly estimate
            
            result = {
                'temperature': main.get('temp', 25.0),
                'humidity': main.get('humidity', 75.0),
                'rainfall': monthly_rain_estimate,
                'description': weather.get('description', 'unknown'),
                'city': data.get('name', 'Unknown'),
                'source': 'api'
            }
            
            logger.info(f"Weather data fetched: {result['city']}, {result['temperature']}°C")
            return result
            
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse weather API response: {str(e)}")
            if self.enable_fallback:
                return self._get_mock_weather_data(city=f"Lat:{lat}, Lon:{lon}")
            raise WeatherServiceError(f"Invalid API response format: {str(e)}")
    
    def get_weather_by_city(self, city: str) -> Dict[str, Any]:
        """
        Fetch current weather data by city name.
        
        Args:
            city: City name (e.g., "Delhi", "Mumbai", "New York")
            
        Returns:
            Dictionary containing weather data (same structure as get_weather_by_coords)
        """
        logger.info(f"Fetching weather for city: {city}")
        
        params = {
            'q': city,
            'appid': self.api_key,
            'units': self.units
        }
        
        data = self._make_api_request('/weather', params)
        
        if data is None:
            if self.enable_fallback:
                logger.warning("Using fallback mock weather data")
                return self._get_mock_weather_data(city=city)
            else:
                raise WeatherServiceError("Weather API unavailable and fallback disabled")
        
        try:
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            rain = data.get('rain', {})
            
            hourly_rain = rain.get('1h', 0)
            monthly_rain_estimate = hourly_rain * 24 * 30
            
            result = {
                'temperature': main.get('temp', 25.0),
                'humidity': main.get('humidity', 75.0),
                'rainfall': monthly_rain_estimate,
                'description': weather.get('description', 'unknown'),
                'city': data.get('name', city),
                'source': 'api'
            }
            
            logger.info(f"Weather data fetched: {result['city']}, {result['temperature']}°C")
            return result
            
        except (KeyError, IndexError) as e:
            logger.error(f"Failed to parse weather API response: {str(e)}")
            if self.enable_fallback:
                return self._get_mock_weather_data(city=city)
            raise WeatherServiceError(f"Invalid API response format: {str(e)}")
    
    def get_weather(self, location: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Unified method to get weather data from various location formats.
        
        Args:
            location: Dictionary with either:
                - 'lat' and 'lon': Geographic coordinates
                - 'city': City name
                - 'latitude' and 'longitude': Alternative keys
                
        Returns:
            Weather data dictionary
            
        Raises:
            WeatherServiceError: If location is invalid or API fails
        """
        if not location:
            raise WeatherServiceError("No location provided. Please provide city name or coordinates.")
        
        # Try different location formats
        if 'lat' in location and 'lon' in location:
            return self.get_weather_by_coords(float(location['lat']), float(location['lon']))
        elif 'latitude' in location and 'longitude' in location:
            return self.get_weather_by_coords(float(location['latitude']), float(location['longitude']))
        elif 'city' in location:
            return self.get_weather_by_city(str(location['city']))
        else:
            raise WeatherServiceError(
                "Invalid location format. Provide either "
                "'lat'/'lon', 'latitude'/'longitude', or 'city'"
            )


class WeatherServiceError(Exception):
    """Custom exception for WeatherService errors."""
    pass


# Convenience function for quick usage
def get_current_weather(location: Dict[str, Any]) -> Dict[str, Any]:
    """
    Quick function to get weather data.
    
    Args:
        location: Location dictionary
        
    Returns:
        Weather data dictionary
    """
    service = WeatherService()
    return service.get_weather(location)


# Example usage and testing
if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    
    # Initialize service
    weather = WeatherService()
    
    # Test with coordinates
    print("=== Test 1: Weather by coordinates (Delhi) ===")
    try:
        weather_data = weather.get_weather_by_coords(28.6139, 77.2090)
        print(f"City: {weather_data['city']}")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Humidity: {weather_data['humidity']}%")
        print(f"Rainfall: {weather_data['rainfall']}mm")
        print(f"Source: {weather_data['source']}")
    except WeatherServiceError as e:
        print(f"Error: {e}")
    
    print("\n=== Test 2: Weather by city name ===")
    try:
        weather_data = weather.get_weather_by_city("Mumbai")
        print(f"City: {weather_data['city']}")
        print(f"Temperature: {weather_data['temperature']}°C")
        print(f"Humidity: {weather_data['humidity']}%")
    except WeatherServiceError as e:
        print(f"Error: {e}")
    
    print("\n=== Test 3: Unified method ===")
    try:
        weather_data = weather.get_weather({'city': 'Bangalore'})
        print(f"City: {weather_data['city']}")
        print(f"Temperature: {weather_data['temperature']}°C")
    except WeatherServiceError as e:
        print(f"Error: {e}")
