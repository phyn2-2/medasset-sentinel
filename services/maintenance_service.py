"""
MedAsset Sentinel - Maintenance Service
Handles maintenance logging, scheduling and compliance checks
"""
from datetime import datetime, date, timedelta
from models import MaintenanceLog, Equipment, AlertType
from extensions import db
from services.alert_service import AlertService

class MaintenanceService:
    """Maintenance management business logic"""

    @staticmethod
    def log_maintenance(equipment_id, performed_by, notes=None, performed_at=None):
        """
        Log completed maintenance action
        Args:
            equipment_id (int): Equipment ID
            performed_by (str): Technician/person who performed maintenance
            notes (str, optional): Service notes
            performed_at (datetime, optional): When performed (defaults to now)
        Returns:
            tuple: (MaintenanceLog object, error_message)
        """
        # Validate equipment exists
        equipment = Equipment.query.get(equipment_id)
        if not equipment:
            return None, "Equipment not found"

        # Validate performed by
        if not performed_by or not performed_by.strip():
            return None, "Performed by is required"

        # Default to current time
        if performed_at is None:
            performed_at = datetime.utcnow()

        # Validate performed_at is not in future
        if performed_at > datetime.utcnow():
            return None, "Maintenance date cannot be in the future"

        # Create maintenance log
        log = MaintenanceLog(
            equipment_id=equipment_id,
            performed_at=performed_at,
            performed_by=performed_by.strip(),
            notes=notes
        )

        # Update equipment maintenance dates
        equipment.last_maintenance_date = performed_at.date()
        equipment.calculate_next_maintenance()
        equipment.updated_at = datetime.utcnow()

        try:
            db.session.add(log)
            db.session.commit()

            # Clear related maintenance alerts (handled by alert service)
            AlertService.resolve_maintenance_alerts(equipment_id)

            return log, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"

    @staticmethod
    def get_maintenance_history(equipment_id, limit=None):
        """
        Get maintenance history for equipment
        Args:
            equipment_id (int): Equipment ID
            limit (int, optional): Limit number of records
        Returns:
            list: List of MaintenanceLog objects
        """
        query = MaintenanceLog.query.filter_by(
            equipment_id=equipment_id
        ).order_by(MaintenanceLog.performed_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    @staticmethod
    def get_recent_maintenance(limit=10):
        """
        Get recent maintenance across all equipment
        Args:
            limit (int): Number of records to return
        Returns:
            list: List of MaintenanceLog objects
        """
        return MaintenanceLog.query.order_by(
            MaintenanceLog.performed_at.desc()
        ).limit(limit).all()

    @staticmethod
    def get_maintenance_by_id(log_id):
        """
        Get specific maintenance log
        Args:
            log_id (int): Maintenance Log or None
        """
        return MaintenanceLog.query.get(log_id)

    @staticmethod
    def check_maintenance_compliance():
        """
        Check all equipment for maintenance compliance
        Generates alerts for upcoming and overdue maintenance

        This should be called by scheduler daily
        Returns:
            dict: Summary of compliance check
        """
        today = date.today()
        upcoming_threshold = today + timedelta(days=7)  # 7 days warning

        all_equipment = Equipment.query.all()

        upcoming_alerts = 0
        overdue_alerts = 0

        for equipment in all_equipment:
            next_date = equipment.next_maintenance_date

            # Check for overdue maintenance
            if next_date < today:
                # Create overdue alert if not already exists
                created = AlertService.create_maintenance_alert(
                    equipment_id=equipment.id,
                    alert_type=AlertType.OVERDUE_MAINTENANCE,
                    days_overdue=abs(equipment.days_until_maintenance())
                )
                if created:
                    overdue_alerts += 1

            # Check for upcoming maintenance (within 7 days)
            elif today <= next_date <= upcoming_threshold:
                # Create upcoming alert if not already exists
                created = AlertService.create_maintenance_alert(
                    equipment_id=equipment.id,
                    alert_type=AlertType.UPCOMING_MAINTENANCE,
                    days_until=equipment.days_until_maintenance()
                )
                if created:
                    upcoming_alerts += 1

        return {
            'total_equipment': len(all_equipment),
            'upcoming_alerts_created': upcoming_alerts,
            'overdue_alerts_created': overdue_alerts,
            'checked_at': datetime.utcnow()
        }

    @staticmethod
    def get_maintenance_statistics():
        """
        Get maintenance statistics for dashboard
        Returns:
            dict: Maintenance statistics
        """
        total_logs = MaintenanceLog.query.count()

        # Count overdue maintenance
        today = date.today()
        overdue_count = Equipment.query.filter(
            Equipment.next_maintenance_date < today
        ).count()

        # Count upcoming maintenance (next 7 days)
        upcoming_threshold = today + timedelta(days=7)
        upcoming_count = Equipment.query.filter(
            Equipment.next_maintenance_date >= today,
            Equipment.next_maintenance_date <= upcoming_threshold
        ).count()

        return {
            'total_maintenance_logs': total_logs,
            'overdue_count': overdue_count,
            'upcoming_count': upcoming_count
        }

