"""
Chat Routes - Chatbot Endpoints

This module provides Flask routes for the chatbot:
- POST /chat: Chat with the crop advisory chatbot
- GET /chat/history: Get chat history

Usage:
    from routes.chat import chat_bp
    app.register_blueprint(chat_bp, url_prefix='/chat')
"""

import logging
from datetime import datetime
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

logger = logging.getLogger(__name__)

# Create blueprint
chat_bp = Blueprint('chat', __name__)


def get_db_connection():
    """Get database connection."""
    from app import get_db_connection as app_db_conn
    return app_db_conn()


# Multi-language responses
RESPONSES = {
    "en": {
        "rice": "🌾 Rice grows best in high humidity (80-85%) with temperatures around 20-27°C. It needs high nitrogen (80-100) and moderate rainfall (200-300mm). Best planting season: June-July.",
        "maize": "🌽 Maize requires moderate humidity (65-75%), temperatures of 21-27°C, and balanced NPK nutrients. Rainfall of 90-120mm is ideal. Best planting season: February-March.",
        "wheat": "🌾 Wheat thrives in cooler temperatures (12-25°C) with low to moderate humidity. It needs nitrogen (40-60) and rainfall around 50-75mm. Best planting season: November-December.",
        "cotton": "🌻 Cotton needs warm temperatures (21-30°C), moderate humidity (60-70%), and balanced nutrients. Best planting season: April-May.",
        "sugarcane": "🎋 Sugarcane requires high temperatures (24-30°C), high humidity, and heavy rainfall. It needs significant nitrogen. Best planting season: February-March.",
        "fertilizer": "🧪 NPK stands for Nitrogen (N), Phosphorus (P), and Potassium (K). N promotes leaf growth, P supports roots, K improves disease resistance. Use our prediction tool for crop-specific recommendations!",
        "help": "👋 Hello! I'm your Crop Assistant. Ask me about specific crops (rice, wheat, maize, cotton, sugarcane), fertilizers, weather, soil, irrigation, pests, or planting seasons!",
        "default": "🌿 I can help with crop recommendations! Try asking about: specific crops, fertilizers (NPK), weather conditions, soil pH, irrigation, pests, or planting seasons. Or use the prediction tool above!"
    },
    "hi": {
        "rice": "🌾 चावल उच्च आर्द्रता (80-85%) में 20-27°C तापमान के साथ सबसे अच्छा उगता है।",
        "maize": "🌽 मक्का को मध्यम आर्द्रता (65-75%), 21-27°C तापमान की आवश्यकता होती है।",
        "wheat": "🌾 गेहूं ठंडे तापमान (12-25°C) में पनपता है।",
        "fertilizer": "🧪 NPK का मतलब नाइट्रोजन (N), फास्फोरस (P), और पोटेशियम (K) है।",
        "help": "👋 नमस्ते! मैं आपका फसल सहायक हूं।",
        "default": "🌿 मैं फसल सिफारिशों में मदद कर सकता हूं!"
    },
    "te": {
        "rice": "🌾 వరి అధिक తేమ (80-85%) మరియు 20-27°C ఉష్ణోగ్రతలో బాగా పెరుగుతుంది।",
        "maize": "🌽 మొక్కజొన్నకు మితమైన తేమ (65-75%) అవసరం।",
        "wheat": "🌾 గోధుమలు చల్లని ఉష్ణోగ్రతలలో (12-25°C) వృద్ధి చెందుతాయి।",
        "fertilizer": "🧪 NPK అంటే నత్రజని (N), భాస్వరం (P), మరియు పొటాషియం (K)।",
        "help": "👋 నమస్కారం! నేను మీ పంట సహాయకుడినि।",
        "default": "🌿 నేను పంట సిఫార్సులతో సహాయం చేయగలను!"
    },
    "ta": {
        "rice": "🌾 நெல் அதிக ஈரப்பதம் (80-85%) மற்றும் 20-27°C வெப்பநிலையில் சிறப்பாக வளரும்।",
        "maize": "🌽 சோளத்திற்கு மிதமான ஈரப்பதம் (65-75%) தேவை।",
        "wheat": "🌾 கோதுமை குளிர்ந்த வெப்பநிலையில் (12-25°C) வளரும்।",
        "fertilizer": "🧪 NPK என்பது நைட்ரஜன் (N), பாஸ்பரஸ் (P), மற்றும் பொட்டாசியம் (K)।",
        "help": "👋 வணக்கம்! நான் உங்கள் பயிர் உதவியாளர்।",
        "default": "🌿 நான் பயிர் பரிந்துரைகளுடன் உதவ முடியும்!"
    }
}


# ============================================================================
# ROUTES
# ============================================================================

