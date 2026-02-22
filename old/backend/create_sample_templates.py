#!/usr/bin/env python3
"""
Create sample booking templates for testing
"""
import asyncio
import sys
import os
from datetime import datetime

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def create_sample_templates():
    """Create sample booking templates"""
    try:
        from app.database import Database
        from app.services.booking_template_service import BookingTemplateService
        from bson import ObjectId
        
        # Initialize database
        Database.connect_db()
        db = Database.get_db()
        
        print("Creating sample booking templates...")
        print("=" * 50)
        
        # Create a sample tenant
        tenant_id = "507f1f77bcf86cd799439011"
        tenant_data = {
            "_id": ObjectId(tenant_id),
            "name": "Sample Salon",
            "subdomain": "sample",
            "created_at": datetime.utcnow()
        }
        
        # Insert tenant if it doesn't exist
        existing_tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        if not existing_tenant:
            db.tenants.insert_one(tenant_data)
            print("✓ Created sample tenant")
        
        # Create a sample client
        client_id = "507f1f77bcf86cd799439012"
        client_data = {
            "_id": ObjectId(client_id),
            "tenant_id": ObjectId(tenant_id),
            "name": "John Doe",
            "phone": "+1234567890",
            "email": "john@example.com",
            "created_at": datetime.utcnow()
        }
        
        existing_client = db.clients.find_one({"_id": ObjectId(client_id)})
        if not existing_client:
            db.clients.insert_one(client_data)
            print("✓ Created sample client")
        
        # Create a sample service
        service_id = "507f1f77bcf86cd799439013"
        service_data = {
            "_id": ObjectId(service_id),
            "tenant_id": ObjectId(tenant_id),
            "name": "Haircut - Men",
            "description": "Professional men's haircut",
            "duration": 45,
            "price": 25.00,
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        existing_service = db.services.find_one({"_id": ObjectId(service_id)})
        if not existing_service:
            db.services.insert_one(service_data)
            print("✓ Created sample service")
        
        # Create a sample stylist
        stylist_id = "507f1f77bcf86cd799439014"
        stylist_data = {
            "_id": ObjectId(stylist_id),
            "tenant_id": ObjectId(tenant_id),
            "name": "Jane Smith",
            "email": "jane@example.com",
            "is_active": True,
            "created_at": datetime.utcnow()
        }
        
        existing_stylist = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        if not existing_stylist:
            db.stylists.insert_one(stylist_data)
            print("✓ Created sample stylist")
        
        # Create sample booking templates
        templates_to_create = [
            {
                "name": "John's Regular Haircut",
                "description": "John's usual haircut with Jane",
                "category": "Regular",
                "duration": 45,
                "pricing": 25.00
            },
            {
                "name": "Quick Trim",
                "description": "Quick hair trim service",
                "category": "Express",
                "duration": 30,
                "pricing": 20.00
            },
            {
                "name": "Premium Cut & Style",
                "description": "Premium haircut with styling",
                "category": "Premium",
                "duration": 60,
                "pricing": 35.00
            }
        ]
        
        for template_data in templates_to_create:
            # Check if template already exists
            existing = db.booking_templates.find_one({
                "tenant_id": ObjectId(tenant_id),
                "name": template_data["name"]
            })
            
            if not existing:
                template = await BookingTemplateService.create_template(
                    tenant_id=tenant_id,
                    name=template_data["name"],
                    client_id=client_id,
                    service_id=service_id,
                    stylist_id=stylist_id,
                    description=template_data["description"],
                    category=template_data["category"],
                    duration=template_data["duration"],
                    pricing=template_data["pricing"],
                    notes="Sample template for testing"
                )
                print(f"✓ Created template: {template_data['name']}")
            else:
                print(f"- Template already exists: {template_data['name']}")
        
        # Test fetching templates
        templates = await BookingTemplateService.get_templates(tenant_id=tenant_id)
        print(f"\n✓ Total templates in database: {len(templates)}")
        
        for template in templates:
            print(f"  - {template['name']} ({template['category']}) - ${template['pricing']}")
        
        print("\n✅ Sample data creation completed!")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(create_sample_templates())
    sys.exit(0 if success else 1)