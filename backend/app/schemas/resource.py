"""Resource schemas."""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, time
from decimal import Decimal


class ResourceCreate(BaseModel):
    """Schema for creating a resource."""

    name: str
    type: str  # room, chair, equipment, tool, supply
    quantity: int = 1
    location_id: Optional[str] = None
    description: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[Decimal] = None
    tags: Optional[List[str]] = None


class ResourceUpdate(BaseModel):
    """Schema for updating a resource."""

    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    tags: Optional[List[str]] = None


class ResourceResponse(BaseModel):
    """Schema for resource response."""

    id: str = Field(alias="_id")
    name: str
    type: str
    quantity: int
    available_quantity: int
    status: str
    is_active: bool
    location_id: Optional[str] = None
    description: Optional[str] = None
    purchase_date: Optional[datetime] = None
    purchase_price: Optional[Decimal] = None
    tags: List[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceAvailabilityCreate(BaseModel):
    """Schema for creating resource availability."""

    resource_id: str
    start_time: time
    end_time: time
    day_of_week: Optional[str] = None
    is_recurring: bool = True
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None


class ResourceAvailabilityResponse(BaseModel):
    """Schema for resource availability response."""

    id: str = Field(alias="_id")
    resource_id: str
    start_time: time
    end_time: time
    day_of_week: Optional[str] = None
    is_recurring: bool
    effective_from: Optional[datetime] = None
    effective_to: Optional[datetime] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceAssignmentResponse(BaseModel):
    """Schema for resource assignment response."""

    id: str = Field(alias="_id")
    appointment_id: str
    resource_id: str
    quantity_used: int
    status: str
    assigned_at: datetime
    released_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceMaintenanceCreate(BaseModel):
    """Schema for creating resource maintenance."""

    resource_id: str
    maintenance_type: str
    scheduled_date: datetime
    estimated_duration_hours: Optional[int] = None
    description: Optional[str] = None
    cost: Optional[Decimal] = None


class ResourceMaintenanceResponse(BaseModel):
    """Schema for resource maintenance response."""

    id: str = Field(alias="_id")
    resource_id: str
    maintenance_type: str
    scheduled_date: datetime
    completed_date: Optional[datetime] = None
    estimated_duration_hours: Optional[int] = None
    status: str
    description: Optional[str] = None
    cost: Optional[Decimal] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ResourceUtilizationResponse(BaseModel):
    """Schema for resource utilization response."""

    id: str = Field(alias="_id")
    resource_id: str
    date: datetime
    usage_hours: Decimal
    utilization_percent: Decimal
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
