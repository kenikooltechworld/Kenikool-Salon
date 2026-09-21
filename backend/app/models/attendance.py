"""Attendance model for staff clock-in/clock-out tracking."""
from datetime import datetime
from mongoengine import (
    StringField, DateTimeField, ObjectIdField, BooleanField, DictField, IntField, FloatField
)
from app.models.base import BaseDocument


class AttendanceRecord(BaseDocument):
    """Attendance record for a staff member's work session."""

    staff_id = ObjectIdField(required=True)
    tenant_id = ObjectIdField(required=True)

    shift_id = ObjectIdField(null=True)

    check_in_time = DateTimeField(required=True)
    check_out_time = DateTimeField(null=True)

    date = DateTimeField(required=True)

    status = StringField(
        required=True,
        choices=["checked_in", "checked_out", "on_break", "completed"],
        default="checked_in",
    )

    hours_worked = FloatField(null=True, default=0.0)
    break_minutes = IntField(default=0)
    is_late = BooleanField(default=False)
    is_early_departure = BooleanField(default=False)
    notes = StringField(max_length=1000, null=True)
    verified_by = ObjectIdField(null=True)

    meta = {
        "collection": "attendance_records",
        "indexes": [
            ("tenant_id", "staff_id", "date"),
            ("tenant_id", "staff_id", "-date"),
            ("tenant_id", "staff_id", "status"),
            ("tenant_id", "date"),
            ("staff_id", "check_in_time"),
        ],
    }

    def __str__(self):
        return f"AttendanceRecord(staff={self.staff_id}, date={self.date})"
