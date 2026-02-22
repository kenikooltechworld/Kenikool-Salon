"""Unit tests for notification system."""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.models.notification import (
    Notification,
    NotificationTemplate,
    NotificationPreference,
    NotificationLog,
)
from app.services.notification_service import NotificationService
from app.context import set_tenant_id


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    test_id = ObjectId()
    set_tenant_id(str(test_id))
    return test_id


class TestNotificationCreation:
    """Test notification creation."""

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

    def test_create_notification_with_template_variables(self, setup_db, tenant_id):
        """Test creating notification with template variables."""
        variables = {"customer_name": "John", "appointment_time": "2024-01-15 10:00"}
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_reminder_24h",
            channel="sms",
            content="Reminder: Your appointment is tomorrow",
            template_variables=variables,
            recipient_phone="+234123456789",
        )

        assert notification.template_variables == variables
        assert notification.channel == "sms"

    def test_create_notification_with_appointment_id(self, setup_db, tenant_id):
        """Test creating notification linked to appointment."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            appointment_id="appointment_456",
            recipient_email="customer@example.com",
        )

        assert notification.appointment_id == "appointment_456"


class TestNotificationRetrieval:
    """Test notification retrieval."""

    def test_get_notification(self, setup_db, tenant_id):
        """Test retrieving a notification."""
        created = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        retrieved = NotificationService.get_notification(str(created.id))
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.recipient_id == "customer_123"

    def test_get_notifications_with_filtering(self, setup_db, tenant_id):
        """Test retrieving notifications with filters."""
        # Create multiple notifications
        NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )
        NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_reminder_24h",
            channel="sms",
            content="Reminder",
            recipient_phone="+234123456789",
        )
        NotificationService.create_notification(
            recipient_id="customer_456",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="other@example.com",
        )

        # Test filtering by recipient
        notifications = NotificationService.get_notifications(
            recipient_id="customer_123"
        )
        assert len(notifications) == 2

        # Test filtering by type
        notifications = NotificationService.get_notifications(
            notification_type="appointment_confirmation"
        )
        assert len(notifications) == 2

        # Test filtering by channel
        notifications = NotificationService.get_notifications(channel="email")
        assert len(notifications) == 2

    def test_get_pending_notifications(self, setup_db, tenant_id):
        """Test retrieving pending notifications."""
        NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )
        NotificationService.create_notification(
            recipient_id="customer_456",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="other@example.com",
        )

        pending = NotificationService.get_pending_notifications()
        assert len(pending) == 2
        assert all(n.status == "pending" for n in pending)


class TestNotificationStatusTracking:
    """Test notification status tracking."""

    def test_mark_notification_sent(self, setup_db, tenant_id):
        """Test marking notification as sent."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        updated = NotificationService.mark_notification_sent(str(notification.id))
        assert updated.status == "sent"
        assert updated.sent_at is not None

    def test_mark_notification_delivered(self, setup_db, tenant_id):
        """Test marking notification as delivered."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        updated = NotificationService.mark_notification_delivered(str(notification.id))
        assert updated.status == "delivered"
        assert updated.delivered_at is not None

    def test_mark_notification_failed(self, setup_db, tenant_id):
        """Test marking notification as failed."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        updated = NotificationService.mark_notification_failed(
            str(notification.id), "Email service unavailable"
        )
        assert updated.status == "failed"
        assert updated.failed_at is not None
        assert updated.failure_reason == "Email service unavailable"

    def test_should_retry_notification(self, setup_db, tenant_id):
        """Test checking if notification should be retried."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        # Mark as failed
        NotificationService.mark_notification_failed(str(notification.id))
        notification = NotificationService.get_notification(str(notification.id))

        # Should retry (retry_count < max_retries)
        assert notification.should_retry() is True

        # Increment retry count to max
        notification.retry_count = 3
        notification.save()
        assert notification.should_retry() is False

    def test_increment_retry_count(self, setup_db, tenant_id):
        """Test incrementing retry count."""
        notification = NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        assert notification.retry_count == 0
        notification.increment_retry()
        notification = NotificationService.get_notification(str(notification.id))
        assert notification.retry_count == 1


class TestNotificationPreferences:
    """Test notification preferences."""

    def test_set_preference(self, setup_db, tenant_id):
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

    def test_get_preference(self, setup_db, tenant_id):
        """Test retrieving notification preference."""
        NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_reminder_24h",
            channel="email",
            enabled=False,
        )

        preference = NotificationService.get_preference(
            customer_id="customer_123",
            notification_type="appointment_reminder_24h",
            channel="email",
        )

        assert preference is not None
        assert preference.enabled is False

    def test_get_all_preferences(self, setup_db, tenant_id):
        """Test retrieving all preferences for a customer."""
        NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_reminder_24h",
            channel="email",
            enabled=False,
        )
        NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_confirmation",
            channel="sms",
            enabled=True,
        )

        preferences = NotificationService.get_preferences("customer_123")
        assert len(preferences) == 2

    def test_is_notification_enabled(self, setup_db, tenant_id):
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

    def test_update_preference(self, setup_db, tenant_id):
        """Test updating notification preference."""
        NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_reminder_24h",
            channel="email",
            enabled=False,
        )

        # Update to enabled
        updated = NotificationService.set_preference(
            customer_id="customer_123",
            notification_type="appointment_reminder_24h",
            channel="email",
            enabled=True,
        )

        assert updated.enabled is True


class TestNotificationTemplates:
    """Test notification templates."""

    def test_create_template(self, setup_db, tenant_id):
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

    def test_get_template(self, setup_db, tenant_id):
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

    def test_get_templates_with_filtering(self, setup_db, tenant_id):
        """Test retrieving templates with filters."""
        NotificationService.create_template(
            template_type="appointment_confirmation",
            channel="email",
            subject="Appointment Confirmed",
            body="Your appointment is confirmed",
        )
        NotificationService.create_template(
            template_type="appointment_reminder_24h",
            channel="email",
            subject="Appointment Reminder",
            body="Reminder: Your appointment is tomorrow",
        )
        NotificationService.create_template(
            template_type="appointment_confirmation",
            channel="sms",
            subject=None,
            body="Appointment confirmed",
        )

        # Filter by type
        templates = NotificationService.get_templates(
            template_type="appointment_confirmation"
        )
        assert len(templates) == 2

        # Filter by channel
        templates = NotificationService.get_templates(channel="email")
        assert len(templates) == 2

    def test_update_template(self, setup_db, tenant_id):
        """Test updating a template."""
        template = NotificationService.create_template(
            template_type="appointment_confirmation",
            channel="email",
            subject="Appointment Confirmed",
            body="Your appointment is confirmed",
        )

        updated = NotificationService.update_template(
            template_id=str(template.id),
            body="Your appointment with {{staff_name}} is confirmed",
            variables=["staff_name"],
        )

        assert updated.body == "Your appointment with {{staff_name}} is confirmed"
        assert "staff_name" in updated.variables


class TestNotificationStats:
    """Test notification statistics."""

    def test_get_notification_stats(self, setup_db, tenant_id):
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
        assert stats["delivery_rate"] == pytest.approx(33.33, rel=0.1)
        assert stats["failure_rate"] == pytest.approx(33.33, rel=0.1)

    def test_get_notification_stats_with_date_range(self, setup_db, tenant_id):
        """Test getting notification statistics with date range."""
        now = datetime.utcnow()
        past = now - timedelta(days=7)

        # Create notification
        NotificationService.create_notification(
            recipient_id="customer_123",
            recipient_type="customer",
            notification_type="appointment_confirmation",
            channel="email",
            content="Appointment confirmed",
            recipient_email="customer@example.com",
        )

        # Get stats for past week
        stats = NotificationService.get_notification_stats(
            start_date=past, end_date=now
        )

        assert stats["total"] == 1
