"""Test roles endpoint."""

import os
import sys
from datetime import datetime, timedelta
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db, close_db
from app.models.tenant import Tenant
from app.models.role import Role
from app.models.user import User
from app.services.rbac_service import RBACService

def test_roles():
    """Test role creation and retrieval."""
    init_db()
    
    try:
        # Find a tenant
        tenant = Tenant.objects().first()
        if not tenant:
            print("No tenants found")
            return
        
        print(f"Testing with tenant: {tenant.id} ({tenant.name})")
        
        # Check existing roles
        roles = Role.objects(tenant_id=tenant.id)
        print(f"\nExisting roles: {roles.count()}")
        for role in roles:
            print(f"  - {role.name} (id: {role.id})")
        
        # If no roles, create them
        if roles.count() == 0:
            print("\nNo roles found, creating default roles...")
            rbac_service = RBACService()
            rbac_service.create_default_roles(str(tenant.id))
            
            # Check again
            roles = Role.objects(tenant_id=tenant.id)
            print(f"After creation: {roles.count()} roles")
            for role in roles:
                print(f"  - {role.name} (id: {role.id})")
        
    finally:
        close_db()

if __name__ == "__main__":
    test_roles()
