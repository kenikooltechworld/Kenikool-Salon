"""
Package audit log schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class PackageAuditLogBase(BaseModel):
    """Base package audit log schema"""
    action_type: str = Field(
        ...,
        description="Type of action: create, purchase, redeem, transfer, refund, extend"
    )
    entity_type: str = Field(
        ...,
        description="Type of entity: definition, purchase, credit"
    )
    entity_id: str = Field(..., description="ID of the entity being audited")
    performed_by_user_id: str = Field(..., description="User ID who performed the action")
    performed_by_role: str = Field(..., description="Role of the user who performed the action")
    client_id: Optional[str] = Field(None, description="Client ID if applicable")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional action details")
    timestamp: datetime = Field(..., description="When the action occurred")


class PackageAuditLogCreate(PackageAuditLogBase):
    """Package audit log creation schema"""
    pass


class PackageAuditLogResponse(PackageAuditLogBase):
    """Package audit log response schema"""
    id: str = Field(..., alias="_id")
    tenant_id: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class PackageAuditLogListResponse(BaseModel):
    """Package audit log list response"""
    logs: list[PackageAuditLogResponse]
    total: int
    page: int
    page_size: int


class PackageAuditLogFilterRequest(BaseModel):
    """Package audit log filter request"""
    action_type: Optional[str] = Field(None, description="Filter by action type")
    entity_type: Optional[str] = Field(None, description="Filter by entity type")
    entity_id: Optional[str] = Field(None, description="Filter by entity ID")
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    performed_by_user_id: Optional[str] = Field(None, description="Filter by user ID")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    page: int = Field(default=1, ge=1, description="Page number")
    page_size: int = Field(default=50, ge=1, le=500, description="Page size")
