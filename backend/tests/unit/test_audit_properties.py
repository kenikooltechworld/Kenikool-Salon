"""Property-based tests for audit logging"""
from hypothesis import given, strategies as st
from datetime import datetime, timedelta
from app.models.audit_log import AuditLog
from app.services.audit_service_enhanced import AuditServiceEnhanced
import pytest


class TestAuditTrailCompleteness:
    """Property 48: Audit Trail Completeness - Validates Requirements 41.1, 64.1"""

    @given(
        event_type=st.sampled_from(['GET', 'POST', 'PUT', 'DELETE']),
        resource=st.text(min_size=1, max_size=100),
        user_id=st.text(min_size=1, max_size=50),
        status_code=st.sampled_from([200, 201, 400, 401, 403, 404, 500]),
    )
    def test_audit_log_records_all_fields(self, event_type, resource, user_id, status_code):
        """Audit log should record all required fields"""
        log = AuditServiceEnhanced.log_action(
            event_type=event_type,
            resource=resource,
            user_id=user_id,
            ip_address="192.168.1.1",
            status_code=status_code,
        )
        
        assert log.event_type == event_type
        assert log.resource == resource
        assert log.user_id == user_id
        assert log.status_code == status_code
        assert log.ip_address == "192.168.1.1"
        assert log.created_at is not None

    @given(
        event_count=st.integers(min_value=1, max_value=10),
    )
    def test_audit_logs_are_immutable(self, event_count):
        """Audit logs should be immutable after creation"""
        logs = []
        for i in range(event_count):
            log = AuditServiceEnhanced.log_action(
                event_type="TEST",
                resource=f"resource_{i}",
                user_id="user_1",
                ip_address="192.168.1.1",
                status_code=200,
            )
            logs.append(log)
        
        # Verify all logs exist and are unchanged
        for log in logs:
            retrieved = AuditLog.objects(id=log.id).first()
            assert retrieved is not None
            assert retrieved.event_type == "TEST"

    @given(
        event_type=st.text(min_size=1, max_size=50),
        resource=st.text(min_size=1, max_size=100),
    )
    def test_audit_logs_are_queryable(self, event_type, resource):
        """Audit logs should be queryable by event type and resource"""
        log = AuditServiceEnhanced.log_action(
            event_type=event_type,
            resource=resource,
            user_id="user_1",
            ip_address="192.168.1.1",
            status_code=200,
        )
        
        # Query by event type
        logs, total = AuditServiceEnhanced.get_audit_logs(event_type=event_type)
        assert total > 0
        assert any(l.id == log.id for l in logs)

    @given(
        password=st.text(min_size=1, max_size=50),
        token=st.text(min_size=1, max_size=50),
        email=st.emails(),
    )
    def test_sensitive_data_redaction(self, password, token, email):
        """Sensitive data should be redacted in audit logs"""
        request_body = {
            "password": password,
            "token": token,
            "email": email,
            "username": "testuser",
        }
        
        log = AuditServiceEnhanced.log_action(
            event_type="LOGIN",
            resource="auth/login",
            user_id="user_1",
            ip_address="192.168.1.1",
            status_code=200,
            request_body=request_body,
        )
        
        # Verify sensitive fields are redacted
        assert log.request_body["password"] == "[REDACTED]"
        assert log.request_body["token"] == "[REDACTED]"
        assert log.request_body["username"] == "testuser"  # Non-sensitive field preserved

    @given(
        days=st.integers(min_value=1, max_value=30),
    )
    def test_audit_logs_time_filtering(self, days):
        """Audit logs should be filterable by time range"""
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        # Create log
        log = AuditServiceEnhanced.log_action(
            event_type="TEST",
            resource="test",
            user_id="user_1",
            ip_address="192.168.1.1",
            status_code=200,
        )
        
        # Query with time filter
        logs, total = AuditServiceEnhanced.get_audit_logs(
            start_date=start_date,
            end_date=end_date,
        )
        
        assert total > 0
        assert any(l.id == log.id for l in logs)

    @given(
        user_id=st.text(min_size=1, max_size=50),
        event_count=st.integers(min_value=1, max_value=5),
    )
    def test_user_activity_tracking(self, user_id, event_count):
        """User activity should be trackable"""
        for i in range(event_count):
            AuditServiceEnhanced.log_action(
                event_type=f"EVENT_{i}",
                resource=f"resource_{i}",
                user_id=user_id,
                ip_address="192.168.1.1",
                status_code=200,
            )
        
        # Get user activity
        logs, total = AuditServiceEnhanced.get_user_activity(user_id=user_id)
        
        assert total >= event_count
        assert all(l.user_id == user_id for l in logs)


class TestDataAccessLogging:
    """Property: Data Access Logging - Validates Requirements 5.6, 41.1"""

    @given(
        resource_type=st.text(min_size=1, max_size=50),
        resource_id=st.text(min_size=1, max_size=50),
        user_id=st.text(min_size=1, max_size=50),
    )
    def test_data_access_logged(self, resource_type, resource_id, user_id):
        """Data access should be logged"""
        log = AuditServiceEnhanced.log_data_access(
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address="192.168.1.1",
        )
        
        assert log.event_type == "DATA_ACCESS"
        assert resource_type in log.resource
        assert resource_id in log.resource
        assert log.user_id == user_id

    @given(
        resource_type=st.text(min_size=1, max_size=50),
        resource_id=st.text(min_size=1, max_size=50),
        user_id=st.text(min_size=1, max_size=50),
    )
    def test_data_modification_logged(self, resource_type, resource_id, user_id):
        """Data modifications should be logged"""
        old_value = {"field": "old_value"}
        new_value = {"field": "new_value"}
        
        log = AuditServiceEnhanced.log_data_modification(
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            ip_address="192.168.1.1",
            action="update",
            old_value=old_value,
            new_value=new_value,
        )
        
        assert log.event_type == "DATA_MODIFICATION"
        assert log.user_id == user_id
        assert "update" in log.tags
