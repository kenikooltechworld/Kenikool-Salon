"""Customer model for customer management."""

from datetime import datetime
from decimal import Decimal
from mongoengine import StringField, ListField, DateField, DateTimeField, ObjectIdField, EmailField, DecimalField
from app.models.base import BaseDocument


class Customer(BaseDocument):
    """Customer document model with contact info and preferences."""

    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)
    email = StringField(required=True, max_length=255, unique_with='tenant_id')
    phone = StringField(required=True, max_length=20)
    address = StringField(max_length=500, null=True)
    date_of_birth = DateField(null=True)
    preferred_staff_id = ObjectIdField(null=True)  # Reference to Staff
    preferred_services = ListField(ObjectIdField(), default=[])  # List of Service IDs
    communication_preference = StringField(
        choices=["email", "sms", "phone", "none"],
        default="email"
    )
    status = StringField(
        choices=["active", "inactive"],
        default="active"
    )
    # Outstanding balance tracking
    outstanding_balance = DecimalField(required=True, min_value=0, default=Decimal("0"))

    meta = {
        "collection": "customers",
        "indexes": [
            ("tenant_id", "email"),
            ("tenant_id", "phone"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
            ("tenant_id", "first_name"),
            ("tenant_id", "last_name"),
        ],
    }

    def __str__(self):
        """Return customer string representation."""
        return f"Customer(name={self.first_name} {self.last_name}, email={self.email})"
