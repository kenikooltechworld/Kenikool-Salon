"""Customer schemas for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import date


class CustomerCreate(BaseModel):
    """Schema for creating a customer."""

    first_name: str = Field(..., max_length=100, description="Customer first name")
    last_name: str = Field(..., max_length=100, description="Customer last name")
    email: EmailStr = Field(..., description="Customer email")
    phone: str = Field(..., max_length=20, description="Customer phone number")
    address: Optional[str] = Field(None, max_length=500, description="Customer address")
    date_of_birth: Optional[date] = Field(None, description="Customer date of birth")
    preferred_staff_id: Optional[str] = Field(None, description="Preferred staff member ID")
    preferred_services: List[str] = Field(default=[], description="List of preferred service IDs")
    communication_preference: str = Field(default="email", description="Communication preference")
    status: str = Field(default="active", description="Customer status")


class CustomerUpdate(BaseModel):
    """Schema for updating a customer."""

    first_name: Optional[str] = Field(None, max_length=100, description="Customer first name")
    last_name: Optional[str] = Field(None, max_length=100, description="Customer last name")
    email: Optional[EmailStr] = Field(None, description="Customer email")
    phone: Optional[str] = Field(None, max_length=20, description="Customer phone number")
    address: Optional[str] = Field(None, max_length=500, description="Customer address")
    date_of_birth: Optional[date] = Field(None, description="Customer date of birth")
    preferred_staff_id: Optional[str] = Field(None, description="Preferred staff member ID")
    preferred_services: Optional[List[str]] = Field(None, description="List of preferred service IDs")
    communication_preference: Optional[str] = Field(None, description="Communication preference")
    status: Optional[str] = Field(None, description="Customer status")


class CustomerResponse(BaseModel):
    """Schema for customer response."""

    id: str = Field(..., description="Customer ID")
    first_name: str = Field(..., description="Customer first name")
    last_name: str = Field(..., description="Customer last name")
    email: str = Field(..., description="Customer email")
    phone: str = Field(..., description="Customer phone number")
    address: Optional[str] = Field(None, description="Customer address")
    date_of_birth: Optional[str] = Field(None, description="Customer date of birth")
    preferred_staff_id: Optional[str] = Field(None, description="Preferred staff member ID")
    preferred_services: List[str] = Field(default=[], description="List of preferred service IDs")
    communication_preference: str = Field(..., description="Communication preference")
    status: str = Field(..., description="Customer status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class CustomerListResponse(BaseModel):
    """Schema for customer list response."""

    customers: List[CustomerResponse] = Field(..., description="List of customers")
    total: int = Field(..., description="Total number of customers")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
