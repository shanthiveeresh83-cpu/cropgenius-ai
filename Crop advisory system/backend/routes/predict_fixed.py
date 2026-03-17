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

# Import services
from services.weather_service import WeatherService, WeatherServiceError
from services.nutrient_estimator import NutrientEstimator, NutrientEstimatorError

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


def get_weather_service() -> WeatherService:
    """Get or create weather service instance."""
    global _weather_service
    if _weather_service is None:
        _weather_service = WeatherService()
    return _weather_service


def get_nutrient_estimator() -> NutrientEstimator:
    """Get or create nutrient estimator instance."""
    global _nutrient_estimator
    if _nutrient_estimator is None:
        _nutrient_estimator = NutrientEstimator()
    return _nutrient_estimator


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
    Hybrid Crop Prediction Endpoint.
    
    This endpoint supports BOTH manual and automatic input modes:
    
    === MANUAL MODE (All 7 features required) ===
    Provide all features explicitly:
    - N: Nitrogen (numeric)
    - P: Phosphorus (numeric)
    - K: Potassium (numeric)
    - temperature: Temperature in Celsius (numeric)
    - humidity: Humidity percentage (numeric)
    - ph: Soil pH (numeric)
    - rainfall: Rainfall in mm (numeric)
    
    === AUTOMATIC MODE (Hybrid - fetches missing values) ===
    When N, P, or temperature is NOT provided, the system will:
    1. Fetch temperature from Weather API based on location
    2. Estimate N and P using ML model or fallback data
    
    Request body for AUTO mode:
    - location: Dictionary with either:
        - lat/lon: Geographic coordinates
        - city: City name
    - soil_type: Soil type (clay, sandy, loam, silt, peaty, chalky)
    - region: Region/state (punjab, haryana, maharashtra, etc.)
    - crop: Target crop (rice, wheat, maize, cotton, etc.)
    - K: Potassium value (optional)
    - ph: Soil pH (optional, defaults to 7.0)
    - humidity: Humidity percentage (optional, will fetch from weather)
    - rainfall: Rainfall in mm (optional, will fetch from weather)
    
    Returns:
        JSON with recommended_crop and feature values used
    """
    data = request.get_json(silent=True) or {}
    
    # Check if this is an automatic/hybrid request
    # Auto-mode is triggered when N, P, or temperature is missing
    requires_auto = any(k not in data or data[k] is None 
                        for k in ['N', 'n', 'P', 'p', 'temperature', 'temp'])
    
    if requires_auto:
        # ============================================================
        # AUTOMATIC/HYBRID MODE: Fetch weather and estimate nutrients
        # ============================================================
        logger.info("Hybrid mode: Auto-fetching weather and estimating nutrients")
        
        try:
            # Step 1: Fetch Weather Data (Temperature, Humidity, Rainfall)
            location = data.get("location", {})
            weather_service = get_weather_service()
            
            try:
                weather_data = weather_service.get_weather(location)
                logger.info(f"Weather fetched: {weather_data}")
            except WeatherServiceError as e:
                logger.warning(f"Weather fetch failed: {str(e)}, using defaults")
                weather_data = {
                    'temperature': 25.0,
                    'humidity': 75.0,
                    'rainfall': 150.0
                }
            
            temperature = weather_data.get('temperature', 25.0)
            humidity = weather_data.get('humidity', 75.0)
            rainfall = weather_data.get('rainfall', 150.0)
            weather_city = weather_data.get('city', 'Unknown')
            weather_source = weather_data.get('source', 'default')
            
            # Step 2: Estimate N and P values
            nutrient_estimator = get_nutrient_estimator()
            
            k_value = float(data.get("K", data.get("k", 40.0)))
            ph_value = float(data.get("ph", 7.0))
            
            needs_n_estimation = 'N' not in data and 'n' not in data
            needs_p_estimation = 'P' not in data and 'p' not in data
            
            if needs_n_estimation or needs_p_estimation:
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
                    logger.info(f"Nutrients estimated: N={n_value}, P={p_value}, source={nutrient_source}")
                except NutrientEstimatorError as e:
                    logger.warning(f"Nutrient estimation failed: {str(e)}, using defaults")
                    n_value, p_value = 50.0, 30.0
                    nutrient_source = "default"
            else:
                n_value = float(data.get('N', data.get('n', 50.0)))
                p_value = float(data.get('P', data.get('p', 30.0)))
                nutrient_source = "user_input"
            
            if 'temperature' in data or 'temp' in data:
                temperature = float(data.get('temperature', data.get('temp', temperature)))
                temp_source = "user_input"
            else:
                temp_source = weather_source
            
            if 'humidity' in data:
                humidity = float(data.get('humidity', humidity))
            if 'rainfall' in data:
                rainfall = float(data.get('rainfall', rainfall))
            
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
                    "temperature": temp_source,
                    "humidity": "weather_api" if temp_source != "user_input" else "user_input",
                    "rainfall": "weather_api" if temp_source != "user_input" else "user_input",
                    "N": nutrient_source,
                    "P": nutrient_source,
                    "K": "user_input",
                    "ph": "user_input" if "ph" in data else "default"
                },
                "location": {
                    "city": weather_city,
                    "provided": location if location else "default"
                },
                "prediction_stored": stored,
                "mode": "automatic"
            })
            
        except Exception as e:
            logger.error(f"Auto prediction error: {str(e)}")
            return jsonify({"error": f"Prediction failed: {str(e)}"}), 500
    
    else:
        # MANUAL MODE
        values, error = parse_feature_payload(data, require_all=True)
        if error:
            return jsonify({"error": error}), 400
        
        validation_error = validate_features(values)
        if validation_error:
            return jsonify({"error": validation_error}), 400
        
        try:
            model = get_model()
            features = np.array([values])
            prediction = model.predict(features)[0]
            
            try:
                from app import get_db_connection
                conn = get_db_connection()
                cursor = conn.cursor()
                user_email = get_jwt_identity() or "user"
                cursor.execute(
                    """INSERT INTO predictions 
                       (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) 
                       VALUES (?,?,?,?,?,?,?,?,?)""",
                    (user_email, prediction, *values)
                )
                conn.commit()
                conn.close()
            except Exception as db_error:
                logger.warning(f"Failed to store prediction: {str(db_error)}")
            
            return jsonify({
                "recommended_crop": prediction,
                "features": {
                    "N": values[0],
                    "P": values[1],
                    "K": values[2],
                    "temperature": values[3],
                    "humidity": values[4],
                    "ph": values[5],
                    "rainfall": values[6]
                },
                "data_sources": {
                    "N": "user_input",
                    "P": "user_input",
                    "K": "user_input",
                    "temperature": "user_input",
                    "humidity": "user_input",
                    "ph": "user_input",
                    "rainfall": "user_input"
                },
                "mode": "manual"
            })
            
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
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
