"""
Fix tenant settings data - populate email and phone from owner data.

This script:
1. Finds all tenants with empty email/phone in settings
2. Populates them from owner_email/owner_phone if available
3. Ensures subdomain is set correctly
"""

import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.user import User

def fix_tenant_settings():
    """Fix tenant settings data."""
    init_db()
    
    print("Starting tenant settings data fix...")
    
    tenants = Tenant.objects(deletion_status="active")
    fixed_count = 0
    
    for tenant in tenants:
        updated = False
        settings = tenant.settings or {}
        
        # Fix email - use owner_email if email is empty
        if not settings.get("email") and settings.get("owner_email"):
            settings["email"] = settings["owner_email"]
            updated = True
            print(f"  - Set email from owner_email: {settings['email']}")
        
        # Fix phone - use owner_phone if phone is empty
        if not settings.get("phone") and settings.get("owner_phone"):
            settings["phone"] = settings["owner_phone"]
            updated = True
            print(f"  - Set phone from owner_phone: {settings['phone']}")
        
        # If still empty, try to get from the owner user
        if not settings.get("email") or not settings.get("phone"):
            owner_user = User.objects(tenant_id=tenant.id, role_ids__size__gte=1).first()
            if owner_user:
                if not settings.get("email") and owner_user.email:
                    settings["email"] = owner_user.email
                    updated = True
                    print(f"  - Set email from owner user: {settings['email']}")
                
                if not settings.get("phone") and owner_user.phone:
                    settings["phone"] = owner_user.phone
                    updated = True
                    print(f"  - Set phone from owner user: {settings['phone']}")
        
        # Verify subdomain exists
        if not tenant.subdomain:
            print(f"  - WARNING: Tenant {tenant.id} has no subdomain!")
        
        if updated:
            tenant.settings = settings
            tenant.updated_at = datetime.utcnow()
            tenant.save()
            fixed_count += 1
            print(f"✓ Fixed tenant: {tenant.name} (ID: {tenant.id})")
    
    print(f"\nFixed {fixed_count} tenants")
    print("Done!")

if __name__ == "__main__":
    fix_tenant_settings()
