"""Commission payout model."""
from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField, ObjectIdField, DateTimeField, DecimalField, BooleanField
)
from app.models.base import BaseDocument


class CommissionPayout(BaseDocument):
    """Record of a commission payout to staff."""

    staff_id = ObjectIdField(required=True)
    tenant_id = ObjectIdField(required=True)

    period = StringField(required=True, max_length=50)
    payout_amount = DecimalField(required=True, min_value=0)
    status = StringField(
        required=True,
        choices=["pending", "processed", "failed"],
        default="pending",
    )
    processed_at = DateTimeField(null=True)
    transaction_id = ObjectIdField(null=True)
    notes = StringField(max_length=500, null=True)

    meta = {
        "collection": "commission_payouts",
        "indexes": [
            ("tenant_id", "staff_id"),
            ("tenant_id", "status"),
            ("tenant_id", "period"),
            ("tenant_id", "-created_at"),
        ],
    }

    def __str__(self):
        return f"CommissionPayout(staff={self.staff_id}, period={self.period})"
