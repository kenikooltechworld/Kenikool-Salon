#!/usr/bin/env python
"""Test login endpoint directly with detailed error logging."""

import sys
import os
from dotenv import load_dotenv
import json
import logging
import traceback

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG)

load_dotenv()
sys.path.insert(0, os.path.dirname(__file__))

try:
    print("=" * 60)
    print("STEP 1: Initializing database...")
    print("=" * 60)
    from app.db import init_db
    init_db()
    print("✓ Database initialized")
    
    print("\n" + "=" * 60)
    print("STEP 2: Loading models and services...")
    print("=" * 60)
    from app.models.user import User
    from app.services.auth_service import AuthenticationService
    from app.config import Settings
    print("✓ Models and services loaded")
    
    print("\n" + "=" * 60)
    print("STEP 3: Creating FastAPI app...")
    print("=" * 60)
    from fastapi.testclient import TestClient
    from app.main import create_app
    app = create_app()
    client = TestClient(app)
    print("✓ FastAPI app created")
    
    print("\n" + "=" * 60)
    print("STEP 4: Getting test user...")
    print("=" * 60)
    settings = Settings()
    auth_service = AuthenticationService(settings)
    
    user = User.objects.first()
    if not user:
        print("✗ No users found in database")
        sys.exit(1)
    print(f"✓ Found user: {user.email}")
    
    print("\n" + "=" * 60)
    print("STEP 5: Setting test password...")
    print("=" * 60)
    test_password = "TestPassword123!"
    hashed = auth_service.hash_password(test_password)
    user.password_hash = hashed
    user.save()
    print(f"✓ Password set to: {test_password}")
    
    print("\n" + "=" * 60)
    print("STEP 6: Testing login endpoint...")
    print("=" * 60)
    print(f"Endpoint: POST /api/v1/auth/login")
    print(f"Payload: {{'email': '{user.email}', 'password': '***', 'remember_me': False}}")
    
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": user.email,
            "password": test_password,
            "remember_me": False,
        }
    )
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body:\n{response.text}")
    
    if response.status_code == 200:
        print("\n✓ Login successful!")
        data = response.json()
        print(f"CSRF Token: {data.get('csrf_token', 'N/A')[:20]}...")
        
        print(f"\nCookies set:")
        for cookie_name in ['access_token', 'refresh_token', 'session_id', 'tenant_id', 'user_id']:
            if cookie_name in response.cookies:
                print(f"  ✓ {cookie_name}")
            else:
                print(f"  ✗ {cookie_name} (missing)")
    else:
        print(f"\n✗ Login failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error Response: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw Response: {response.text}")

except Exception as e:
    print(f"\n✗ ERROR: {str(e)}")
    print("\nFull Traceback:")
    traceback.print_exc()
    sys.exit(1)
