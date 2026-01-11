#!/usr/bin/env python3
"""
MedAsset Sentinel - Application Factory
Main Flask application initialization
"""
from flask import Flask
import models
from config import config
from extensions import db

def create_app(config_name='development'):
    """
    Application factory pattern

    Args:
        config_name: Configuration to use ('development', 'production')
    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)

    # Create database tables
    with app.app_context():
        # Create all tables
        db.create_all()

        print("✓ Database tables created successfully")

    return app

if __name__ == '__main__':
    app = create_app('development')
    app.run(debug=True, host='0.0.0.0', port=5000)
