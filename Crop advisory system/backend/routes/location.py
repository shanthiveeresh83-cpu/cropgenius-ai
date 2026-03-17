"""
Location Routes - User Location Management
Handles automatic location detection and user preferences
"""

import logging
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import sqlite3

logger = logging.getLogger(__name__)

location_bp = Blueprint('location', __name__)

def get_db_connection():
    """Get database connection"""
    from app import get_db_connection as app_db_conn
    return app_db_conn()


@location_bp.route('/detect', methods=['POST'])
@jwt_required()
def detect_location():
    """
    Detect and save user location from coordinates
    
    Request body:
    - latitude: User's latitude
    - longitude: User's longitude
    
    Returns:
        Location details with district, state, country
    """
    data = request.get_json(silent=True) or {}
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    user_email = get_jwt_identity()
    
    if latitude is None or longitude is None:
        return jsonify({'error': 'latitude and longitude are required'}), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
    except (TypeError, ValueError):
        return jsonify({'error': 'Invalid coordinates'}), 400
    
    # Validate coordinates
    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({'error': 'Coordinates out of valid range'}), 400
    
    try:
        # Import location service
        from services.location_service import LocationService
        location_service = LocationService()
        
        # Reverse geocode
        location_info = location_service.reverse_geocode(latitude, longitude)
        
        # Get real-time weather data
        try:
            from services.weather_service import WeatherService
            weather_service = WeatherService()
            weather_data = weather_service.get_weather_by_coords(latitude, longitude)
            location_info['weather'] = weather_data
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}")
            location_info['weather'] = {
                'temperature': 25.0,
                'humidity': 75.0,
                'rainfall': 150.0,
                'source': 'fallback'
            }
        
        # Save to database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET latitude = ?, longitude = ?, district = ?, state = ?, 
                city = ?, formatted_address = ?, location_updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (
            latitude, longitude,
            location_info.get('district'),
            location_info.get('state'),
            location_info.get('city'),
            location_info.get('formatted_address'),
            user_email
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Location saved successfully',
            'location': location_info
        })
        
    except Exception as e:
        logger.error(f"Location detection error: {str(e)}")
        return jsonify({'error': f'Failed to process location: {str(e)}'}), 500


