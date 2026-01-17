"""
MedAsset Sentinel - Equipment Service
Handles equipment CRUD operations and validation
"""
from datetime import datetime, date, timedelta
from models import Equipment, EquipmentStatus
from extensions import db
class EquipmentService:
    """Equipment management business logic"""

    @staticmethod
    def get_all_equipment():
        """
        Retrieve all equipment ordered by serial number
        Returns:
            list: List of Equipment objects
        """
        return Equipment.query.order_by(Equipment.serial_number).all()

    @staticmethod
    def get_equipment_by_id(equipment_id):
        """
        Retrieve equipment by ID
        Args:
            equipment_id (int): Equipment ID
        Returns Equipment object or None
        """
        return Equipment.query.get(equipment_id)

    @staticmethod
    def get_equipment_by_serial(serial_number):
        """
        Retrieve equipment by serial number
        Args:
            serial_number (str): Serial number
        Returns:
            Equipment: Equipment object or None
        """
        return Equipment.query.filter_by(serial_number=serial_number).first()

    @staticmethod
    def get_equipment_by_status(status):
        """
        Retrieve all equipment with specific status
        Args:
            status (EquipmentStatus): Equipment status enum
        Returns:
            list: List of Equipment objects

        """
        return Equipment.query.filter_by(current_status=status).all()

    @staticmethod
    def get_failing_equipment():
        """
        Retrieve all equipment with FAIL status
        Returns:
            list: List of Equipment objects
        """
        return EquipmentService.get_equipment_by_status(EquipmentStatus.FAIL)

    @staticmethod
    def get_overdue_equipment():
        """
        Retrieve all equipment with overdue maintenance
        Returns:
            list: List of Equipment objects
        """
        today = date.today()
        return Equipment.query.filter(
            Equipment.next_maintenance_date < today
        ).all()

    @staticmethod
    def get_upcoming_maintenance(days=7):
        """
        Retrieve equipment needing maintenance in next N days
        Args:
            days (int): Number of days to look ahead
        Returns:
            list: List of Equipment objects
        """
        today = date.today()
        future_date = today + timedelta(days=days)

        return Equipment.query.filter(
            Equipment.next_maintenance_date >= today,
            Equipment.next_maintenance_date <= future_date
        ).all()

    @staticmethod
    def create_equipment(name, serial_number, equipment_type, maintenance_interval, location=None, manufacturer=None):
        """
        Create new equipment
        Args:
            name (str): Equipment name
            serial_number (str): Unique serial number
            equipment_type (str): Type of equipment
            maintenance_interval (int): Days between maintenance
            location (str, optional): Physical location
            manufacturer (str, optional): Manufacturer name
        Returns:
            tuple: (Equipment object, error_message)
        """
        # Validate input
        if not name or not serial_number or not equipment_type:
            return None, "Name, serial number and type are required"

        if not maintenance_interval or maintenance_interval <= 0:
            return None, "Maintenance interval must be greater than 0"

        # Check for duplicate serial number
        exsting = EquipmentService.get_equipment_by_serial(serial_number)
        if exsting:
            return None, f"Equipment with serial number {serial_number} already exsts"

        # Create equipment
        equipment = Equipment(
            name=name,
            serial_number=serial_number,
            equipment_type=equipment_type,
            location=location,
            manufacturer=manufacturer,
            maintenance_interval=maintenance_interval,
            current_status=EquipmentStatus.OK
        )

        # Calculate initial next maintenance date
        equipment.calculate_next_maintenance()

        try:
            db.session.add(equipment)
            db.session.commit()
            return equipment, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"

    @staticmethod
    def update_equipment(equipment_id, **kwargs):
        """
        Update equipment fields
        Args:
            equipment_id (int): Equipment ID
            **kwargs: Fields to update
        Returns:
            tuple: (Equipment object, error_message)
        """
        equipment = EquipmentService.get_equipment_by_id(equipment_id)

        if not equipment:
            return None, "Equipment not found"

        # Update allowed fields
        allowed_fields = ['name', 'equipment_type', 'location', 'manufacturer', 'maintenance_interval']

        for field, value in kwargs.items():
            if field in allowed_fields and value is not None:
                setattr(equipment, field, value)

        # Update timestamp
        equipment.updated_at = datetime.utcnow()

        # Recalculate maintenance date if interval changed
        if 'maintenance_interval' in kwargs:
            equipment.calculate_next_maintenance()

        try:
            db.session.commit()
            return equipment, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"

    @staticmethod
    def update_equipment_status(equipment_id, new_status):
        """
        Update equipment operational status
        Args:
            equipment_id (int): Equipment ID
            new_status (EquipmentStatus): New status enum
        Returns:
            tuple: (Equipment object, error_message)
        """
        equipment = EquipmentService.get_equipment_by_id(equipment_id)

        if not equipment:
            return None, "Equipment not found"

        old_status = equipment.current_status
        equipment.current_status = new_status
        equipment.updated_at = datetime.utcnow()

        try:
            db.session.commit()
            return equipment, None
        except Exception as e:
            db.session.rollback()
            return None, f"Database error: {str(e)}"

    @staticmethod
    def delete_equipment(equipment_id):
        """
        Delete equipment (cascade deletes logs/events, nullifies alerts)
        Args:
            equipment_id (int): Equipment ID
        Returns:
            tuple: (success boolean, error_message)
        """
        equipment = EquipmentService.get_equipment_by_id(equipment_id)

        if not equipment:
            return False, "Equipment not found"

        try:
            db.session.delete(equipment)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, f"Database error: {str(e)}"

    @staticmethod
    def get_equipment_statistics():
        """
        Get equipment statistics for dashboard
        Returns:
            dict: Statistics summary
        """
        total = Equipment.query.count()
        ok_count = Equipment.query.filter_by(current_status=EquipmentStatus.OK).count()
        warning_count = Equipment.query.filter_by(current_status=EquipmentStatus.WARNING).count()
        fail_count = Equipment.query.filter_by(current_status=EquipmentStatus.FAIL).count()
        overdue_count = len(EquipmentService.get_overdue_equipment())

        return {
            'total': total,
            'ok': ok_count,
            'warning': warning_count,
            'fail': fail_count,
            'overdue_maintenance': overdue_count
        }





