"""Base document model for all entities."""

from datetime import datetime
from mongoengine import Document, ObjectIdField, DateTimeField, StringField


class BaseDocument(Document):
    """Base document class for all entities with tenant isolation."""

    tenant_id = ObjectIdField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    updated_at = DateTimeField(default=datetime.utcnow)

    meta = {
        "abstract": True,
        "indexes": [
            ("tenant_id", "_id"),
            ("tenant_id", "created_at"),
        ],
    }

    def save(self, *args, **kwargs):
        """Override save to update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
        return super().save(*args, **kwargs)
