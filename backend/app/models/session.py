"""Session model for session management."""

from datetime import datetime
from mongoengine import StringField, DateTimeField, ObjectIdField
from app.models.base import BaseDocument


class Session(BaseDocument):
    """Session document model for tracking active user sessions."""

    user_id = ObjectIdField(required=True)
    token = StringField(required=True)
    refresh_token = StringField(required=True)
    csrf_token_hash = StringField(required=True)  # Hash of CSRF token for validation
    expires_at = DateTimeField(required=True)
    ip_address = StringField(required=True)
    user_agent = StringField(required=True)
    browser_fingerprint = StringField(required=True)  # Unique browser identifier
    status = StringField(choices=["active", "revoked"], default="active")

    meta = {
        "collection": "sessions",
        "indexes": [
            ("tenant_id", "user_id"),
            ("tenant_id", "status"),
            ("tenant_id", "browser_fingerprint"),
            ("expires_at",),
        ],
    }

    def __str__(self):
        """Return session string representation."""
        return f"Session for user {self.user_id}"
