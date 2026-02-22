"""Schemas for time slot reservation operations."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TimeSlotReserveRequest(BaseModel):
    """Request to reserve a time slot."""
    
    staff_id: str = Field(..., description="Staff member ID")
    service_id: str = Field(..., description="Service ID")
    start_time: datetime = Field(..., description="Slot start time (UTC)")
    end_time: datetime = Field(..., description="Slot end time (UTC)")
    customer_id: Optional[str] = Field(None, description="Optional customer ID")


class TimeSlotConfirmRequest(BaseModel):
    """Request to confirm a time slot reservation."""
    
    appointment_id: str = Field(..., description="Appointment ID")


class TimeSlotReleaseRequest(BaseModel):
    """Request to release a time slot reservation."""
    
    reason: Optional[str] = Field(None, description="Optional release reason")


class TimeSlotResponse(BaseModel):
    """Response containing time slot details."""
    
    id: str = Field(..., description="TimeSlot ID")
    staff_id: str = Field(..., description="Staff member ID")
    service_id: str = Field(..., description="Service ID")
    customer_id: Optional[str] = Field(None, description="Customer ID")
    start_time: str = Field(..., description="Slot start time (ISO format)")
    end_time: str = Field(..., description="Slot end time (ISO format)")
    status: str = Field(..., description="Reservation status")
    reserved_at: str = Field(..., description="Reservation time (ISO format)")
    expires_at: str = Field(..., description="Expiration time (ISO format)")
    appointment_id: Optional[str] = Field(None, description="Associated appointment ID")
    created_at: str = Field(..., description="Creation time (ISO format)")
    updated_at: str = Field(..., description="Update time (ISO format)")


class TimeSlotListResponse(BaseModel):
    """Response containing list of time slots."""
    
    time_slots: list[TimeSlotResponse] = Field(..., description="List of time slots")
    total: int = Field(..., description="Total number of time slots")
