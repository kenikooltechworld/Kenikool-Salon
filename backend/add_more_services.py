#!/usr/bin/env python
"""Add more services for public booking."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.db import init_db
    from app.models.tenant import Tenant
    from app.models.service import Service
    from app.models.service_category import ServiceCategory

    init_db()

    # Find tenant
    tenant = Tenant.objects(subdomain="kenzola-salon").first()
    print(f"Tenant: {tenant}")

    if tenant:
        # Create or get category
        category = ServiceCategory.objects(tenant_id=tenant.id, name="Hair Services").first()
        if not category:
            category = ServiceCategory(
                tenant_id=tenant.id,
                name="Hair Services",
                description="Professional hair services",
                is_active=True
            )
            category.save()
            print(f"Created category: {category.name}")
        
        # Add services
        services_to_add = [
            {
                "name": "Hair Cut",
                "description": "Professional hair cutting",
                "public_description": "Get a fresh, professional haircut",
                "duration_minutes": 30,
                "price": 5000.0,
            },
            {
                "name": "Hair Coloring",
                "description": "Professional hair coloring",
                "public_description": "Transform your look with professional coloring",
                "duration_minutes": 60,
                "price": 15000.0,
            },
            {
                "name": "Hair Treatment",
                "description": "Restorative hair treatment",
                "public_description": "Restore and rejuvenate your hair",
                "duration_minutes": 45,
                "price": 10000.0,
            },
        ]
        
        for service_data in services_to_add:
            existing = Service.objects(tenant_id=tenant.id, name=service_data["name"]).first()
            if not existing:
                service = Service(
                    tenant_id=tenant.id,
                    category="Hair Services",
                    name=service_data["name"],
                    description=service_data["description"],
                    public_description=service_data["public_description"],
                    duration_minutes=service_data["duration_minutes"],
                    price=service_data["price"],
                    is_published=True,
                    allow_public_booking=True,
                )
                service.save()
                print(f"Created service: {service.name}")
            else:
                print(f"Service already exists: {service_data['name']}")
        
        # List all services
        services = Service.objects(tenant_id=tenant.id)
        print(f"\nTotal services: {services.count()}")
        for s in services:
            print(f"  - {s.name}: published={s.is_published}, public={s.allow_public_booking}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
