"""Availability event model for real-time updates."""

from datetime import datetime
from typing import Optional
from mongoengine import Document, ObjectIdField, DateTimeField, StringField, IntField
from bson import ObjectId


class AvailabilityEvent(Document):
    """Model for tracking availability changes for real-time updates."""
    
    tenant_id = ObjectIdField(required=True)
    service_id = ObjectIdField(required=True)
    staff_id = ObjectIdField()
    date = DateTimeField(required=True)
    time_slot = StringField(required=True)  # e.g., "09:00"
    event_type = StringField(required=True)  # "slot_taken", "slot_freed", "slot_blocked"
    viewer_count = IntField(default=0)  # Number of users viewing this slot
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'availability_events',
        'indexes': [
            'tenant_id',
            'service_id',
            'staff_id',
            'date',
            ('tenant_id', 'date', 'service_id'),
            'created_at',  # For cleanup of old events
        ]
    }
