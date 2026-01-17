"""
MedAsset Sentinel - Alert Service
Handles alert creation, resolution and deduplication
"""
from datetime import datetime
from models import Alert, AlertType, AlertSeverity, Equipment
from extensions import db

class AlertService:
    """Alert management business logic"""

    @staticmethod
    def create_alert(equipment_id, alert_type, severity, message):
        """
        Create new alert with deduplication check
        Args:
            equipment_id (int): Equipment ID (can be None for system alerts)
            alert_type (AlertType): Type of alert
            severity (AlertSeverity): Severity level
            message (str): Alert message
        Returns:
            Alert: Created alert or None if duplicate
        """
        # Check for duplicate unresolved alert
        if equipment_id and Alert.check_duplicate(equipment_id, alert_type):
            return None  # Alert already exists, skip creation

        alert = Alert(
            equipment_id=equipment_id,
            alert_type=alert_type,
            severity=severity,
            message=message
        )

        try:
            db.session.add(alert)
            db.session.commit()
            return alert
        except Exception as e:
            db.session.rollback()
            return None

    @staticmethod
    def create_equipment_failure_alert(equipment_id):
        """
        Create critical for equipment failure
        Args:
            equipment_id (int): Equipment ID
        Returns:
            Alert: Created alert or None
        """
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return None

        message = f"CRITICAL: {equipment.name} ({equipment.serial_number} has FAILED)"

        return AlertService.create_alert(
            equipment_id=equipment_id,
            alert_type=AlertType.EQUIPMENT_FAILURE,
            severity=AlertSeverity.CRITICAL,
            message=message
        )

    @staticmethod
    def create_maintenance_alert(equipment_id, alert_type, days_overdue=None, days_until=None):
        """
        Create maintenance-related alert
        Args:
            equipment_id (int): Equipment ID
            alert_type (AlertType): UPCOMING_MAINTENANCE or OVERDUE_MAINTENANCE
            days_overdue (int, optional): Days overdue
            days_until (int, optional): Days until due
        Returns:
            bool: True if alert created, False if duplicate
        """
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return False

        # Determine message and severity
        if alert_type == AlertType.OVERDUE_MAINTENANCE:
            message = f"OVERDUE: {equipment.name} ({equipment.serial_number})"\
                f"maintenance overdue by {days_overdue} days"
            severity = AlertSeverity.CRITICAL
        elif alert_type == AlertType.UPCOMING_MAINTENANCE:
            message = f"UPCOMING: {equipment.name} ({equipment.serial_number})"\
                f"maintenance due in {days_until} days"
            severity = AlertSeverity.WARNING
        else:
            return False

        alert = AlertService.create_alert(
            equipment_id=equipment_id,
            alert_type=alert_type,
            severity=severity,
            message=message
        )

        return alert is not None

    @staticmethod
    def resolve_alert(alert_id):
        """
        Mark alert as resolved
        Args:
            alert_id (int): Alert ID
        Returns:
            tuple: (success boolean, error_message)
        """
        alert = Alert.query.get(alert_id)

        if not alert:
            return False, "Alert not found"

        if alert.resolved:
            return False, "Alert already resolved"

        alert.resolve()

        try:
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"

    @staticmethod
    def resolve_maintenance_alerts(equipment_id):
        """
        Resolve all unresolved maintenance alerts for equipment
        Called after maintenance is logged
        Args:
            equipment_id (int): Equipment ID
        Returns:
            int: Number of alerts resolved
        """
        alerts = Alert.query.filter_by(
            equipment_id=equipment_id,
            resolved=False
        ).filter(
            Alert.alert_type.in_([
                AlertType.UPCOMING_MAINTENANCE,
                AlertType.OVERDUE_MAINTENANCE
            ])
        ).all()

        count = 0
        for alert in alerts:
            alert.resolve()
            count += 1

        if count > 0:
            try:
                db.session.commit()
            except Exception:
                db.session.rollback()
                count = 0

        return count

    @staticmethod
    def get_unresolved_alerts(limit=None):
        """
        Get all unresolved alerts ordered by severity and date
        Args:
            limit (int, optional): Maximum number of alerts
        Returns:
            list: List of Alert objects
        """
        # Order: CRITICAL first, then by creation date (newest first)
        query = Alert.query.filter_by(resolved=False).order_by(
            Alert.severity.desc(),
            Alert.created_at.desc()
        )

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_recent_alerts(limit=10, include_resolved=True):
        """
        Get recent alerts
        Args:
            limit (int): Number of alerts to return
            include_resolved (bool): Include resolved alerts
        Returns:
            list: List of Alert objects
        """
        query = Alert.query

        if not include_resolved:
            query = query.filter_by(resolved=False)

        return query.order_by(Alert.created_at.desc()).limit(limit).all()

    @staticmethod
    def get_alerts_by_equipment(equipment_id, resolved=None):
        """
        Get all alerts for specific equipment
        Args:
            equipment_id (int): Equipment ID
            resolved (bool, optional): Filter by resolved status
        Returns:
            list: List of Alert objects
        """
        query = Alert.query.filter_by(equipment_id=equipment_id)

        if resolved is not None:
            query = query.filter_by(resolved=resolved)

        return query.order_by(Alert.created_at.desc()).all()

    @staticmethod
    def get_alert_statistics():
        """
        Get alert statistics for dashboard
        Returns:
            dict: Alert statistics
        """
        total = Alert.query.count()
        unresolved = Alert.query.filter_by(resolved=False).count()
        critical = Alert.query.filter_by(
            severity=AlertSeverity.CRITICAL,
            resolved=False
        ).count()

        return {
            'total_alerts': total,
            'unresolved_alerts': unresolved,
            'critical_unresolved': critical
        }




