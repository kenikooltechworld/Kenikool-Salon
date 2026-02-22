from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SegmentCriteria(BaseModel):
    """Criteria for filtering clients in a segment"""
    visit_frequency: Optional[Dict[str, Any]] = None
    last_visit: Optional[Dict[str, Any]] = None
    total_spending: Optional[Dict[str, Any]] = None
    service_preferences: Optional[List[str]] = None
    loyalty_tier: Optional[List[str]] = None
    demographics: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None


class ClientSegment(BaseModel):
    """Client segment model"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    tenant_id: str
    name: str
    description: Optional[str] = None
    criteria: SegmentCriteria
    client_count: int = 0
    last_calculated_at: datetime = Field(default_factory=datetime.utcnow)
    is_dynamic: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "id": "seg_123",
                "tenant_id": "tenant_1",
                "name": "High-Value Clients",
                "description": "Clients with spending > $500",
                "criteria": {
                    "total_spending": {
                        "operator": "gt",
                        "amount": 500
                    }
                },
                "client_count": 45,
                "is_dynamic": True,
                "created_by": "user_1"
            }
        }
