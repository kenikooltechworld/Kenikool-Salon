"""
Booking schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.base import BaseSchema


class GroupSubtype(str, Enum):
    """Group booking subtypes"""
    FAMILY = "family"
    CORPORATE = "corporate"
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    GENERAL = "general"


class BookingCreate(BaseModel):
    """Booking creation request"""
    location_id: str = Field(..., description="Location ID (required)")
    client_name: str = Field(..., min_length=2, max_length=100)
    client_phone: str = Field(..., min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    service_id: str = Field(..., description="Service ID")
    stylist_id: str = Field(..., description="Stylist ID")
    booking_date: str = Field(..., description="Booking date/time in ISO format")
    notes: Optional[str] = Field(None, max_length=500)
    group_subtype: Optional[GroupSubtype] = None


class BookingEdit(BaseModel):
    """Booking edit request"""
    location_id: Optional[str] = Field(None, description="Location ID (cannot be changed after creation)")
    client_name: Optional[str] = Field(None, min_length=2, max_length=100)
    client_phone: Optional[str] = Field(None, min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    service_id: Optional[str] = Field(None, description="Service ID")
    stylist_id: Optional[str] = Field(None, description="Stylist ID")
    booking_date: Optional[str] = Field(None, description="Booking date/time in ISO format")
    notes: Optional[str] = Field(None, max_length=500)
    group_subtype: Optional[GroupSubtype] = None


class BookingStatusUpdate(BaseModel):
    """Booking status update request"""
    status: str = Field(..., description="Status: pending, confirmed, completed, cancelled, no_show")


class BookingFilter(BaseModel):
    """Booking filter parameters"""
    status: Optional[str] = None
    stylist_id: Optional[str] = None
    client_id: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


class BookingResponse(BaseSchema):
    """Booking response"""
    id: str
    tenant_id: str
    location_id: str
    location_name: str
    client_id: str
    client_name: str
    client_phone: str
    service_id: str
    service_name: str
    service_price: float
    stylist_id: str
    stylist_name: str
    booking_date: datetime
    duration_minutes: int
    status: str
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None


class TimeSlotResponse(BaseModel):
    """Available time slot response"""
    start_time: str
    end_time: str
    available: bool


class AvailabilityRequest(BaseModel):
    """Availability check request"""
    stylist_id: str
    service_id: str
    date: str = Field(..., description="Date in YYYY-MM-DD format")


class AvailabilityResponse(BaseModel):
    """Availability response"""
    date: str
    slots: List[TimeSlotResponse]



class RecurringFrequency(str, Enum):
    """Recurring booking frequency"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class RecurringBookingCreate(BaseModel):
    """Recurring booking creation request"""
    client_name: str = Field(..., min_length=2, max_length=100)
    client_phone: str = Field(..., min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    service_id: str = Field(..., description="Service ID")
    stylist_id: str = Field(..., description="Stylist ID")
    booking_date: str = Field(..., description="Booking date/time in ISO format")
    notes: Optional[str] = Field(None, max_length=500)
    group_subtype: Optional[GroupSubtype] = None
    frequency: RecurringFrequency = Field(..., description="Frequency: daily, weekly, monthly")
    interval: int = Field(1, ge=1, description="Every N days/weeks/months")
    end_date: Optional[str] = Field(None, description="End date in YYYY-MM-DD format")
    occurrences: Optional[int] = Field(None, ge=1, description="Number of occurrences")
    skip_conflicts: bool = Field(True, description="Skip conflicting occurrences")


class BulkActionType(str, Enum):
    """Bulk action types"""
    UPDATE_STATUS = "update_status"
    CANCEL = "cancel"
    SEND_REMINDER = "send_reminder"
    EXPORT = "export"


class BulkBookingAction(BaseModel):
    """Bulk booking action request"""
    booking_ids: List[str] = Field(..., min_items=1, description="List of booking IDs")
    action: BulkActionType = Field(..., description="Action to perform")
    status: Optional[str] = Field(None, description="New status for update_status action")
    cancellation_reason: Optional[str] = Field(None, max_length=500, description="Reason for cancel action")


class BookingAnalyticsResponse(BaseModel):
    """Booking analytics response"""
    total_bookings: int
    bookings_by_status: dict
    bookings_by_stylist: dict
    bookings_by_subtype: dict
    cancellation_rate: float
    no_show_rate: float
    completion_rate: float
    peak_hours: List[dict]
    peak_days: List[dict]
    total_revenue: float
    revenue_by_subtype: dict
    trend_data: List[dict]
