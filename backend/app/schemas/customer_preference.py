"""Customer preference schemas for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field


class CustomerPreferenceCreate(BaseModel):
    """Schema for creating customer preferences."""

    preferred_staff_ids: List[str] = Field(default=[], description="List of preferred staff IDs")
    preferred_service_ids: List[str] = Field(default=[], description="List of preferred service IDs")
    communication_methods: List[str] = Field(
        default=["email"],
        description="Preferred communication methods (email, sms, phone)"
    )
    preferred_time_slots: List[str] = Field(
        default=[],
        description="Preferred time slots (morning, afternoon, evening)"
    )
    language: str = Field(default="en", max_length=10, description="Preferred language")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional preference notes")


class CustomerPreferenceUpdate(BaseModel):
    """Schema for updating customer preferences."""

    preferred_staff_ids: Optional[List[str]] = Field(None, description="List of preferred staff IDs")
    preferred_service_ids: Optional[List[str]] = Field(None, description="List of preferred service IDs")
    communication_methods: Optional[List[str]] = Field(None, description="Preferred communication methods")
    preferred_time_slots: Optional[List[str]] = Field(None, description="Preferred time slots")
    language: Optional[str] = Field(None, max_length=10, description="Preferred language")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional preference notes")


class CustomerPreferenceResponse(BaseModel):
    """Schema for customer preference response."""

    id: str = Field(..., description="Preference ID")
    customer_id: str = Field(..., description="Customer ID")
    preferred_staff_ids: List[str] = Field(default=[], description="List of preferred staff IDs")
    preferred_service_ids: List[str] = Field(default=[], description="List of preferred service IDs")
    communication_methods: List[str] = Field(default=["email"], description="Preferred communication methods")
    preferred_time_slots: List[str] = Field(default=[], description="Preferred time slots")
    language: str = Field(..., description="Preferred language")
    notes: Optional[str] = Field(None, description="Additional preference notes")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True
