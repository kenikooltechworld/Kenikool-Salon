#!/usr/bin/env python
"""Seed a test user for development."""

import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.services.auth_service import AuthenticationService
from app.config import Settings

def seed_test_user():
    """Create a test tenant and user."""
    # Initialize database
    init_db()
    
    settings = Settings()
    auth_service = AuthenticationService(settings)
    
    # Create test tenant
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        subscription_tier="starter",
        status="active",
    )
    tenant.save()
    print(f"✓ Created tenant: {tenant.id}")
    
    # Create test role
    role = Role(
        tenant_id=tenant.id,
        name="Admin",
    )
    role.save()
    print(f"✓ Created role: {role.id}")
    
    # Create test user with proper password hash
    password = "password123"
    hashed_password = auth_service.hash_password(password)
    
    user = User(
        tenant_id=tenant.id,
        email="test@example.com",
        password_hash=hashed_password,
        first_name="Test",
        last_name="User",
        role_ids=[role.id],
        status="active",
    )
    user.save()
    print(f"✓ Created user: {user.id}")
    print(f"\nTest credentials:")
    print(f"  Email: test@example.com")
    print(f"  Password: {password}")

if __name__ == "__main__":
    try:
        seed_test_user()
        print("\n✓ Test user seeded successfully!")
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
