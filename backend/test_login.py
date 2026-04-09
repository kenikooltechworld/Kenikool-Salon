#!/usr/bin/env python
"""Test login endpoint."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

from app.db import init_db
from app.models.user import User
from app.services.auth_service import AuthenticationService
from app.config import Settings

print("Initializing database...")
init_db()

settings = Settings()
auth_service = AuthenticationService(settings)

# Get first user
user = User.objects.first()
if not user:
    print("✗ No users found")
    sys.exit(1)

print(f"Testing login with user: {user.email}")
print(f"User ID: {user.id}")
print(f"Tenant ID: {user.tenant_id}")
print(f"Status: {user.status}")
print(f"Password hash exists: {bool(user.password_hash)}")

# Try to authenticate with wrong password first
print("\n1. Testing with wrong password...")
result = auth_service.authenticate_user(user.email, "wrongpassword", str(user.tenant_id))
print(f"   Result: {result}")

# Now we need to know the correct password - let's check if we can reset it
print("\n2. Setting a known password...")
test_password = "TestPassword123!"
hashed = auth_service.hash_password(test_password)
user.password_hash = hashed
user.save()
print(f"   Password set to: {test_password}")

# Try to authenticate with correct password
print("\n3. Testing with correct password...")
result = auth_service.authenticate_user(user.email, test_password, str(user.tenant_id))
if result:
    print(f"   ✓ Authentication successful!")
    print(f"   User ID: {result.get('user_id')}")
    print(f"   Email: {result.get('email')}")
    print(f"   Tenant ID: {result.get('tenant_id')}")
    print(f"   Role IDs: {result.get('role_ids')}")
else:
    print(f"   ✗ Authentication failed")
