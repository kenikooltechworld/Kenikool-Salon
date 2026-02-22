"""Appointment model for managing salon/spa/gym appointments."""

from datetime import datetime
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    BooleanField,
    DecimalField,
)
from app.models.base import BaseDocument


class Appointment(BaseDocument):
    """Appointment document representing a booked appointment."""

    customer_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    service_id = ObjectIdField(required=True)
    location_id = ObjectIdField(null=True)
    
    # Appointment timing
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    
    # Status tracking
    status = StringField(
        required=True,
        choices=["scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"],
        default="scheduled"
    )
    
    # Cancellation details
    cancellation_reason = StringField(null=True, max_length=500)
    cancelled_at = DateTimeField(null=True)
    cancelled_by = ObjectIdField(null=True)
    
    # No-show details
    no_show_reason = StringField(null=True, max_length=500)
    marked_no_show_at = DateTimeField(null=True)
    
    # Appointment notes
    notes = StringField(null=True, max_length=1000)
    
    # Price information (captured at booking time)
    price = DecimalField(null=True, min_value=0)
    
    # Payment reference (for refund processing)
    payment_id = ObjectIdField(null=True)
    
    # Confirmation tracking
    confirmed_at = DateTimeField(null=True)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "appointments",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "service_id"),
            ("tenant_id", "start_time"),
            ("tenant_id", "end_time"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
            # Compound index for double-booking prevention
            ("tenant_id", "staff_id", "start_time", "end_time", "status"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def __str__(self):
        """String representation of appointment."""
        return f"Appointment({self.customer_id} - {self.start_time})"

    def __repr__(self):
        """Representation of appointment."""
        return f"<Appointment id={self.id} staff_id={self.staff_id} status={self.status}>"