@chat_bp.route("", methods=["POST"])
@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():
    """
    Simple chatbot with pre-defined responses in multiple languages.
    
    Request body:
    - message: User message
    - language: Language code (en, hi, te, ta)
    
    Returns:
        JSON with chatbot response in requested language
    """
    data = request.get_json(silent=True) or {}
    user_message = str(data.get("message", "")).lower()
    language = data.get("language", "en")
    user_email = get_jwt_identity() or "user"
    
    if not user_message.strip():
        return jsonify({"error": "message is required"}), 400
    
    # Get responses for selected language
    lang_responses = RESPONSES.get(language, RESPONSES["en"])
    
    # Determine response based on keywords
    if "rice" in user_message or "धान" in user_message or "వరి" in user_message or "நெல்" in user_message:
        response = lang_responses.get("rice", RESPONSES["en"]["rice"])
    elif "maize" in user_message or "corn" in user_message or "मक्का" in user_message or "మొక్కజొన్న" in user_message:
        response = lang_responses.get("maize", RESPONSES["en"]["maize"])
    elif "wheat" in user_message or "गेहूं" in user_message or "గోధుమలు" in user_message:
        response = lang_responses.get("wheat", RESPONSES["en"]["wheat"])
    elif "cotton" in user_message or "कपास" in user_message:
        response = lang_responses.get("cotton", RESPONSES["en"]["cotton"])
    elif "sugarcane" in user_message or "गन्ना" in user_message:
        response = lang_responses.get("sugarcane", RESPONSES["en"]["sugarcane"])
    elif "fertilizer" in user_message or "npk" in user_message or "उर्वरक" in user_message:
        response = lang_responses.get("fertilizer", RESPONSES["en"]["fertilizer"])
    elif "help" in user_message or "hello" in user_message or "hi" in user_message or "नमस्ते" in user_message:
        response = lang_responses.get("help", RESPONSES["en"]["help"])
    else:
        response = lang_responses.get("default", RESPONSES["en"]["default"])
    
    # Store chat in database
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO chat_messages (user_email, message, response) VALUES (?,?,?)",
            (user_email, user_message, response)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        logger.warning(f"Failed to store chat message: {e}")
    
    return jsonify({"response": response, "language": language})


@chat_bp.route("/history", methods=["GET"])
@jwt_required()
def get_chat_history():
    """
    Get chat history for current user.
    
    Query params:
    - limit: Maximum number of records (default 50)
    
    Returns:
        JSON with list of past chat messages
    """
    limit = request.args.get("limit", 50, type=int)
    user_email = get_jwt_identity() or "user"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT message, response, timestamp 
               FROM chat_messages 
               WHERE user_email = ? 
               ORDER BY timestamp DESC 
               LIMIT ?""",
            (user_email, limit)
        )
        rows = cursor.fetchall()
        conn.close()
        
        messages = [
            {
                "message": row[0],
                "response": row[1],
                "timestamp": row[2]
            }
            for row in rows
        ]
        
        return jsonify({"chat_history": messages})
        
    except Exception as e:
        logger.error(f"Chat history fetch error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/history", methods=["DELETE"])
@jwt_required()
def clear_chat_history():
    """
    Clear all chat history for current user.
    
    Returns:
        JSON with success message
    """
    user_email = get_jwt_identity() or "user"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM chat_messages WHERE user_email = ?",
            (user_email,)
        )
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        return jsonify({
            "success": True,
            "message": f"Cleared {deleted_count} chat messages",
            "deleted_count": deleted_count
        })
        
    except Exception as e:
        logger.error(f"Clear history error: {str(e)}")
        return jsonify({"error": str(e)}), 500


@chat_bp.route("/languages", methods=["GET"])
def get_supported_languages():
    """
    Get list of supported languages.
    
    Returns:
        JSON with supported languages
    """
    return jsonify({
        "languages": [
            {"code": "en", "name": "English", "native": "English"},
            {"code": "hi", "name": "Hindi", "native": "हिन्दी"},
            {"code": "te", "name": "Telugu", "native": "తెలుగు"},
            {"code": "ta", "name": "Tamil", "native": "தமிழ்"},
            {"code": "kn", "name": "Kannada", "native": "ಕನ್ನಡ"},
            {"code": "ml", "name": "Malayalam", "native": "മലയാളം"},
            {"code": "mr", "name": "Marathi", "native": "मराठी"},
            {"code": "bn", "name": "Bengali", "native": "বাংলা"},
            {"code": "gu", "name": "Gujarati", "native": "ગુજરાતી"},
            {"code": "pa", "name": "Punjabi", "native": "ਪੰਜਾਬੀ"}
        ]
    })
