"""Availability model for managing staff availability schedules."""

from datetime import datetime, time
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    DateField,
    BooleanField,
    DictField,
    ListField,
    IntField,
)
from app.models.base import BaseDocument


class Availability(BaseDocument):
    """Availability document representing staff member's availability schedule."""

    staff_id = ObjectIdField(required=True)
    
    # Recurring pattern: day_of_week (0-6, where 0=Monday, 6=Sunday)
    day_of_week = IntField(null=True, min_value=0, max_value=6)
    
    # Time range for availability (stored as strings in HH:MM:SS format)
    start_time = StringField(required=True)  # Format: "HH:MM:SS"
    end_time = StringField(required=True)  # Format: "HH:MM:SS"
    
    # Recurring schedule indicator
    is_recurring = BooleanField(default=False)
    
    # Date range for availability
    effective_from = DateField(required=True)
    effective_to = DateField(null=True)
    
    # Break times (list of {start_time, end_time} dicts)
    breaks = ListField(DictField(), default=[])
    
    # Slot configuration (configurable per availability)
    slot_interval_minutes = IntField(default=30, min_value=5, max_value=120)
    buffer_time_minutes = IntField(default=15, min_value=0, max_value=120)
    concurrent_bookings_allowed = IntField(default=1, min_value=1, max_value=10)
    
    # Status
    is_active = BooleanField(default=True)
    
    # Metadata
    notes = StringField(null=True, max_length=500)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "availability",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "created_at"),
            ("tenant_id", "staff_id", "effective_from"),
            ("tenant_id", "staff_id", "is_recurring"),
            ("tenant_id", "staff_id", "is_active"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of availability."""
        pattern = f"Day {self.day_of_week}" if self.is_recurring else f"{self.effective_from}"
        return f"Availability({self.staff_id} - {pattern})"

    def __repr__(self):
        """Representation of availability."""
        return f"<Availability id={self.id} staff_id={self.staff_id} recurring={self.is_recurring}>"
