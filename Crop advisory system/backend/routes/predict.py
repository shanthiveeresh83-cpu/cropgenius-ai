"""
Predict Routes - Crop Prediction Endpoints

This module provides Flask routes for crop prediction:
- POST /predict: Manual prediction with all features
- POST /predict/auto: Automatic prediction with location-based weather and estimated nutrients
- GET /predict/status: Check prediction service status

Usage:
    from routes.predict import predict_bp
    app.register_blueprint(predict_bp, url_prefix='/predict')
"""

import os
import logging
from typing import Dict, Any, Optional, Tuple

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np
import pickle

# Lazy imports - services are imported when first used to avoid startup errors
# This allows the app to start even if pandas/scikit-learn are not installed
WeatherService = None
WeatherServiceError = None
NutrientEstimator = None
NutrientEstimatorError = None

def get_weather_service():
    """Get or create weather service instance with lazy import."""
    global WeatherService, WeatherServiceError
    if WeatherService is None:
        from services.weather_service import WeatherService, WeatherServiceError
    return WeatherService()

def get_nutrient_estimator():
    """Get or create nutrient estimator instance with lazy import."""
    global NutrientEstimator, NutrientEstimatorError
    if NutrientEstimator is None:
        from services.nutrient_estimator import NutrientEstimator, NutrientEstimatorError
    return NutrientEstimator()

logger = logging.getLogger(__name__)

# Create blueprint
predict_bp = Blueprint('predict', __name__)

# Feature keys required for prediction
FEATURE_KEYS = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Initialize services (will be done in app.py or lazily)
_model = None
_weather_service = None
_nutrient_estimator = None


def get_model():
    """Get or load the crop prediction model."""
    global _model
    if _model is None:
        backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(backend_dir, "model.pkl")
        try:
            _model = pickle.load(open(model_path, "rb"))
            logger.info(f"Loaded crop prediction model from: {model_path}")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise
    return _model


# Note: get_weather_service() and get_nutrient_estimator() are defined above with lazy imports
# The global variables _weather_service and _nutrient_estimator are kept for backward compatibility


def parse_feature_payload(data: Dict[str, Any], require_all: bool = True) -> Tuple[list, Optional[str]]:
    """
    Parse and validate feature payload from request.
    
    Args:
        data: Request JSON data
        require_all: If True, all features must be present
        
    Returns:
        Tuple of (feature_values, error_message)
    """
    if not isinstance(data, dict):
        return None, "Request body must be a JSON object"
    
    if require_all:
        missing = [k for k in FEATURE_KEYS if k not in data]
        if missing:
            return None, f"Missing required fields: {', '.join(missing)}"
    
    try:
        values = []
        for key in FEATURE_KEYS:
            if key in data:
                values.append(float(data[key]))
            else:
                values.append(None)
    except (TypeError, ValueError):
        return None, "All feature fields must be numeric"
    
    return values, None


def validate_features(values: list) -> Optional[str]:
    """
    Validate feature values are within acceptable ranges.
    
    Args:
        values: List of feature values [N, P, K, temperature, humidity, ph, rainfall]
        
    Returns:
        Error message if invalid, None if valid
    """
    n, p, k, temperature, humidity, ph, rainfall = values
    
    if humidity is not None and not (0 <= humidity <= 100):
        return "humidity must be between 0 and 100"
    if ph is not None and not (0 <= ph <= 14):
        return "ph must be between 0 and 14"
    if rainfall is not None and rainfall < 0:
        return "rainfall must be >= 0"
    if temperature is not None and temperature < -50 or temperature > 60:
        return "temperature must be between -50 and 60"
    
    return None


# ============================================================================
# ROUTES
# ============================================================================

@predict_bp.route("/status", methods=["GET"])
def get_status():
    """
    Check prediction service status.
    
    Returns:
        JSON with service status information
    """
    try:
        model = get_model()
        model_loaded = model is not None
    except Exception:
        model_loaded = False
    
    return jsonify({
        "status": "ok" if model_loaded else "degraded",
        "model_loaded": model_loaded,
        "weather_service": "available" if get_weather_service() else "unavailable",
        "nutrient_estimator": "available" if get_nutrient_estimator() else "unavailable"
    })


