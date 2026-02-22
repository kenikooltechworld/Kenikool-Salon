"""Staff commission model for POS system."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DecimalField,
    EmbeddedDocument,
    EmbeddedDocumentField,
)
from app.models.base import BaseDocument


class CommissionStructure(EmbeddedDocument):
    """Embedded document for commission structure."""

    commission_type = StringField(
        required=True,
        choices=["percentage", "fixed", "tiered"],
        default="percentage"
    )
    commission_value = DecimalField(required=True, min_value=0)
    effective_from = DateTimeField(required=True)
    effective_to = DateTimeField(null=True)

    def __str__(self):
        """String representation of commission structure."""
        return f"CommissionStructure({self.commission_type} - {self.commission_value})"


class StaffCommission(BaseDocument):
    """Staff commission document for tracking commissions."""

    # References
    staff_id = ObjectIdField(required=True)
    transaction_id = ObjectIdField(required=True)

    # Commission details
    commission_amount = DecimalField(required=True, min_value=0, default=Decimal("0"))
    commission_rate = DecimalField(required=True, min_value=0, default=Decimal("0"))
    commission_type = StringField(
        required=True,
        choices=["percentage", "fixed", "tiered"],
        default="percentage"
    )

    # Timestamps
    calculated_at = DateTimeField(default=datetime.utcnow)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "staff_commissions",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "transaction_id"),
            ("tenant_id", "created_at"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of staff commission."""
        return f"StaffCommission({self.staff_id} - {self.commission_amount})"

    def __repr__(self):
        """Representation of staff commission."""
        return f"<StaffCommission id={self.id} staff_id={self.staff_id} amount={self.commission_amount}>"
