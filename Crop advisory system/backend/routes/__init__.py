"""
Routes Package for Crop Advisory System

This package contains Flask blueprints:
- predict: Crop prediction endpoints
- analytics: Analysis and comprehensive endpoints
- chat: Chatbot endpoints
- auth: Authentication endpoints
"""

from .predict import predict_bp
from .analytics import analytics_bp
from .chat import chat_bp
from .auth import auth_bp

__all__ = ["predict_bp", "analytics_bp", "chat_bp", "auth_bp"]
