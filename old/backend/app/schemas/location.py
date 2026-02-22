"""Pydantic schemas for location management system."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator


class LocationStatus(str, Enum):
    """Location status options"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    TEMPORARILY_CLOSED = "temporarily_closed"


# Request Schemas
class LocationBase(BaseModel):
    """Base schema with common location fields"""
    name: str = Field(..., min_length=1, max_length=255)
    address: str = Field(..., min_length=1, max_length=500)
    city: str = Field(..., min_length=1, max_length=100)
    state: str = Field(..., min_length=1, max_length=100)
    country: str = Field(..., min_length=1, max_length=100)
    postal_code: str = Field(..., min_length=1, max_length=20)
    phone: str = Field(..., min_length=1, max_length=20)
    email: str = Field(..., min_length=1, max_length=255)
    timezone: str = Field(default="UTC", max_length=50)
    status: LocationStatus = LocationStatus.ACTIVE
    is_primary: bool = False
    amenities: List[str] = Field(default_factory=list)
    capacity: int = Field(default=1, ge=1)
    manager_id: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    reopening_date: Optional[datetime] = None


class LocationCreate(LocationBase):
    """Schema for creating a location"""
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None


class LocationUpdate(BaseModel):
    """Schema for updating a location"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, min_length=1, max_length=500)
    city: Optional[str] = Field(None, min_length=1, max_length=100)
    state: Optional[str] = Field(None, min_length=1, max_length=100)
    country: Optional[str] = Field(None, min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, min_length=1, max_length=20)
    phone: Optional[str] = Field(None, min_length=1, max_length=20)
    email: Optional[str] = Field(None, min_length=1, max_length=255)
    timezone: Optional[str] = Field(None, max_length=50)
    status: Optional[LocationStatus] = None
    is_primary: Optional[bool] = None
    amenities: Optional[List[str]] = None
    capacity: Optional[int] = Field(None, ge=1)
    manager_id: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
    reopening_date: Optional[datetime] = None


class LocationImageResponse(BaseModel):
    """Schema for location image"""
    id: str
    url: str
    is_primary: bool = False
    uploaded_at: datetime


class LocationAnalytics(BaseModel):
    """Schema for location analytics"""
    total_revenue: float = 0.0
    total_bookings: int = 0
    completed_bookings: int = 0
    occupancy_rate: float = 0.0
    average_booking_value: float = 0.0
    top_services: List[Dict[str, Any]] = Field(default_factory=list)
    staff_performance: List[Dict[str, Any]] = Field(default_factory=list)


class LocationResponse(BaseModel):
    """Schema for location response"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    name: str
    address: str
    city: str
    state: str
    country: str
    postal_code: str
    phone: str
    email: str
    timezone: str
    status: LocationStatus
    is_primary: bool
    amenities: List[str]
    capacity: int
    manager_id: Optional[str] = None
    business_hours: Optional[Dict[str, Any]] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    formatted_address: Optional[str] = None
    reopening_date: Optional[datetime] = None
    images: List[LocationImageResponse] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True
        use_enum_values = True


class LocationListResponse(BaseModel):
    """Schema for location list response"""
    items: List[LocationResponse]
    total: int
    page: int
    limit: int
    pages: int


class LocationDependencies(BaseModel):
    """Schema for location dependency check"""
    can_delete: bool
    staff_count: int = 0
    service_count: int = 0
    booking_count: int = 0
    messages: List[str] = Field(default_factory=list)
