"""Refund model for managing refund transactions."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DecimalField,
    DictField,
)
from app.models.base import BaseDocument


class Refund(BaseDocument):
    """Refund document representing a refund transaction."""

    # References
    payment_id = ObjectIdField(required=True)

    # Refund details
    amount = DecimalField(required=True, min_value=0)
    reason = StringField(required=True, max_length=500)
    status = StringField(
        required=True,
        choices=["pending", "success", "failed"],
        default="pending"
    )

    # Payment gateway information
    reference = StringField(required=True, unique_with="tenant_id")  # Paystack refund reference

    # Metadata for additional data
    metadata = DictField(default=dict)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "refunds",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "reference"),
            ("tenant_id", "payment_id"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of refund."""
        return f"Refund({self.reference} - {self.amount} - {self.status})"

    def __repr__(self):
        """Representation of refund."""
        return f"<Refund id={self.id} reference={self.reference} amount={self.amount} status={self.status}>"
