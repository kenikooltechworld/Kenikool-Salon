"""Service commission model for tracking commissions earned per completed service."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DecimalField,
    BooleanField,
)
from app.models.base import BaseDocument


class ServiceCommission(BaseDocument):
    """Service commission document for tracking commissions earned per completed appointment."""

    # References
    staff_id = ObjectIdField(required=True)
    appointment_id = ObjectIdField(required=True)
    service_id = ObjectIdField(required=True)

    # Commission details
    service_price = DecimalField(required=True, min_value=0)
    commission_percentage = DecimalField(required=True, min_value=0, max_value=100)
    commission_amount = DecimalField(required=True, min_value=0, default=Decimal("0"))

    # Status tracking
    status = StringField(
        required=True,
        choices=["pending", "paid"],
        default="pending"
    )

    # Timestamps
    earned_date = DateTimeField(default=datetime.utcnow)
    paid_date = DateTimeField(null=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "service_commissions",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "appointment_id"),
            ("tenant_id", "service_id"),
            ("tenant_id", "status"),
            ("tenant_id", "earned_date"),
            ("tenant_id", "staff_id", "status"),
            ("tenant_id", "staff_id", "earned_date"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of service commission."""
        return f"ServiceCommission({self.staff_id} - {self.commission_amount})"

    def __repr__(self):
        """Representation of service commission."""
        return f"<ServiceCommission id={self.id} staff_id={self.staff_id} amount={self.commission_amount}>"
