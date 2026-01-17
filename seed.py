#!/usr/bin/env python3
"""
MedAsset Sentinel - Database Seeding Script
Creates initial admin user and sample equipment for testing
"""
from datetime import date, timedelta
from app import create_app
from extensions import db
from models import Admin, Equipment, EquipmentStatus

def seed_database():
    """Seed database with initial data"""

    app = create_app('development')

    with app.app_context():
        print("🌱 Starting database seeding...")

        # ===============================
        # CREATE ADMIN USER
        # ===============================

        # Check if admin already exists
        existing_admin = Admin.query.filter_by(username='admin').first()

        if existing_admin:
            print("⚠️ Admin user already exists, skipping...")
        else:
            admin = Admin(username='admin')
            admin.set_password('admin123')  # Change in production!
            db.session.add(admin)
            print("Created admin user (username: admin, password: admin123)")

        # ============================
        # CREATE SAMPLE EQUIPMENT
        # ============================
        sample_equipment = [
            {
                'name': 'Ventilator Unit 1',
                'serial_number': 'VENT-001',
                'equipment_type': 'Ventilator',
                'location': 'ICU',
                'manufacturer': 'MedTech Solutions',
                'maintenance_interval': 90,  # 90 days
            },
            {
                'name': 'Infusion Pump 12',
                'serial_number': 'INF-012',
                'equipment_type': 'Infusion Pump',
                'location': 'Ward 3',
                'manufacturer': 'PharmaTech',
                'maintenance_interval': 30,  # 30 days
            },
            {
                'name': 'ECG Monitor A',
                'serial_number': 'ECG-A-001',
                'equipment_type': 'ECG Monitor',
                'location': 'Emergency Room',
                'manufacturer': 'CardioTech Inc',
                'maintenance_interval': 60,  # 60 days
            },
            {
                'name': 'X-Ray Machine B',
                'serial_number': 'XRAY-B-003',
                'equipment_type': 'X-Ray',
                'location': 'Radiology',
                'manufacturer': 'ImageSys Corp',
                'maintenance_interval': 180,  # 180 days
            },
            {
                'name': 'Defibrillator Unit 5',
                'serial_number': 'DEFIB-005',
                'equipment_type': 'Defibrillator',
                'location': 'Emergency Room',
                'manufacturer': 'LifeSave Medical',
                'maintenance_interval': 45,  # 45 days
            },
        ]

        equipment_created = 0

        for eq_data in sample_equipment:
            # Check if equipment already exists
            existing = Equipment.query.filter_by(
                serial_number=eq_data['serial_number']
            ).first()

            if existing:
                print(f"Equipment {eq_data['serial_number']} already exists, skipping...")
                continue

            # Create equipment
            equipment = Equipment(
                name=eq_data['name'],
                serial_number=eq_data['serial_number'],
                equipment_type=eq_data['equipment_type'],
                location=eq_data['location'],
                manufacturer=eq_data['manufacturer'],
                maintenance_interval=eq_data['maintenance_interval'],
                current_status=EquipmentStatus.OK,
                next_maintenance_date=date.today() + timedelta(
                    days=eq_data['maintenance_interval']
                )
            )

            db.session.add(equipment)
            equipment_created += 1
            print(f"Created equipment: {eq_data['name']} ({eq_data['serial_number']})")

        # Commit all changes
        try:
            db.session.commit()
            print(f"\n Seeding complete")
            print(f"    - Admin users: 1")
            print(f"    - Equipment items: {equipment_created}")
            print(f"\n Login credentials:")
            print(f"    Username: admin")
            print(f"    Password: admin123")
            print(f"\n IMPORTANT: Change admin password in production")

        except Exception as e:
            db.session.rollback()
            print(f"\n Error during seeding: {e}")
            raise

if __name__ == '__main__':
    seed_database()


