"""
Client Occasion Schema
For tracking special occasions like anniversaries, first visit, etc.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClientOccasionBase(BaseModel):
    """Base schema for client occasions"""
    occasion_type: str = Field(..., description="Type of occasion (anniversary, first_visit, etc.)")
    occasion_date: datetime = Field(..., description="Date of the occasion")
    title: str = Field(..., description="Occasion title")
    description: Optional[str] = Field(None, description="Occasion description")
    send_reminder: bool = Field(True, description="Whether to send reminder")
    reminder_days_before: int = Field(7, description="Days before to send reminder")


class ClientOccasionCreate(ClientOccasionBase):
    """Schema for creating a client occasion"""
    pass


class ClientOccasionUpdate(BaseModel):
    """Schema for updating a client occasion"""
    occasion_type: Optional[str] = None
    occasion_date: Optional[datetime] = None
    title: Optional[str] = None
    description: Optional[str] = None
    send_reminder: Optional[bool] = None
    reminder_days_before: Optional[int] = None


class ClientOccasionResponse(ClientOccasionBase):
    """Schema for client occasion response"""
    id: str = Field(..., description="Occasion ID")
    client_id: str = Field(..., description="Client ID")
    tenant_id: str = Field(..., description="Tenant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True
