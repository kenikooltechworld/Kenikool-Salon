"""Pydantic schemas for appointment management."""

from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from decimal import Decimal
from datetime import datetime


class AppointmentCreateRequest(BaseModel):
    """Request schema for creating an appointment."""

    customer_id: Optional[str] = Field(None, alias="customerId", description="Customer ID (optional if creating new customer)")
    customer_name: Optional[str] = Field(None, alias="customerName", description="Customer name (for new customers)")
    customer_email: Optional[str] = Field(None, alias="customerEmail", description="Customer email (for new customers)")
    customer_phone: Optional[str] = Field(None, alias="customerPhone", description="Customer phone (for new customers)")
    staff_id: str = Field(..., alias="staffId", description="Staff member ID")
    service_id: str = Field(..., alias="serviceId", description="Service ID")
    location_id: Optional[str] = Field(None, alias="locationId", description="Location ID")
    start_time: str = Field(..., alias="startTime", description="Appointment start time (local timezone, ISO format)")
    end_time: str = Field(..., alias="endTime", description="Appointment end time (local timezone, ISO format)")
    notes: Optional[str] = Field(None, max_length=1000, description="Appointment notes")
    payment_option: Optional[str] = Field(None, alias="paymentOption", description="Payment option: 'now' or 'later'")

    model_config = ConfigDict(
        populate_by_name=True,
        str_strip_whitespace=True
    )


class AppointmentUpdateRequest(BaseModel):
    """Request schema for updating an appointment."""

    status: Optional[str] = Field(None, description="Appointment status")
    notes: Optional[str] = Field(None, max_length=1000, description="Appointment notes")
    cancellation_reason: Optional[str] = Field(None, max_length=500, description="Cancellation reason")


class AppointmentCancelRequest(BaseModel):
    """Request schema for cancelling an appointment."""

    reason: Optional[str] = Field(None, max_length=500, description="Cancellation reason")


class AppointmentConfirmRequest(BaseModel):
    """Request schema for confirming an appointment."""

    time_slot_id: Optional[str] = Field(None, description="Optional TimeSlot ID to confirm")


class AppointmentResponse(BaseModel):
    """Response schema for an appointment."""

    id: str
    customer_id: str
    staff_id: str
    service_id: str
    location_id: Optional[str]
    start_time: str
    end_time: str
    status: str
    notes: Optional[str]
    price: Optional[Decimal]
    cancellation_reason: Optional[str]
    cancelled_at: Optional[str]
    no_show_reason: Optional[str]
    marked_no_show_at: Optional[str]
    confirmed_at: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class AppointmentListResponse(BaseModel):
    """Response schema for listing appointments."""

    appointments: List[AppointmentResponse]
    total: int
    page: int
    page_size: int


class AvailableSlot(BaseModel):
    """Response schema for an available time slot."""

    start_time: str = Field(..., description="Slot start time (UTC)")
    end_time: str = Field(..., description="Slot end time (UTC)")
    staff_id: str = Field(..., description="Staff member ID")
    available: bool = Field(default=True, description="Whether slot is available")


class AvailableSlotsResponse(BaseModel):
    """Response schema for available slots."""

    date: str = Field(..., description="Date for slots")
    slots: List[AvailableSlot]
    total_available: int



class CalendarAvailabilityResponse(BaseModel):
    """Response schema for calendar availability."""

    start_date: str = Field(..., description="Start date (ISO format)")
    end_date: str = Field(..., description="End date (ISO format)")
    availability: dict = Field(..., description="Availability by date")
    timezone: str = Field(..., description="Timezone for slots")


class DayViewResponse(BaseModel):
    """Response schema for day view appointments."""

    date: str = Field(..., description="Date (ISO format)")
    appointments: List[AppointmentResponse] = Field(..., description="Appointments for the day")
    total: int = Field(..., description="Total appointments")


class WeekViewResponse(BaseModel):
    """Response schema for week view appointments."""

    week_start: str = Field(..., description="Week start date (ISO format)")
    week_end: str = Field(..., description="Week end date (ISO format)")
    appointments: List[AppointmentResponse] = Field(..., description="Appointments for the week")
    total: int = Field(..., description="Total appointments")


class MonthViewResponse(BaseModel):
    """Response schema for month view appointments."""

    month: str = Field(..., description="Month (YYYY-MM format)")
    appointments: List[AppointmentResponse] = Field(..., description="Appointments for the month")
    total: int = Field(..., description="Total appointments")
