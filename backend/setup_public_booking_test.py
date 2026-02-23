#!/usr/bin/env python
"""Setup test tenant for public booking."""

import sys
sys.path.insert(0, '.')

from app.db import init_db, close_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.staff import Staff
from app.models.service import Service
from app.models.availability import Availability
from datetime import datetime, timedelta
from decimal import Decimal

def main():
    """Setup test tenant."""
    init_db()
    
    try:
        # Check if kenzola-salon tenant exists
        tenant = Tenant.objects(subdomain="kenzola-salon").first()
        
        if tenant:
            print(f"✓ Tenant 'kenzola-salon' already exists")
            print(f"  ID: {tenant.id}")
            print(f"  Name: {tenant.name}")
            print(f"  Published: {tenant.is_published}")
            print(f"  Status: {tenant.status}")
        else:
            print("Creating test tenant 'kenzola-salon'...")
            tenant = Tenant(
                name="Kenzola Salon",
                subdomain="kenzola-salon",
                email="test@kenzola-salon.com",
                description="Test salon for public booking",
                status="active",
                is_published=True,
                subscription_tier="trial",
            )
            tenant.save()
            print(f"✓ Tenant created: {tenant.id}")
        
        # Check if there are services
        services = Service.objects(tenant_id=tenant.id, is_published=True)
        print(f"\n✓ Published services: {services.count()}")
        
        for service in services[:3]:
            print(f"  - {service.name} (${service.price})")
        
        # Check if there are staff
        staff_list = Staff.objects(tenant_id=tenant.id)
        print(f"\n✓ Staff members: {staff_list.count()}")
        
        for staff in staff_list[:3]:
            print(f"  - {staff.first_name} {staff.last_name}")
        
        # Check availability
        availability = Availability.objects(tenant_id=tenant.id)
        print(f"\n✓ Availability records: {availability.count()}")
        
    finally:
        close_db()

if __name__ == '__main__':
    main()
