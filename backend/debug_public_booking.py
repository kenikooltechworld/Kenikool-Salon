#!/usr/bin/env python
"""Debug public booking endpoint issues."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, '.')

from app.db import init_db, close_db
from app.models.tenant import Tenant

def main():
    """Debug tenant and public booking setup."""
    init_db()
    
    try:
        # Get the tenant
        tenant = Tenant.objects.first()
        if not tenant:
            print("❌ No tenant found!")
            return
        
        print(f"✓ Tenant: {tenant.name}")
        print(f"  ID: {tenant.id}")
        print(f"  Subdomain: {tenant.subdomain}")
        print(f"  Status: {tenant.status}")
        print(f"  is_published: {tenant.is_published}")
        print(f"  is_active: {getattr(tenant, 'is_active', 'N/A')}")
        
        # Check if tenant needs to be published
        if not tenant.is_published:
            print(f"\n⚠️  Tenant is NOT published. Setting is_published=True...")
            tenant.is_published = True
            tenant.save()
            print(f"✓ Tenant published successfully")
        
        # Verify fields
        print(f"\n✓ Tenant fields:")
        print(f"  email: {getattr(tenant, 'email', 'N/A')}")
        print(f"  description: {getattr(tenant, 'description', 'N/A')}")
        print(f"  logo_url: {getattr(tenant, 'logo_url', 'N/A')}")
        print(f"  primary_color: {getattr(tenant, 'primary_color', 'N/A')}")
        print(f"  secondary_color: {getattr(tenant, 'secondary_color', 'N/A')}")
        
        print("\n✅ Tenant is ready for public booking!")
        
    finally:
        close_db()

if __name__ == '__main__':
    main()
