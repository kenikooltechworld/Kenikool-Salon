"""
Settings system models for MongoDB collections
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
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


class Session(BaseModel):
    """Session model for sessions collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    token_hash: str
    device: str
    browser: str
    ip_address: str
    location: Optional[str] = None
    user_agent: str
    last_active: datetime = Field(default_factory=datetime.utcnow)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class APIKey(BaseModel):
    """API Key model for api_keys collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    name: str
    key_hash: str
    key_prefix: str
    permissions: List[str] = Field(default_factory=list)
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserPreferences(BaseModel):
    """User Preferences model for user_preferences collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    language: str = "en"
    timezone: str = "Africa/Lagos"
    date_format: str = "DD/MM/YYYY"
    time_format: str = "24h"
    currency: str = "NGN"
    font_size: str = "medium"
    high_contrast: bool = False
    reduce_motion: bool = False
    screen_reader: bool = False
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class PrivacySettings(BaseModel):
    """Privacy Settings model for privacy_settings collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    analytics_enabled: bool = True
    marketing_emails: bool = True
    third_party_sharing: bool = False
    data_retention_days: int = 365
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class SecurityLog(BaseModel):
    """Security Log model for security_logs collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    event_type: str
    ip_address: str
    device: str
    browser: str
    location: Optional[str] = None
    success: bool
    details: Optional[Dict[str, Any]] = None
    flagged: bool = False
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class DataExport(BaseModel):
    """Data Export model for data_exports collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    status: str  # pending, processing, completed, failed
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    expires_at: Optional[datetime] = None
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class AccountDeletion(BaseModel):
    """Account Deletion model for account_deletions collection"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    user_id: str
    tenant_id: str
    status: str  # pending, cancelled, completed
    scheduled_for: datetime
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    cancellation_token: Optional[str] = None

    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}
