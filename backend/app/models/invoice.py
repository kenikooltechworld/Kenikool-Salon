"""Invoice model for managing invoices and billing."""

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
)
from app.models.base import BaseDocument


class InvoiceLineItem(EmbeddedDocument):
    """Embedded document for invoice line items."""

    service_id = ObjectIdField(required=True)
    service_name = StringField(required=True, max_length=255)
    quantity = DecimalField(required=True, min_value=1, default=1)
    unit_price = DecimalField(required=True, min_value=0)
    total = DecimalField(required=True, min_value=0)

    def __str__(self):
        """String representation of line item."""
        return f"LineItem({self.service_name} x {self.quantity})"


class Invoice(BaseDocument):
    """Invoice document representing a billing invoice."""

    # References
    appointment_id = ObjectIdField(null=True)
    customer_id = ObjectIdField(required=True)

    # Line items
    line_items = ListField(EmbeddedDocumentField(InvoiceLineItem), default=list)

    # Financial details
    subtotal = DecimalField(required=True, min_value=0, default=Decimal("0"))
    discount = DecimalField(required=True, min_value=0, default=Decimal("0"))
    tax = DecimalField(required=True, min_value=0, default=Decimal("0"))
    total = DecimalField(required=True, min_value=0, default=Decimal("0"))

    # Status tracking
    status = StringField(
        required=True,
        choices=["draft", "issued", "paid", "cancelled"],
        default="draft"
    )

    # Dates
    due_date = DateTimeField(null=True)
    paid_at = DateTimeField(null=True)

    # Metadata
    notes = StringField(null=True, max_length=1000)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "invoices",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "appointment_id"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
            ("tenant_id", "due_date"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of invoice."""
        return f"Invoice({self.customer_id} - {self.total})"

    def __repr__(self):
        """Representation of invoice."""
        return f"<Invoice id={self.id} customer_id={self.customer_id} status={self.status} total={self.total}>"
