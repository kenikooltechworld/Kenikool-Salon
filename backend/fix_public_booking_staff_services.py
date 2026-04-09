#!/usr/bin/env python3
"""Fix script to assign services to staff for public booking."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import init_db, close_db
from app.models.staff import Staff
from app.models.service import Service
from app.models.tenant import Tenant

init_db()

try:
    # Get all published tenants
    tenants = Tenant.objects(is_published=True)
    print(f"Found {tenants.count()} published tenants\n")
    
    total_assignments = 0
    
    for tenant in tenants:
        print(f"Processing tenant: {tenant.name}")
        
        # Get all public services for this tenant
        services = Service.objects(
            tenant_id=tenant.id,
            is_published=True,
            allow_public_booking=True
        )
        print(f"  Public services: {services.count()}")
        
        # Get all staff available for public booking
        staff_list = Staff.objects(
            tenant_id=tenant.id,
            is_available_for_public_booking=True,
            status="active"
        )
        print(f"  Staff available for public booking: {staff_list.count()}")
        
        # Assign each service to each staff member
        for staff in staff_list:
            name = f"{staff.user_id.first_name} {staff.user_id.last_name}" if staff.user_id else "Unknown"
            before_count = len(staff.service_ids) if staff.service_ids else 0
            
            # Add services that aren't already assigned
            for service in services:
                if service.id not in staff.service_ids:
                    staff.service_ids.append(service.id)
            
            after_count = len(staff.service_ids) if staff.service_ids else 0
            
            if after_count > before_count:
                staff.save()
                added = after_count - before_count
                print(f"    ✓ {name}: +{added} services (total: {after_count})")
                total_assignments += added
            else:
                print(f"    - {name}: already has all services ({after_count})")
    
    print(f"\nTotal service assignments added: {total_assignments}")
    print("✓ Public booking staff services fixed!")
    
finally:
    close_db()
