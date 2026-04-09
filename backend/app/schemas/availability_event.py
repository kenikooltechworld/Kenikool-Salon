"""Schemas for availability events."""

from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class AvailabilityEventBase(BaseModel):
    """Base schema for availability events."""
    service_id: str
    staff_id: Optional[str] = None
    date: datetime
    time_slot: str
    event_type: str  # "slot_taken", "slot_freed", "slot_blocked"


class AvailabilityEventCreate(AvailabilityEventBase):
    """Schema for creating availability events."""
    pass


class AvailabilityEventResponse(AvailabilityEventBase):
    """Schema for availability event responses."""
    id: str
    tenant_id: str
    viewer_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class SlotViewerUpdate(BaseModel):
    """Schema for slot viewer count updates."""
    service_id: str
    staff_id: Optional[str] = None
    date: datetime
    time_slot: str
    action: str  # "join" or "leave"


class SlotViewerResponse(BaseModel):
    """Schema for slot viewer count response."""
    service_id: str
    staff_id: Optional[str] = None
    date: datetime
    time_slot: str
    viewer_count: int
