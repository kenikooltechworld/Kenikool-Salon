"""Discount model for POS system."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DecimalField,
    DictField,
    BooleanField,
    IntField,
)
from app.models.base import BaseDocument


class Discount(BaseDocument):
    """Discount document for managing discount codes and promotions."""

    # Discount identification
    discount_code = StringField(required=True, max_length=50, unique_with="tenant_id")
    discount_type = StringField(
        required=True,
        choices=["percentage", "fixed", "loyalty", "bulk"],
        default="percentage"
    )
    discount_value = DecimalField(required=True, min_value=0)

    # Applicability
    applicable_to = StringField(
        required=True,
        choices=["transaction", "item", "service", "product"],
        default="transaction"
    )

    # Conditions (JSON for flexibility)
    conditions = DictField(default=dict)
    max_discount = DecimalField(null=True, min_value=0)

    # Status and validity
    active = BooleanField(default=True)
    valid_from = DateTimeField(null=True)
    valid_until = DateTimeField(null=True)

    # Usage tracking
    usage_count = IntField(default=0)
    usage_limit = IntField(null=True)

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "discounts",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "discount_code"),
            ("tenant_id", "active"),
            ("tenant_id", "created_at"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def is_valid(self):
        """Check if discount is currently valid."""
        if not self.active:
            return False
        
        now = datetime.utcnow()
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        
        return True

    def __str__(self):
        """String representation of discount."""
        return f"Discount({self.discount_code} - {self.discount_value} {self.discount_type})"

    def __repr__(self):
        """Representation of discount."""
        return f"<Discount id={self.id} code={self.discount_code} value={self.discount_value} type={self.discount_type}>"
