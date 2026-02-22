"""
Settings system schemas for security, preferences, privacy, and data management
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from app.schemas.base import BaseSchema


class PasswordChangeRequest(BaseModel):
    """Password change request schema"""
    current_password: str = Field(..., min_length=1)
    new_password: str = Field(..., min_length=8)

    class Config:
        json_schema_extra = {
            "example": {
                "current_password": "oldPassword123!",
                "new_password": "newPassword456!"
            }
        }


class TwoFactorSetupResponse(BaseModel):
    """2FA setup response schema"""
    secret: str
    qr_code_url: str
    backup_codes: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "secret": "JBSWY3DPEBLW64TMMQ======",
                "qr_code_url": "data:image/png;base64,...",
                "backup_codes": ["code1", "code2", "code3", "code4", "code5"]
            }
        }


class TwoFactorVerifyRequest(BaseModel):
    """2FA verification request schema"""
    code: str = Field(..., min_length=6, max_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class TwoFactorDisableRequest(BaseModel):
    """2FA disable request schema"""
    password: str = Field(..., min_length=1)
    code: str = Field(..., min_length=6, max_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "password": "currentPassword123!",
                "code": "123456"
            }
        }


class SessionInfo(BaseSchema):
    """Session information schema"""
    id: str
    device: str
    browser: str
    ip_address: str
    location: Optional[str] = None
    last_active: datetime
    created_at: datetime
    is_current: bool

    class Config:
        json_schema_extra = {
            "example": {
                "id": "session_123",
                "device": "Chrome on Windows",
                "browser": "Chrome 120.0",
                "ip_address": "192.168.1.1",
                "location": "Lagos, Nigeria",
                "last_active": "2024-01-25T10:30:00Z",
                "created_at": "2024-01-20T10:30:00Z",
                "is_current": True
            }
        }


class APIKeyCreate(BaseModel):
    """API key creation request schema"""
    name: str = Field(..., min_length=1, max_length=100)
    expires_at: Optional[datetime] = None
    permissions: List[str] = Field(default_factory=list)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "My API Key",
                "expires_at": "2025-01-25T00:00:00Z",
                "permissions": ["read:bookings", "write:clients"]
            }
        }


class APIKeyResponse(BaseSchema):
    """API key response schema"""
    id: str
    name: str
    key_prefix: str
    created_at: datetime
    last_used: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    is_active: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "id": "key_123",
                "name": "My API Key",
                "key_prefix": "sk_live_abc123",
                "created_at": "2024-01-20T10:30:00Z",
                "last_used": "2024-01-25T10:30:00Z",
                "expires_at": "2025-01-25T00:00:00Z",
                "is_active": True
            }
        }


class APIKeyDisplayResponse(BaseSchema):
    """API key display response (with full key, shown only once)"""
    id: str
    name: str
    key: str  # Full key, only shown once
    key_prefix: str
    created_at: datetime
    expires_at: Optional[datetime] = None
    permissions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "id": "key_123",
                "name": "My API Key",
                "key": "sk_live_abc123def456ghi789",
                "key_prefix": "sk_live_abc123",
                "created_at": "2024-01-20T10:30:00Z",
                "expires_at": "2025-01-25T00:00:00Z",
                "permissions": ["read:bookings", "write:clients"]
            }
        }


class UserPreferences(BaseSchema):
    """User preferences schema"""
    language: str = "en"
    timezone: str = "Africa/Lagos"
    date_format: str = "DD/MM/YYYY"
    time_format: str = "24h"
    currency: str = "NGN"
    font_size: str = "medium"
    high_contrast: bool = False
    reduce_motion: bool = False
    screen_reader: bool = False

    @validator('language')
    def validate_language(cls, v):
        valid_languages = ['en', 'fr', 'es', 'de', 'pt', 'yo']
        if v not in valid_languages:
            raise ValueError(f'Language must be one of {valid_languages}')
        return v

    @validator('time_format')
    def validate_time_format(cls, v):
        if v not in ['12h', '24h']:
            raise ValueError('Time format must be 12h or 24h')
        return v

    @validator('font_size')
    def validate_font_size(cls, v):
        if v not in ['small', 'medium', 'large']:
            raise ValueError('Font size must be small, medium, or large')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "language": "en",
                "timezone": "Africa/Lagos",
                "date_format": "DD/MM/YYYY",
                "time_format": "24h",
                "currency": "NGN",
                "font_size": "medium",
                "high_contrast": False,
                "reduce_motion": False,
                "screen_reader": False
            }
        }


class PrivacySettings(BaseSchema):
    """Privacy settings schema"""
    analytics_enabled: bool = True
    marketing_emails: bool = True
    third_party_sharing: bool = False
    data_retention_days: int = 365

    @validator('data_retention_days')
    def validate_retention_days(cls, v):
        if v < 30 or v > 2555:  # 30 days to 7 years
            raise ValueError('Data retention days must be between 30 and 2555')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "analytics_enabled": True,
                "marketing_emails": True,
                "third_party_sharing": False,
                "data_retention_days": 365
            }
        }


class DataExportRequest(BaseModel):
    """Data export request schema"""
    include_bookings: bool = True
    include_clients: bool = True
    include_payments: bool = True
    include_settings: bool = True

    class Config:
        json_schema_extra = {
            "example": {
                "include_bookings": True,
                "include_clients": True,
                "include_payments": True,
                "include_settings": True
            }
        }


class DataExportResponse(BaseSchema):
    """Data export response schema"""
    id: str
    status: str  # pending, processing, completed, failed
    file_url: Optional[str] = None
    file_size: Optional[int] = None
    requested_at: datetime
    completed_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "export_123",
                "status": "completed",
                "file_url": "https://cdn.example.com/exports/export_123.json",
                "file_size": 1024000,
                "requested_at": "2024-01-20T10:30:00Z",
                "completed_at": "2024-01-20T10:35:00Z",
                "expires_at": "2024-01-27T10:35:00Z"
            }
        }


class SecurityLogEntry(BaseSchema):
    """Security log entry schema"""
    id: str
    event_type: str
    ip_address: str
    device: str
    browser: str
    location: Optional[str] = None
    success: bool
    details: Optional[Dict[str, Any]] = None
    flagged: bool = False
    timestamp: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "id": "log_123",
                "event_type": "login",
                "ip_address": "192.168.1.1",
                "device": "Chrome on Windows",
                "browser": "Chrome 120.0",
                "location": "Lagos, Nigeria",
                "success": True,
                "details": {"mfa_used": True},
                "flagged": False,
                "timestamp": "2024-01-25T10:30:00Z"
            }
        }


class AccountDeletionRequest(BaseModel):
    """Account deletion request schema"""
    password: str = Field(..., min_length=1)

    class Config:
        json_schema_extra = {
            "example": {
                "password": "currentPassword123!"
            }
        }


class AccountDeletionResponse(BaseSchema):
    """Account deletion response schema"""
    id: str
    status: str  # pending, cancelled, completed
    scheduled_for: datetime
    requested_at: datetime
    cancellation_token: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "deletion_123",
                "status": "pending",
                "scheduled_for": "2024-02-24T10:30:00Z",
                "requested_at": "2024-01-25T10:30:00Z",
                "cancellation_token": "token_abc123"
            }
        }


class EmailChangeRequest(BaseModel):
    """Email change request schema"""
    new_email: EmailStr

    class Config:
        json_schema_extra = {
            "example": {
                "new_email": "newemail@example.com"
            }
        }


class PhoneVerificationRequest(BaseModel):
    """Phone verification request schema"""
    phone_number: str = Field(..., min_length=10, max_length=20)

    class Config:
        json_schema_extra = {
            "example": {
                "phone_number": "+2348012345678"
            }
        }


class PhoneVerificationConfirmRequest(BaseModel):
    """Phone verification confirmation request schema"""
    code: str = Field(..., min_length=4, max_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "code": "123456"
            }
        }


class PasswordStrengthResponse(BaseSchema):
    """Password strength response schema"""
    strength: str  # weak, medium, strong
    score: int  # 0-100
    requirements_met: Dict[str, bool]
    suggestions: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "strength": "strong",
                "score": 85,
                "requirements_met": {
                    "min_length": True,
                    "uppercase": True,
                    "lowercase": True,
                    "numbers": True,
                    "special_chars": True
                },
                "suggestions": []
            }
        }


class SecurityScoreResponse(BaseSchema):
    """Security score response schema"""
    score: int  # 0-100
    level: str  # low, medium, high
    recommendations: List[str]
    last_updated: datetime

    class Config:
        json_schema_extra = {
            "example": {
                "score": 75,
                "level": "high",
                "recommendations": [
                    "Enable two-factor authentication",
                    "Update your password"
                ],
                "last_updated": "2024-01-25T10:30:00Z"
            }
        }



class ReviewIncentiveSettings(BaseSchema):
    """Review incentive settings schema"""
    incentive_enabled: bool = True
    incentive_points: int = 50
    max_reviews_per_client_per_month: int = 12
    total_points_awarded: int = 0

    @validator('incentive_points')
    def validate_points(cls, v):
        if v < 0 or v > 1000:
            raise ValueError('Points must be between 0 and 1000')
        return v

    @validator('max_reviews_per_client_per_month')
    def validate_max_reviews(cls, v):
        if v < 1 or v > 100:
            raise ValueError('Max reviews must be between 1 and 100')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "incentive_enabled": True,
                "incentive_points": 50,
                "max_reviews_per_client_per_month": 12,
                "total_points_awarded": 1500
            }
        }


class ReviewNotificationSettings(BaseSchema):
    """Review notification settings schema"""
    notification_enabled: bool = True
    email_enabled: bool = True
    in_app_enabled: bool = True
    digest_mode: bool = False
    digest_frequency: str = "daily"  # daily, weekly, monthly

    @validator('digest_frequency')
    def validate_frequency(cls, v):
        if v not in ['daily', 'weekly', 'monthly']:
            raise ValueError('Digest frequency must be daily, weekly, or monthly')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "notification_enabled": True,
                "email_enabled": True,
                "in_app_enabled": True,
                "digest_mode": False,
                "digest_frequency": "daily"
            }
        }


class ReviewReminderSettings(BaseSchema):
    """Review reminder settings schema"""
    reminder_enabled: bool = True
    reminder_delay_hours: int = 24
    email_template: Optional[str] = None
    sms_template: Optional[str] = None

    @validator('reminder_delay_hours')
    def validate_delay(cls, v):
        if v < 1 or v > 168:  # 1 hour to 7 days
            raise ValueError('Reminder delay must be between 1 and 168 hours')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "reminder_enabled": True,
                "reminder_delay_hours": 24,
                "email_template": "Review reminder email template",
                "sms_template": "Review reminder SMS template"
            }
        }
