"""Shift schema for request/response validation."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, field_validator


class ShiftBase(BaseModel):
    """Base shift schema with common fields."""

    staff_id: str = Field(..., description="Staff member ID")
    start_time: datetime = Field(..., description="Shift start time")
    end_time: datetime = Field(..., description="Shift end time")
    status: str = Field(default="scheduled", description="Shift status")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate shift status."""
        valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v

    @field_validator("end_time")
    @classmethod
    def validate_end_time(cls, v, info):
        """Validate that end_time is after start_time."""
        if "start_time" in info.data and v <= info.data["start_time"]:
            raise ValueError("end_time must be after start_time")
        return v


class ShiftCreate(ShiftBase):
    """Schema for creating a new shift."""

    pass


class ShiftUpdate(BaseModel):
    """Schema for updating a shift."""

    status: str = Field(None, description="Shift status")
    start_time: datetime = Field(None, description="Shift start time")
    end_time: datetime = Field(None, description="Shift end time")

    @field_validator("status")
    @classmethod
    def validate_status(cls, v):
        """Validate shift status."""
        if v is None:
            return v
        valid_statuses = ["scheduled", "in_progress", "completed", "cancelled"]
        if v not in valid_statuses:
            raise ValueError(f"Status must be one of {valid_statuses}")
        return v


class ShiftResponse(ShiftBase):
    """Schema for shift response."""

    id: str = Field(..., description="Shift ID", alias="_id")
    labor_cost: Decimal = Field(None, description="Calculated labor cost")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        populate_by_name = True
        from_attributes = True


class ShiftListResponse(BaseModel):
    """Schema for shift list response."""

    shifts: list[ShiftResponse] = Field(..., description="List of shifts")
    total: int = Field(..., description="Total number of shifts")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
