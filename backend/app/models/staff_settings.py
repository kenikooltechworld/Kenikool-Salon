"""Staff settings model for staff-specific preferences."""

from datetime import datetime
from mongoengine import StringField, BooleanField, DateTimeField, ObjectIdField, ListField
from app.models.base import BaseDocument


class StaffSettings(BaseDocument):
    """Staff settings document model for staff-specific preferences."""

    user_id = ObjectIdField(required=True)
    first_name = StringField(required=True, max_length=100)
    last_name = StringField(required=True, max_length=100)
    phone = StringField(max_length=20, null=True)
    email_bookings = BooleanField(default=True)
    email_reminders = BooleanField(default=True)
    email_messages = BooleanField(default=True)
    sms_bookings = BooleanField(default=False)
    sms_reminders = BooleanField(default=False)
    push_bookings = BooleanField(default=True)
    push_reminders = BooleanField(default=True)
    
    # Phase 3: Availability preferences
    working_hours_start = StringField(max_length=5, null=True)  # e.g., "09:00"
    working_hours_end = StringField(max_length=5, null=True)  # e.g., "17:00"
    days_off = ListField(StringField(max_length=10), default=[])  # e.g., ["sunday", "monday"]
    
    # Phase 3: Emergency contact
    emergency_contact_name = StringField(max_length=100, null=True)
    emergency_contact_phone = StringField(max_length=20, null=True)
    emergency_contact_relationship = StringField(max_length=50, null=True)
    
    # Phase 3: Work preferences
    service_specializations = ListField(ObjectIdField(), default=[])  # Service IDs
    preferred_customer_types = ListField(StringField(max_length=50), default=[])  # e.g., ["walk-in", "regular", "vip"]

    meta = {
        "collection": "staff_settings",
        "indexes": [
            ("tenant_id", "user_id"),
            ("tenant_id", "created_at"),
        ],
    }

    def __str__(self):
        """Return staff settings string representation."""
        return f"Settings for {self.first_name} {self.last_name}"
