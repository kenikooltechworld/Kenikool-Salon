"""User model for authentication and authorization."""

from datetime import datetime
from mongoengine import StringField, BooleanField, DateTimeField, ObjectIdField, IntField, ListField
from app.models.base import BaseDocument


class User(BaseDocument):
    """User document model with authentication fields."""

    email = StringField(required=True, unique=True, max_length=255)
    password_hash = StringField(required=True)
    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)
    phone = StringField(max_length=20)
    role_ids = ListField(ObjectIdField(), default=[])  # Multiple roles per user
    status = StringField(
        choices=["active", "inactive", "suspended"], default="active"
    )
    mfa_enabled = BooleanField(default=False)
    mfa_method = StringField(choices=["totp", "sms"], null=True)
    last_login = DateTimeField(null=True)
    failed_login_attempts = IntField(default=0)
    last_failed_login = DateTimeField(null=True)
    account_locked_until = DateTimeField(null=True)
    specialty = StringField(max_length=100, null=True)

    meta = {
        "collection": "users",
        "indexes": [
            ("tenant_id", "email"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
        ],
    }

    def __str__(self):
        """Return user string representation."""
        return f"{self.first_name} {self.last_name} ({self.email})"
