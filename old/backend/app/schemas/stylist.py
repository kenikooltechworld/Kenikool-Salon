"""
Stylist schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, time
from app.schemas.base import BaseSchema


class WorkingHoursInput(BaseModel):
    """Working hours for a specific day"""
    day: str = Field(..., description="Day of week (monday, tuesday, etc.)")
    start_time: str = Field(..., description="Start time in HH:MM format")
    end_time: str = Field(..., description="End time in HH:MM format")
    is_working: bool = Field(default=True, description="Whether stylist works this day")


class WorkingHoursResponse(BaseModel):
    """Working hours response"""
    day: str
    start_time: str
    end_time: str
    is_working: bool


class StylistScheduleInput(BaseModel):
    """Stylist schedule input"""
    working_hours: List[WorkingHoursInput] = Field(..., description="Working hours for each day")
    break_start: Optional[str] = Field(None, description="Break start time in HH:MM format")
    break_end: Optional[str] = Field(None, description="Break end time in HH:MM format")


class StylistScheduleResponse(BaseModel):
    """Stylist schedule response"""
    working_hours: List[WorkingHoursResponse]
    break_start: Optional[str] = None
    break_end: Optional[str] = None


class LocationAvailability(BaseModel):
    """Location-specific availability for a stylist"""
    location_id: str = Field(..., description="Location ID")
    monday: Optional[WorkingHoursInput] = None
    tuesday: Optional[WorkingHoursInput] = None
    wednesday: Optional[WorkingHoursInput] = None
    thursday: Optional[WorkingHoursInput] = None
    friday: Optional[WorkingHoursInput] = None
    saturday: Optional[WorkingHoursInput] = None
    sunday: Optional[WorkingHoursInput] = None


class StylistCreate(BaseModel):
    """Stylist creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: str = Field(..., min_length=10, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    photo: Optional[str] = Field(None, description="Photo URL")
    specialties: List[str] = Field(default_factory=list, description="List of specialties")
    commission_type: Optional[str] = Field(None, description="percentage or fixed")
    commission_value: Optional[float] = Field(None, ge=0, description="Commission rate or amount")
    schedule: Optional[StylistScheduleInput] = None
    assigned_locations: List[str] = Field(default_factory=list, description="List of location IDs")
    location_availability: Optional[Dict[str, Dict[str, Any]]] = Field(
        default_factory=dict,
        description="Location-specific availability {location_id: {day: hours}}"
    )


class StylistUpdate(BaseModel):
    """Stylist update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    bio: Optional[str] = Field(None, max_length=500)
    photo: Optional[str] = None
    is_active: Optional[bool] = None
    specialties: Optional[List[str]] = None
    commission_type: Optional[str] = None
    commission_value: Optional[float] = Field(None, ge=0)
    schedule: Optional[StylistScheduleInput] = None
    assigned_locations: Optional[List[str]] = None
    location_availability: Optional[Dict[str, Dict[str, Any]]] = None


class StylistResponse(BaseSchema):
    """Stylist response"""
    id: str
    tenant_id: str
    name: str
    email: Optional[str] = None
    phone: str
    bio: Optional[str] = None
    photo_url: Optional[str] = None
    is_active: bool
    specialties: List[str] = []
    commission_type: Optional[str] = None
    commission_value: Optional[float] = None
    assigned_services: List[str] = []
    assigned_locations: List[str] = []
    location_names: Optional[Dict[str, str]] = Field(default_factory=dict, description="Mapping of location IDs to location names")
    location_availability: Optional[Dict[str, Dict[str, Any]]] = None
    schedule: Optional[StylistScheduleResponse] = None
    created_at: datetime
    updated_at: datetime
