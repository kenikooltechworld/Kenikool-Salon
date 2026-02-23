"""Service model for managing salon/spa/gym services."""

from datetime import datetime
from mongoengine import StringField, IntField, DecimalField, ListField, DateTimeField, BooleanField
from app.models.base import BaseDocument


class Service(BaseDocument):
    """Service document representing a service offered by a tenant."""

    name = StringField(required=True, max_length=255)
    description = StringField(null=True, max_length=1000)
    duration_minutes = IntField(required=True, min_value=1)
    price = DecimalField(required=True, min_value=0)
    category = StringField(required=True, max_length=100)
    color = StringField(null=True, max_length=7, default="#3B82F6")
    icon = StringField(null=True, max_length=50, default="Scissors")
    is_active = BooleanField(default=True)
    is_published = BooleanField(default=False)
    public_description = StringField(null=True, max_length=1000)
    public_image_url = StringField(null=True, max_length=500)
    allow_public_booking = BooleanField(default=False)
    allow_pay_now = BooleanField(default=False)  # Whether service allows immediate payment
    tags = ListField(StringField(max_length=50), default=[])
    benefits = ListField(StringField(max_length=200), default=[])  # Service benefits/features
    # Option B: Per-service commission rate (overrides staff default)
    commission_percentage = DecimalField(null=True, min_value=0, max_value=100)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "services",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "created_at"),
            ("tenant_id", "category"),
            ("tenant_id", "is_active"),
            ("tenant_id", "is_published"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of service."""
        return f"Service({self.name})"

    def __repr__(self):
        """Representation of service."""
        return f"<Service id={self.id} name={self.name} category={self.category}>"
