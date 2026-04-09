"""Model for tracking recent booking activities for social proof."""

from mongoengine import Document, StringField, DateTimeField, ObjectIdField, BooleanField
from datetime import datetime
from bson import ObjectId


class BookingActivity(Document):
    """Track recent booking activities for social proof display"""
    
    meta = {
        'collection': 'booking_activities',
        'indexes': [
            'tenant_id',
            'created_at',
            {'fields': ['tenant_id', '-created_at']},
            {'fields': ['tenant_id', 'is_visible', '-created_at']},
        ]
    }
    
    tenant_id = ObjectIdField(required=True)
    customer_name = StringField(required=True, max_length=100)  # Anonymized or first name only
    service_name = StringField(required=True, max_length=200)
    booking_type = StringField(choices=['appointment', 'package', 'membership', 'group'], default='appointment')
    is_visible = BooleanField(default=True)  # Can be toggled off by admin
    created_at = DateTimeField(default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary for API response"""
        return {
            'id': str(self.id),
            'customer_name': self.customer_name,
            'service_name': self.service_name,
            'booking_type': self.booking_type,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
