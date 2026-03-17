"""
Location Service - Automatic Location Detection & Reverse Geocoding
Handles user location preferences for personalized crop recommendations
"""

import requests
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger(__name__)

class LocationService:
    """Service for handling user location and reverse geocoding"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize location service
        
        Args:
            api_key: OpenCage Geocoding API key (or use environment variable)
        """
        import os
        self.api_key = api_key or os.getenv('OPENCAGE_API_KEY')
        self.base_url = "https://api.opencagedata.com/geocode/v1/json"
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Dict:
        """
        Convert coordinates to address (district, state, country)
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Dict with location details
        """
        # Try OpenCage first if API key is available
        if self.api_key:
            try:
                params = {
                    'q': f'{latitude},{longitude}',
                    'key': self.api_key,
                    'language': 'en',
                    'pretty': 1
                }
                
                response = requests.get(self.base_url, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()
                
                if data['results']:
                    components = data['results'][0]['components']
                    formatted = data['results'][0]['formatted']
                    
                    city = components.get('city') or components.get('town') or components.get('village') or components.get('municipality')
                    state = components.get('state') or components.get('province') or components.get('region')
                    district = components.get('state_district') or components.get('county')
                    country = components.get('country')
                    
                    # Avoid duplicate values
                    if district == city:
                        district = ''
                    if state == city:
                        state = ''
                    
                    return {
                        'success': True,
                        'latitude': latitude,
                        'longitude': longitude,
                        'district': district or '',
                        'state': state or '',
                        'country': country or '',
                        'formatted_address': formatted,
                        'city': city or state or ''
                    }
            except Exception as e:
                logger.warning(f"OpenCage geocoding failed: {str(e)}, trying Nominatim")
        
        # Fallback to free Nominatim API (OpenStreetMap)
        try:
            nominatim_url = "https://nominatim.openstreetmap.org/reverse"
            params = {
                'lat': latitude,
                'lon': longitude,
                'format': 'json',
                'addressdetails': 1,
                'accept-language': 'en'
            }
            headers = {
                'User-Agent': 'CropAdvisorySystem/1.0'
            }
            
            response = requests.get(nominatim_url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            
            if 'address' in data:
                addr = data['address']
                city = addr.get('city') or addr.get('town') or addr.get('village') or addr.get('municipality')
                state = addr.get('state') or addr.get('province') or addr.get('region')
                district = addr.get('county') or addr.get('state_district')
                country = addr.get('country')
                
                # Avoid duplicate values
                if district == city:
                    district = ''
                if state == city:
                    state = ''
                
                return {
                    'success': True,
                    'latitude': latitude,
                    'longitude': longitude,
                    'district': district or '',
                    'state': state or '',
                    'country': country or '',
                    'formatted_address': data.get('display_name'),
                    'city': city or state or ''
                }
        except Exception as e:
            logger.error(f"Nominatim geocoding error: {str(e)}")
        
        return self._fallback_location(latitude, longitude)
    
    def _fallback_location(self, lat: float, lon: float) -> Dict:
        """Fallback when geocoding fails"""
        return {
            'success': False,
            'latitude': lat,
            'longitude': lon,
            'district': f'Lat: {lat:.4f}, Lon: {lon:.4f}',
            'state': '',
            'country': '',
            'formatted_address': f'Coordinates: {lat:.4f}, {lon:.4f}',
            'city': ''
        }
    
    def validate_coordinates(self, latitude: float, longitude: float) -> bool:
        """Validate if coordinates are within valid range"""
        return -90 <= latitude <= 90 and -180 <= longitude <= 180
    
    def get_indian_location_info(self, latitude: float, longitude: float) -> Dict:
        """
        Get detailed Indian location information
        
        Returns district, state, and agricultural zone
        """
        location = self.reverse_geocode(latitude, longitude)
        
        # Add agricultural zone based on state
        state = location.get('state', '').lower()
        agri_zones = {
            'punjab': 'Northern Plains',
            'haryana': 'Northern Plains',
            'uttar pradesh': 'Northern Plains',
            'maharashtra': 'Western Plateau',
            'karnataka': 'Southern Plateau',
            'tamil nadu': 'Southern Coastal',
            'andhra pradesh': 'Eastern Coastal',
            'telangana': 'Southern Plateau',
            'west bengal': 'Eastern Plains',
            'bihar': 'Eastern Plains',
            'madhya pradesh': 'Central Plateau',
            'rajasthan': 'Western Arid'
        }
        
        location['agricultural_zone'] = agri_zones.get(state, 'General')
        return location


# Convenience function
def get_location_from_coordinates(lat: float, lon: float) -> Dict:
    """Quick function to get location from coordinates"""
    service = LocationService()
    return service.reverse_geocode(lat, lon)
