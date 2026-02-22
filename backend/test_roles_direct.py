"""Test roles endpoint directly."""

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
from app.context import set_tenant_id, set_user_id
from bson import ObjectId

def test_roles_endpoint():
    """Test the roles endpoint logic directly."""
    init_db()
    
    try:
        # Get the tenant
        tenant = Tenant.objects(name="Kenzola - Abuja").first()
        if not tenant:
            print("Tenant not found!")
            return
        
        print(f"Tenant: {tenant.name}")
        print(f"Tenant ID: {tenant.id}")
        
        # Simulate the endpoint logic
        tenant_id = tenant.id
        print(f"\nQuerying roles with tenant_id: {tenant_id}")
        
        roles = Role.objects(tenant_id=tenant_id).order_by("name")
        print(f"Found {roles.count()} roles:")
        for role in roles:
            print(f"  - {role.name} (id: {role.id})")
        
        # Convert to response format
        def role_to_response(role):
            return {
                "id": str(role.id),
                "name": role.name,
                "description": role.description,
                "isCustom": role.is_custom,
            }
        
        response_roles = [role_to_response(r) for r in roles]
        print(f"\nResponse format:")
        for r in response_roles:
            print(f"  - {r}")
        
        result = {"roles": response_roles}
        print(f"\nFinal result:")
        print(result)
        
    finally:
        close_db()

if __name__ == "__main__":
    test_roles_endpoint()
