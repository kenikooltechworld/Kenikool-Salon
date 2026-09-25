"""Pydantic schemas for location management."""

from typing import Optional
from pydantic import BaseModel, Field


class LocationCreateRequest(BaseModel):
    """Request schema for creating a location."""

    name: str = Field(..., min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    is_active: bool = Field(default=True)
    timezone: Optional[str] = Field(None, max_length=100)


class LocationUpdateRequest(BaseModel):
    """Request schema for updating a location."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    address: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=50)
    email: Optional[str] = Field(None, max_length=255)
    is_active: Optional[bool] = None
    timezone: Optional[str] = Field(None, max_length=100)


class LocationResponse(BaseModel):
    """Response schema for a location."""

    id: str
    name: str
    address: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    is_active: bool = True
    timezone: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class LocationListResponse(BaseModel):
    """Response schema for listing locations."""

    locations: list[LocationResponse]
    total: int
    page: int
    page_size: int
