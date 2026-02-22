"""
Client Activity schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ClientActivityCreate(BaseModel):
    """Client activity creation request"""
    activity_type: str = Field(..., description="Type: booking, communication, loyalty, payment, profile_update, etc.")
    activity_subtype: Optional[str] = Field(None, description="Subtype for more specific categorization")
    description: str = Field(..., description="Human-readable description of the activity")
    metadata: Dict[str, Any] = Field(default={}, description="Additional activity data")


class ClientActivityResponse(BaseModel):
    """Client activity response"""
    id: str
    client_id: str
    tenant_id: str
    activity_type: str
    activity_subtype: Optional[str] = None
    description: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    created_by: Optional[str] = None  # user_id who created the activity
    
    class Config:
        populate_by_name = True


class ClientActivityFilter(BaseModel):
    """Client activity filter parameters"""
    activity_type: Optional[str] = Field(None, description="Filter by activity type")
    start_date: Optional[datetime] = Field(None, description="Filter activities from this date")
    end_date: Optional[datetime] = Field(None, description="Filter activities until this date")
    offset: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=200)
