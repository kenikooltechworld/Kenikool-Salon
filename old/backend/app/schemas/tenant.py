"""
Tenant schemas
"""
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.schemas.base import BaseSchema
from app.schemas.auth import BankAccountInput


class TenantResponse(BaseSchema):
    """Tenant response"""
    id: str
    salon_name: str
    subdomain: str
    custom_domain: Optional[str]
    owner_name: str
    phone: str
    email: str
    address: Optional[str]
    description: Optional[str]
    logo_url: Optional[str]
    brand_color: str
    qr_code_url: Optional[str]
    is_active: bool
    subscription_plan: str
    bank_account: Optional[BankAccountInput]
    created_at: datetime


class UpdateTenantRequest(BaseModel):
    """Update tenant request"""
    salon_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    address: Optional[str] = None
    description: Optional[str] = None
    logo: Optional[str] = None
    brand_color: Optional[str] = None
    bank_account: Optional[BankAccountInput] = None


class SalonNameAvailability(BaseModel):
    """Salon name availability check"""
    available: bool
    suggestion: Optional[str] = None


class PublicSalonResponse(BaseModel):
    """Public salon information"""
    id: str
    business_name: str
    subdomain: str
    logo: Optional[str]
    primary_color: str
    secondary_color: Optional[str]
    description: Optional[str]
    phone: str
    email: str
    address: Optional[str]
