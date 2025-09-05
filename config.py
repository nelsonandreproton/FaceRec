#!/usr/bin/env python3
# config.py - Configuration management with environment variables
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration from environment variables"""
    
    # Database Configuration
    DB_PATH = os.getenv('DB_PATH', 'face_recognition.db')
    
    # Web Server Configuration
    FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
    FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
    
    # Paths Configuration
    IMAGES_BASE_PATH = os.getenv('IMAGES_BASE_PATH', 'test_images')
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/face_model.pkl')
    TEMPLATES_PATH = os.getenv('TEMPLATES_PATH', 'templates')
    STATIC_PATH = os.getenv('STATIC_PATH', 'static')
    
    # Model Configuration
    CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', 0.6))
    FACE_TOLERANCE = float(os.getenv('FACE_TOLERANCE', 0.6))
    MAX_DETECTIONS_LIMIT = int(os.getenv('MAX_DETECTIONS_LIMIT', 50))
    
    # Home Assistant Configuration
    HA_ENABLED = os.getenv('HA_ENABLED', 'false').lower() == 'true'
    HA_URL = os.getenv('HA_URL', 'http://localhost:8123')
    HA_TOKEN = os.getenv('HA_TOKEN', '')
    
    @classmethod
    def validate(cls):
        """Validate configuration and create necessary directories"""
        # Create directories if they don't exist
        os.makedirs(os.path.dirname(cls.MODEL_PATH), exist_ok=True)
        os.makedirs(cls.IMAGES_BASE_PATH, exist_ok=True)
        os.makedirs(cls.TEMPLATES_PATH, exist_ok=True)
        os.makedirs(cls.STATIC_PATH, exist_ok=True)
        
        # Validate Home Assistant configuration if enabled
        if cls.HA_ENABLED and not cls.HA_TOKEN:
            print("⚠️ Warning: HA_ENABLED is true but HA_TOKEN is not set")
        
        return True
    
    @classmethod
    def print_config(cls):
        """Print current configuration (excluding sensitive data)"""
        print("🔧 Current Configuration:")
        print(f"   Database: {cls.DB_PATH}")
        print(f"   Web Server: {cls.FLASK_HOST}:{cls.FLASK_PORT}")
        print(f"   Debug Mode: {cls.FLASK_DEBUG}")
        print(f"   Images Path: {cls.IMAGES_BASE_PATH}")
        print(f"   Model Path: {cls.MODEL_PATH}")
        print(f"   Confidence Threshold: {cls.CONFIDENCE_THRESHOLD}")
        print(f"   Face Tolerance: {cls.FACE_TOLERANCE}")
        print(f"   Home Assistant: {'Enabled' if cls.HA_ENABLED else 'Disabled'}")
        if cls.HA_ENABLED:
            print(f"   HA URL: {cls.HA_URL}")
            print(f"   HA Token: {'***' if cls.HA_TOKEN else 'Not set'}")

# Initialize configuration
config = Config()
config.validate()