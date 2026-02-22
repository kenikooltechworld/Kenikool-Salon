"""Schemas for AppointmentHistory API responses."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field
from typing import Optional, List


class AppointmentHistoryResponse(BaseModel):
    """Response schema for a single appointment history entry."""

    id: str = Field(..., description="History entry ID")
    customer_id: str = Field(..., description="Customer ID")
    appointment_id: str = Field(..., description="Appointment ID")
    service_id: str = Field(..., description="Service ID")
    staff_id: str = Field(..., description="Staff ID")
    service_name: str = Field(..., description="Service name")
    staff_name: str = Field(..., description="Staff name")
    appointment_date: str = Field(..., description="Appointment date (ISO format)")
    appointment_time: str = Field(..., description="Appointment time (HH:MM format)")
    notes: str = Field(default="", description="Optional notes")
    rating: int = Field(default=0, description="Rating (0-5)")
    feedback: str = Field(default="", description="Optional feedback")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")

    class Config:
        """Pydantic config."""
        from_attributes = True


class AppointmentHistoryListResponse(BaseModel):
    """Response schema for listing appointment history."""

    history: List[AppointmentHistoryResponse] = Field(..., description="List of history entries")
    total: int = Field(..., description="Total number of entries")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")

    class Config:
        """Pydantic config."""
        from_attributes = True


class AppointmentHistoryDetailResponse(BaseModel):
    """Response schema for a single appointment history entry with details."""

    id: str = Field(..., description="History entry ID")
    customer_id: str = Field(..., description="Customer ID")
    appointment_id: str = Field(..., description="Appointment ID")
    service_id: str = Field(..., description="Service ID")
    staff_id: str = Field(..., description="Staff ID")
    service_name: str = Field(..., description="Service name")
    staff_name: str = Field(..., description="Staff name")
    appointment_date: str = Field(..., description="Appointment date (ISO format)")
    appointment_time: str = Field(..., description="Appointment time (HH:MM format)")
    notes: str = Field(default="", description="Optional notes")
    rating: int = Field(default=0, description="Rating (0-5)")
    feedback: str = Field(default="", description="Optional feedback")
    created_at: str = Field(..., description="Creation timestamp (ISO format)")

    class Config:
        """Pydantic config."""
        from_attributes = True
