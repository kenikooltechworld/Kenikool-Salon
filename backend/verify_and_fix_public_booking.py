#!/usr/bin/env python
"""Verify and fix public booking tenant setup."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from app.db import init_db, close_db
from app.models.tenant import Tenant
from app.models.service import Service
from app.models.staff import Staff
from app.models.availability import Availability
from datetime import datetime, timedelta
from decimal import Decimal

def main():
    """Verify and fix public booking setup."""
    init_db()
    
    try:
        print("=" * 60)
        print("PUBLIC BOOKING TENANT VERIFICATION")
        print("=" * 60)
        
        # Check if kenzola-salon tenant exists
        tenant = Tenant.objects(subdomain="kenzola-salon").first()
        
        if not tenant:
            print("\n❌ Tenant 'kenzola-salon' NOT FOUND")
            print("Creating tenant...")
            tenant = Tenant(
                name="Kenzola Salon",
                subdomain="kenzola-salon",
                email="info@kenzola-salon.com",
                description="Professional salon services",
                status="active",
                is_published=True,
                subscription_tier="professional",
                primary_color="#FF6B9D",
                secondary_color="#FFC75F",
            )
            tenant.save()
            print(f"✓ Tenant created: {tenant.id}")
        else:
            print(f"\n✓ Tenant found: {tenant.name}")
            print(f"  ID: {tenant.id}")
            print(f"  Subdomain: {tenant.subdomain}")
            print(f"  Status: {tenant.status}")
            print(f"  Published: {tenant.is_published}")
            
            # Fix if needed
            if tenant.status != "active":
                print(f"  ⚠️  Status is '{tenant.status}', changing to 'active'...")
                tenant.status = "active"
                tenant.save()
                print(f"  ✓ Status updated")
            
            if not tenant.is_published:
                print(f"  ⚠️  Not published, setting is_published=True...")
                tenant.is_published = True
                tenant.save()
                print(f"  ✓ Published")
        
        # Verify tenant fields
        print(f"\n✓ Tenant fields:")
        print(f"  Email: {tenant.email}")
        print(f"  Description: {tenant.description}")
        print(f"  Logo URL: {tenant.logo_url}")
        print(f"  Primary Color: {tenant.primary_color}")
        print(f"  Secondary Color: {tenant.secondary_color}")
        
        # Check services
        services = Service.objects(tenant_id=tenant.id, is_published=True)
        print(f"\n✓ Published services: {services.count()}")
        if services.count() > 0:
            for service in services[:3]:
                print(f"  - {service.name} (${service.price})")
        else:
            print("  ⚠️  No published services found")
        
        # Check staff
        staff_list = Staff.objects(tenant_id=tenant.id)
        print(f"\n✓ Staff members: {staff_list.count()}")
        if staff_list.count() > 0:
            for staff in staff_list[:3]:
                print(f"  - {staff.first_name} {staff.last_name}")
        else:
            print("  ⚠️  No staff members found")
        
        # Check availability
        availability = Availability.objects(tenant_id=tenant.id)
        print(f"\n✓ Availability records: {availability.count()}")
        
        print("\n" + "=" * 60)
        print("✅ PUBLIC BOOKING TENANT READY")
        print("=" * 60)
        print("\nTo test:")
        print("1. Access http://kenzola-salon.localhost:3000")
        print("2. Or call: curl -H 'Host: kenzola-salon.localhost:8000' http://localhost:8000/api/v1/public/salon-info")
        
    finally:
        close_db()

if __name__ == '__main__':
    main()
