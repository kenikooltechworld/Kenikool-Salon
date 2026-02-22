"""Service category model for managing service categories per tenant."""

from datetime import datetime
from mongoengine import StringField, DateTimeField, BooleanField
from app.models.base import BaseDocument


class ServiceCategory(BaseDocument):
    """ServiceCategory document representing a service category for a tenant."""

    name = StringField(required=True, max_length=100)
    description = StringField(null=True, max_length=500)
    color = StringField(null=True, max_length=7)  # Hex color code
    icon = StringField(null=True, max_length=50)  # Icon name
    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "service_categories",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "created_at"),
            ("tenant_id", "name"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of service category."""
        return f"ServiceCategory({self.name})"

    def __repr__(self):
        """Representation of service category."""
        return f"<ServiceCategory id={self.id} name={self.name}>"
