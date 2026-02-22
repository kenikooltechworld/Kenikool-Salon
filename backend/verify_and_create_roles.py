"""Verify and create roles for all tenants."""

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

def verify_and_create_roles():
    """Verify roles exist for all tenants, create if missing."""
    init_db()
    
    try:
        # Find all tenants
        tenants = Tenant.objects()
        print(f"Found {tenants.count()} tenants\n")
        
        rbac_service = RBACService()
        
        for tenant in tenants:
            print(f"Tenant: {tenant.name} ({tenant.id})")
            
            # Check existing roles
            roles = Role.objects(tenant_id=tenant.id)
            print(f"  Existing roles: {roles.count()}")
            
            for role in roles:
                print(f"    - {role.name}")
            
            # Create if missing
            if roles.count() == 0:
                print(f"  Creating default roles...")
                rbac_service.create_default_roles(str(tenant.id))
                
                # Verify creation
                roles = Role.objects(tenant_id=tenant.id)
                print(f"  After creation: {roles.count()} roles")
                for role in roles:
                    print(f"    - {role.name}")
            
            print()
        
        print("Done!")
        
    finally:
        close_db()

if __name__ == "__main__":
    verify_and_create_roles()
