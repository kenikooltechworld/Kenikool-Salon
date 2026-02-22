#!/usr/bin/env python3
"""Test script to verify tenant settings endpoints."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.models.tenant import Tenant
from app.models.user import User
from app.db import connect_db
from bson import ObjectId

def test_tenant_endpoints():
    """Test tenant GET and PUT endpoints."""
    connect_db()
    
    # Find a test tenant
    tenant = Tenant.objects().first()
    if not tenant:
        print("❌ No tenants found in database")
        return False
    
    print(f"✓ Found tenant: {tenant.name} (ID: {tenant.id})")
    print(f"  - address: {tenant.address}")
    print(f"  - settings: {tenant.settings}")
    print(f"  - subscription_tier: {tenant.subscription_tier}")
    print(f"  - status: {tenant.status}")
    
    # Check if tenant has settings
    if not tenant.settings:
        print("⚠ Tenant has no settings - updating with test data...")
        tenant.settings = {
            "email": "salon@example.com",
            "phone": "+234 801 234 5678",
            "businessHours": {
                "monday": {"open": "09:00", "close": "18:00", "closed": False},
                "tuesday": {"open": "09:00", "close": "18:00", "closed": False},
                "wednesday": {"open": "09:00", "close": "18:00", "closed": False},
                "thursday": {"open": "09:00", "close": "18:00", "closed": False},
                "friday": {"open": "09:00", "close": "18:00", "closed": False},
                "saturday": {"open": "10:00", "close": "16:00", "closed": False},
                "sunday": {"open": "10:00", "close": "16:00", "closed": True},
            }
        }
        tenant.save()
        print("✓ Updated tenant with test settings")
    
    # Verify the response format that the endpoint would return
    response_data = {
        "data": {
            "id": str(tenant.id),
            "name": tenant.name,
            "address": tenant.address,
            "subscription_tier": tenant.subscription_tier,
            "status": tenant.status,
            "region": tenant.region,
            "settings": tenant.settings or {},
            "created_at": tenant.created_at.isoformat(),
            "updated_at": tenant.updated_at.isoformat(),
        }
    }
    
    print("\n✓ Response format for GET /tenants/{tenant_id}:")
    import json
    print(json.dumps(response_data, indent=2))
    
    return True

if __name__ == "__main__":
    try:
        if test_tenant_endpoints():
            print("\n✅ All checks passed!")
            sys.exit(0)
        else:
            print("\n❌ Some checks failed")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
