"""Cart model for POS system."""

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


class CartItem(EmbeddedDocument):
    """Embedded document for cart items."""

    item_type = StringField(
        required=True,
        choices=["service", "product", "package"]
    )
    item_id = ObjectIdField(required=True)
    item_name = StringField(required=True, max_length=255)
    quantity = IntField(required=True, min_value=1)
    unit_price = DecimalField(required=True, min_value=0)
    line_total = DecimalField(required=True, min_value=0)

    def __str__(self):
        """String representation of cart item."""
        return f"CartItem({self.item_name} x {self.quantity})"


class Cart(BaseDocument):
    """Cart document for offline mode and transaction staging."""

    # References
    customer_id = ObjectIdField(null=True)
    staff_id = ObjectIdField(required=True)

    # Cart items
    items = ListField(EmbeddedDocumentField(CartItem), default=list)

    # Totals
    subtotal = DecimalField(default=Decimal("0"), min_value=0)
    tax_amount = DecimalField(default=Decimal("0"), min_value=0)
    discount_amount = DecimalField(default=Decimal("0"), min_value=0)
    total = DecimalField(default=Decimal("0"), min_value=0)

    # Status
    status = StringField(
        required=True,
        choices=["active", "completed", "abandoned"],
        default="active"
    )

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "carts",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of cart."""
        return f"Cart({len(self.items)} items - {self.total})"

    def __repr__(self):
        """Representation of cart."""
        return f"<Cart id={self.id} status={self.status} total={self.total}>"