@location_bp.route('/update', methods=['PUT'])
@jwt_required()
def update_location():
    """
    Manually update user's preferred location
    
    Request body:
    - latitude: New latitude
    - longitude: New longitude
    - district: District name (optional)
    - state: State name (optional)
    
    Returns:
        Updated location details
    """
    data = request.get_json(silent=True) or {}
    user_email = get_jwt_identity()
    
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    district = data.get('district')
    state = data.get('state')
    
    if latitude is None or longitude is None:
        return jsonify({'error': 'latitude and longitude are required'}), 400
    
    try:
        latitude = float(latitude)
        longitude = float(longitude)
        
        # Get location details if not provided
        if not district or not state:
            from services.location_service import LocationService
            location_service = LocationService()
            location_info = location_service.reverse_geocode(latitude, longitude)
            district = district or location_info.get('district')
            state = state or location_info.get('state')
            city = location_info.get('city')
            formatted_address = location_info.get('formatted_address')
        else:
            city = data.get('city', district)
            formatted_address = f"{district}, {state}"
        
        # Update database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE users 
            SET latitude = ?, longitude = ?, district = ?, state = ?, 
                city = ?, formatted_address = ?, location_updated_at = CURRENT_TIMESTAMP
            WHERE email = ?
        ''', (latitude, longitude, district, state, city, formatted_address, user_email))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Location updated successfully',
            'location': {
                'latitude': latitude,
                'longitude': longitude,
                'district': district,
                'state': state,
                'city': city,
                'formatted_address': formatted_address
            }
        })
        
    except Exception as e:
        logger.error(f"Location update error: {str(e)}")
        return jsonify({'error': f'Failed to update location: {str(e)}'}), 500


@location_bp.route('/current', methods=['GET'])
@jwt_required()
def get_current_location():
    """
    Get user's saved location
    
    Returns:
        User's current location preferences
    """
    user_email = get_jwt_identity()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT latitude, longitude, district, state, city, 
                   formatted_address, location_updated_at
            FROM users 
            WHERE email = ?
        ''', (user_email,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row and row[0] is not None:
            return jsonify({
                'success': True,
                'location': {
                    'latitude': row[0],
                    'longitude': row[1],
                    'district': row[2],
                    'state': row[3],
                    'city': row[4],
                    'formatted_address': row[5],
                    'updated_at': row[6]
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'No location saved. Please enable location access.'
            }), 404
            
    except Exception as e:
        logger.error(f"Get location error: {str(e)}")
        return jsonify({'error': f'Failed to retrieve location: {str(e)}'}), 500


@location_bp.route('/search', methods=['POST'])
def search_location():
    """
    Search for any location and get its details with weather data
    No authentication required - public endpoint
    
    Request body:
    - query: City name, district, or address
    
    Returns:
        Location details with current weather
    """
    data = request.get_json(silent=True) or {}
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'query is required'}), 400
    
    try:
        import requests
        
        # Use Nominatim for free geocoding
        nominatim_url = "https://nominatim.openstreetmap.org/search"
        params = {
            'q': query,
            'format': 'json',
            'addressdetails': 1,
            'limit': 1,
            'countrycodes': 'in'  # Restrict to India
        }
        headers = {'User-Agent': 'CropAdvisorySystem/1.0'}
        
        response = requests.get(nominatim_url, params=params, headers=headers, timeout=5)
        response.raise_for_status()
        results = response.json()
        
        if not results:
            return jsonify({'error': 'Location not found'}), 404
        
        result = results[0]
        addr = result.get('address', {})
        
        location_info = {
            'latitude': float(result['lat']),
            'longitude': float(result['lon']),
            'city': addr.get('city') or addr.get('town') or addr.get('village'),
            'district': addr.get('county') or addr.get('state_district'),
            'state': addr.get('state'),
            'country': addr.get('country'),
            'formatted_address': result.get('display_name')
        }
        
        # Get weather data for this location
        try:
            from services.weather_service import WeatherService
            weather_service = WeatherService()
            weather_data = weather_service.get_weather({
                'lat': location_info['latitude'],
                'lon': location_info['longitude']
            })
            location_info['weather'] = weather_data
        except Exception as e:
            logger.warning(f"Weather fetch failed: {e}")
            location_info['weather'] = None
        
        return jsonify({
            'success': True,
            'location': location_info
        })
        
    except Exception as e:
        logger.error(f"Location search error: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@location_bp.route('/geocode', methods=['POST'])
def geocode_address():
    """
    Convert address to coordinates (forward geocoding)
    
    Request body:
    - address: Address string
    
    Returns:
        Coordinates and location details
    """
    data = request.get_json(silent=True) or {}
    address = data.get('address')
    
    if not address:
        return jsonify({'error': 'address is required'}), 400
    
    try:
        import requests
        import os
        
        api_key = os.getenv('OPENCAGE_API_KEY')
        url = "https://api.opencagedata.com/geocode/v1/json"
        
        params = {
            'q': address,
            'key': api_key,
            'language': 'en',
            'countrycode': 'in'  # Restrict to India
        }
        
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()
        
        if data['results']:
            result = data['results'][0]
            geometry = result['geometry']
            components = result['components']
            
            return jsonify({
                'success': True,
                'location': {
                    'latitude': geometry['lat'],
                    'longitude': geometry['lng'],
                    'district': components.get('state_district') or components.get('county'),
                    'state': components.get('state'),
                    'city': components.get('city') or components.get('town'),
                    'formatted_address': result['formatted']
                }
            })
        else:
            return jsonify({'error': 'Address not found'}), 404
            
    except Exception as e:
        logger.error(f"Geocoding error: {str(e)}")
        return jsonify({'error': f'Geocoding failed: {str(e)}'}), 500
