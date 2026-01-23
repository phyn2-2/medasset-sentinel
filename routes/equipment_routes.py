"""
MedAsset Sentinel - Equipment Routes
Equipment management and detail views
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services import EquipmentService, MaintenanceService, AlertService
from models import EquipmentStatus
from functools import wraps

# Create blueprint
equipment_bp = Blueprint('equipment', __name__, url_prefix='/equipment')

def login_required(f):
    """Decorator to require login for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

@equipment_bp.route('/')
@login_required
def list():
    """
    Equipment inventory list view
    Features:
    - Filterable by status, type, location
    - Sortable columns
    - Paginated (future)
    """
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    type_filter = request.args.get('type', 'all')
    location_filter = request.args.get('location', 'all')

    # Get all equipment
    all_equipment = EquipmentService.get_all_equipment()

    # Apply filters
    equipment = all_equipment

    if status_filter != 'all':
        try:
            status_enum = EquipmentStatus[status_filter.upper()]
            equipment = [eq for eq in equipment if eq.current_status == status_enum]
        except KeyError:
            pass

    if type_filter != 'all':
        equipment = [eq for eq in equipment if eq.equipment_type == type_filter]

    if location_filter != 'all':
        equipment = [eq for eq in equipment if eq.location == location_filter]

    # Get unique values for filter dropdowns
    all_types = sorted(set(eq.equipment_type for eq in all_equipment))
    all_locations = sorted(set(eq.location for eq in all_equipment if eq.location))

    return render_template(
        'equipment_list.html',
        equipment=equipment,
        all_types=all_types,
        all_locations=all_locations,
        status_filter=status_filter,
        type_filter=type_filter,
        location_filter=location_filter
    )

@equipment_bp.route('/<int:equipment_id>')
@login_required
def detail(equipment_id):
    """
    Equipment detail view
    Shows:
    - Current status
    - Maintenance schedule
    - Active alerts
    - Maintenance history
    - Sensor event log
    """
    equipment = EquipmentService.get_equipment_by_id(equipment_id)

    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('equipment.list'))

    # Get Maintenance history
    maintenance_history = MaintenanceService.get_maintenance_history(
        equipment_id,
        limit=5
    )

    # Get active alerts for this equipment
    active_alerts = AlertService.get_alerts_by_equipment(
        equipment_id,
        resolved=False
    )

    # Get recent sensor events (latest 10)
    sensor_events = equipment.sensor_events.order_by(
        equipment.sensor_events.recorded_at.desc()
    ).limit(10).all()

    return render_template(
        'equipment_detail.html',
        equipment=equipment,
        maintenance_history=maintenance_history,
        active_alerts=active_alerts,
        sensor_events=sensor_events
    )

@equipment_bp.route('/add', methods=['POST'])
@login_required
def add():
    """
    Add new equipment
    Form fields:
    - name, serial_number, equipment_type (required)
    - location, manufacturer (optional)
    - maintenance_interval (required)
    """
    name = request.form.get('name', '').strip()
    serial_number = request.get('serial_number', '').strip()
    equipment_type = request.form.get('equipment_type', '').strip()
    location = request.form.get('location', '').strip() or None
    manufacturer = request.form.get('manufacturer', '').strip() or None
    maintenance_interval = request.form.get('maintenance_interval', type=int)

    equipment, error = EquipmentService.create_equipment(
        name=name,
        serial_number=serial_number,
        equipment_type=equipment_type,
        maintenance_interval=maintenance_interval,
        location=location,
        manufacturer=manufacturer
    )

    if equipment:
        flash(f'Equipment {serial_number} added successfully', 'success')
        return redirect(url_for('equipment.detail', equipment_id=equipment.id))
    else:
        flash(f"Error adding equipment: {error}", 'error')
        return redirect(url_for('equipment_list'))

@equipment_bp.route('/<int:equipment_id>/log-maintenance', methods=['POST'])
@login_required
def log_maintenance(equipment_id):
    """
    Log completed maintenance for equipment
    Form fields:
    - performed_by (required)
    - notes (optional)
    """
    performed_by = request.form.get('performed_by', '').strip()
    notes = request.form.get('notes', '').strip() or None

    log, error = MaintenanceService.log_maintenance(
        equipment_id=equipment_id,
        performed_by=performed_by,
        notes=notes
    )

    if log:
        flash('Maintenance logged successfully', 'success')
    else:
        flash(f"Error logging maintenance: {error}", 'error')

    return redirect(url_for('equipment.detail', equipment_id=equipment_id))

@equipment_bp.route('/<int:equipment_id>/edit', methods=['POST'])
@login_required
def edit(equipment_id):
    """
    Edit equipment details
    Allows updating: name, type, location, manufacturer, interval
    Cannot change: serial_number
    """
    name = request.form.get('name', '').strip() or None
    equipment_type = request.form.get('equipment_type', '').strip() or None
    location = request.form.get('location', '').strip() or None
    manufacturer = request.form.get('manufacturer', '').strip() or None
    maintenance_interval = request.form.get('maintenance_interval', type=int)

    equipment, error = EquipmentService.update_equipment(
        equipment_id=equipment_id,
        name=name,
        equipment_type=equipment_type,
        location=location,
        manufacturer=manufacturer,
        maintenance_interval=maintenance_interval
    )

    if equipment:
        flash('Equipment updated successfully', 'success')
    else:
        flash(f'Error updating equipment: {error}', 'error')

    return redirect(url_for('equipment_detail', equipment_id=equipment_id))

@equipment_bp.route('/<int:equipment_id>/delete', methods=['POST'])
@login_required
def delete(equipment_id):
    """
    Delete equipment
    Cascades to logs/events, nullifies alerts
    """
    success, error = EquipmentService.delete_equipment(equipment_id)

    if success:
        flash('Equipment deleted successfully', 'success')
        return redirect(url_for('equipment.list'))
    else:
        flash(f'Error deleting equipment: {error}', 'error')
        return redirect(url_for('equipment.detail', equipment_id=equipment_id))

@equipment_bp.route('/alert/<int:alert_id>/resolve', methods=['POST'])
@login_required
def resolve_alert(alert_id):
    """
    Mark alert as resolved
    Can be called from dashboard or equipment detail
    """
    success, error = AlertService.resolve_alert(alert_id)

    if success:
        flash('Alert resolved', 'success')
    else:
        flash(f'Error resolving alert: {error}', 'error')

    # Redirect back to referrer or dashboard
    referrer = request.referrer
    if referrer and 'equipment' in referrer:
        return redirect(referrer)
    else:
        return redirect(url_for('dashboard.index'))


