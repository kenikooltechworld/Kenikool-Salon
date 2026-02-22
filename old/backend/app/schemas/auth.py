"""
Authentication schemas
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema


class BankAccountInput(BaseModel):
    """Bank account input"""
    bank_name: str
    account_number: str
    account_name: str
    bank_code: Optional[str] = None


class RegisterRequest(BaseModel):
    """Registration request"""
    salon_name: str = Field(..., min_length=2, max_length=100)
    owner_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    address: Optional[str] = None
    bank_account: Optional[BankAccountInput] = None


class LoginRequest(BaseModel):
    """Login request"""
    email: EmailStr
    password: str


class UserResponse(BaseSchema):
    """User response"""
    id: str
    email: str
    full_name: str
    phone: Optional[str]
    role: str
    is_active: bool
    tenant_id: str
    created_at: datetime


class AuthResponse(BaseModel):
    """Authentication response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class VerifyEmailRequest(BaseModel):
    """Email verification request"""
    token: str


class ResendVerificationRequest(BaseModel):
    """Resend verification email request"""
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    """Forgot password request"""
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Reset password request"""
    token: str
    new_password: str = Field(..., min_length=8)
