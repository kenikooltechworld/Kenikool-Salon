"""Notification model for managing notifications."""

from datetime import datetime
from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    BooleanField,
    IntField,
    ListField,
    DictField,
    ReferenceField,
    CASCADE,
    ObjectIdField,
)
from app.models.base import BaseDocument


class Notification(BaseDocument):
    """Notification document model."""

    # Notification types
    NOTIFICATION_TYPES = [
        "appointment_confirmation",
        "appointment_reminder_24h",
        "appointment_reminder_1h",
        "appointment_cancelled",
        "appointment_completed",
        "payment_receipt",
        "shift_assigned",
        "time_off_approved",
        "time_off_rejected",
        "custom",
    ]

    # Channels
    CHANNELS = ["email", "sms", "push", "in_app"]

    # Status
    STATUSES = ["pending", "sent", "delivered", "failed", "bounced"]

    # Recipient types
    RECIPIENT_TYPES = ["customer", "staff", "owner"]

    recipient_id = StringField(required=True)  # User or Customer ID
    recipient_type = StringField(
        choices=RECIPIENT_TYPES, required=True
    )  # customer, staff, owner
    recipient_email = StringField(null=True)
    recipient_phone = StringField(null=True)

    notification_type = StringField(
        choices=NOTIFICATION_TYPES, required=True
    )  # Type of notification
    channel = StringField(choices=CHANNELS, required=True)  # email, sms, push, in_app
    status = StringField(
        choices=STATUSES, default="pending", required=True
    )  # Delivery status

    subject = StringField(null=True)  # For email notifications
    content = StringField(required=True)  # Notification content
    template_id = StringField(null=True)  # Reference to template used

    # Variables for template rendering
    template_variables = DictField(default={})

    # Delivery tracking
    sent_at = DateTimeField(null=True)
    delivered_at = DateTimeField(null=True)
    failed_at = DateTimeField(null=True)
    failure_reason = StringField(null=True)

    # Retry tracking
    retry_count = IntField(default=0)
    max_retries = IntField(default=3)
    last_retry_at = DateTimeField(null=True)

    # Related entities
    appointment_id = StringField(null=True)
    payment_id = StringField(null=True)
    shift_id = StringField(null=True)
    time_off_request_id = StringField(null=True)

    # Metadata
    is_read = BooleanField(default=False)
    read_at = DateTimeField(null=True)
    external_id = StringField(null=True)  # ID from external service (SendGrid, Twilio)

    meta = {
        "collection": "notifications",
        "indexes": [
            ("tenant_id", "recipient_id", "-created_at"),
            ("tenant_id", "status", "-created_at"),
            ("tenant_id", "notification_type", "-created_at"),
            ("tenant_id", "channel", "-created_at"),
            ("tenant_id", "appointment_id"),
            ("tenant_id", "payment_id"),
            ("tenant_id", "shift_id"),
            ("tenant_id", "time_off_request_id"),
            ("tenant_id", "-created_at"),
            ("status", "-created_at"),
        ],
    }

    def __str__(self):
        """Return notification string representation."""
        return f"{self.notification_type} to {self.recipient_id} ({self.status})"

    def mark_sent(self):
        """Mark notification as sent."""
        self.status = "sent"
        self.sent_at = datetime.utcnow()
        self.save()

    def mark_delivered(self):
        """Mark notification as delivered."""
        self.status = "delivered"
        self.delivered_at = datetime.utcnow()
        self.save()

    def mark_failed(self, reason: str = None):
        """Mark notification as failed."""
        self.status = "failed"
        self.failed_at = datetime.utcnow()
        self.failure_reason = reason
        self.save()

    def mark_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
        self.save()

    def should_retry(self) -> bool:
        """Check if notification should be retried."""
        return self.status == "failed" and self.retry_count < self.max_retries

    def increment_retry(self):
        """Increment retry count."""
        self.retry_count += 1
        self.last_retry_at = datetime.utcnow()
        self.save()


class NotificationTemplate(BaseDocument):
    """Notification template model."""

    TEMPLATE_TYPES = [
        "appointment_confirmation",
        "appointment_reminder_24h",
        "appointment_reminder_1h",
        "appointment_cancelled",
        "appointment_completed",
        "payment_receipt",
        "shift_assigned",
        "time_off_approved",
        "time_off_rejected",
    ]

    CHANNELS = ["email", "sms", "push", "in_app"]

    template_type = StringField(choices=TEMPLATE_TYPES, required=True)
    channel = StringField(choices=CHANNELS, required=True)

    subject = StringField(null=True)  # For email templates
    body = StringField(required=True)  # Template body with variables

    # Variables that can be used in template (e.g., {{customer_name}}, {{appointment_time}})
    variables = ListField(StringField(), default=[])

    is_active = BooleanField(default=True)
    is_default = BooleanField(default=False)  # System default template

    meta = {
        "collection": "notification_templates",
        "indexes": [
            ("tenant_id", "template_type", "channel"),
            ("tenant_id", "is_active"),
        ],
    }

    def __str__(self):
        """Return template string representation."""
        return f"{self.template_type} - {self.channel}"


class NotificationPreference(BaseDocument):
    """Notification preference model for customers."""

    NOTIFICATION_TYPES = [
        "appointment_confirmation",
        "appointment_reminder_24h",
        "appointment_reminder_1h",
        "appointment_cancelled",
        "appointment_completed",
        "payment_receipt",
    ]

    CHANNELS = ["email", "sms", "push", "in_app"]

    customer_id = StringField(required=True)
    notification_type = StringField(choices=NOTIFICATION_TYPES, required=True)
    channel = StringField(choices=CHANNELS, required=True)

    enabled = BooleanField(default=True)  # Whether this notification is enabled

    meta = {
        "collection": "notification_preferences",
        "indexes": [
            ("tenant_id", "customer_id", "notification_type", "channel"),
            ("tenant_id", "customer_id"),
        ],
    }

    def __str__(self):
        """Return preference string representation."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.notification_type} via {self.channel} ({status})"


class NotificationLog(BaseDocument):
    """Notification delivery log for tracking and debugging."""

    STATUSES = ["pending", "sent", "delivered", "failed", "bounced"]

    notification_id = StringField(required=True)
    status = StringField(choices=STATUSES, required=True)
    error_message = StringField(null=True)
    retry_count = IntField(default=0)
    last_retry_at = DateTimeField(null=True)

    # External service response
    external_response = DictField(default={})
    external_id = StringField(null=True)

    meta = {
        "collection": "notification_logs",
        "indexes": [
            ("tenant_id", "notification_id"),
            ("tenant_id", "status", "-created_at"),
        ],
    }

    def __str__(self):
        """Return log string representation."""
        return f"Notification {self.notification_id} - {self.status}"
