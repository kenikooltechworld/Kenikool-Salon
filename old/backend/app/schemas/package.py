"""
Package schemas
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime

class ServiceQuantity(BaseModel):
    """Service with quantity in package"""
    service_id: str = Field(..., description="Service ID")
    quantity: int = Field(..., gt=0, description="Number of times this service can be redeemed")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        if v <= 0:
            raise ValueError('Quantity must be a positive integer')
        return v

class TimeRestriction(BaseModel):
    """Time-based restrictions for package redemption"""
    days_of_week: Optional[List[int]] = Field(None, description="Days of week (0-6, 0=Monday)")
    start_time: Optional[str] = Field(None, description="Start time (HH:MM format)")
    end_time: Optional[str] = Field(None, description="End time (HH:MM format)")

class PackageRestrictions(BaseModel):
    """Restrictions for package usage"""
    stylist_ids: Optional[List[str]] = Field(None, description="Allowed stylist IDs (empty = all)")
    location_ids: Optional[List[str]] = Field(None, description="Allowed location IDs (empty = all)")
    time_restrictions: Optional[TimeRestriction] = Field(None, description="Time-based restrictions")
    blackout_dates: Optional[List[datetime]] = Field(None, description="Dates when package cannot be redeemed")

class PackageBase(BaseModel):
    """Base package schema"""
    name: str = Field(..., min_length=2, max_length=100, description="Package name")
    description: Optional[str] = Field(None, description="Package description")
    services: List[ServiceQuantity] = Field(..., description="Services with quantities included in package")
    original_price: float = Field(..., gt=0, description="Original total price of services")
    package_price: float = Field(..., gt=0, description="Discounted package price")
    discount_percentage: float = Field(default=0, ge=0, le=100, description="Discount percentage")
    validity_days: Optional[int] = Field(None, gt=0, description="Number of days package is valid from purchase")
    is_active: bool = Field(default=True, description="Whether package is active")
    is_transferable: bool = Field(default=True, description="Whether package can be transferred between clients")
    is_giftable: bool = Field(default=True, description="Whether package can be purchased as a gift")
    restrictions: Optional[PackageRestrictions] = Field(None, description="Usage restrictions for package")
    valid_from: Optional[datetime] = Field(None, description="Package validity start date")
    valid_until: Optional[datetime] = Field(None, description="Package validity end date")
    max_redemptions: Optional[int] = Field(None, description="Maximum number of redemptions")

class PackageCreate(PackageBase):
    """Package creation schema"""
    pass

class PackageUpdate(BaseModel):
    """Package update schema"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    services: Optional[List[ServiceQuantity]] = None
    original_price: Optional[float] = Field(None, gt=0)
    package_price: Optional[float] = Field(None, gt=0)
    discount_percentage: Optional[float] = Field(None, ge=0, le=100)
    validity_days: Optional[int] = Field(None, gt=0)
    is_active: Optional[bool] = None
    is_transferable: Optional[bool] = None
    is_giftable: Optional[bool] = None
    restrictions: Optional[PackageRestrictions] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    max_redemptions: Optional[int] = None

class PackageResponse(PackageBase):
    """Package response schema"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    current_redemptions: int = Field(default=0, description="Current number of redemptions")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True

class PackageListResponse(BaseModel):
    """Package list response schema"""
    packages: List[PackageResponse]
    total: int
