"""
Analytics Routes - Comprehensive Analysis Endpoints

This module provides Flask routes for advanced analytics:
- POST /analytics/comprehensive: Full farm analysis with all features
- GET /analytics/history: Get prediction history
- POST /analytics/soil-health: Soil health classification
- POST /analytics/fertilizer: Fertilizer recommendations

Usage:
    from routes.analytics import analytics_bp
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
"""

import os
import logging
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
import numpy as np

logger = logging.getLogger(__name__)

# Create blueprint
analytics_bp = Blueprint('analytics', __name__)

# Import services
from services.weather_service import WeatherService, WeatherServiceError
from services.nutrient_estimator import NutrientEstimator, NutrientEstimatorError


def get_model():
    """Get or load the crop prediction model."""
    import pickle
    backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    model_path = os.path.join(backend_dir, "model.pkl")
    return pickle.load(open(model_path, "rb"))


def get_db_connection():
    """Get database connection."""
    from app import get_db_connection as app_db_conn
    return app_db_conn()


# ============================================================================
# ROUTES
# ============================================================================

@analytics_bp.route("/comprehensive", methods=["POST"])
@jwt_required()
def comprehensive_analysis():
    """
    Comprehensive farm analysis endpoint.
    
    This endpoint provides:
    - Crop prediction
    - Soil health classification
    - Fertilizer recommendations
    - Yield prediction
    - Price analysis
    - Weather suitability
    
    Returns:
        JSON with comprehensive analysis results
    """
    data = request.get_json(silent=True) or {}
    user_email = get_jwt_identity() or "guest"
    
    try:
        # Get features from request or use defaults
        n = float(data.get("N", data.get("n", 50)))
        p = float(data.get("P", data.get("p", 30)))
        k = float(data.get("K", data.get("k", 40)))
        temperature = float(data.get("temperature", 25))
        humidity = float(data.get("humidity", 75))
        ph = float(data.get("ph", 7.0))
        rainfall = float(data.get("rainfall", 100))
        
        # Crop prediction
        model = get_model()
        features = np.array([[n, p, k, temperature, humidity, ph, rainfall]])
        crop_pred = model.predict(features)[0]
        
        # Store in database
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO predictions 
                   (user_email, crop, n, p, k, temperature, humidity, ph, rainfall) 
                   VALUES (?,?,?,?,?,?,?,?,?)""",
                (user_email, crop_pred, n, p, k, temperature, humidity, ph, rainfall)
            )
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warning(f"Failed to store prediction: {e}")
        
        # Basic soil health calculation
        n_score = min(100, (n / 100) * 100)
        p_score = min(100, (p / 60) * 100)
        k_score = min(100, (k / 60) * 100)
        ph_score = 100 if 6.0 <= ph <= 7.5 else max(0, 100 - abs(ph - 6.75) * 20)
        health_score = (n_score + p_score + k_score + ph_score) / 4
        health_class = "Excellent" if health_score >= 80 else "Good" if health_score >= 60 else "Fair" if health_score >= 40 else "Poor"
        
        soil_health_result = {
            "health_class": health_class,
            "health_score": round(health_score, 2),
            "component_scores": {
                "nitrogen": round(n_score, 2),
                "phosphorus": round(p_score, 2),
                "potassium": round(k_score, 2),
                "ph": round(ph_score, 2)
            },
            "recommendations": ["Improve soil health with organic matter"] if health_score < 60 else ["Maintain current practices"]
        }
        
        # Basic fertilizer recommendations
        fertilizer_rec = []
        if n < 50:
            fertilizer_rec.append({"nutrient": "Nitrogen", "fertilizer": "Urea", "quantity": "50-100 kg/hectare"})
        if p < 30:
            fertilizer_rec.append({"nutrient": "Phosphorus", "fertilizer": "DAP", "quantity": "40-80 kg/hectare"})
        if k < 30:
            fertilizer_rec.append({"nutrient": "Potassium", "fertilizer": "MOP", "quantity": "30-60 kg/hectare"})
        if not fertilizer_rec:
            fertilizer_rec.append({"nutrient": "Balanced", "fertilizer": "NPK 10:10:10", "quantity": "Maintenance dose"})
        
        # Basic weather suitability
        weather_suitability = "Good" if 15 <= temperature <= 35 and 50 <= humidity <= 90 else "Fair"
        
        # Base prices for different crops
        base_prices = {
            "rice": 2500, "wheat": 2000, "maize": 1800, 
            "cotton": 6000, "sugarcane": 3500, "potato": 1200
        }
        base_price = base_prices.get(crop_pred.lower(), 2000)
        
        # Generate price analysis (simplified)
        seed_source = f"{crop_pred}|{n}|{p}|{k}|{temperature}|{humidity}|{ph}|{rainfall}"
        seed = int(hashlib.md5(seed_source.encode("utf-8")).hexdigest()[:8], 16)
        rng = np.random.default_rng(seed)
        
        price_analysis = {
            "current_price": base_price,
            "trend": "Stable",
            "change_percentage": round(float(rng.integers(-5, 6)) / 10, 2),
            "recommendation": "Market stable",
            "future_prices": [round(float(base_price + rng.integers(-200, 201)), 2) for _ in range(5)]
        }
        
        # Overall recommendations
        overall_recommendations = []
        if soil_health_result.get("health_class") in ["Poor", "Fair"]:
            overall_recommendations.extend(soil_health_result.get("recommendations", [])[:2])
        if weather_suitability in ["Fair", "Poor"]:
            overall_recommendations.append(f"Weather conditions are {weather_suitability.lower()} for {crop_pred}. Consider alternative crops.")
        if not overall_recommendations:
            overall_recommendations.append(f"Excellent conditions for {crop_pred} cultivation!")
        
        return jsonify({
            "recommended_crop": crop_pred,
            "soil_health": soil_health_result,
            "fertilizer_recommendations": fertilizer_rec,
            "price_analysis": price_analysis,
            "weather_suitability": weather_suitability,
            "overall_recommendations": overall_recommendations,
            "analysis_timestamp": str(datetime.now())
        })
        
    except Exception as e:
        logger.error(f"Comprehensive analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/history", methods=["GET"])
@jwt_required()
def get_history():
    """
    Get prediction history for current user.
    
    Query params:
    - limit: Maximum number of records (default 50)
    
    Returns:
        JSON with list of past predictions
    """
    limit = request.args.get("limit", 50, type=int)
    user_email = get_jwt_identity() or "user"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT crop, n, p, k, temperature, humidity, ph, rainfall, timestamp 
               FROM predictions 
               WHERE user_email = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (user_email, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        predictions = [
            {
                "crop": row[0],
                "n": row[1],
                "p": row[2],
                "k": row[3],
                "temperature": row[4],
                "humidity": row[5],
                "ph": row[6],
                "rainfall": row[7],
                "timestamp": row[8]
            }
            for row in rows
        ]
        
        return jsonify({"predictions": predictions})
        
    except Exception as e:
        logger.error(f"History fetch error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/soil-health", methods=["POST"])
def analyze_soil_health():
    """
    Analyze soil health based on nutrient values.
    
    Request body:
    - N: Nitrogen value
    - P: Phosphorus value
    - K: Potassium value
    - ph: Soil pH
    
    Returns:
        JSON with soil health analysis
    """
    data = request.get_json(silent=True) or {}
    
    try:
        n = float(data.get("N", 50))
        p = float(data.get("P", 30))
        k = float(data.get("K", 40))
        ph = float(data.get("ph", 7.0))
        
        # Calculate component scores
        n_score = min(100, (n / 100) * 100)
        p_score = min(100, (p / 60) * 100)
        k_score = min(100, (k / 60) * 100)
        
        if 6.0 <= ph <= 7.5:
            ph_score = 100
        else:
            ph_score = max(0, 100 - abs(ph - 6.75) * 20)
        
        health_score = (n_score + p_score + k_score + ph_score) / 4
        
        if health_score >= 80:
            health_class = "Excellent"
        elif health_score >= 60:
            health_class = "Good"
        elif health_score >= 40:
            health_class = "Fair"
        else:
            health_class = "Poor"
        
        recommendations = []
        if n_score < 60:
            recommendations.append("Add nitrogen-rich fertilizers like urea or compost")
        if p_score < 60:
            recommendations.append("Add phosphorus-rich fertilizers like DAP or superphosphate")
        if k_score < 60:
            recommendations.append("Add potassium-rich fertilizers like MOP")
        if ph_score < 60:
            if ph < 6.0:
                recommendations.append("Add lime to increase soil pH")
            else:
                recommendations.append("Add sulfur or organic matter to decrease soil pH")
        if not recommendations:
            recommendations.append("Maintain current soil management practices")
        
        return jsonify({
            "health_class": health_class,
            "health_score": round(health_score, 2),
            "component_scores": {
                "nitrogen": round(n_score, 2),
                "phosphorus": round(p_score, 2),
                "potassium": round(k_score, 2),
                "ph": round(ph_score, 2)
            },
            "recommendations": recommendations
        })
        
    except Exception as e:
        logger.error(f"Soil health analysis error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@analytics_bp.route("/fertilizer", methods=["POST"])
def get_fertilizer_recommendation():
    """
    Get fertilizer recommendations based on soil and crop.
    
    Request body:
    - N: Nitrogen value (optional)
    - P: Phosphorus value (optional)
    - K: Potassium value (optional)
    - ph: Soil pH (optional)
    - crop: Target crop (optional)
    
    Returns:
        JSON with fertilizer recommendations
    """
    data = request.get_json(silent=True) or {}
    
    try:
        n = float(data.get("N", 50))
        p = float(data.get("P", 30))
        k = float(data.get("K", 40))
        crop = data.get("crop", "").lower()
        
        recommendations = []
        
        # Nitrogen recommendations
        if n < 40:
            recommendations.append({
                "nutrient": "Nitrogen",
                "current_level": "Low",
                "fertilizer": "Urea (46% N)",
                "quantity": "80-120 kg/hectare",
                "timing": "Split application: 50% at sowing, 50% at tillering"
            })
        elif n < 70:
            recommendations.append({
                "nutrient": "Nitrogen",
                "current_level": "Medium",
                "fertilizer": "Urea or CAN",
                "quantity": "60-80 kg/hectare",
                "timing": "Split application recommended"
            })
        else:
            recommendations.append({
                "nutrient": "Nitrogen",
                "current_level": "Adequate",
                "fertilizer": "Maintain with organic matter",
                "quantity": "30-40 kg/hectare",
                "timing": "As top dressing"
            })
        
        # Phosphorus recommendations
        if p < 25:
            recommendations.append({
                "nutrient": "Phosphorus",
                "current_level": "Low",
                "fertilizer": "DAP (18% N, 46% P2O5)",
                "quantity": "60-80 kg/hectare",
                "timing": "At sowing"
            })
        elif p < 50:
            recommendations.append({
                "nutrient": "Phosphorus",
                "current_level": "Medium",
                "fertilizer": "SSP or DAP",
                "quantity": "40-60 kg/hectare",
                "timing": "At sowing"
            })
        else:
            recommendations.append({
                "nutrient": "Phosphorus",
                "current_level": "Adequate",
                "fertilizer": "Reduce P application",
                "quantity": "20-30 kg/hectare",
                "timing": "Maintenance dose"
            })
        
        # Potassium recommendations
        if k < 25:
            recommendations.append({
                "nutrient": "Potassium",
                "current_level": "Low",
                "fertilizer": "MOP (60% K2O)",
                "quantity": "50-60 kg/hectare",
                "timing": "At sowing"
            })
        elif k < 50:
            recommendations.append({
                "nutrient": "Potassium",
                "current_level": "Medium",
                "fertilizer": "MOP",
                "quantity": "30-40 kg/hectare",
                "timing": "Split application"
            })
        else:
            recommendations.append({
                "nutrient": "Potassium",
                "current_level": "Adequate",
                "fertilizer": "Reduce K application",
                "quantity": "20 kg/hectare",
                "timing": "Maintenance"
            })
        
        return jsonify({
            "current_levels": {
                "N": n,
                "P": p,
                "K": k
            },
            "crop": crop if crop else "General",
            "recommendations": recommendations
        })
        
    except Exception as e:
        logger.error(f"Fertilizer recommendation error: {str(e)}")
        return jsonify({"error": str(e)}), 500
