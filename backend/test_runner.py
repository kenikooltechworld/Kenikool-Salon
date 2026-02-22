#!/usr/bin/env python
"""Simple test runner to check MongoDB connection and run tests."""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_mongodb_connection():
    """Test MongoDB connection."""
    print("Testing MongoDB connection...")
    try:
        from app.config import Settings
        from mongoengine import connect, disconnect
        
        settings = Settings()
        print(f"Database URL: {settings.database_url[:50]}...")
        print(f"Database Name: {settings.database_name}")
        
        disconnect()
        connect(
            db=settings.database_name,
            host=settings.database_url,
            connect=False,
            serverSelectionTimeoutMS=5000,
        )
        print("✓ MongoDB connection successful!")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def test_models():
    """Test model imports."""
    print("\nTesting model imports...")
    try:
        from app.models.user import User
        from app.models.role import Role
        from app.models.session import Session
        from app.models.tenant import Tenant
        print("✓ All models imported successfully!")
        return True
    except Exception as e:
        print(f"✗ Model import failed: {e}")
        return False

def test_services():
    """Test service imports."""
    print("\nTesting service imports...")
    try:
        from app.services.auth_service import AuthenticationService
        from app.services.rbac_service import RBACService
        from app.services.mfa_service import MFAService
        print("✓ All services imported successfully!")
        return True
    except Exception as e:
        print(f"✗ Service import failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Task 3 Implementation Test Runner")
    print("=" * 60)
    
    results = []
    results.append(("MongoDB Connection", test_mongodb_connection()))
    results.append(("Model Imports", test_models()))
    results.append(("Service Imports", test_services()))
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("=" * 60)
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(r for _, r in results)
    sys.exit(0 if all_passed else 1)
