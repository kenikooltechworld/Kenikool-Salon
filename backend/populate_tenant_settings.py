#!/usr/bin/env python
"""Populate tenant settings with test data."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant

def populate_settings():
    """Populate all tenants with default settings if they don't have any."""
    # Initialize database
    init_db()
    
    # Get all tenants
    tenants = Tenant.objects()
    
    if not tenants:
        print("❌ No tenants found in database")
        return False
    
    updated_count = 0
    for tenant in tenants:
        if not tenant.settings or not tenant.settings.get("email"):
            # Populate with default settings
            tenant.settings = {
                "email": f"salon@{tenant.subdomain}.com" if tenant.subdomain else "salon@example.com",
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
            
            # Also populate address if empty
            if not tenant.address:
                tenant.address = "123 Main Street, Lagos"
            
            tenant.save()
            updated_count += 1
            print(f"✓ Updated tenant: {tenant.name} (ID: {tenant.id})")
            print(f"  - Email: {tenant.settings['email']}")
            print(f"  - Address: {tenant.address}")
        else:
            print(f"✓ Tenant already has settings: {tenant.name} (ID: {tenant.id})")
    
    print(f"\n✅ Updated {updated_count} tenant(s) with settings")
    return True

if __name__ == "__main__":
    try:
        if populate_settings():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
