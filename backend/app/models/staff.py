"""Staff model for staff management."""

from datetime import datetime
from mongoengine import StringField, DecimalField, ListField, DateField, DateTimeField, ObjectIdField, BooleanField
from app.models.base import BaseDocument


class Staff(BaseDocument):
    """Staff document model with specialties, certifications, and flexible payment structure."""

    user_id = ObjectIdField(required=True)  # Reference to User model
    specialties = ListField(StringField(max_length=100), default=[])  # e.g., ["haircut", "coloring"]
    certifications = ListField(StringField(max_length=255), default=[])  # e.g., ["Cosmetology License", "CPR Certified"]
    certification_files = ListField(StringField(max_length=500), default=[])  # URLs to uploaded certificate files
    payment_type = StringField(
        choices=["hourly", "daily", "weekly", "monthly", "commission"],
        default="hourly"
    )  # Payment type for the staff member
    payment_rate = DecimalField(required=False, min_value=0, default=0)  # Payment rate based on payment_type
    hire_date = DateField(null=True)  # Date staff member was hired
    bio = StringField(max_length=500, null=True)  # Staff bio/description
    profile_image_url = StringField(max_length=500, null=True)  # Profile image URL
    status = StringField(
        choices=["active", "inactive", "on_leave", "terminated"],
        default="active"
    )
    # Public booking flag - uses profile_image_url and bio for public display
    is_available_for_public_booking = BooleanField(default=False)

    meta = {
        "collection": "staff",
        "indexes": [
            ("tenant_id", "user_id"),
            ("tenant_id", "status"),
            ("tenant_id", "created_at"),
            ("tenant_id", "specialties"),
        ],
    }

    def __str__(self):
        """Return staff string representation."""
        return f"Staff(user_id={self.user_id}, payment_type={self.payment_type}, payment_rate={self.payment_rate})"
