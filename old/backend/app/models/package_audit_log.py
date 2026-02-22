"""
Package Audit Log Pydantic models
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)


class PackageAuditLogBase(BaseModel):
    """Base package audit log model"""
    action_type: str  # create, purchase, redeem, transfer, refund, extend
    entity_type: str  # definition, purchase, credit
    entity_id: str
    performed_by_user_id: str
    performed_by_role: str
    client_id: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime


class PackageAuditLogCreate(PackageAuditLogBase):
    """Package audit log creation model"""
    tenant_id: str


class PackageAuditLogInDB(PackageAuditLogBase):
    """Package audit log model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
