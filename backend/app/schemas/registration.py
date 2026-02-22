"""Pydantic schemas for registration endpoints."""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional


class RegisterRequest(BaseModel):
    """Registration request schema."""

    salon_name: str = Field(..., min_length=3, max_length=255)
    owner_name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=12)
    address: str = Field(..., min_length=5, max_length=500)
    bank_account: Optional[str] = Field(None, min_length=10, max_length=50)
    referral_code: Optional[str] = Field(None, pattern="^[a-zA-Z0-9]+$")

    @field_validator("bank_account", "referral_code", mode="before")
    @classmethod
    def empty_str_to_none(cls, v):
        """Convert empty strings to None for optional fields."""
        if v == "":
            return None
        return v


class RegisterResponse(BaseModel):
    """Registration response schema."""

    success: bool
    message: str
    data: Optional[dict] = None


class VerifyCodeRequest(BaseModel):
    """Verify code request schema."""

    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6, pattern="^[0-9]{6}$")


class VerifyCodeResponse(BaseModel):
    """Verify code response schema."""

    success: bool
    message: str
    data: Optional[dict] = None


class ResendCodeRequest(BaseModel):
    """Resend code request schema."""

    email: EmailStr


class ResendCodeResponse(BaseModel):
    """Resend code response schema."""

    success: bool
    message: str
    data: Optional[dict] = None
