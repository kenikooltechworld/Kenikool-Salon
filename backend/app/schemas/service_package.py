from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, validator


class ServicePackageItemBase(BaseModel):
    """Base schema for service package item"""
    service_id: str
    quantity: int = Field(default=1, ge=1)


class ServicePackageItemCreate(ServicePackageItemBase):
    """Schema for creating service package item"""
    pass


class ServicePackageItemResponse(ServicePackageItemBase):
    """Schema for service package item response"""
    id: str
    service_name: str
    service_price: float
    service_duration: int
    
    class Config:
        from_attributes = True


class ServicePackageBase(BaseModel):
    """Base schema for service package"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    package_price: float = Field(..., ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = Field(default=True)
    max_bookings_per_customer: Optional[int] = Field(None, ge=1)
    total_bookings_limit: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    display_order: int = Field(default=0)
    is_featured: bool = Field(default=False)


class ServicePackageCreate(ServicePackageBase):
    """Schema for creating service package"""
    services: List[ServicePackageItemCreate] = Field(..., min_items=2)
    
    @validator('valid_until')
    def validate_dates(cls, v, values):
        if v and 'valid_from' in values and values['valid_from']:
            if v <= values['valid_from']:
                raise ValueError('valid_until must be after valid_from')
        return v


class ServicePackageUpdate(BaseModel):
    """Schema for updating service package"""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    services: Optional[List[ServicePackageItemCreate]] = Field(None, min_items=2)
    package_price: Optional[float] = Field(None, ge=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    max_bookings_per_customer: Optional[int] = Field(None, ge=1)
    total_bookings_limit: Optional[int] = Field(None, ge=1)
    image_url: Optional[str] = None
    display_order: Optional[int] = None
    is_featured: Optional[bool] = None


class ServicePackageResponse(ServicePackageBase):
    """Schema for service package response"""
    id: str
    tenant_id: str
    services: List[ServicePackageItemResponse]
    original_price: float
    discount_amount: float
    discount_percentage: float
    current_bookings_count: int
    total_duration: int  # Sum of all service durations
    is_valid: bool
    savings: dict
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ServicePackageListResponse(BaseModel):
    """Schema for paginated service package list"""
    packages: List[ServicePackageResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
