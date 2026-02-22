"""
User and Tenant Pydantic models
"""
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
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


class BankAccount(BaseModel):
    """Bank account information for payouts"""
    bank_name: str
    account_number: str
    account_name: str
    bank_code: Optional[str] = None


class ReferralSettings(BaseModel):
    """Referral program settings for tenant"""
    enabled: bool = True
    reward_type: str = "fixed"  # fixed or percentage
    reward_amount: float = 1000  # ₦1,000 default
    min_booking_amount: float = 5000  # ₦5,000 minimum booking
    expiration_days: int = 90
    max_referrals_per_client: int = 50
    max_rewards_per_month: float = 100000  # ₦100,000 max per month


class TenantBase(BaseModel):
    """Base tenant model"""
    salon_name: str = Field(..., min_length=2, max_length=100)
    subdomain: str = Field(..., min_length=3, max_length=50)
    custom_domain: Optional[str] = None
    owner_name: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=10, max_length=20)
    email: EmailStr
    address: Optional[str] = None
    logo_url: Optional[str] = None
    brand_color: str = "#6366f1"
    qr_code_url: Optional[str] = None
    is_active: bool = True
    subscription_plan: str = "free"  # free, starter, professional, business, enterprise, unlimited
    bank_account: Optional[BankAccount] = None
    referral_settings: ReferralSettings = Field(default_factory=ReferralSettings)
    
    @validator('subdomain')
    def validate_subdomain(cls, v):
        """Validate subdomain format"""
        import re
        if not re.match(r'^[a-z0-9-]+$', v):
            raise ValueError('Subdomain must contain only lowercase letters, numbers, and hyphens')
        return v.lower()


class TenantCreate(TenantBase):
    """Tenant creation model"""
    password: str = Field(..., min_length=8)


class TenantInDB(TenantBase):
    """Tenant model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserBase(BaseModel):
    """Base user model"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    phone: Optional[str] = None
    role: str = "owner"  # owner, admin, stylist, receptionist
    is_active: bool = True


class UserCreate(UserBase):
    """User creation model"""
    password: str = Field(..., min_length=8)
    tenant_id: Optional[str] = None


class UserInDB(UserBase):
    """User model as stored in database"""
    id: PyObjectId = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    tenant_id: str
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # 2FA fields
    totp_secret: Optional[str] = None
    totp_enabled: bool = False
    backup_codes: List[str] = Field(default_factory=list)
    
    # Profile fields
    profile_picture_url: Optional[str] = None
    phone_verified: bool = False
    phone_verification_code: Optional[str] = None
    phone_verification_expires: Optional[datetime] = None
    
    # Security fields
    password_changed_at: Optional[datetime] = None
    failed_login_attempts: int = 0
    account_locked_until: Optional[datetime] = None
    security_score: int = 0
    
    # Email change fields
    pending_email: Optional[str] = None
    email_change_token: Optional[str] = None
    email_change_expires: Optional[datetime] = None
    
    # Internationalization fields
    language_preference: str = "en"  # Default language preference
    
    class Config:
        populate_by_name = True
        json_encoders = {ObjectId: str}


class UserResponse(UserBase):
    """User response model (without password)"""
    id: str
    tenant_id: str
    created_at: datetime
    
    class Config:
        populate_by_name = True


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
