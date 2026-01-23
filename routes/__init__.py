"""
MedAsset Sentinel - Routes Package
Flasks blueprints for application routing
"""
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.equipment_routes import equipment_bp

__all__ = [
    'auth_bp',
    'dashboard_bp',
    'equipment_bp'
]

