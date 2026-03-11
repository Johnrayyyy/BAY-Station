"""
Configuration file for BSU Kiosk System
Environment-specific settings
"""

import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    # Application
    SECRET_KEY = os.getenv('SECRET_KEY', 'bsu-smart-kiosk-unified-2026-secure-key')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    
    # LostLink Database (PostgreSQL)
    LOSTLINK_DB_HOST = os.getenv('LOSTLINK_DB_HOST', 'localhost')
    LOSTLINK_DB_PORT = os.getenv('LOSTLINK_DB_PORT', '5432')
    LOSTLINK_DB_NAME = os.getenv('LOSTLINK_DB_NAME', 'LostLink')
    LOSTLINK_DB_USER = os.getenv('LOSTLINK_DB_USER', 'postgres')
    LOSTLINK_DB_PASSWORD = os.getenv('LOSTLINK_DB_PASSWORD', 'johnray08')
    
    LOSTLINK_DB_URI = f'postgresql://{LOSTLINK_DB_USER}:{LOSTLINK_DB_PASSWORD}@{LOSTLINK_DB_HOST}:{LOSTLINK_DB_PORT}/{LOSTLINK_DB_NAME}'
    
    # RGO Database (MySQL)
    RGO_DB_HOST = os.getenv('RGO_DB_HOST', 'localhost')
    RGO_DB_PORT = os.getenv('RGO_DB_PORT', '3306')
    RGO_DB_NAME = os.getenv('RGO_DB_NAME', 'rgo_system')
    RGO_DB_USER = os.getenv('RGO_DB_USER', 'root')
    RGO_DB_PASSWORD = os.getenv('RGO_DB_PASSWORD', '')
    
    RGO_DB_URI = f'mysql+pymysql://{RGO_DB_USER}:{RGO_DB_PASSWORD}@{RGO_DB_HOST}:{RGO_DB_PORT}/{RGO_DB_NAME}'
    
    # Grievance Database (PostgreSQL)
    GRIEVANCE_DB_HOST = os.getenv('GRIEVANCE_DB_HOST', 'localhost')
    GRIEVANCE_DB_PORT = os.getenv('GRIEVANCE_DB_PORT', '5432')
    GRIEVANCE_DB_NAME = os.getenv('GRIEVANCE_DB_NAME', 'grievance_system')
    GRIEVANCE_DB_USER = os.getenv('GRIEVANCE_DB_USER', 'postgres')
    GRIEVANCE_DB_PASSWORD = os.getenv('GRIEVANCE_DB_PASSWORD', '')
    
    GRIEVANCE_DB_URI = f'postgresql://{GRIEVANCE_DB_USER}:{GRIEVANCE_DB_PASSWORD}@{GRIEVANCE_DB_HOST}:{GRIEVANCE_DB_PORT}/{GRIEVANCE_DB_NAME}'
    
    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = LOSTLINK_DB_URI  # Default database
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_BINDS = {
        'lostlink': LOSTLINK_DB_URI,
        'rgo': RGO_DB_URI,
        'grievance': GRIEVANCE_DB_URI
    }
    
    # Email Configuration (for LostLink)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 587))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'True') == 'True'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME', 'lostlink.official@gmail.com')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD', 'izhu jksj gqfs ilcj')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'lostlink.official@gmail.com')
    
    # Upload Configuration
    UPLOAD_FOLDER = 'static/uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'doc', 'docx'}

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
