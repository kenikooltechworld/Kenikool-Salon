"""TimeOffRequest model for time-off request management."""

from datetime import datetime, date
from mongoengine import StringField, DateField, DateTimeField, ObjectIdField
from app.models.base import BaseDocument


class TimeOffRequest(BaseDocument):
    """TimeOffRequest document model for managing staff time-off requests."""

    staff_id = ObjectIdField(required=True)  # Reference to Staff model
    start_date = DateField(required=True)  # Start date of time off
    end_date = DateField(required=True)  # End date of time off
    reason = StringField(max_length=500, required=True)  # Reason for time off
    status = StringField(
        choices=["pending", "approved", "denied"],
        default="pending"
    )
    requested_at = DateTimeField(default=datetime.utcnow)  # When request was made
    reviewed_at = DateTimeField(null=True)  # When request was reviewed
    reviewed_by = ObjectIdField(null=True)  # User ID of manager who reviewed

    meta = {
        "collection": "time_off_requests",
        "indexes": [
            ("tenant_id", "staff_id"),
            ("tenant_id", "status"),
            ("tenant_id", "start_date"),
            ("tenant_id", "end_date"),
            ("tenant_id", "created_at"),
            ("staff_id", "start_date", "end_date"),  # For conflict detection
        ],
    }

    def __str__(self):
        """Return time-off request string representation."""
        return f"TimeOffRequest(staff_id={self.staff_id}, start_date={self.start_date}, status={self.status})"
