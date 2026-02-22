"""Ensure all tenants have default roles created."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db, close_db
from app.models.tenant import Tenant
from app.models.role import Role
from app.services.rbac_service import RBACService

def ensure_roles():
    """Ensure all tenants have default roles."""
    init_db()
    
    try:
        # Find all tenants
        tenants = Tenant.objects()
        print(f"Found {tenants.count()} tenants")
        
        rbac_service = RBACService()
        
        for tenant in tenants:
            # Check if roles exist
            roles = Role.objects(tenant_id=tenant.id)
            if roles.count() == 0:
                print(f"\nCreating roles for tenant: {tenant.name} ({tenant.id})")
                rbac_service.create_default_roles(str(tenant.id))
                print(f"  Created {Role.objects(tenant_id=tenant.id).count()} roles")
            else:
                print(f"\nTenant {tenant.name} already has {roles.count()} roles")
        
        print("\nDone!")
        
    finally:
        close_db()

if __name__ == "__main__":
    ensure_roles()
