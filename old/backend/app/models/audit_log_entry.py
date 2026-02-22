"""
Audit Log Entry Model
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Any
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


class FieldChange(BaseModel):
    """Field change record"""
    field: str
    old_value: Any = None
    new_value: Any = None


class AuditLogEntryBase(BaseModel):
    """Base audit log entry model"""
    booking_id: str
    user_id: str
    action: str
    changes: List[FieldChange] = []
    reason: Optional[str] = None


class AuditLogEntryCreate(AuditLogEntryBase):
    """Audit log entry creation model"""
    tenant_id: str


class AuditLogEntryInDB(AuditLogEntryBase):
    """Audit log entry model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
