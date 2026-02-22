"""
Service Package schemas
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class ServicePackageCreate(BaseModel):
    """Service package creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    service_ids: List[str] = Field(..., min_length=1)
    package_price: float = Field(..., gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: bool = Field(default=True)
    
    @field_validator('service_ids')
    @classmethod
    def validate_service_ids(cls, v: List[str]) -> List[str]:
        if len(v) < 1:
            raise ValueError('Package must include at least one service')
        return v


class ServicePackageUpdate(BaseModel):
    """Service package update request"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    service_ids: Optional[List[str]] = None
    package_price: Optional[float] = Field(None, gt=0)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    is_active: Optional[bool] = None
    
    @field_validator('service_ids')
    @classmethod
    def validate_service_ids(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        if v is not None and len(v) < 1:
            raise ValueError('Package must include at least one service')
        return v


class ServicePackageResponse(BaseSchema):
    """Service package response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    service_ids: List[str]
    package_price: float
    total_service_price: float
    savings: float
    savings_percentage: float
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
