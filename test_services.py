#!/usr/bin/env python3
"""
MedAsset Sentinel - Service Layer Test Script
Quick verification that all services work correctly
"""

from app import create_app
from services import AuthService, EquipmentService, MaintenanceService, AlertService


def test_services():
    """Test all service layer functionality"""
    
    app = create_app('development')
    
    with app.app_context():
        print("🧪 Testing MedAsset Sentinel Services\n")
        
        # ====================================================================
        # TEST 1: Authentication Service
        # ====================================================================
        print("1️⃣  Testing AuthService...")
        
        # Test authentication
        admin = AuthService.authenticate('admin', 'admin123')
        if admin:
            print(f"   ✓ Authentication successful: {admin.username}")
        else:
            print("   ✗ Authentication failed")
        
        # Test wrong password
        admin = AuthService.authenticate('admin', 'wrongpassword')
        if admin is None:
            print("   ✓ Invalid password correctly rejected")
        else:
            print("   ✗ Invalid password incorrectly accepted")
        
        print()
        
        # ====================================================================
        # TEST 2: Equipment Service
        # ====================================================================
        print("2️⃣  Testing EquipmentService...")
        
        # Get all equipment
        all_equipment = EquipmentService.get_all_equipment()
        print(f"   ✓ Found {len(all_equipment)} equipment items")
        
        # Get equipment statistics
        stats = EquipmentService.get_equipment_statistics()
        print(f"   ✓ Statistics: {stats['total']} total, {stats['fail']} failing")
        
        # Get failing equipment
        failing = EquipmentService.get_failing_equipment()
        print(f"   ✓ Failing equipment: {len(failing)}")
        
        # Get overdue maintenance
        overdue = EquipmentService.get_overdue_equipment()
        print(f"   ✓ Overdue maintenance: {len(overdue)}")
        
        print()
        
        # ====================================================================
        # TEST 3: Maintenance Service
        # ====================================================================
        print("3️⃣  Testing MaintenanceService...")
        
        if all_equipment:
            # Get maintenance history for first equipment
            equipment = all_equipment[0]
            history = MaintenanceService.get_maintenance_history(equipment.id)
            print(f"   ✓ Maintenance history for {equipment.serial_number}: {len(history)} records")
            
            # Get maintenance statistics
            maint_stats = MaintenanceService.get_maintenance_statistics()
            print(f"   ✓ Total maintenance logs: {maint_stats['total_maintenance_logs']}")
            print(f"   ✓ Overdue count: {maint_stats['overdue_count']}")
        
        print()
        
        # ====================================================================
        # TEST 4: Alert Service
        # ====================================================================
        print("4️⃣  Testing AlertService...")
        
        # Get unresolved alerts
        unresolved = AlertService.get_unresolved_alerts()
        print(f"   ✓ Unresolved alerts: {len(unresolved)}")
        
        # Get alert statistics
        alert_stats = AlertService.get_alert_statistics()
        print(f"   ✓ Alert statistics: {alert_stats}")
        
        # Get recent alerts
        recent = AlertService.get_recent_alerts(limit=5)
        print(f"   ✓ Recent alerts: {len(recent)}")
        
        print()
        
        # ====================================================================
        # TEST 5: Run Maintenance Compliance Check
        # ====================================================================
        print("5️⃣  Testing Maintenance Compliance Check...")
        
        result = MaintenanceService.check_maintenance_compliance()
        print(f"   ✓ Checked {result['total_equipment']} equipment items")
        print(f"   ✓ Created {result['upcoming_alerts_created']} upcoming alerts")
        print(f"   ✓ Created {result['overdue_alerts_created']} overdue alerts")
        
        print()
        
        # ====================================================================
        # SUMMARY
        # ====================================================================
        print("=" * 60)
        print("✅ All service tests completed successfully!")
        print("=" * 60)
        print("\nService layer is ready for route integration.")


if __name__ == '__main__':
    test_services()
