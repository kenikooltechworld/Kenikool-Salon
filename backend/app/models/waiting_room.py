"""Waiting Room model for managing queue and check-in."""

from datetime import datetime, timedelta
from mongoengine import (
    StringField,
    DateTimeField,
    BooleanField,
    IntField,
    ListField,
    DictField,
    ObjectIdField,
)
from app.models.base import BaseDocument


class QueueEntry(BaseDocument):
    """Queue entry model for tracking customers in waiting room."""

    STATUSES = ["waiting", "called", "in_service", "completed", "no_show", "cancelled"]

    appointment_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    customer_name = StringField(required=True)
    customer_phone = StringField(null=True)

    # Queue tracking
    check_in_time = DateTimeField(required=True)
    called_time = DateTimeField(null=True)
    service_start_time = DateTimeField(null=True)
    service_end_time = DateTimeField(null=True)

    status = StringField(choices=STATUSES, default="waiting")
    position = IntField(default=0)  # Position in queue

    # Wait time tracking
    wait_duration_minutes = IntField(null=True)  # Actual wait time
    service_duration_minutes = IntField(null=True)  # Actual service time
    estimated_wait_time_minutes = IntField(null=True)  # Estimated wait time at check-in

    # Service information
    service_id = ObjectIdField(null=True)
    service_name = StringField(null=True)
    staff_id = ObjectIdField(null=True)
    staff_name = StringField(null=True)

    # Notes
    notes = StringField(null=True)
    no_show_reason = StringField(null=True)

    meta = {
        "collection": "queue_entries",
        "indexes": [
            ("tenant_id", "status", "-check_in_time"),
            ("tenant_id", "appointment_id"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "check_in_time"),
            ("tenant_id", "-created_at"),
        ],
    }

    def __str__(self):
        """Return queue entry string representation."""
        return f"{self.customer_name} - Position {self.position} ({self.status})"

    def mark_called(self):
        """Mark customer as called."""
        self.status = "called"
        self.called_time = datetime.utcnow()
        self.save()

    def mark_in_service(self):
        """Mark customer as in service."""
        self.status = "in_service"
        self.service_start_time = datetime.utcnow()
        self.save()

    def mark_completed(self):
        """Mark service as completed."""
        self.status = "completed"
        self.service_end_time = datetime.utcnow()

        # Calculate wait and service durations
        if self.check_in_time:
            self.wait_duration_minutes = int(
                (self.called_time - self.check_in_time).total_seconds() / 60
            )
        if self.service_start_time and self.service_end_time:
            self.service_duration_minutes = int(
                (self.service_end_time - self.service_start_time).total_seconds() / 60
            )

        self.save()

    def mark_no_show(self, reason: str = None):
        """Mark customer as no-show."""
        self.status = "no_show"
        self.no_show_reason = reason
        self.save()

    def mark_cancelled(self):
        """Mark queue entry as cancelled."""
        self.status = "cancelled"
        self.save()


class WaitingRoom(BaseDocument):
    """Waiting room model for tracking queue status."""

    location_id = ObjectIdField(null=True)  # Reference to location
    name = StringField(required=True)  # e.g., "Main Waiting Room", "VIP Lounge"

    # Queue status
    current_queue_count = IntField(default=0)
    average_wait_time_minutes = IntField(default=0)
    max_queue_length = IntField(null=True)  # Maximum queue length before overflow

    # Status
    is_active = BooleanField(default=True)
    is_accepting_checkins = BooleanField(default=True)

    # Metadata
    last_updated = DateTimeField(default=datetime.utcnow)
    notes = StringField(null=True)

    meta = {
        "collection": "waiting_rooms",
        "indexes": [
            ("tenant_id", "location_id"),
            ("tenant_id", "is_active"),
            ("tenant_id", "-last_updated"),
        ],
    }

    def __str__(self):
        """Return waiting room string representation."""
        return f"{self.name} - {self.current_queue_count} waiting"

    def update_queue_status(self, queue_count: int, avg_wait_time: int):
        """Update queue status."""
        self.current_queue_count = queue_count
        self.average_wait_time_minutes = avg_wait_time
        self.last_updated = datetime.utcnow()
        self.save()


class QueueHistory(BaseDocument):
    """Queue history model for analytics and reporting."""

    appointment_id = ObjectIdField(required=True)
    customer_id = ObjectIdField(required=True)
    customer_name = StringField(required=True)

    # Timeline
    check_in_time = DateTimeField(required=True)
    called_time = DateTimeField(null=True)
    service_start_time = DateTimeField(null=True)
    service_end_time = DateTimeField(null=True)

    # Durations
    wait_duration_minutes = IntField(null=True)
    service_duration_minutes = IntField(null=True)
    total_duration_minutes = IntField(null=True)

    # Status
    status = StringField(choices=QueueEntry.STATUSES, required=True)
    no_show_reason = StringField(null=True)

    # Service information
    service_id = ObjectIdField(null=True)
    service_name = StringField(null=True)
    staff_id = ObjectIdField(null=True)
    staff_name = StringField(null=True)

    meta = {
        "collection": "queue_history",
        "indexes": [
            ("tenant_id", "appointment_id"),
            ("tenant_id", "customer_id"),
            ("tenant_id", "check_in_time"),
            ("tenant_id", "status"),
            ("tenant_id", "-created_at"),
        ],
    }

    def __str__(self):
        """Return history string representation."""
        return f"{self.customer_name} - {self.status} ({self.check_in_time})"
