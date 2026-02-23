#!/usr/bin/env python3
"""Setup tenant for public booking testing."""

import os
import sys
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import connect_db
from app.models.tenant import Tenant

def setup_tenant():
    """Create or update tenant for public booking."""
    connect_db()
    
    subdomain = "kenzola-salon"
    
    # Check if tenant exists
    tenant = Tenant.objects(subdomain=subdomain).first()
    
    if tenant:
        print(f"✓ Tenant exists: {tenant.name}")
        print(f"  - ID: {tenant.id}")
        print(f"  - Status: {tenant.status}")
        print(f"  - Published: {tenant.is_published}")
        
        # Update if needed
        if tenant.status != "active":
            tenant.status = "active"
            tenant.save()
            print(f"  ✓ Updated status to 'active'")
        
        if not tenant.is_published:
            tenant.is_published = True
            tenant.save()
            print(f"  ✓ Updated is_published to True")
    else:
        print(f"✗ Tenant not found, creating...")
        tenant = Tenant(
            name="Kenzola Salon",
            subdomain=subdomain,
            email="info@kenzola-salon.com",
            description="Professional salon services",
            status="active",
            is_published=True,
            subscription_tier="professional",
        )
        tenant.save()
        print(f"✓ Tenant created successfully")
        print(f"  - ID: {tenant.id}")
        print(f"  - Subdomain: {tenant.subdomain}")

if __name__ == "__main__":
    setup_tenant()
