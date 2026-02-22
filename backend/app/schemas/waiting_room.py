"""Waiting room schemas."""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class QueueEntryCheckIn(BaseModel):
    """Schema for checking in a customer."""

    appointment_id: str
    customer_id: str
    customer_name: str
    customer_phone: Optional[str] = None
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    staff_id: Optional[str] = None
    staff_name: Optional[str] = None
    estimated_wait_time: Optional[int] = None


class QueueEntryResponse(BaseModel):
    """Schema for queue entry response."""

    id: str = Field(alias="_id")
    appointment_id: str
    customer_id: str
    customer_name: str
    customer_phone: Optional[str] = None
    check_in_time: datetime
    called_time: Optional[datetime] = None
    service_start_time: Optional[datetime] = None
    service_end_time: Optional[datetime] = None
    status: str
    position: int
    wait_duration_minutes: Optional[int] = None
    service_duration_minutes: Optional[int] = None
    estimated_wait_time_minutes: Optional[int] = None
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    staff_id: Optional[str] = None
    staff_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class WaitingRoomResponse(BaseModel):
    """Schema for waiting room response."""

    id: str = Field(alias="_id")
    name: str
    location_id: Optional[str] = None
    current_queue_count: int
    average_wait_time_minutes: int
    max_queue_length: Optional[int] = None
    is_active: bool
    is_accepting_checkins: bool
    last_updated: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueueHistoryResponse(BaseModel):
    """Schema for queue history response."""

    id: str = Field(alias="_id")
    appointment_id: str
    customer_id: str
    customer_name: str
    check_in_time: datetime
    called_time: Optional[datetime] = None
    service_start_time: Optional[datetime] = None
    service_end_time: Optional[datetime] = None
    wait_duration_minutes: Optional[int] = None
    service_duration_minutes: Optional[int] = None
    total_duration_minutes: Optional[int] = None
    status: str
    service_id: Optional[str] = None
    service_name: Optional[str] = None
    staff_id: Optional[str] = None
    staff_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QueueStatsResponse(BaseModel):
    """Schema for queue statistics response."""

    current_queue: dict
    today: dict
    average_wait_time_minutes: int
