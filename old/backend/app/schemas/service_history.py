"""
Service History schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ServiceHistoryItem(BaseModel):
    """Single service history item"""
    booking_id: str = Field(alias="bookingId")
    service_id: str = Field(alias="serviceId")
    service_name: str = Field(alias="serviceName")
    stylist_id: str = Field(alias="stylistId")
    stylist_name: str = Field(alias="stylistName")
    booking_date: datetime = Field(alias="bookingDate")
    duration_minutes: int = Field(alias="durationMinutes")
    cost: float
    status: str
    notes: Optional[str] = None
    photos: List[str] = []  # Photo URLs
    
    class Config:
        populate_by_name = True
        by_alias = True


class ServiceHistoryFilter(BaseModel):
    """Service history filter parameters"""
    start_date: Optional[datetime] = Field(None, description="Filter from this date")
    end_date: Optional[datetime] = Field(None, description="Filter until this date")
    service_type: Optional[str] = Field(None, description="Filter by service category")
    stylist_id: Optional[str] = Field(None, description="Filter by stylist")
    offset: int = Field(0, ge=0)
    limit: int = Field(20, ge=1, le=100)


class ServiceHistoryResponse(BaseModel):
    """Service history response with pagination"""
    items: List[ServiceHistoryItem]
    total: int
    page_info: dict
    
    class Config:
        populate_by_name = True
