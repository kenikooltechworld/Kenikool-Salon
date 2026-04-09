"""Simple script to fix tenant settings."""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.user import User
from datetime import datetime

def fix_settings():
    """Fix tenant settings."""
    print("=" * 60)
    print("FIXING TENANT SETTINGS")
    print("=" * 60)
    
    # Initialize database connection
    print("\n[1/3] Initializing database connection...")
    init_db()
    print("✓ Database connected")
    
    print("\n[2/3] Finding tenants...")
    print("Fixing tenant settings...")
    
    tenants = Tenant.objects(deletion_status="active")
    fixed = 0
    
    for tenant in tenants:
        settings = tenant.settings or {}
        updated = False
        
        print(f"\nTenant: {tenant.name} (ID: {tenant.id})")
        print(f"  Current email: '{settings.get('email', '')}'")
        print(f"  Current phone: '{settings.get('phone', '')}'")
        print(f"  Subdomain: '{tenant.subdomain}'")
        
        # Fix email
        if not settings.get("email"):
            if settings.get("owner_email"):
                settings["email"] = settings["owner_email"]
                updated = True
                print(f"  → Set email from owner_email: {settings['email']}")
            else:
                # Try from user
                user = User.objects(tenant_id=tenant.id).first()
                if user and user.email:
                    settings["email"] = user.email
                    updated = True
                    print(f"  → Set email from user: {settings['email']}")
        
        # Fix phone
        if not settings.get("phone"):
            if settings.get("owner_phone"):
                settings["phone"] = settings["owner_phone"]
                updated = True
                print(f"  → Set phone from owner_phone: {settings['phone']}")
            else:
                # Try from user
                user = User.objects(tenant_id=tenant.id).first()
                if user and user.phone:
                    settings["phone"] = user.phone
                    updated = True
                    print(f"  → Set phone from user: {settings['phone']}")
        
        if updated:
            tenant.settings = settings
            tenant.updated_at = datetime.utcnow()
            tenant.save()
            fixed += 1
            print(f"  ✓ SAVED")
    
    print(f"\n\nFixed {fixed} tenants")

if __name__ == "__main__":
    fix_settings()
