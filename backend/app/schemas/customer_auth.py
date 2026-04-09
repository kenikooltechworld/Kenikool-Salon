"""Customer Authentication Schemas"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class CustomerRegister(BaseModel):
    """Customer registration schema"""
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=20)
    password: str = Field(..., min_length=8)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class CustomerLogin(BaseModel):
    """Customer login schema"""
    email: EmailStr
    password: str


class CustomerToken(BaseModel):
    """Customer authentication token response"""
    access_token: str
    token_type: str = "bearer"
    customer_id: str
    email: str
    first_name: str
    last_name: str


class CustomerProfileUpdate(BaseModel):
    """Customer profile update schema"""
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, min_length=10, max_length=20)
    address: Optional[str] = Field(None, max_length=500)
    date_of_birth: Optional[str] = None
    communication_preference: Optional[str] = Field(None, pattern="^(email|sms|phone|none)$")
    notification_preferences: Optional[dict] = None


class CustomerProfile(BaseModel):
    """Customer profile response"""
    id: str
    email: str
    first_name: str
    last_name: str
    phone: str
    address: Optional[str] = None
    date_of_birth: Optional[str] = None
    email_verified: bool
    phone_verified: bool
    communication_preference: str
    notification_preferences: dict
    outstanding_balance: float
    created_at: datetime
    
    class Config:
        from_attributes = True


class BookingHistory(BaseModel):
    """Booking history response"""
    id: str
    service_name: str
    staff_name: str
    booking_date: str
    booking_time: str
    status: str
    payment_status: Optional[str] = None
    total_price: float
    notes: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True
