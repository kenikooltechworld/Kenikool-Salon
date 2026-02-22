"""Tests for audit logging."""

import pytest
from datetime import datetime, timedelta
from app.services.audit_service import AuditService
from app.models.audit_log import AuditLog


@pytest.fixture
def audit_service():
    """Create audit service."""
    return AuditService()


@pytest.fixture
def tenant_id():
    """Test tenant ID."""
    return "test_tenant_123"


class TestAuditLogging:
    """Test audit logging functionality."""

    @pytest.mark.asyncio
    async def test_log_event(self, audit_service, tenant_id):
        """Test logging an event."""
        log = await audit_service.log_event(
            event_type="POST",
            resource="/auth/login",
            user_id="user123",
            tenant_id=tenant_id,
            ip_address="192.168.1.1",
            status_code=200,
        )

        assert log is not None
        assert log.event_type == "POST"
        assert log.resource == "/auth/login"
        assert log.user_id == "user123"
        assert log.ip_address == "192.168.1.1"

    def test_get_audit_logs(self, audit_service, tenant_id):
        """Test retrieving audit logs."""
        logs = audit_service.get_audit_logs(tenant_id=tenant_id, limit=10)
        assert isinstance(logs, list)

    def test_get_audit_logs_by_user(self, audit_service, tenant_id):
        """Test retrieving audit logs by user."""
        logs = audit_service.get_audit_logs(
            tenant_id=tenant_id, user_id="user123", limit=10
        )
        assert isinstance(logs, list)

    def test_get_audit_logs_by_event_type(self, audit_service, tenant_id):
        """Test retrieving audit logs by event type."""
        logs = audit_service.get_audit_logs(
            tenant_id=tenant_id, event_type="POST", limit=10
        )
        assert isinstance(logs, list)

    def test_get_user_activity(self, audit_service, tenant_id):
        """Test retrieving user activity."""
        logs = audit_service.get_user_activity(
            tenant_id=tenant_id, user_id="user123", days=7
        )
        assert isinstance(logs, list)

    def test_get_suspicious_activity(self, audit_service, tenant_id):
        """Test retrieving suspicious activity."""
        logs = audit_service.get_suspicious_activity(tenant_id=tenant_id, days=7)
        assert isinstance(logs, list)

    def test_generate_compliance_report(self, audit_service, tenant_id):
        """Test generating compliance report."""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)

        report = audit_service.generate_compliance_report(
            tenant_id=tenant_id, start_date=start_date, end_date=end_date
        )

        assert isinstance(report, dict)
        assert "total_events" in report
        assert "events_by_type" in report
        assert "events_by_resource" in report
        assert "failed_operations" in report
        assert "unique_users" in report
        assert "unique_ips" in report

    def test_cleanup_old_logs(self, audit_service, tenant_id):
        """Test cleaning up old logs."""
        result = audit_service.cleanup_old_logs(tenant_id=tenant_id, days=90)
        assert isinstance(result, int)
