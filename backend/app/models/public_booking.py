"""Public booking model for guest appointments via subdomain."""

from datetime import datetime
from enum import Enum
from typing import Optional

from mongoengine import (
    Document,
    StringField,
    DateTimeField,
    DateField,
    IntField,
    ObjectIdField,
    EnumField,
    BooleanField,
)


class PublicBookingStatus(str, Enum):
    """Status of a public booking."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PublicBooking(Document):
    """Public booking model for guest appointments via subdomain."""

    tenant_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=False, null=True)  # Null for guest bookings
    service_id = ObjectIdField(required=True)
    staff_id = ObjectIdField(required=True)
    appointment_id = ObjectIdField(required=False, null=True)  # Link to created appointment

    # Guest customer information
    customer_name = StringField(required=True, max_length=255)
    customer_email = StringField(required=True, max_length=255)
    customer_phone = StringField(required=True, max_length=20)

    # Booking details
    booking_date = DateField(required=True)
    booking_time = StringField(required=True)  # Store as HH:MM format
    duration_minutes = IntField(required=True, min_value=15, max_value=480)
    status = EnumField(PublicBookingStatus, default=PublicBookingStatus.PENDING)

    # Idempotency key for preventing duplicate bookings from retries
    idempotency_key = StringField(required=False, null=True, unique_with=['tenant_id'])

    # Additional information
    notes = StringField(required=False, null=True, max_length=1000)
    cancellation_reason = StringField(required=False, null=True, max_length=500)

    # Payment information
    payment_option = StringField(
        required=False, null=True, choices=["now", "later"], default="later"
    )
    payment_id = ObjectIdField(required=False, null=True)  # Link to payment record
    payment_status = StringField(
        required=False, null=True, choices=["pending", "completed", "failed"]
    )

    # Timestamps
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)
    cancelled_at = DateTimeField(required=False, null=True)

    # Metadata
    ip_address = StringField(required=False, null=True)  # For rate limiting tracking
    user_agent = StringField(required=False, null=True)  # For analytics

    meta = {
        "collection": "public_bookings",
        "indexes": [
            ("tenant_id", "created_at"),
            ("tenant_id", "booking_date"),
            ("tenant_id", "status"),
            ("tenant_id", "customer_email"),
            ("tenant_id", "service_id"),
            ("tenant_id", "staff_id"),
            ("tenant_id", "idempotency_key"),
            ("appointment_id",),
        ],
    }

    def __str__(self):
        return f"PublicBooking({self.customer_name}, {self.booking_date} {self.booking_time})"
