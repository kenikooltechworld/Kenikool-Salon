"""Simple unit tests for notification system."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
)
from app.services.notification_service import NotificationService
from app.context import set_tenant_id


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    test_id = ObjectId()
    set_tenant_id(str(test_id))
    return test_id


class TestNotificationService:
    """Test notification service."""

    def test_create_notification(self, tenant_id):
        """Test creating a notification."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Your appointment is confirmed",
            subject="Appointment Confirmation",
            recipient_email="customer@example.com",
        )

        assert notification is not None
        assert notification.recipient_id == "customer_123"
        assert notification.notification_type == "appointment_confirmation"
        assert notification.channel == "email"
        assert notification.status == "pending"
        assert notification.retry_count == 0

    def test_mark_notification_sent(self, tenant_id):
        """Test marking notification as sent."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Your appointment is confirmed",
            recipient_email="customer@example.com",
        )

        updated = NotificationService.mark_notification_sent(str(notification.id))
        assert updated.status == "sent"
        assert updated.sent_at is not None

    def test_mark_notification_delivered(self, tenant_id):
        """Test marking notification as delivered."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Your appointment is confirmed",
            recipient_email="customer@example.com",
        )

        updated = NotificationService.mark_notification_delivered(str(notification.id))
        assert updated.status == "delivered"
        assert updated.delivered_at is not None

    def test_mark_notification_failed(self, tenant_id):
        """Test marking notification as failed."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Your appointment is confirmed",
            recipient_email="customer@example.com",
        )

        updated = NotificationService.mark_notification_failed(
            str(notification.id), "Email service unavailable"
        )
        assert updated.status == "failed"
        assert updated.failed_at is not None
        assert updated.failure_reason == "Email service unavailable"

    def test_set_preference(self, tenant_id):
        """Test setting notification preference."""
        preference = NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_reminder_24h",
            channel="email",
            enabled=False,
        )

        assert preference.customer_id == "customer_123"
        assert preference.notification_type == "appointment_reminder_24h"
        assert preference.channel == "email"
        assert preference.enabled is False

    def test_is_notification_enabled(self, tenant_id):
        """Test checking if notification is enabled."""
        # Default should be enabled
        assert (
            NotificationService.is_notification_enabled(
                "customer_123", "appointment_confirmation", "email"
            )
            is True
        )

        # Set to disabled
        NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_confirmation",
            channel="email",
            enabled=False,
        )

        assert (
            NotificationService.is_notification_enabled(
                "customer_123", "appointment_confirmation", "email"
            )
            is False
        )

    def test_create_template(self, tenant_id):
        """Test creating a notification template."""
        template = NotificationService.create_template(
            template_type="appointment_confirmation",
            channel="email",
            subject="Appointment Confirmed",
            body="Your appointment with {{staff_name}} is confirmed for {{appointment_time}}",
            variables=["staff_name", "appointment_time"],
        )

        assert template.template_type == "appointment_confirmation"
        assert template.channel == "email"
        assert template.subject == "Appointment Confirmed"
        assert "{{staff_name}}" in template.body
        assert len(template.variables) == 2

    def test_get_template(self, tenant_id):
        """Test retrieving a template."""
        NotificationService.create_template(
            template_type="appointment_confirmation",
            channel="email",
            subject="Appointment Confirmed",
            body="Your appointment is confirmed",
            variables=["staff_name"],
        )

        template = NotificationService.get_template(
            template_type="appointment_confirmation", channel="email"
        )

        assert template is not None
        assert template.template_type == "appointment_confirmation"

    def test_get_notification_stats(self, tenant_id):
        """Test getting notification statistics."""
        # Create notifications with different statuses
        n1 = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )
        NotificationService.mark_notification_sent(str(n1.id))
        NotificationService.mark_notification_delivered(str(n1.id))

        n2 = NotificationService.create_notification(
            recipient_id="customer_456",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="other@example.com",
        )
        NotificationService.mark_notification_sent(str(n2.id))

        n3 = NotificationService.create_notification(
            recipient_id="customer_789",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="third@example.com",
        )
        NotificationService.mark_notification_failed(str(n3.id))

        stats = NotificationService.get_notification_stats()

        assert stats["total"] == 3
        assert stats["delivered"] == 1
        assert stats["sent"] == 1
        assert stats["failed"] == 1
        assert stats["pending"] == 0
