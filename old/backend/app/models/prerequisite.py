"""
Prerequisite Service Model
"""
from pydantic import BaseModel, Field
from typing import Optional
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


class PrerequisiteBase(BaseModel):
    """Base prerequisite model"""
    service_id: str
    prerequisite_service_id: str
    is_required: bool = True


class PrerequisiteCreate(PrerequisiteBase):
    """Prerequisite creation model"""
    tenant_id: str


class PrerequisiteInDB(PrerequisiteBase):
    """Prerequisite model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
