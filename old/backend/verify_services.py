#!/usr/bin/env python
"""Quick verification script to check services in database"""
from app.database import Database
from bson import ObjectId

db = Database.get_db()

# Get all services
all_services = list(db.services.find())
print(f"\n📊 Total services in database: {len(all_services)}")

if all_services:
    print("\n📋 Services by tenant_id:")
    tenant_ids = {}
    for service in all_services:
        tenant_id = service.get("tenant_id", "UNKNOWN")
        if tenant_id not in tenant_ids:
            tenant_ids[tenant_id] = []
        tenant_ids[tenant_id].append(service.get("name", "UNNAMED"))
    
    for tenant_id, services in tenant_ids.items():
        print(f"\n  Tenant: {tenant_id}")
        print(f"  Services ({len(services)}):")
        for service_name in services:
            print(f"    - {service_name}")
else:
    print("\n❌ No services found in database")

# Get all users
all_users = list(db.users.find())
print(f"\n👥 Total users in database: {len(all_users)}")

if all_users:
    print("\n📋 Users:")
    for user in all_users:
        print(f"  - {user.get('email', 'UNKNOWN')} (tenant_id: {user.get('tenant_id', 'UNKNOWN')})")
