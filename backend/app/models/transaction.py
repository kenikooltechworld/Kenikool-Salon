"""Transaction model for POS system."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DecimalField,
    ListField,
    EmbeddedDocument,
    EmbeddedDocumentField,
    IntField,
)
from app.models.base import BaseDocument


class TransactionItem(EmbeddedDocument):
    """Embedded document for transaction items."""

    item_type = StringField(
        required=True,
        choices=["service", "product", "package"]
    )
    item_id = ObjectIdField(required=True)
    item_name = StringField(required=True, max_length=255)
    quantity = IntField(required=True, min_value=1)
    unit_price = DecimalField(required=True, min_value=0)
    line_total = DecimalField(required=True, min_value=0)
    tax_rate = DecimalField(default=Decimal("0"), min_value=0)
    tax_amount = DecimalField(default=Decimal("0"), min_value=0)
    discount_rate = DecimalField(default=Decimal("0"), min_value=0)
    discount_amount = DecimalField(default=Decimal("0"), min_value=0)

    def __str__(self):
        """String representation of transaction item."""
        return f"TransactionItem({self.item_name} x {self.quantity})"


class Transaction(BaseDocument):
    """Transaction document representing a POS transaction."""

    # References
    customer_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    appointment_id = ObjectIdField(null=True)
    invoice_id = ObjectIdField(null=True)

    # Transaction details
    transaction_type = StringField(
        required=True,
        choices=["service", "product", "package", "refund"],
        default="service"
    )
    items = ListField(EmbeddedDocumentField(TransactionItem), default=list)

    # Financial details
    subtotal = DecimalField(required=True, min_value=0, default=Decimal("0"))
    tax_amount = DecimalField(required=True, min_value=0, default=Decimal("0"))
    discount_amount = DecimalField(required=True, min_value=0, default=Decimal("0"))
    total = DecimalField(required=True, min_value=0, default=Decimal("0"))

    # Payment details
    payment_method = StringField(
        required=True,
        choices=["cash", "card", "mobile_money", "check", "bank_transfer"],
        default="cash"
    )
    payment_status = StringField(
        required=True,
        choices=["pending", "completed", "failed", "refunded"],
        default="pending"
    )
    reference_number = StringField(required=True, max_length=255)
    paystack_reference = StringField(null=True)

    # Metadata
    notes = StringField(null=True, max_length=1000)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "transactions",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "created_at"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "payment_status"),
            ("tenant_id", "reference_number"),
            ("reference_number", "tenant_id"),
            ("tenant_id", "invoice_id"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of transaction."""
        return f"Transaction({self.reference_number} - {self.total})"

    def __repr__(self):
        """Representation of transaction."""
        return f"<Transaction id={self.id} ref={self.reference_number} status={self.payment_status} total={self.total}>"
