"""
MedAsset Sentinel - Database Models
Phase 1 (SQlite)
Authoritative schema implementation
"""

import enum
from datetime import datetime, date, timedelta
from extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

# =======================
# ENUMS (Type Safety)
# =======================

class EquipmentStatus(enum.Enum):
    """Equipment operational status from IoT monitoring"""
    OK = "OK"
    WARNING = "WARNING"
    FAIL = "FAIL"

class AlertType(enum.Enum):
    """Alert classification types"""
    UPCOMING_MAINTENANCE = "UPCOMING_MAINTENANCE"
    OVERDUE_MAINTENANCE = "OVERDUE_MAINTENANCE"
    EQUIPMENT_FAILURE = "EQUIPMENT_FAILURE"

class AlertSeverity(enum.Enum):
    """Alert Priority levels"""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"

# =======================
# AUTHENTICATION MODEL
# ========================

class Admin(db.Model):
    """Admin user authentication model"""
    __tablename__ = 'admin'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    def set_password(self, password):
        """Hash and store password"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Verify password against hash"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<Admin {self.username}>'
# =========================
# CORE DOMAIN MODEL
# =========================

class Equipment(db.Model):
    """Central equipment registry with operational status and maintenance schedule"""
    __tablename__ = 'equipment'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(100), unique=True, nullable=False, index=True)
    equipment_type = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    manufacturer = db.Column(db.String(100), nullable=True)
    maintenance_interval = db.Column(db.Integer, nullable=False)
    last_maintenance_date = db.Column(db.Date, nullable=True)
    next_maintenance_date = db.Column(db.Date, nullable=False, index=True)
    current_status = db.Column(db.Enum(EquipmentStatus), nullable=False, default=EquipmentStatus.OK, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True, onupdate=datetime.utcnow)

    # Relationships
    maintenance_logs = db.relationship('MaintenanceLog', back_populates='equipment', lazy='dynamic', cascade='all, delete-orphan')
    alerts = db.relationship('Alert', back_populates='equipment', lazy='dynamic')
    sensor_events = db.relationship('SensorEvent', back_populates='equipment', lazy='dynamic', cascade='all, delete-orphan')

    def calculate_next_maintenance(self):
        """Calculate next maintenance date + interval"""
        if self.last_maintenance_date:
            self.next_maintenance_date = self.last_maintenance_date + timedelta(
                days=self.maintenance_interval
            )
        else:
            # If no maintenance yet, schedule from creation
            self.next_maintenance_date = date.today() + timedelta(
                days=self.maintenance_interval
            )

    def is_overdue(self):
        """Check if maintenance is overdue"""
        return date.today() > self.next_maintenance_date

    def days_until_maintenance(self):
        """Calculate days until next maintenance (negative if overdue)"""
        delta = self.next_maintenance_date - date.today()
        return delta.days

    def __repr__(self):
        return f'<Equipment {self.serial_number}: {self.name}>'

# =============================
# AUDIT & INTELLIGENCE MODELS
# =============================

class MaintenanceLog(db.Model):
    """Permanent record of all maintenance actions (append-only)"""
    __tablename__ = 'maintenance_log'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(
        db.Integer,
        db.ForeignKey('equipment.id'),
        nullable=False,
        index=True
    )
    performed_at = db.Column(db.DateTime, nullable=False, index=True)
    performed_by = db.Column(db.String(100), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    equipment = db.relationship('Equipment', back_populates='maintenance_logs')

    def __repr__(self):
        return f'<MaintenanceLog {self.id} for Equipment {self.equipment_id}>'

class Alert(db.Model):
    """System alert for maintenance and equipment issues (resolution-only, never deleted)"""
    __tablename__ = 'alert'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(
        db.Integer,
        db.ForeignKey('equipment.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    alert_type = db.Column(db.Enum(AlertType), nullable=False)
    severity = db.Column(db.Enum(AlertSeverity), nullable=False)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    resolved = db.Column(db.Boolean, nullable=False, default=False, index=True)
    resolved_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    equipment = db.relationship('Equipment', back_populates='alerts')

    def resolve(self):
        """Mark alert as resolved"""
        self.resolved = True
        self.resolved_at = datetime.utcnow()

    @staticmethod
    def check_duplicate(equipment_id, alert_type):
        """Check if unresolved alert of this type already exists"""
        return Alert.query.filter_by(
            equipment_id=equipment_id,
            alert_type=alert_type,
            resolved=False
        ).first() is not None

    def __repr__(self):
        return f'<Alert {self.alert_type.value} for Equipment {self.equipment_id}>'

class SensorEvent(db.Model):
    """IoT sensor telemetry history (append-only, time-series data)"""
    __tablename__ = 'sensor_event'

    id = db.Column(db.Integer, primary_key=True)
    equipment_id = db.Column(db.Integer, db.ForeignKey('equipment.id'), nullable=False, index=True)
    status = db.Column(db.Enum(EquipmentStatus), nullable=False)
    recorded_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)

    # Relationships
    equipment = db.relationship('Equipment', back_populates='sensor_events')

    def __repr__(self):
        return f'<SensorEvent {self.status.value} for Equipment {self.equipment_id}>'















