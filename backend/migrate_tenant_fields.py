#!/usr/bin/env python
"""Migrate existing tenants to add missing fields for public booking."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

sys.path.insert(0, '.')

from app.db import init_db, close_db
from app.models.tenant import Tenant

def main():
    """Migrate tenant documents to add missing fields."""
    init_db()
    
    try:
        # Get all tenants
        tenants = Tenant.objects()
        total = tenants.count()
        
        if total == 0:
            print("No tenants found to migrate.")
            return
        
        print(f"Found {total} tenants to migrate...")
        updated = 0
        
        for tenant in tenants:
            needs_update = False
            
            # Check and set missing fields
            if not hasattr(tenant, 'email') or tenant.email is None:
                tenant.email = None
                needs_update = True
            
            if not hasattr(tenant, 'description') or tenant.description is None:
                tenant.description = None
                needs_update = True
            
            if not hasattr(tenant, 'logo_url') or tenant.logo_url is None:
                tenant.logo_url = None
                needs_update = True
            
            if not hasattr(tenant, 'primary_color') or tenant.primary_color is None:
                tenant.primary_color = None
                needs_update = True
            
            if not hasattr(tenant, 'secondary_color') or tenant.secondary_color is None:
                tenant.secondary_color = None
                needs_update = True
            
            if needs_update:
                tenant.save()
                updated += 1
                print(f"  ✓ Updated: {tenant.name}")
        
        print(f"\nMigration complete!")
        print(f"  Total tenants: {total}")
        print(f"  Updated: {updated}")
        
    finally:
        close_db()

if __name__ == '__main__':
    main()
