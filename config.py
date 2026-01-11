"""
MedAsset Sentinel - Configuration
Environment-specific settings
"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'

    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///medasset_sentinel.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Session
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

    # Scheduler (APScheduler - Phase 3)
    SCHEDULER_API_ENABLED = False  # Disable API endpoints for scheduler

class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production environment configuration (future)"""
    DEBUG = False
    TESTING = False
    # Override with real secrets in production
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Must be set

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


