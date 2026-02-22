"""Database models."""

from app.models.base import BaseDocument
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role, Permission
from app.models.session import Session
from app.models.service import Service
from app.models.availability import Availability
from app.models.appointment import Appointment
from app.models.time_slot import TimeSlot
from app.models.audit_log import AuditLog
from app.models.temp_registration import TempRegistration
from app.models.staff import Staff
from app.models.customer import Customer

__all__ = [
    "BaseDocument",
    "Tenant",
    "User",
    "Role",
    "Permission",
    "Session",
    "Service",
    "Availability",
    "Appointment",
    "TimeSlot",
    "AuditLog",
    "TempRegistration",
    "Staff",
    "Customer",
]
