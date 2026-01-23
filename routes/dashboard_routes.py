"""
MedAsset Sentinel - Dashboard Routes
Main monitoring console view
"""
from flask import Blueprint, render_template, session, redirect, url_for
from services import EquipmentService, MaintenanceService, AlertService
from functools import wraps

# Create blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/')

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    """
    Main dashboard view - monitoring console
    Displays:
        - Failing equipment (CRITICAL)
        - Overdue maintenance
        - Upcoming maintenance
        - Recent alerts
        - System statistics
    """
    # Get failing equipment
    failing_equipment = EquipmentService.get_failing_equipment()

    # Get Overdue maintenance
    overdue_equipment = EquipmentService.get_overdue_equipment()

    # Get Upcoming maintenance (next 7 days)
    upcoming_equipment = EquipmentService.get_upcoming_maintenance(days=7)

    # Get recent unresolved alerts
    recent_alerts = AlertService.get_unresolved_alerts(limit=10)

    # Get statistics
    equipment_stats = EquipmentService.get_equipment_statistics()
    alert_stats = AlertService.get_alert_statistics()
    maintenance_stats = MaintenanceService.get_maintenance_statistics()

    return render_template(
        'dashboard.html',
        failing_equipment=failing_equipment,
        overdue_equipment=overdue_equipment,
        upcoming_equipment=upcoming_equipment,
        recent_alerts=recent_alerts,
        equipment_stats=equipment_stats,
        alert_stats=alert_stats,
        maintenance_stats=maintenance_stats
    )



