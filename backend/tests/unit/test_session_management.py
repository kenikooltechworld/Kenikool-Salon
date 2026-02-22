"""Property-based tests for session management."""

import pytest
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from app.services.auth_service import AuthenticationService
from app.models.session import Session
from app.models.user import User
from app.models.tenant import Tenant
from app.config import Settings


class TestSessionManagement:
    """Test session management functionality."""

    @pytest.fixture
    def auth_service(self):
        """Create authentication service."""
        settings = Settings()
        return AuthenticationService(settings)

    @pytest.fixture
    def test_tenant(self):
        """Create test tenant."""
        tenant = Tenant(
            name="Test Tenant",
            subscription_tier="starter",
            status="active",
        )
        tenant.save()
        return tenant

    @pytest.fixture
    def test_user(self, test_tenant):
        """Create test user."""
        from app.models.role import Role
        
        role = Role(
            tenant_id=test_tenant.id,
            name="Test Role",
        )
        role.save()

        user = User(
            tenant_id=test_tenant.id,
            email="test@example.com",
            password_hash="hashed_password",
            first_name="Test",
            last_name="User",
            role_ids=[role.id],  # Multiple roles per user
        )
        user.save()
        return user

    def test_session_creation(self, auth_service, test_tenant, test_user):
        """Test session creation."""
        token = "test_token"
        refresh_token = "test_refresh_token"
        ip_address = "192.168.1.1"
        user_agent = "Mozilla/5.0"

        session = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            token=token,
            refresh_token=refresh_token,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        assert session is not None
        assert session.user_id == test_user.id
        assert session.token == token
        assert session.refresh_token == refresh_token
        assert session.ip_address == ip_address
        assert session.user_agent == user_agent
        assert session.status == "active"

    def test_session_invalidation(self, auth_service, test_tenant, test_user):
        """Test session invalidation."""
        # Create session
        session = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            token="test_token",
            refresh_token="test_refresh_token",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        # Invalidate session
        success = auth_service.invalidate_session(
            session_id=str(session.id),
            tenant_id=str(test_tenant.id),
        )

        assert success is True

        # Verify session is revoked
        updated_session = Session.objects(id=session.id).first()
        assert updated_session.status == "revoked"

    def test_session_expiration(self, auth_service, test_tenant, test_user):
        """Test session expiration."""
        # Create session
        session = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            token="test_token",
            refresh_token="test_refresh_token",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        # Verify session has expiration time
        assert session.expires_at is not None
        assert session.expires_at > datetime.utcnow()

    def test_concurrent_session_limit_enforcement(self, auth_service, test_tenant, test_user):
        """Test concurrent session limit enforcement."""
        # Create 5 sessions
        sessions = []
        for i in range(5):
            session = auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=str(test_tenant.id),
                token=f"token_{i}",
                refresh_token=f"refresh_token_{i}",
                ip_address=f"192.168.1.{i}",
                user_agent=f"Mozilla/5.0 {i}",
            )
            sessions.append(session)

        # All sessions should be active
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )
        assert len(active_sessions) == 5

        # Enforce limit (should invalidate oldest)
        auth_service.enforce_concurrent_session_limit(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            max_sessions=5,
        )

        # Create 6th session
        session6 = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            token="token_6",
            refresh_token="refresh_token_6",
            ip_address="192.168.1.6",
            user_agent="Mozilla/5.0 6",
        )

        # Enforce limit again
        auth_service.enforce_concurrent_session_limit(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            max_sessions=5,
        )

        # Should still have 5 active sessions
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )
        assert len(active_sessions) == 5

    def test_invalidate_all_user_sessions(self, auth_service, test_tenant, test_user):
        """Test invalidating all sessions for a user."""
        # Create multiple sessions
        for i in range(3):
            auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=str(test_tenant.id),
                token=f"token_{i}",
                refresh_token=f"refresh_token_{i}",
                ip_address=f"192.168.1.{i}",
                user_agent=f"Mozilla/5.0 {i}",
            )

        # Verify all sessions are active
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )
        assert len(active_sessions) == 3

        # Invalidate all sessions
        success = auth_service.invalidate_user_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )

        assert success is True

        # Verify all sessions are revoked
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )
        assert len(active_sessions) == 0

    def test_get_active_sessions(self, auth_service, test_tenant, test_user):
        """Test retrieving active sessions."""
        # Create sessions
        for i in range(3):
            auth_service.create_session(
                user_id=str(test_user.id),
                tenant_id=str(test_tenant.id),
                token=f"token_{i}",
                refresh_token=f"refresh_token_{i}",
                ip_address=f"192.168.1.{i}",
                user_agent=f"Mozilla/5.0 {i}",
            )

        # Get active sessions
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )

        assert len(active_sessions) == 3
        assert all(s.status == "active" for s in active_sessions)

    @given(
        ip_address=st.ip_addresses().map(str),
        user_agent=st.text(min_size=1, max_size=200),
    )
    def test_session_with_various_metadata(self, auth_service, test_tenant, test_user, ip_address, user_agent):
        """Test session creation with various metadata."""
        session = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            token="test_token",
            refresh_token="test_refresh_token",
            ip_address=ip_address,
            user_agent=user_agent,
        )

        assert session is not None
        assert session.ip_address == ip_address
        assert session.user_agent == user_agent

    def test_session_state_consistency(self, auth_service, test_tenant, test_user):
        """Test that session state is consistent across operations."""
        # Create session
        session = auth_service.create_session(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
            token="test_token",
            refresh_token="test_refresh_token",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
        )

        session_id = str(session.id)

        # Verify session is active
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )
        assert any(str(s.id) == session_id for s in active_sessions)

        # Invalidate session
        auth_service.invalidate_session(
            session_id=session_id,
            tenant_id=str(test_tenant.id),
        )

        # Verify session is no longer active
        active_sessions = auth_service.get_active_sessions(
            user_id=str(test_user.id),
            tenant_id=str(test_tenant.id),
        )
        assert not any(str(s.id) == session_id for s in active_sessions)
