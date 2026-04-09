#!/usr/bin/env python3
"""Migration to populate staff service_ids from service staff_ids."""

import os
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from app.db import init_db, close_db
from app.models.staff import Staff
from app.models.service import Service
from app.models.tenant import Tenant
from bson import ObjectId

def main():
    """Populate staff service_ids from service staff_ids."""
    init_db()
    
    try:
        print("\n" + "="*60)
        print("Migration: Populate Staff Service IDs")
        print("="*60 + "\n")
        
        # Get all tenants
        tenants = Tenant.objects()
        total_staff_updated = 0
        
        for tenant in tenants:
            print(f"Processing tenant: {tenant.name} (ID: {tenant.id})")
            
            # Get all services for this tenant
            services = Service.objects(tenant_id=tenant.id)
            
            for service in services:
                # For each service, add it to the service_ids of all staff members listed in the service
                if service.staff_ids:
                    for staff_id in service.staff_ids:
                        staff = Staff.objects(id=staff_id, tenant_id=tenant.id).first()
                        if staff:
                            # Add service_id to staff's service_ids if not already there
                            if service.id not in staff.service_ids:
                                staff.service_ids.append(service.id)
                                staff.save()
                                print(f"  ✓ Added service {service.name} to staff {staff.user_id.first_name if staff.user_id else 'Unknown'}")
                                total_staff_updated += 1
        
        print(f"\n{'='*60}")
        print(f"Migration complete!")
        print(f"Total staff records updated: {total_staff_updated}")
        print(f"{'='*60}\n")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        close_db()

if __name__ == "__main__":
    main()
