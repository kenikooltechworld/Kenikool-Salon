"""Customer preference model for storing customer preferences."""

from datetime import datetime
from mongoengine import StringField, ListField, DateTimeField, ObjectIdField
from app.models.base import BaseDocument


class CustomerPreference(BaseDocument):
    """Customer preference document model."""

    customer_id = ObjectIdField(required=True)  # Reference to Customer
    preferred_staff_ids = ListField(ObjectIdField(), default=[])  # List of preferred Staff IDs
    preferred_service_ids = ListField(ObjectIdField(), default=[])  # List of preferred Service IDs
    communication_methods = ListField(
        StringField(choices=["email", "sms", "phone"]),
        default=["email"]
    )
    preferred_time_slots = ListField(StringField(), default=[])  # e.g., ["morning", "afternoon", "evening"]
    language = StringField(default="en", max_length=10)
    notes = StringField(max_length=1000, null=True)

    meta = {
        "collection": "customer_preferences",
        "indexes": [
            ("tenant_id", "customer_id"),
            ("tenant_id", "created_at"),
        ],
    }

    def __str__(self):
        """Return customer preference string representation."""
        return f"CustomerPreference(customer_id={self.customer_id})"
