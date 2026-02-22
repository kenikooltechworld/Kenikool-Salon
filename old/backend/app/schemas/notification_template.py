"""
Notification Template Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from app.schemas.base import BaseSchema


class NotificationTemplateCreate(BaseModel):
    """Schema for creating a notification template"""
    name: str = Field(..., min_length=1, max_length=100, description="Template name")
    message: str = Field(..., min_length=1, max_length=1000, description="Template message with variables")
    variables: List[str] = Field(default_factory=list, description="List of variable names used in template")
    is_default: bool = Field(default=False, description="Whether this is the default template")


class NotificationTemplateUpdate(BaseModel):
    """Schema for updating a notification template"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    message: Optional[str] = Field(None, min_length=1, max_length=1000)
    variables: Optional[List[str]] = None
    is_default: Optional[bool] = None


class NotificationTemplateResponse(BaseSchema):
    """Schema for notification template response"""
    id: str
    tenant_id: str
    name: str
    message: str
    variables: List[str]
    is_default: bool
    created_at: datetime
    updated_at: datetime
