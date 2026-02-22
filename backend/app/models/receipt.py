"""Receipt model for POS system."""

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


class ReceiptItem(EmbeddedDocument):
    """Embedded document for receipt items."""

    item_type = StringField(
        required=True,
        choices=["service", "product", "package"]
    )
    item_id = ObjectIdField(required=True)
    item_name = StringField(required=True, max_length=255)
    quantity = IntField(required=True, min_value=1)
    unit_price = DecimalField(required=True, min_value=0)
    line_total = DecimalField(required=True, min_value=0)
    tax_amount = DecimalField(default=Decimal("0"), min_value=0)
    discount_amount = DecimalField(default=Decimal("0"), min_value=0)

    def __str__(self):
        """String representation of receipt item."""
        return f"ReceiptItem({self.item_name} x {self.quantity})"


class Receipt(BaseDocument):
    """Receipt document for transaction receipts."""

    # References
    transaction_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)

    # Receipt details
    receipt_number = StringField(required=True, max_length=255)
    receipt_date = DateTimeField(default=datetime.utcnow)
    customer_name = StringField(required=True, max_length=255)
    customer_email = StringField(null=True, max_length=255)
    customer_phone = StringField(null=True, max_length=20)

    # Items
    items = ListField(EmbeddedDocumentField(ReceiptItem), default=list)

    # Financial details
    subtotal = DecimalField(required=True, min_value=0, default=Decimal("0"))
    tax_amount = DecimalField(required=True, min_value=0, default=Decimal("0"))
    discount_amount = DecimalField(required=True, min_value=0, default=Decimal("0"))
    total = DecimalField(required=True, min_value=0, default=Decimal("0"))

    # Payment details
    payment_method = StringField(required=True, max_length=50)
    payment_reference = StringField(null=True, max_length=255)

    # Receipt format
    receipt_format = StringField(
        required=True,
        choices=["thermal", "standard", "email", "digital"],
        default="thermal"
    )

    # Delivery tracking
    printed_at = DateTimeField(null=True)
    emailed_at = DateTimeField(null=True)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "receipts",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "receipt_date"),
            ("transaction_id", "tenant_id"),
            ("customer_id", "tenant_id"),
        ],
    }

    def __str__(self):
        """String representation of receipt."""
        return f"Receipt({self.receipt_number} - {self.total})"

    def __repr__(self):
        """Representation of receipt."""
        return f"<Receipt id={self.id} number={self.receipt_number} total={self.total}>"
