"""Pydantic schemas for availability management."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import time, date


class BreakTime(BaseModel):
    """Break time within availability window."""

    start_time: time = Field(...)
    end_time: time = Field(...)


class AvailabilityCreateRequest(BaseModel):
    """Request schema for creating availability."""

    staff_id: str = Field(..., description="Staff member ID")
    day_of_week: Optional[int] = Field(None, ge=0, le=6, description="Day of week (0=Monday, 6=Sunday) for recurring schedules")
    start_time: time = Field(..., description="Start time of availability")
    end_time: time = Field(..., description="End time of availability")
    is_recurring: bool = Field(default=False, description="Whether this is a recurring schedule")
    effective_from: date = Field(..., description="Date when availability becomes effective")
    effective_to: Optional[date] = Field(None, description="Date when availability ends (null for ongoing)")
    breaks: List[BreakTime] = Field(default=[], description="Break times within availability window")
    is_active: bool = Field(default=True, description="Whether availability is active")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class AvailabilityUpdateRequest(BaseModel):
    """Request schema for updating availability."""

    day_of_week: Optional[int] = Field(None, ge=0, le=6)
    start_time: Optional[time] = None
    end_time: Optional[time] = None
    is_recurring: Optional[bool] = None
    effective_from: Optional[date] = None
    effective_to: Optional[date] = None
    breaks: Optional[List[BreakTime]] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = Field(None, max_length=500)


class AvailabilityResponse(BaseModel):
    """Response schema for availability."""

    id: str
    staff_id: str
    day_of_week: Optional[int]
    start_time: str
    end_time: str
    is_recurring: bool
    effective_from: str
    effective_to: Optional[str]
    breaks: List[dict]
    is_active: bool
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class AvailabilityListResponse(BaseModel):
    """Response schema for listing availability."""

    availabilities: List[AvailabilityResponse]
    total: int
    page: int
    page_size: int


class AvailableSlot(BaseModel):
    """Available time slot for booking."""

    start_time: str = Field(..., description="Start time of slot (HH:MM format)")
    end_time: str = Field(..., description="End time of slot (HH:MM format)")
    staff_id: str = Field(..., description="Staff member ID")
    duration_minutes: int = Field(..., description="Duration of the slot in minutes")
    isAvailable: bool = Field(..., description="Whether the slot is available for booking")


class AvailableSlotsResponse(BaseModel):
    """Response schema for available slots."""

    date: str = Field(..., description="Date for which slots are available")
    slots: List[AvailableSlot] = Field(..., description="List of available slots")
    staff_id: Optional[str] = Field(None, description="Staff member ID (if filtered)")
    total_slots: int = Field(..., description="Total number of available slots")
