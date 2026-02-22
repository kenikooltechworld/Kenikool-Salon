"""Pydantic schemas for service management."""

from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class ServiceCreateRequest(BaseModel):
    """Request schema for creating a service."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_minutes: int = Field(..., gt=0)
    price: Decimal = Field(..., ge=0)
    category: str = Field(..., min_length=1, max_length=100)
    color: Optional[str] = Field(default="#3B82F6", max_length=7)
    icon: Optional[str] = Field(default="Scissors", max_length=50)
    is_active: bool = Field(default=True)
    is_published: bool = Field(default=False)
    public_description: Optional[str] = Field(None, max_length=1000)
    public_image_url: Optional[str] = Field(None, max_length=500)
    allow_public_booking: bool = Field(default=False)
    tags: List[str] = Field(default=[])


class ServiceUpdateRequest(BaseModel):
    """Request schema for updating a service."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    duration_minutes: Optional[int] = Field(None, gt=0)
    price: Optional[Decimal] = Field(None, ge=0)
    category: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None
    is_published: Optional[bool] = None
    public_description: Optional[str] = Field(None, max_length=1000)
    public_image_url: Optional[str] = Field(None, max_length=500)
    allow_public_booking: Optional[bool] = None
    tags: Optional[List[str]] = None


class ServiceResponse(BaseModel):
    """Response schema for a service."""

    id: str
    name: str
    description: Optional[str]
    duration_minutes: int
    price: float
    category: str
    color: Optional[str] = None
    icon: Optional[str] = None
    is_active: bool
    is_published: bool
    public_description: Optional[str]
    public_image_url: Optional[str]
    allow_public_booking: bool
    tags: List[str]
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class ServiceListResponse(BaseModel):
    """Response schema for listing services."""

    services: List[ServiceResponse]
    total: int
    page: int
    page_size: int
