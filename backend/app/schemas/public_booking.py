"""Pydantic schemas for public booking requests and responses."""

from datetime import date, time
from enum import Enum
from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class PublicBookingStatus(str, Enum):
    """Status of a public booking."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"


class PublicBookingCreate(BaseModel):
    """Schema for creating a public booking."""

    service_id: str = Field(..., description="Service ID")
    staff_id: str = Field(..., description="Staff ID")
    booking_date: date = Field(..., description="Booking date")
    booking_time: time = Field(..., description="Booking time")
    duration_minutes: int = Field(
        ..., ge=15, le=480, description="Duration in minutes"
    )
    customer_name: str = Field(..., min_length=1, max_length=255)
    customer_email: EmailStr = Field(..., description="Customer email")
    customer_phone: str = Field(..., min_length=10, max_length=20)
    notes: Optional[str] = Field(None, max_length=1000)
    payment_option: Optional[str] = Field(
        "later", description="Payment option: 'now' or 'later'"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "service_id": "507f1f77bcf86cd799439011",
                "staff_id": "507f1f77bcf86cd799439012",
                "booking_date": "2024-01-20",
                "booking_time": "14:30",
                "duration_minutes": 60,
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "customer_phone": "+234 123 456 7890",
                "notes": "First time customer",
                "payment_option": "later",
            }
        }


class PublicBookingUpdate(BaseModel):
    """Schema for updating a public booking."""

    status: Optional[PublicBookingStatus] = None
    notes: Optional[str] = Field(None, max_length=1000)
    cancellation_reason: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "status": "cancelled",
                "cancellation_reason": "Customer requested cancellation",
            }
        }


class PublicBookingResponse(BaseModel):
    """Schema for public booking response."""

    id: str = Field(..., alias="_id")
    tenant_id: str
    service_id: str
    staff_id: str
    appointment_id: Optional[str] = None
    customer_name: str
    customer_email: str
    customer_phone: str
    booking_date: date
    booking_time: time
    duration_minutes: int
    status: PublicBookingStatus
    notes: Optional[str] = None
    created_at: str
    updated_at: str

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "507f1f77bcf86cd799439013",
                "tenant_id": "507f1f77bcf86cd799439010",
                "service_id": "507f1f77bcf86cd799439011",
                "staff_id": "507f1f77bcf86cd799439012",
                "appointment_id": "507f1f77bcf86cd799439014",
                "customer_name": "John Doe",
                "customer_email": "john@example.com",
                "customer_phone": "+234 123 456 7890",
                "booking_date": "2024-01-20",
                "booking_time": "14:30",
                "duration_minutes": 60,
                "status": "confirmed",
                "notes": "First time customer",
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:30:00Z",
            }
        }


class PublicServiceResponse(BaseModel):
    """Schema for public service response."""

    id: str = Field(..., alias="_id")
    name: str
    description: str
    duration_minutes: int
    price: float
    is_published: bool
    public_description: Optional[str] = None
    public_image_url: Optional[str] = None
    allow_public_booking: bool

    class Config:
        populate_by_name = True


class PublicStaffResponse(BaseModel):
    """Schema for public staff response."""

    id: str = Field(..., alias="_id")
    first_name: str
    last_name: str
    is_available_for_public_booking: bool
    bio: Optional[str] = None
    profile_image_url: Optional[str] = None

    class Config:
        populate_by_name = True


class AvailabilitySlot(BaseModel):
    """Schema for an available time slot."""

    slot_time: str = Field(..., description="Available time in HH:MM format", alias="time")
    available: bool = Field(default=True, description="Whether slot is available")

    class Config:
        populate_by_name = True


class AvailabilityResponse(BaseModel):
    """Schema for availability response."""

    availability_date: date = Field(..., description="Date for availability", alias="date")
    slots: list[AvailabilitySlot] = Field(..., description="Available time slots")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "date": "2024-01-20",
                "slots": [
                    {"time": "09:00", "available": True},
                    {"time": "09:30", "available": True},
                    {"time": "10:00", "available": False},
                    {"time": "10:30", "available": True},
                ],
            }
        }
