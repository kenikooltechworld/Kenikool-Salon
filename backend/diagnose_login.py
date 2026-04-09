#!/usr/bin/env python
"""Diagnose login endpoint issues."""

import sys
import os
from dotenv import load_dotenv

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

print("=" * 70)
print("LOGIN ENDPOINT DIAGNOSTIC")
print("=" * 70)

# Step 1: Check imports
print("\n[1/5] Checking imports...")
try:
    from app.db import init_db
    from app.models.user import User
    from app.services.auth_service import AuthenticationService
    from app.config import Settings
    from fastapi.testclient import TestClient
    from app.main import create_app
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)

# Step 2: Initialize database
print("\n[2/5] Initializing database...")
try:
    init_db()
    print("✓ Database initialized")
except Exception as e:
    print(f"✗ Database initialization failed: {e}")
    sys.exit(1)

# Step 3: Create app and client
print("\n[3/5] Creating FastAPI app...")
try:
    app = create_app()
    client = TestClient(app)
    print("✓ FastAPI app created")
except Exception as e:
    print(f"✗ App creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 4: Get test user
print("\n[4/5] Getting test user...")
try:
    settings = Settings()
    auth_service = AuthenticationService(settings)
    
    user = User.objects.first()
    if not user:
        print("✗ No users found - creating test user...")
        from app.models.tenant import Tenant
        from app.models.role import Role
        
        tenant = Tenant(
            name="Test Tenant",
            subdomain="test",
            subscription_tier="starter",
            status="active",
        )
        tenant.save()
        
        role = Role(
            tenant_id=tenant.id,
            name="Admin",
        )
        role.save()
        
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)
        
        user = User(
            tenant_id=tenant.id,
            email="test@example.com",
            password_hash=hashed,
            first_name="Test",
            last_name="User",
            role_ids=[role.id],
            status="active",
        )
        user.save()
        print(f"✓ Test user created: {user.email}")
    else:
        # Update password
        password = "TestPassword123!"
        hashed = auth_service.hash_password(password)
        user.password_hash = hashed
        user.save()
        print(f"✓ Test user found: {user.email}")
        print(f"  Password set to: {password}")
except Exception as e:
    print(f"✗ User setup failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Step 5: Test login endpoint
print("\n[5/5] Testing login endpoint...")
print(f"  Email: {user.email}")
print(f"  Password: TestPassword123!")

try:
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": "TestPassword123!",
            "remember_me": False,
        }
    )
    
    print(f"\n  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✓ Login successful!")
        data = response.json()
        print(f"  Response: {data}")
        print(f"\n  Cookies set:")
        for cookie_name in ['access_token', 'refresh_token', 'session_id', 'tenant_id', 'user_id']:
            if cookie_name in response.cookies:
                print(f"    ✓ {cookie_name}")
            else:
                print(f"    ✗ {cookie_name} (missing)")
    else:
        print(f"✗ Login failed with status {response.status_code}")
        print(f"  Response: {response.text}")
        
except Exception as e:
    print(f"✗ Login test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("DIAGNOSTIC COMPLETE")
print("=" * 70)
