"""Location model for multi-location salon management."""

from datetime import datetime
from mongoengine import (
    StringField,
    BooleanField,
    ObjectIdField,
)
from app.models.base import BaseDocument


class Location(BaseDocument):
    """Location document model for salon branches/rooms."""

    name = StringField(required=True, max_length=255)
    address = StringField(null=True, max_length=500)
    phone = StringField(null=True, max_length=50)
    email = StringField(null=True, max_length=255)
    is_active = BooleanField(default=True)
    timezone = StringField(null=True, max_length=100)

    meta = {
        "collection": "locations",
        "indexes": [
            ("tenant_id", "name"),
            ("tenant_id", "is_active"),
            ("tenant_id", "-created_at"),
        ],
    }

    def __str__(self):
        return f"{self.name} ({self.address or 'No address'})"
