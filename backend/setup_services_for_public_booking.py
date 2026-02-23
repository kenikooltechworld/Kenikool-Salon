#!/usr/bin/env python
"""Setup services for public booking testing."""

import os
import sys

# Setup path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.service import Service
from app.models.service_category import ServiceCategory
from bson import ObjectId

def setup_services():
    """Create services for the Kenzola Salon tenant."""
    init_db()
    
    # Find the Kenzola Salon tenant
    tenant = Tenant.objects(subdomain="kenzola-salon").first()
    if not tenant:
        print("❌ Kenzola Salon tenant not found")
        return
    
    print(f"✓ Found tenant: {tenant.name} (ID: {tenant.id})")
    
    # Check if services already exist
    existing_services = Service.objects(tenant_id=tenant.id).count()
    print(f"✓ Existing services: {existing_services}")
    
    # Update existing service to be public
    massage_service = Service.objects(tenant_id=tenant.id, name="Massage").first()
    if massage_service:
        massage_service.allow_public_booking = True
        massage_service.is_published = True
        massage_service.public_description = massage_service.public_description or "Relaxing massage service"
        massage_service.save()
        print(f"✓ Updated service: {massage_service.name} - now public and published")
    
    # List existing services
    print("✓ Services after update:")
    for service in Service.objects(tenant_id=tenant.id):
        print(f"  - {service.name} (ID: {service.id}, Published: {service.is_published}, Public: {service.allow_public_booking})")
    
    # Create additional services if needed
    if existing_services < 4:
        # Create service category
        category = ServiceCategory.objects(
            tenant_id=tenant.id,
            name="Hair Services"
        ).first()
        
        if not category:
            category = ServiceCategory(
                tenant_id=tenant.id,
                name="Hair Services",
                description="Professional hair services",
                is_active=True
            )
            category.save()
            print(f"✓ Created category: {category.name}")
        
        # Create services
        services_data = [
            {
                "name": "Hair Cut",
                "description": "Professional hair cutting service",
                "public_description": "Get a fresh, professional haircut tailored to your style",
                "duration_minutes": 30,
                "price": 5000.0,
                "benefits": ["Expert styling", "Professional finish", "Personalized consultation"]
            },
            {
                "name": "Hair Coloring",
                "description": "Professional hair coloring service",
                "public_description": "Transform your look with our professional hair coloring",
                "duration_minutes": 60,
                "price": 15000.0,
                "benefits": ["Premium color products", "Expert application", "Color consultation"]
            },
            {
                "name": "Hair Treatment",
                "description": "Restorative hair treatment",
                "public_description": "Restore and rejuvenate your hair with our premium treatments",
                "duration_minutes": 45,
                "price": 10000.0,
                "benefits": ["Deep conditioning", "Scalp treatment", "Hair restoration"]
            },
        ]
        
        for service_data in services_data:
            # Check if service already exists
            existing = Service.objects(tenant_id=tenant.id, name=service_data["name"]).first()
            if not existing:
                service = Service(
                    tenant_id=tenant.id,
                    category_id=category.id,
                    name=service_data["name"],
                    description=service_data["description"],
                    public_description=service_data["public_description"],
                    duration_minutes=service_data["duration_minutes"],
                    price=service_data["price"],
                    benefits=service_data["benefits"],
                    is_published=True,
                    allow_public_booking=True,
                )
                service.save()
                print(f"✓ Created service: {service.name} (ID: {service.id})")
    
    # Verify services were created
    services = Service.objects(tenant_id=tenant.id)
    print(f"\n✓ Total services: {services.count()}")
    for service in services:
        print(f"  - {service.name}: Published={service.is_published}, Public={service.allow_public_booking}")

if __name__ == "__main__":
    try:
        setup_services()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
