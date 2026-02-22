"""
Service Template schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.schemas.base import BaseSchema


class ServiceTemplateCreate(BaseModel):
    """Service template creation request"""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    category: Optional[str] = None
    is_default: bool = Field(default=False, description="Is this a default template")
    
    # Template data (service properties to copy)
    template_data: Dict[str, Any] = Field(..., description="Service properties to use as template")


class ServiceTemplateUpdate(BaseModel):
    """Service template update request"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None
    template_data: Optional[Dict[str, Any]] = None


class ServiceTemplateResponse(BaseSchema):
    """Service template response"""
    id: str
    tenant_id: str
    name: str
    description: Optional[str]
    category: Optional[str]
    is_default: bool
    is_active: bool
    template_data: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class CreateFromTemplateRequest(BaseModel):
    """Request to create service from template"""
    template_id: str
    name: str = Field(..., min_length=2, max_length=100)
    customizations: Optional[Dict[str, Any]] = Field(default={}, description="Override template values")