@predict_bp.route("", methods=["POST"])
@predict_bp.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    """
    Fully Automatic Crop Prediction Endpoint.
    
    Automatically uses logged-in user's saved location for weather data.
    If no location is saved, prompts user to enable location detection.
    
    NO MANUAL INPUT REQUIRED.
    
    Returns:
        JSON with recommended_crop and all automatically collected parameter values
    """
    try:
        data = request.get_json(silent=True) or {}
        user_email = get_jwt_identity()
        
        # Get user's saved location from database
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT latitude, longitude, city, district, state FROM users WHERE email = ?",
            (user_email,)
        )
        user_data = cursor.fetchone()
        conn.close()
        
        # Check if user has saved location
        if user_data and user_data[0] is not None and user_data[1] is not None:
            # Use user's saved location
            location = {
                'lat': user_data[0],
                'lon': user_data[1],
                'city': user_data[2] or 'Unknown',
                'district': user_data[3] or 'Unknown',
                'state': user_data[4] or 'Unknown'
            }
            logger.info(f"Using user's saved location: {location['city']}, {location['state']}")
        else:
            # No saved location - return error asking user to enable location
            return jsonify({
                "error": "Location not set",
                "message": "Please enable location detection to get personalized recommendations",
                "action_required": "enable_location"
            }), 400
        
        # Import the environmental data collector
        from services.environmental_data import EnvironmentalDataCollector, EnvironmentalDataError
        
        # Collect all data automatically using user's location
        collector = EnvironmentalDataCollector()
        env_data = collector.get_all_data({
            'city': location['city'],
            'lat': location['lat'],
            'lon': location['lon']
        })
        
        # Prepare feature values
        feature_values = [
            env_data['N'],
            env_data['P'],
            env_data['K'],
            env_data['temperature'],
            env_data['humidity'],
            env_data['ph'],
            env_data['rainfall']
        ]
        
        # Validate features
        validation_error = validate_features(feature_values)
        if validation_error:
            return jsonify({"error": f"Invalid feature values: {validation_error}"}), 400
        
        # Make prediction
        model = get_model()
        features = np.array([feature_values])
        prediction = model.predict(features)[0]
        
        # Get confidence if available
        try:
            probabilities = model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 2)
        except Exception:
            confidence = None
        
        # Store prediction in database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO predictions 
                   (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) 
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (user_email, prediction, *feature_values)
            )
            conn.commit()
            conn.close()
            stored = True
        except Exception as db_error:
            logger.warning(f"Failed to store prediction: {str(db_error)}")
            stored = False
        
        return jsonify({
            "recommended_crop": prediction,
            "confidence": confidence,
            "features": {
                "N": env_data['N'],
                "P": env_data['P'],
                "K": env_data['K'],
                "temperature": env_data['temperature'],
                "humidity": env_data['humidity'],
                "ph": env_data['ph'],
                "rainfall": env_data['rainfall']
            },
            "data_sources": env_data['sources'],
            "location": {
                "city": location['city'],
                "district": location['district'],
                "state": location['state'],
                "coordinates": {
                    "latitude": location['lat'],
                    "longitude": location['lon']
                }
            },
            "prediction_stored": stored,
            "mode": "fully_automatic"
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@predict_bp.route("/auto", methods=["POST"])
@jwt_required()
def predict_auto():
    """
    Automatic crop prediction endpoint.
    """
    data = request.get_json(silent=True) or {}
    
    try:
        location = data.get("location", {})
        weather_service = get_weather_service()
        
        try:
            weather_data = weather_service.get_weather(location)
        except WeatherServiceError as e:
            logger.warning(f"Weather fetch failed: {str(e)}, using defaults")
            weather_data = {'temperature': 25.0, 'humidity': 75.0, 'rainfall': 150.0}
        
        temperature = weather_data.get('temperature', 25.0)
        humidity = weather_data.get('humidity', 75.0)
        rainfall = weather_data.get('rainfall', 150.0)
        weather_city = weather_data.get('city', 'Unknown')
        weather_source = weather_data.get('source', 'default')
        
        nutrient_estimator = get_nutrient_estimator()
        k_value = float(data.get("K", data.get("k", 40.0)))
        ph_value = float(data.get("ph", 7.0))
        
        try:
            n_value, p_value = nutrient_estimator.estimate_nutrients(
                soil_type=data.get("soil_type"),
                region=data.get("region"),
                crop=data.get("crop"),
                ph=ph_value,
                rainfall=rainfall,
                temperature=temperature,
                humidity=humidity,
                k=k_value
            )
            nutrient_source = "ml_model" if nutrient_estimator.is_loaded else "fallback"
        except NutrientEstimatorError as e:
            logger.warning(f"Nutrient estimation failed: {str(e)}, using defaults")
            n_value, p_value = 50.0, 30.0
            nutrient_source = "default"
        
        feature_values = [n_value, p_value, k_value, temperature, humidity, ph_value, rainfall]
        
        validation_error = validate_features(feature_values)
        if validation_error:
            return jsonify({"error": f"Invalid feature values: {validation_error}"}), 400
        
        model = get_model()
        features = np.array([feature_values])
        prediction = model.predict(features)[0]
        
        try:
            probabilities = model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 2)
        except Exception:
            confidence = None
        
        try:
            from app import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            user_email = get_jwt_identity() or "user"
            cursor.execute(
                """INSERT INTO predictions 
                   (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) 
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (user_email, prediction, *feature_values)
            )
            conn.commit()
            conn.close()
            stored = True
        except Exception as db_error:
            logger.warning(f"Failed to store prediction: {str(db_error)}")
            stored = False
        
        return jsonify({
            "recommended_crop": prediction,
            "confidence": confidence,
            "features": {
                "N": n_value,
                "P": p_value,
                "K": k_value,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph_value,
                "rainfall": rainfall
            },
            "data_sources": {
                "temperature": weather_source,
                "humidity": weather_source,
                "rainfall": weather_source,
                "N": nutrient_source,
                "P": nutrient_source,
                "K": "user_input",
                "ph": "user_input" if "ph" in data else "default"
            },
            "location": {
                "city": weather_city,
                "provided": location if location else "default"
            },
            "prediction_stored": stored
        })
        
    except Exception as e:
        logger.error(f"Auto prediction error: {str(e)}")
        return jsonify({"error": f"Auto prediction failed: {str(e)}"}), 500


@predict_bp.route("/weather", methods=["POST"])
def get_weather_only():
    """Standalone weather fetch endpoint."""
    data = request.get_json(silent=True) or {}
    location = data.get("location", {})
    
    try:
        weather_service = get_weather_service()
        weather_data = weather_service.get_weather(location)
        return jsonify(weather_data)
    except WeatherServiceError as e:
        return jsonify({"error": str(e)}), 400


@predict_bp.route("/nutrients", methods=["POST"])
def estimate_nutrients_only():
    """Standalone nutrient estimation endpoint."""
    data = request.get_json(silent=True) or {}
    
    try:
        nutrient_estimator = get_nutrient_estimator()
        n_value, p_value = nutrient_estimator.estimate_nutrients(
            soil_type=data.get("soil_type"),
            region=data.get("region"),
            crop=data.get("crop"),
            ph=float(data.get("ph", 7.0)),
            rainfall=float(data.get("rainfall", 100.0))
        )
        
        return jsonify({
            "estimated_N": n_value,
            "estimated_P": p_value,
            "source": "ml_model" if nutrient_estimator.is_loaded else "fallback"
        })
    except NutrientEstimatorError as e:
        return jsonify({"error": str(e)}), 400


# ============================================================================
# NEW: Fully Automatic Prediction Endpoints (No User Input Required)
# ============================================================================

@predict_bp.route("/fully-auto", methods=["POST"])
@jwt_required()
def predict_fully_auto():
    """
    Fully Automatic Crop Prediction - NO USER INPUT REQUIRED.
    
    This endpoint automatically fetches ALL parameters:
    - Temperature, Humidity, Rainfall → from Weather API
    - N, P, K, pH → from dataset OR simulated IoT sensors
    
    Optional request body:
    - location: dict with 'city' or 'lat'/'lon'
    
    Returns:
        JSON with predicted crop and all fetched parameter values
    """
    data = request.get_json(silent=True) or {}
    location = data.get("location", {})
    
    try:
        # Import the environmental data collector
        from services.environmental_data import EnvironmentalDataCollector, EnvironmentalDataError
        
        # Collect all data automatically
        collector = EnvironmentalDataCollector()
        env_data = collector.get_all_data(location)
        
        # Prepare feature values
        feature_values = [
            env_data['N'],
            env_data['P'],
            env_data['K'],
            env_data['temperature'],
            env_data['humidity'],
            env_data['ph'],
            env_data['rainfall']
        ]
        
        # Validate features
        validation_error = validate_features(feature_values)
        if validation_error:
            return jsonify({"error": f"Invalid feature values: {validation_error}"}), 400
        
        # Make prediction
        model = get_model()
        features = np.array([feature_values])
        prediction = model.predict(features)[0]
        
        # Get confidence if available
        try:
            probabilities = model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 2)
        except Exception:
            confidence = None
        
        # Store prediction in database
        try:
            from app import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            user_email = get_jwt_identity() or "user"
            cursor.execute(
                """INSERT INTO predictions 
                   (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) 
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (user_email, prediction, *feature_values)
            )
            conn.commit()
            conn.close()
            stored = True
        except Exception as db_error:
            logger.warning(f"Failed to store prediction: {str(db_error)}")
            stored = False
        
        # Generate price analysis
        price_analysis = None
        try:
            import hashlib
            import json
            
            # Load base prices from CSV
            base_prices = {}
            try:
                import pandas as pd
                backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                price_csv_path = os.path.join(backend_dir, 'crop_prices.csv')
                if os.path.exists(price_csv_path):
                    price_df = pd.read_csv(price_csv_path)
                    for _, row in price_df.iterrows():
                        base_prices[row['crop'].lower()] = int(row['base_price'])
            except:
                pass
            
            if not base_prices:
                base_prices = {'rice': 2650, 'wheat': 2150, 'maize': 1850, 'cotton': 6200, 'sugarcane': 3200}
            
            base_price = base_prices.get(prediction.lower(), 2500)
            seed_source = f"{prediction}|{env_data['N']}|{env_data['P']}|{env_data['K']}"
            seed = int(hashlib.md5(seed_source.encode("utf-8")).hexdigest()[:8], 16)
            rng = np.random.default_rng(seed)
            price_history = np.array([base_price + int(rng.integers(-200, 201)) for _ in range(40)])
            
            # Import price predictor
            try:
                from price_prediction import CropPricePrediction
                price_predictor = CropPricePrediction()
                price_predictor.train_price_model(price_history)
                trend_analysis = price_predictor.analyze_price_trend(price_history)
                future_prices = price_predictor.predict_future_prices(price_history, days=7)
                
                price_analysis = {
                    'current_price': trend_analysis.get('current_price', base_price),
                    'trend': trend_analysis.get('trend', 'Stable'),
                    'change_percentage': trend_analysis.get('change_percentage', 0),
                    'recommendation': trend_analysis.get('recommendation', 'Market stable'),
                    'future_prices': [round(float(p), 2) for p in future_prices[:7]]
                }
            except:
                price_analysis = {
                    'current_price': base_price,
                    'trend': 'Stable',
                    'change_percentage': 0,
                    'recommendation': 'Price data unavailable',
                    'future_prices': []
                }
        except Exception as price_error:
            logger.warning(f"Price analysis failed: {str(price_error)}")
            price_analysis = None
        
        return jsonify({
            "recommended_crop": prediction,
            "confidence": confidence,
            "features": {
                "N": env_data['N'],
                "P": env_data['P'],
                "K": env_data['K'],
                "temperature": env_data['temperature'],
                "humidity": env_data['humidity'],
                "ph": env_data['ph'],
                "rainfall": env_data['rainfall']
            },
            "data_sources": env_data['sources'],
            "location": env_data['location'],
            "prediction_stored": stored,
            "mode": "fully_automatic",
            "price_analysis": price_analysis
        })
        
    except EnvironmentalDataError as e:
        logger.error(f"Environmental data collection error: {str(e)}")
        return jsonify({"error": f"Failed to collect environmental data: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Fully auto prediction error: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500


@predict_bp.route("/history", methods=["DELETE"])
@jwt_required()
def clear_history():
    """
    Clear all prediction history for the current user.
    
    Returns:
        JSON with success message and count of deleted records
    """
    try:
        user_email = get_jwt_identity()
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete all predictions for this user
        cursor.execute("DELETE FROM predictions WHERE user_email = ?", (user_email,))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": "Prediction history cleared successfully",
            "deleted_count": deleted_count
        })
    except Exception as e:
        logger.error(f"Failed to clear history: {str(e)}")
        return jsonify({"error": f"Failed to clear history: {str(e)}"}), 500
@jwt_required()
def predict_fully_auto_ml():
    """
    Fully Automatic Crop Prediction with ML Nutrient Estimation.
    
    This endpoint uses ML-based nutrient estimation for better accuracy:
    - Temperature, Humidity, Rainfall → from Weather API
    - N, P → from ML Nutrient Estimator
    - K, pH → default values
    
    Optional request body:
    - location: dict with 'city' or 'lat'/'lon'
    
    Returns:
        JSON with predicted crop and all fetched parameter values
    """
    data = request.get_json(silent=True) or {}
    location = data.get("location", {})
    
    try:
        # Import the environmental data collector
        from services.environmental_data import EnvironmentalDataCollector, EnvironmentalDataError
        
        # Collect all data with ML estimation
        collector = EnvironmentalDataCollector()
        env_data = collector.get_data_with_estimator(location)
        
        # Prepare feature values
        feature_values = [
            env_data['N'],
            env_data['P'],
            env_data['K'],
            env_data['temperature'],
            env_data['humidity'],
            env_data['ph'],
            env_data['rainfall']
        ]
        
        # Validate features
        validation_error = validate_features(feature_values)
        if validation_error:
            return jsonify({"error": f"Invalid feature values: {validation_error}"}), 400
        
        # Make prediction
        model = get_model()
        features = np.array([feature_values])
        prediction = model.predict(features)[0]
        
        # Get confidence if available
        try:
            probabilities = model.predict_proba(features)[0]
            confidence = round(max(probabilities) * 100, 2)
        except Exception:
            confidence = None
        
        # Store prediction in database
        try:
            from app import get_db_connection
            conn = get_db_connection()
            cursor = conn.cursor()
            user_email = get_jwt_identity() or "user"
            cursor.execute(
                """INSERT INTO predictions 
                   (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) 
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (user_email, prediction, *feature_values)
            )
            conn.commit()
            conn.close()
            stored = True
        except Exception as db_error:
            logger.warning(f"Failed to store prediction: {str(db_error)}")
            stored = False
        
        return jsonify({
            "recommended_crop": prediction,
            "confidence": confidence,
            "features": {
                "N": env_data['N'],
                "P": env_data['P'],
                "K": env_data['K'],
                "temperature": env_data['temperature'],
                "humidity": env_data['humidity'],
                "ph": env_data['ph'],
                "rainfall": env_data['rainfall']
            },
            "data_sources": env_data['sources'],
            "location": env_data['location'],
            "prediction_stored": stored,
            "mode": "fully_automatic_ml"
        })
        
    except EnvironmentalDataError as e:
        logger.error(f"Environmental data collection error: {str(e)}")
        return jsonify({"error": f"Failed to collect environmental data: {str(e)}"}), 500
    except Exception as e:
        logger.error(f"Fully auto ML prediction error: {str(e)}")
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
