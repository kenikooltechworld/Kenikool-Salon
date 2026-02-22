"""Tenant model for multi-tenant architecture."""

from datetime import datetime
from mongoengine import Document, DateTimeField, StringField, DictField, BooleanField


class Tenant(Document):
    """Tenant document representing a business using the platform."""

    name = StringField(required=True, max_length=255)
    subdomain = StringField(required=True, unique=True, max_length=63)
    subscription_tier = StringField(
        choices=["trial", "starter", "professional", "enterprise"],
        default="trial",
    )
    status = StringField(
        choices=["active", "suspended", "deleted"],
        default="active",
    )
    address = StringField(null=True, max_length=500)
    region = StringField(default="us-east-1")
    is_published = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    deleted_at = DateTimeField(null=True)
    settings = DictField(default={})

    meta = {
        "collection": "tenants",
        "indexes": [
            "created_at",
            "status",
            ("status", "created_at"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of tenant."""
        return f"Tenant({self.name})"

    def __repr__(self):
        """Representation of tenant."""
        return f"<Tenant id={self.id} name={self.name} status={self.status}>"
