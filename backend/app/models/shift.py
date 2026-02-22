"""Shift model for staff shift management."""

from datetime import datetime
from decimal import Decimal
from mongoengine import StringField, DateTimeField, ObjectIdField, DecimalField
from app.models.base import BaseDocument


class Shift(BaseDocument):
    """Shift document model with status tracking and labor cost calculation."""

    staff_id = ObjectIdField(required=True)  # Reference to Staff model
    start_time = DateTimeField(required=True)  # Shift start time
    end_time = DateTimeField(required=True)  # Shift end time
    status = StringField(
        choices=["scheduled", "in_progress", "completed", "cancelled"],
        default="scheduled"
    )
    labor_cost = DecimalField(required=False, null=True)  # Calculated labor cost

    meta = {
        "collection": "shifts",
        "indexes": [
            ("tenant_id", "staff_id"),
            ("tenant_id", "start_time"),
            ("tenant_id", "end_time"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
            ("staff_id", "start_time", "end_time"),  # For conflict detection
        ],
    }

    def calculate_labor_cost(self, hourly_rate: Decimal) -> Decimal:
        """Calculate labor cost based on shift duration and hourly rate.
        
        Args:
            hourly_rate: Hourly rate in decimal format
            
        Returns:
            Calculated labor cost
        """
        if not self.start_time or not self.end_time:
            return Decimal("0")
        
        duration_seconds = (self.end_time - self.start_time).total_seconds()
        duration_hours = Decimal(str(duration_seconds)) / Decimal("3600")
        labor_cost = duration_hours * hourly_rate
        
        return labor_cost.quantize(Decimal("0.01"))

    def __str__(self):
        """Return shift string representation."""
        return f"Shift(staff_id={self.staff_id}, start_time={self.start_time}, status={self.status})"
