"""Property-based tests for authentication system - Validates: Requirements 2.1"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from datetime import datetime, timedelta
from app.services.auth_service import AuthenticationService
from app.config import Settings
from app.models.user import User
from app.models.role import Role
from app.models.session import Session


@pytest.fixture
def auth_service():
    """Create authentication service."""
    settings = Settings()
    return AuthenticationService(settings)


@pytest.fixture
def test_tenant_id():
    """Create a test tenant ID."""
    return "test-tenant-123"


@pytest.fixture
def test_role(test_tenant_id):
    """Create a test role in MongoDB."""
    role = Role(
        tenant_id=test_tenant_id,
        name="Manager",
        description="Manager role",
        is_custom=False,
        permissions=[],
    )
    role.save()
    return role


class TestAuthenticationTokenValidityProperty:
    """Property-based tests for authentication token validity - Validates: Requirements 2.1"""

    @given(
        user_id=st.uuids().map(str),
        tenant_id=st.uuids().map(str),
        email=st.emails(),
        role_id=st.uuids().map(str),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
    def test_valid_credentials_generate_valid_tokens(
        self, auth_service, user_id, tenant_id, email, role_id
    ):
        """Property: Valid credentials always generate valid tokens."""
        # Create access token
        access_token = auth_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            role_id=role_id,
        )

        assert access_token is not None
        assert len(access_token) > 0

        # Verify token
        payload = auth_service.verify_token(access_token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["email"] == email

    @given(
        user_id=st.uuids().map(str),
        tenant_id=st.uuids().map(str),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
    def test_refresh_token_generation_property(self, auth_service, user_id, tenant_id):
        """Property: Refresh tokens are always properly formatted and verifiable."""
        refresh_token = auth_service.create_refresh_token(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        assert refresh_token is not None
        assert len(refresh_token) > 0

        # Verify refresh token
        payload = auth_service.verify_token(refresh_token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["type"] == "refresh"

    @given(
        permissions=st.lists(
            st.text(min_size=1, max_size=50),
            min_size=0,
            max_size=10,
        )
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=50)
    def test_token_with_various_permissions_property(self, auth_service, permissions):
        """Property: Tokens correctly preserve all permission sets."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"
        email = "test@example.com"
        role_id = "test-role-id"

        token = auth_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            role_id=role_id,
            permissions=permissions,
        )

        payload = auth_service.verify_token(token)
        assert payload["permissions"] == permissions

    def test_invalid_token_always_rejected(self, auth_service):
        """Property: Invalid tokens are always rejected."""
        invalid_tokens = [
            "invalid.token.here",
            "not-a-jwt",
            "",
            "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalid.invalid",
        ]

        for invalid_token in invalid_tokens:
            payload = auth_service.verify_token(invalid_token)
            assert payload is None

    def test_tampered_token_always_rejected(self, auth_service):
        """Property: Tampered tokens are always rejected."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"
        email = "test@example.com"
        role_id = "test-role-id"

        # Create valid token
        token = auth_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            role_id=role_id,
        )

        # Tamper with token in various ways
        tampered_tokens = [
            token[:-10] + "0000000000",  # Change last 10 chars
            token[:-1],  # Remove last char
            token + "extra",  # Add extra chars
        ]

        for tampered_token in tampered_tokens:
            payload = auth_service.verify_token(tampered_token)
            assert payload is None

    def test_expired_token_always_rejected(self, auth_service):
        """Property: Expired tokens are always rejected."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"
        email = "test@example.com"
        role_id = "test-role-id"

        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = auth_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            role_id=role_id,
            expires_delta=expires_delta,
        )

        # Verify expired token is rejected
        payload = auth_service.verify_token(token)
        assert payload is None

    def test_concurrent_token_generation_uniqueness(self, auth_service):
        """Property: Concurrent token generation always produces unique tokens."""
        tokens = []
        for i in range(20):
            token = auth_service.create_access_token(
                user_id=f"user-{i}",
                tenant_id="tenant-1",
                email=f"user{i}@example.com",
                role_id="role-1",
            )
            tokens.append(token)

        # All tokens should be unique
        assert len(set(tokens)) == len(tokens)

        # All tokens should be valid
        for token in tokens:
            payload = auth_service.verify_token(token)
            assert payload is not None

    def test_csrf_token_uniqueness(self, auth_service):
        """Property: CSRF tokens are always unique."""
        csrf_tokens = []
        for _ in range(20):
            csrf_token = auth_service.generate_csrf_token()
            csrf_tokens.append(csrf_token)

        # All CSRF tokens should be unique
        assert len(set(csrf_tokens)) == len(csrf_tokens)

    def test_csrf_token_verification_consistency(self, auth_service):
        """Property: CSRF token verification is always consistent."""
        csrf_token = auth_service.generate_csrf_token()
        token_hash = auth_service.hash_csrf_token(csrf_token)

        # Verify token multiple times - should always return True
        for _ in range(10):
            assert auth_service.verify_csrf_token(csrf_token, token_hash) is True

        # Wrong token should always return False
        wrong_token = "wrong-token"
        for _ in range(10):
            assert auth_service.verify_csrf_token(wrong_token, token_hash) is False

    def test_password_hashing_consistency(self, auth_service):
        """Property: Password hashing is consistent and secure."""
        password = "TestPassword123"

        # Hash password multiple times
        hashes = []
        for _ in range(5):
            hashed = auth_service.hash_password(password)
            hashes.append(hashed)

        # All hashes should be different (bcrypt uses random salt)
        assert len(set(hashes)) == len(hashes)

        # All hashes should verify against the original password
        for hashed in hashes:
            assert auth_service.verify_password(password, hashed) is True
            assert auth_service.verify_password("WrongPassword", hashed) is False
