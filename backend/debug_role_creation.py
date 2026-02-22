"""Debug role creation process."""

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
from app.models.user import User
from app.services.rbac_service import RBACService

def debug_role_creation():
    """Debug role creation for the tenant."""
    init_db()
    
    try:
        # Get the tenant
        tenant = Tenant.objects(name="Kenzola - Abuja").first()
        if not tenant:
            print("Tenant not found!")
            return
        
        print(f"Tenant: {tenant.name} ({tenant.id})")
        print(f"Tenant ID type: {type(tenant.id)}")
        
        # Check existing roles
        roles = Role.objects(tenant_id=tenant.id)
        print(f"\nExisting roles: {roles.count()}")
        for role in roles:
            print(f"  - {role.name} (id: {role.id})")
        
        # Check users
        users = User.objects(tenant_id=tenant.id)
        print(f"\nExisting users: {users.count()}")
        for user in users:
            print(f"  - {user.email} (role_id: {user.role_id})")
        
        # Try creating default roles
        print("\n" + "="*60)
        print("Creating default roles...")
        print("="*60)
        
        rbac_service = RBACService()
        result = rbac_service.create_default_roles(str(tenant.id))
        print(f"Result: {result}")
        
        # Check roles after creation
        roles = Role.objects(tenant_id=tenant.id)
        print(f"\nRoles after creation: {roles.count()}")
        for role in roles:
            print(f"  - {role.name} (id: {role.id}, permissions: {len(role.permissions)})")
        
    finally:
        close_db()

if __name__ == "__main__":
    debug_role_creation()
