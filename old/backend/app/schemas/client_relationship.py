"""
Client Relationship schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClientRelationshipCreate(BaseModel):
    """Client relationship creation request"""
    related_client_id: str = Field(..., description="ID of the related client")
    relationship_type: str = Field(..., description="Type: family, friend, referral")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about the relationship")


class ClientRelationshipUpdate(BaseModel):
    """Client relationship update request"""
    relationship_type: Optional[str] = Field(None, description="Type: family, friend, referral")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes about the relationship")


class ClientRelationshipResponse(BaseModel):
    """Client relationship response"""
    id: str
    tenant_id: str
    client_id: str
    related_client_id: str
    related_client_name: str  # Populated from related client
    relationship_type: str
    notes: Optional[str] = None
    created_at: datetime
    created_by: Optional[str] = None
    
    class Config:
        populate_by_name = True
