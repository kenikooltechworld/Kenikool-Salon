"""TimeSlot model for temporary appointment reservations."""

from datetime import datetime, timedelta
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    BooleanField,
)
from app.models.base import BaseDocument


class TimeSlot(BaseDocument):
    """TimeSlot document representing a temporary reservation of a time slot."""

    staff_id = ObjectIdField(required=True)
    service_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(null=True)  # Null until appointment is confirmed
    
    # Time slot details
    start_time = DateTimeField(required=True)
    end_time = DateTimeField(required=True)
    
    # Reservation status
    status = StringField(
        required=True,
        choices=["reserved", "confirmed", "expired", "released"],
        default="reserved"
    )
    
    # Reservation window (10 minutes from creation)
    reserved_at = DateTimeField(default=datetime.utcnow)
    expires_at = DateTimeField(required=True)
    
    # Associated appointment (if confirmed)
    appointment_id = ObjectIdField(null=True)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "time_slots",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "status"),
            ("tenant_id", "expires_at"),
            ("tenant_id", "start_time", "end_time"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)

    def is_expired(self) -> bool:
        """Check if reservation has expired."""
        return datetime.utcnow() > self.expires_at

    def __str__(self):
        """String representation of time slot."""
        return f"TimeSlot({self.staff_id} - {self.start_time})"

    def __repr__(self):
        """Representation of time slot."""
        return f"<TimeSlot id={self.id} staff_id={self.staff_id} status={self.status}>"
