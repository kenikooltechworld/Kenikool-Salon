"""
Service Variant schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class ServiceVariantCreate(BaseModel):
    """Service variant creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    price_adjustment: float = Field(default=0.0)
    price_adjustment_type: str = Field(default="fixed", pattern="^(fixed|percentage)$")
    duration_adjustment: int = Field(default=0)
    is_active: bool = Field(default=True)


class ServiceVariantUpdate(BaseModel):
    """Service variant update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    price_adjustment: Optional[float] = None
    price_adjustment_type: Optional[str] = Field(None, pattern="^(fixed|percentage)$")
    duration_adjustment: Optional[int] = None
    is_active: Optional[bool] = None


class ServiceVariantResponse(BaseSchema):
    """Service variant response"""
    id: str
    service_id: str
    tenant_id: str
    name: str
    description: Optional[str]
    price_adjustment: float
    price_adjustment_type: str
    duration_adjustment: int
    final_price: float
    final_duration: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
