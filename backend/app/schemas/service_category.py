"""Pydantic schemas for service category management."""

from typing import Optional, List
from pydantic import BaseModel, Field


class ServiceCategoryCreateRequest(BaseModel):
    """Request schema for creating a service category."""

    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: bool = Field(default=True)


class ServiceCategoryUpdateRequest(BaseModel):
    """Request schema for updating a service category."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class ServiceCategoryResponse(BaseModel):
    """Response schema for a service category."""

    id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class ServiceCategoryListResponse(BaseModel):
    """Response schema for listing service categories."""

    categories: List[ServiceCategoryResponse]
    total: int
