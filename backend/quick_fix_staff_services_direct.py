#!/usr/bin/env python3
"""Quick fix to assign services to staff - direct MongoDB approach."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pymongo import MongoClient
from bson import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Connect directly to MongoDB
mongo_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
database_name = os.getenv("DATABASE_NAME", "kenikool-salon")
client = MongoClient(mongo_url)
db = client[database_name]

print("=" * 80)
print("FIXING PUBLIC BOOKING STAFF SERVICES")
print("=" * 80)

try:
    # Get all published tenants
    tenants = list(db.tenant.find({"is_published": True}))
    print(f"\nFound {len(tenants)} published tenants\n")
    
    total_updates = 0
    
    for tenant in tenants:
        tenant_id = tenant["_id"]
        tenant_name = tenant.get("name", "Unknown")
        print(f"Tenant: {tenant_name}")
        
        # Get all public services
        services = list(db.service.find({
            "tenant_id": tenant_id,
            "is_published": True,
            "allow_public_booking": True
        }))
        print(f"  Public services: {len(services)}")
        service_ids = [s["_id"] for s in services]
        
        # Get all staff available for public booking
        staff_list = list(db.staff.find({
            "tenant_id": tenant_id,
            "is_available_for_public_booking": True,
            "status": "active"
        }))
        print(f"  Staff available for public booking: {len(staff_list)}")
        
        # Update each staff member
        for staff in staff_list:
            staff_id = staff["_id"]
            current_services = staff.get("service_ids", [])
            
            # Add missing services
            new_services = list(set(current_services + service_ids))
            
            if len(new_services) > len(current_services):
                db.staff.update_one(
                    {"_id": staff_id},
                    {"$set": {"service_ids": new_services}}
                )
                added = len(new_services) - len(current_services)
                print(f"    ✓ Staff {staff_id}: +{added} services")
                total_updates += added
            else:
                print(f"    - Staff {staff_id}: already has all services")
    
    print(f"\n{'=' * 80}")
    print(f"Total service assignments added: {total_updates}")
    print("✓ Public booking staff services fixed!")
    print(f"{'=' * 80}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
finally:
    client.close()
