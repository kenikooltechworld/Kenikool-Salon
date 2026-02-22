"""Unit tests for authentication system with real MongoDB data."""

import pytest
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


@pytest.fixture
def test_user(test_tenant_id, test_role, auth_service):
    """Create a test user in MongoDB."""
    password = "TestPassword123"
    hashed_password = auth_service.hash_password(password)

    user = User(
        tenant_id=test_tenant_id,
        email="test@example.com",
        password_hash=hashed_password,
        first_name="Test",
        last_name="User",
        phone="1234567890",
        role_ids=[test_role.id],  # Multiple roles per user
        status="active",
        mfa_enabled=False,
    )
    user.save()
    return user, password


class TestAuthenticationWithRealMongoDB:
    """Test authentication with real MongoDB data."""

    def test_user_creation_in_mongodb(self, test_user, test_tenant_id):
        """Test that user is created in MongoDB."""
        user, _ = test_user
        
        # Verify user exists in database
        db_user = User.objects(id=user.id, tenant_id=test_tenant_id).first()
        assert db_user is not None
        assert db_user.email == "test@example.com"
        assert db_user.first_name == "Test"

    def test_password_hashing_and_verification(self, auth_service):
        """Test password hashing and verification."""
        password = "MySecurePass123"
        
        # Hash password
        hashed = auth_service.hash_password(password)
        assert hashed != password
        assert len(hashed) > 0

        # Verify correct password
        assert auth_service.verify_password(password, hashed) is True

        # Verify incorrect password
        wrong_password = "WrongPassword123"
        assert auth_service.verify_password(wrong_password, hashed) is False

    def test_authenticate_user_with_valid_credentials(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test user authentication with valid credentials."""
        user, password = test_user

        # Authenticate user
        user_data = auth_service.authenticate_user(
            user.email, password, test_tenant_id
        )

        assert user_data is not None
        assert user_data["email"] == user.email
        assert user_data["user_id"] == str(user.id)
        assert user_data["mfa_enabled"] is False

    def test_authenticate_user_with_invalid_password(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test user authentication with invalid password."""
        user, _ = test_user

        # Authenticate with wrong password
        user_data = auth_service.authenticate_user(
            user.email, "WrongPassword", test_tenant_id
        )

        assert user_data is None

    def test_authenticate_user_with_invalid_email(
        self, auth_service, test_tenant_id
    ):
        """Test user authentication with invalid email."""
        user_data = auth_service.authenticate_user(
            "nonexistent@example.com", "password", test_tenant_id
        )

        assert user_data is None

    def test_authenticate_inactive_user(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test that inactive users cannot authenticate."""
        user, password = test_user

        # Deactivate user
        user.status = "inactive"
        user.save()

        # Try to authenticate
        user_data = auth_service.authenticate_user(
            user.email, password, test_tenant_id
        )

        assert user_data is None

    def test_access_token_generation(self, auth_service):
        """Test access token generation."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"
        email = "test@example.com"
        role_id = "test-role-id"

        token = auth_service.create_access_token(
            user_id=user_id,
            tenant_id=tenant_id,
            email=email,
            role_id=role_id,
        )

        assert token is not None
        assert len(token) > 0

        # Verify token
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["email"] == email

    def test_refresh_token_generation(self, auth_service):
        """Test refresh token generation."""
        user_id = "test-user-id"
        tenant_id = "test-tenant-id"

        token = auth_service.create_refresh_token(
            user_id=user_id,
            tenant_id=tenant_id,
        )

        assert token is not None
        assert len(token) > 0

        # Verify token
        payload = auth_service.verify_token(token)
        assert payload is not None
        assert payload["sub"] == user_id
        assert payload["tenant_id"] == tenant_id
        assert payload["type"] == "refresh"

    def test_session_creation_in_mongodb(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test session creation in MongoDB."""
        user, _ = test_user

        # Create session
        session_data = auth_service.create_session(
            user_id=str(user.id),
            tenant_id=test_tenant_id,
            token="test-token",
            refresh_token="test-refresh-token",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )

        assert session_data is not None
        assert "session_id" in session_data
        assert "csrf_token" in session_data

        # Verify session exists in database
        session = Session.objects(id=session_data["session_id"]).first()
        assert session is not None
        assert session.user_id == user.id
        assert session.status == "active"

    def test_csrf_token_generation_and_verification(self, auth_service):
        """Test CSRF token generation and verification."""
        # Generate CSRF token
        csrf_token = auth_service.generate_csrf_token()
        assert csrf_token is not None
        assert len(csrf_token) > 0

        # Hash token
        token_hash = auth_service.hash_csrf_token(csrf_token)
        assert token_hash is not None
        assert token_hash != csrf_token

        # Verify token
        assert auth_service.verify_csrf_token(csrf_token, token_hash) is True

        # Verify wrong token fails
        wrong_token = "wrong-token"
        assert auth_service.verify_csrf_token(wrong_token, token_hash) is False

    def test_session_invalidation(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test session invalidation."""
        user, _ = test_user

        # Create session
        session_data = auth_service.create_session(
            user_id=str(user.id),
            tenant_id=test_tenant_id,
            token="test-token",
            refresh_token="test-refresh-token",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )

        session_id = session_data["session_id"]

        # Verify session is active
        session = Session.objects(id=session_id).first()
        assert session.status == "active"

        # Invalidate session
        result = auth_service.invalidate_session(session_id, test_tenant_id)
        assert result is True

        # Verify session is revoked
        session = Session.objects(id=session_id).first()
        assert session.status == "revoked"

    def test_concurrent_session_limit(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test concurrent session limit enforcement."""
        user, _ = test_user

        # Create 5 sessions
        session_ids = []
        for i in range(5):
            session_data = auth_service.create_session(
                user_id=str(user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )
            session_ids.append(session_data["session_id"])

        # Verify all 5 sessions are active
        active_sessions = Session.objects(
            tenant_id=test_tenant_id, user_id=user.id, status="active"
        )
        assert len(active_sessions) == 5

        # Create 6th session - should invalidate oldest
        session_data = auth_service.create_session(
            user_id=str(user.id),
            tenant_id=test_tenant_id,
            token="test-token-6",
            refresh_token="test-refresh-token-6",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )

        # Enforce limit
        auth_service.enforce_concurrent_session_limit(
            str(user.id), test_tenant_id, max_sessions=5
        )

        # Verify oldest session is revoked
        oldest_session = Session.objects(id=session_ids[0]).first()
        assert oldest_session.status == "revoked"

    def test_invalidate_all_user_sessions(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test invalidating all sessions for a user."""
        user, _ = test_user

        # Create 3 sessions
        for i in range(3):
            auth_service.create_session(
                user_id=str(user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )

        # Verify all sessions are active
        active_sessions = Session.objects(
            tenant_id=test_tenant_id, user_id=user.id, status="active"
        )
        assert len(active_sessions) == 3

        # Invalidate all sessions
        result = auth_service.invalidate_user_sessions(str(user.id), test_tenant_id)
        assert result is True

        # Verify all sessions are revoked
        active_sessions = Session.objects(
            tenant_id=test_tenant_id, user_id=user.id, status="active"
        )
        assert len(active_sessions) == 0

    def test_get_active_sessions(
        self, auth_service, test_user, test_tenant_id
    ):
        """Test retrieving active sessions."""
        user, _ = test_user

        # Create 2 sessions
        for i in range(2):
            auth_service.create_session(
                user_id=str(user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )

        # Get active sessions
        sessions = auth_service.get_active_sessions(str(user.id), test_tenant_id)
        assert len(sessions) == 2

        # Invalidate one session
        auth_service.invalidate_session(str(sessions[0].id), test_tenant_id)

        # Get active sessions again
        sessions = auth_service.get_active_sessions(str(user.id), test_tenant_id)
        assert len(sessions) == 1

    def test_token_expiration(self, auth_service):
        """Test that expired tokens are rejected."""
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

    def test_tampered_token_rejected(self, auth_service):
        """Test that tampered tokens are rejected."""
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

        # Tamper with token
        tampered_token = token[:-10] + "0000000000"

        # Verify tampered token is rejected
        payload = auth_service.verify_token(tampered_token)
        assert payload is None
