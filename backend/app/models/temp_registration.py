"""Temporary registration model for salon owner registration flow."""

from datetime import datetime, timedelta
from mongoengine import Document, StringField, DateTimeField, IntField, ObjectIdField


class TempRegistration(Document):
    """Temporary registration document for multi-phase registration process."""

    email = StringField(required=True, unique=True)
    phone = StringField(required=True)
    salon_name = StringField(required=True)
    owner_name = StringField(required=True)
    address = StringField(required=True)
    bank_account = StringField()
    password_hash = StringField(required=True)
    subdomain = StringField(required=True, unique=True)
    verification_code = StringField(required=True)
    verification_code_expires = DateTimeField(required=True)
    referral_code = StringField()
    referral_tenant_id = ObjectIdField()
    created_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)  # TTL index for auto-deletion
    attempt_count = IntField(default=0)
    locked_until = DateTimeField()

    meta = {
        "collection": "temp_registrations",
        "indexes": [
            "email",
            "phone",
            "subdomain",
        ],
    }

    def __str__(self):
        """String representation of temp registration."""
        return f"TempRegistration({self.email})"

    def __repr__(self):
        """Representation of temp registration."""
        return f"<TempRegistration email={self.email} subdomain={self.subdomain}>"

    @property
    def is_locked(self) -> bool:
        """Check if registration is locked due to too many failed attempts."""
        if not self.locked_until:
            return False
        return datetime.utcnow() < self.locked_until

    @property
    def is_code_expired(self) -> bool:
        """Check if verification code has expired."""
        return datetime.utcnow() > self.verification_code_expires

    @property
    def is_registration_expired(self) -> bool:
        """Check if entire registration has expired."""
        return datetime.utcnow() > self.expires_at
