"""Payment model for managing payment transactions."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DecimalField,
    DictField,
    IntField,
)
from app.models.base import BaseDocument


class Payment(BaseDocument):
    """Payment document representing a payment transaction."""

    # Override tenant_id to make it optional (for booking payments without tenant context)
    tenant_id = ObjectIdField(required=False)

    # References
    customer_id = ObjectIdField(required=False)
    invoice_id = ObjectIdField(required=False)

    # Payment details
    amount = DecimalField(required=True, min_value=0)
    status = StringField(
        required=True,
        choices=["pending", "success", "failed", "cancelled"],
        default="pending"
    )

    # Payment gateway information
    reference = StringField(required=True, unique_with="tenant_id")  # Paystack reference
    gateway = StringField(required=True, default="paystack")  # paystack, stripe, etc.

    # Idempotency
    idempotency_key = StringField(unique_with="tenant_id", sparse=True)  # For duplicate detection

    # Retry logic
    retry_count = IntField(default=0, min_value=0, max_value=3)
    max_retries = IntField(default=3)
    last_retry_at = DateTimeField(nullable=True)
    next_retry_at = DateTimeField(nullable=True)

    # Metadata for additional data
    metadata = DictField(default=dict)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "payments",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "reference"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "invoice_id"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
            ("tenant_id", "idempotency_key"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of payment."""
        return f"Payment({self.reference} - {self.amount} - {self.status})"

    def __repr__(self):
        """Representation of payment."""
        return f"<Payment id={self.id} reference={self.reference} amount={self.amount} status={self.status}>"
