#!/usr/bin/env python
"""Quick test to verify Task 3 implementation."""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Test imports
try:
    from app.services.auth_service import AuthenticationService
    from app.services.rbac_service import RBACService
    from app.services.mfa_service import MFAService
    from app.models.user import User
    from app.models.role import Role
    from app.models.session import Session
    from app.models.tenant import Tenant
    from app.config import Settings
    
    print("✓ All imports successful")
    
    # Test service instantiation
    settings = Settings()
    auth_service = AuthenticationService(settings)
    rbac_service = RBACService()
    mfa_service = MFAService()
    
    print("✓ All services instantiated successfully")
    
    # Test basic functionality
    password = "TestPassword123"
    hashed = auth_service.hash_password(password)
    verified = auth_service.verify_password(password, hashed)
    
    assert verified, "Password verification failed"
    print("✓ Password hashing and verification working")
    
    # Test token generation
    token = auth_service.create_access_token(
        user_id="test-user",
        tenant_id="test-tenant",
        email="test@example.com",
        role_id="test-role"
    )
    
    assert token, "Token generation failed"
    print("✓ Token generation working")
    
    # Test token verification
    payload = auth_service.verify_token(token)
    assert payload, "Token verification failed"
    assert payload["sub"] == "test-user"
    print("✓ Token verification working")
    
    # Test MFA
    secret = mfa_service.generate_totp_secret()
    assert secret, "TOTP secret generation failed"
    print("✓ TOTP secret generation working")
    
    # Test backup codes
    backup_codes = mfa_service.generate_backup_codes(10)
    assert len(backup_codes) == 10, "Backup code generation failed"
    print("✓ Backup code generation working")
    
    print("\n✅ All quick tests passed!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
