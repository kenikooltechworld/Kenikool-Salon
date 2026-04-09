#!/usr/bin/env python3
"""Fix script to assign all active staff to all public services."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import init_db, close_db
from app.models.staff import Staff
from app.models.service import Service
from app.models.tenant import Tenant

def main():
    """Assign all active staff to all public services."""
    init_db()
    
    try:
        print("\n" + "="*60)
        print("Fix: Assign Staff to Public Services")
        print("="*60 + "\n")
        
        # Get all tenants
        tenants = Tenant.objects(is_published=True)
        print(f"Found {tenants.count()} published tenants\n")
        
        total_assignments = 0
        
        for tenant in tenants:
            print(f"Tenant: {tenant.name} (ID: {tenant.id})")
            
            # Get all public services for this tenant
            services = Service.objects(
                tenant_id=tenant.id,
                is_published=True,
                allow_public_booking=True
            )
            print(f"  Public services: {services.count()}")
            
            if services.count() == 0:
                print(f"  ⚠️  No public services found\n")
                continue
            
            # Get all active staff available for public booking
            staff_members = Staff.objects(
                tenant_id=tenant.id,
                is_available_for_public_booking=True,
                status="active"
            )
            print(f"  Active staff for public booking: {staff_members.count()}")
            
            if staff_members.count() == 0:
                print(f"  ⚠️  No active staff found\n")
                continue
            
            # Assign each staff to each service
            for staff in staff_members:
                user_name = f"{staff.user_id.first_name} {staff.user_id.last_name}" if staff.user_id else "Unknown"
                
                # Get current service count
                initial_count = len(staff.service_ids)
                
                # Add all public services to this staff member
                for service in services:
                    if service.id not in staff.service_ids:
                        staff.service_ids.append(service.id)
                
                # Save if changes were made
                if len(staff.service_ids) > initial_count:
                    staff.save()
                    added = len(staff.service_ids) - initial_count
                    print(f"    ✓ {user_name}: Added {added} service(s)")
                    total_assignments += added
                else:
                    print(f"    - {user_name}: Already has all services")
            
            print()
        
        print("="*60)
        print(f"✓ Fix complete!")
        print(f"Total service assignments added: {total_assignments}")
        print("="*60 + "\n")
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        close_db()

if __name__ == "__main__":
    main()
