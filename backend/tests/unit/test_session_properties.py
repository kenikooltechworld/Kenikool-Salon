"""Property-based tests for session management with real MongoDB data - Validates: Requirements 2.7"""

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
    return "test-tenant-session"


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
def test_user(test_tenant_id, test_role):
    """Create a test user in MongoDB."""
    user = User(
        tenant_id=test_tenant_id,
        email="session-test@example.com",
        password_hash="hashed-password",
        first_name="Session",
        last_name="Test",
        phone="1234567890",
        role_ids=[test_role.id],  # Multiple roles per user
        status="active",
        mfa_enabled=False,
    )
    user.save()
    return user


class TestSessionManagementProperty:
    """Property-based tests for session management - Validates: Requirements 2.7"""

    def test_session_creation_always_succeeds(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Session creation always succeeds with valid data."""
        for i in range(10):
            session_data = auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )

            assert session_data is not None
            assert "session_id" in session_data
            assert "csrf_token" in session_data

    def test_session_invalidation_always_succeeds(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Session invalidation always succeeds for valid sessions."""
        # Create session
        session_data = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=test_tenant_id,
            token="test-token",
            refresh_token="test-refresh-token",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )

        session_id = session_data["session_id"]

        # Invalidate session
        result = auth_service.invalidate_session(session_id, test_tenant_id)
        assert result is True

        # Verify session is revoked
        session = Session.objects(id=session_id).first()
        assert session.status == "revoked"

    def test_concurrent_session_limit_enforcement(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Concurrent session limit is always enforced."""
        # Create 6 sessions
        for i in range(6):
            auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )

        # Enforce limit of 5
        auth_service.enforce_concurrent_session_limit(
            str(test_user.id), test_tenant_id, max_sessions=5
        )

        # Verify only 5 sessions are active
        active_sessions = Session.objects(
            tenant_id=test_tenant_id, user_id=test_user.id, status="active"
        )
        assert len(active_sessions) == 5

    def test_session_expiration_consistency(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Session expiration is always consistent."""
        # Create multiple sessions
        session_ids = []
        for i in range(5):
            session_data = auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )
            session_ids.append(session_data["session_id"])

        # Verify all sessions have expiration times
        for session_id in session_ids:
            session = Session.objects(id=session_id).first()
            assert session.expires_at is not None
            assert session.expires_at > datetime.utcnow()

    def test_session_invalidation_idempotency(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Session invalidation is idempotent."""
        # Create session
        session_data = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=test_tenant_id,
            token="test-token",
            refresh_token="test-refresh-token",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )

        session_id = session_data["session_id"]

        # Invalidate session multiple times
        for _ in range(3):
            result = auth_service.invalidate_session(session_id, test_tenant_id)
            assert result is True

        # Verify session is still revoked
        session = Session.objects(id=session_id).first()
        assert session.status == "revoked"

    def test_user_session_isolation(
        self, auth_service, test_tenant_id, test_role
    ):
        """Property: Sessions are always isolated between users."""
        # Create two users
        user1 = User(
            tenant_id=test_tenant_id,
            email="user1-session@example.com",
            password_hash="hashed-password",
            first_name="User",
            last_name="One",
            phone="1111111111",
            role_ids=[test_role.id],  # Multiple roles per user
            status="active",
            mfa_enabled=False,
        )
        user1.save()

        user2 = User(
            tenant_id=test_tenant_id,
            email="user2-session@example.com",
            password_hash="hashed-password",
            first_name="User",
            last_name="Two",
            phone="2222222222",
            role_ids=[test_role.id],  # Multiple roles per user
            status="active",
            mfa_enabled=False,
        )
        user2.save()

        # Create sessions for both users
        session1_data = auth_service.create_session(
            user_id=str(user1.id),
            tenant_id=test_tenant_id,
            token="token-1",
            refresh_token="refresh-1",
            ip_address="127.0.0.1",
            user_agent="agent-1",
        )

        session2_data = auth_service.create_session(
            user_id=str(user2.id),
            tenant_id=test_tenant_id,
            token="token-2",
            refresh_token="refresh-2",
            ip_address="127.0.0.1",
            user_agent="agent-2",
        )

        # Invalidate user1's session
        auth_service.invalidate_session(session1_data["session_id"], test_tenant_id)

        # Verify user2's session is still active
        session2 = Session.objects(id=session2_data["session_id"]).first()
        assert session2.status == "active"

    def test_invalidate_all_user_sessions_completeness(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Invalidating all user sessions always invalidates all sessions."""
        # Create 5 sessions
        session_ids = []
        for i in range(5):
            session_data = auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )
            session_ids.append(session_data["session_id"])

        # Invalidate all sessions
        result = auth_service.invalidate_user_sessions(str(test_user.id), test_tenant_id)
        assert result is True

        # Verify all sessions are revoked
        for session_id in session_ids:
            session = Session.objects(id=session_id).first()
            assert session.status == "revoked"

    def test_get_active_sessions_accuracy(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Get active sessions always returns accurate count."""
        # Create 3 sessions
        for i in range(3):
            auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=test_tenant_id,
                token=f"test-token-{i}",
                refresh_token=f"test-refresh-token-{i}",
                ip_address="127.0.0.1",
                user_agent="test-agent",
            )

        # Get active sessions
        sessions = auth_service.get_active_sessions(str(test_user.id), test_tenant_id)
        assert len(sessions) == 3

        # Invalidate one session
        auth_service.invalidate_session(str(sessions[0].id), test_tenant_id)

        # Get active sessions again
        sessions = auth_service.get_active_sessions(str(test_user.id), test_tenant_id)
        assert len(sessions) == 2

    def test_session_data_integrity(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: Session data is always stored and retrieved correctly."""
        ip_address = "192.168.1.100"
        user_agent = "Mozilla/5.0"

        session_data = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=test_tenant_id,
            token="test-token",
            refresh_token="test-refresh-token",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        # Retrieve session
        session = Session.objects(id=session_data["session_id"]).first()

        # Verify all data is correct
        assert session.user_id == test_user.id
        assert session.ip_address == ip_address
        assert session.user_agent == user_agent
        assert session.status == "active"
        assert session.token == "test-token"
        assert session.refresh_token == "test-refresh-token"

    def test_csrf_token_in_session(
        self, auth_service, test_user, test_tenant_id
    ):
        """Property: CSRF token is always generated and stored in session."""
        session_data = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=test_tenant_id,
            token="test-token",
            refresh_token="test-refresh-token",
            ip_address="127.0.0.1",
            user_agent="test-agent",
        )

        # Verify CSRF token is returned
        assert "csrf_token" in session_data
        csrf_token = session_data["csrf_token"]
        assert len(csrf_token) > 0

        # Verify CSRF token hash is stored in session
        session = Session.objects(id=session_data["session_id"]).first()
        assert session.csrf_token_hash is not None

        # Verify CSRF token can be verified
        assert auth_service.verify_csrf_token(csrf_token, session.csrf_token_hash) is True
