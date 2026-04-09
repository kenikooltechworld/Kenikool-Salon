from mongoengine import Document, EmbeddedDocument, fields
from datetime import datetime
from bson import ObjectId, Decimal128
from typing import Optional


class GroupBookingParticipant(EmbeddedDocument):
    """Individual participant in a group booking"""
    name = fields.StringField(required=True)
    email = fields.EmailField()
    phone = fields.StringField()
    service_id = fields.ObjectIdField(required=True)
    staff_id = fields.ObjectIdField()
    appointment_id = fields.ObjectIdField()  # Link to individual appointment
    status = fields.StringField(
        choices=["pending", "confirmed", "cancelled"],
        default="pending"
    )
    notes = fields.StringField()


class GroupBooking(Document):
    """Group booking model for coordinating multiple appointments"""
    tenant_id = fields.ObjectIdField(required=True)
    
    # Group details
    group_name = fields.StringField(required=True)  # e.g., "Smith Family Spa Day"
    group_type = fields.StringField(
        choices=["family", "corporate", "party", "event", "other"],
        default="other"
    )
    
    # Organizer details
    organizer_name = fields.StringField(required=True)
    organizer_email = fields.EmailField(required=True)
    organizer_phone = fields.StringField(required=True)
    organizer_customer_id = fields.ObjectIdField()  # If organizer is existing customer
    
    # Booking details
    booking_date = fields.DateTimeField(required=True)
    participants = fields.EmbeddedDocumentListField(GroupBookingParticipant)
    total_participants = fields.IntField(default=0)
    
    # Pricing
    base_total = fields.DecimalField(precision=2, default=0)
    discount_percentage = fields.FloatField(default=0)  # Group discount
    discount_amount = fields.DecimalField(precision=2, default=0)
    final_total = fields.DecimalField(precision=2, default=0)
    
    # Payment
    payment_option = fields.StringField(
        choices=["pay_now", "pay_later", "split"],
        default="pay_later"
    )
    payment_status = fields.StringField(
        choices=["pending", "partial", "paid", "refunded"],
        default="pending"
    )
    amount_paid = fields.DecimalField(precision=2, default=0)
    
    # Status
    status = fields.StringField(
        choices=["pending", "confirmed", "in_progress", "completed", "cancelled"],
        default="pending"
    )
    
    # Metadata
    special_requests = fields.StringField()
    internal_notes = fields.StringField()
    created_at = fields.DateTimeField(default=datetime.utcnow)
    updated_at = fields.DateTimeField(default=datetime.utcnow)
    confirmed_at = fields.DateTimeField()
    cancelled_at = fields.DateTimeField()
    cancellation_reason = fields.StringField()
    
    # Tracking
    is_guest = fields.BooleanField(default=True)
    ip_address = fields.StringField()
    user_agent = fields.StringField()
    
    meta = {
        "collection": "group_bookings",
        "indexes": [
            "tenant_id",
            "booking_date",
            "status",
            "organizer_email",
            ("tenant_id", "booking_date"),
            ("tenant_id", "status"),
        ]
    }
