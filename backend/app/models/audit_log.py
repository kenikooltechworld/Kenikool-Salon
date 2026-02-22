"""Audit log model for tracking all operations."""

from datetime import datetime
from mongoengine import (
    StringField,
    IntField,
    DateTimeField,
    DictField,
    ListField,
)
from app.models.base import BaseDocument


class AuditLog(BaseDocument):
    """Immutable audit log for compliance and security."""

    event_type = StringField(required=True)  # GET, POST, PUT, DELETE, etc.
    resource = StringField(required=True)  # API endpoint or resource
    user_id = StringField(null=True)  # User who performed the action
    ip_address = StringField(required=True)  # Client IP address
    status_code = IntField(required=True)  # HTTP status code
    request_body = DictField(null=True)  # Request payload (redacted)
    response_body = DictField(null=True)  # Response payload (redacted)
    user_agent = StringField(null=True)  # Client user agent
    error_message = StringField(null=True)  # Error details if applicable
    duration_ms = IntField(null=True)  # Request duration in milliseconds
    tags = ListField(StringField(), default=list)  # For categorization

    meta = {
        "collection": "audit_logs",
        "indexes": [
            ("tenant_id", "-created_at"),
            ("tenant_id", "user_id", "-created_at"),
            ("tenant_id", "event_type", "-created_at"),
            ("tenant_id", "resource", "-created_at"),
            ("ip_address", "-created_at"),
        ],
    }

    def __str__(self):
        """Return audit log string representation."""
        return f"{self.event_type} {self.resource} - {self.status_code} ({self.created_at})"
