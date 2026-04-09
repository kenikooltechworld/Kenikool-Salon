"""Service Add-on Schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime


class ServiceAddonBase(BaseModel):
    """Base schema for service addon"""
    name: str = Field(..., max_length=200)
    description: str
    price: Decimal = Field(..., gt=0)
    duration_minutes: int = Field(..., ge=0)
    image_url: Optional[str] = None
    applicable_services: List[str]
    category: str = Field(..., pattern="^(product|upgrade|treatment)$")
    display_order: int = 0


class ServiceAddonCreate(ServiceAddonBase):
    """Schema for creating service addon"""
    pass


class ServiceAddonUpdate(BaseModel):
    """Schema for updating service addon"""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    duration_minutes: Optional[int] = Field(None, ge=0)
    image_url: Optional[str] = None
    is_active: Optional[bool] = None
    applicable_services: Optional[List[str]] = None
    category: Optional[str] = Field(None, pattern="^(product|upgrade|treatment)$")
    display_order: Optional[int] = None


class ServiceAddonResponse(ServiceAddonBase):
    """Schema for service addon response"""
    id: str
    tenant_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat()
        }
