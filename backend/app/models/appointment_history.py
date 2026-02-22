"""AppointmentHistory model for tracking customer appointment history."""

from datetime import datetime
from decimal import Decimal
from mongoengine import (
    StringField,
    ObjectIdField,
    DateTimeField,
    IntField,
    DecimalField,
)
from app.models.base import BaseDocument


class AppointmentHistory(BaseDocument):
    """AppointmentHistory document tracking completed appointments."""

    customer_id = ObjectIdField(required=True)
    appointment_id = ObjectIdField(required=True)
    service_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    
    # Appointment details
    appointment_date = DateTimeField(required=True)
    duration_minutes = IntField(required=True, min_value=1)
    
    # Financial information
    amount_paid = DecimalField(required=True, min_value=0)
    
    # Optional notes
    notes = StringField(null=True, max_length=1000)
    
    # Metadata
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "collection": "appointment_history",
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "appointment_id"),
            ("tenant_id", "service_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "appointment_date"),
            ("tenant_id", "created_at"),
            # Compound index for customer history retrieval
            ("tenant_id", "customer_id", "appointment_date"),
        ],
    }

    def __str__(self):
        """String representation of appointment history."""
        return f"AppointmentHistory(customer={self.customer_id}, appointment={self.appointment_id})"

    def __repr__(self):
        """Representation of appointment history."""
        return f"<AppointmentHistory id={self.id} customer_id={self.customer_id}>"
