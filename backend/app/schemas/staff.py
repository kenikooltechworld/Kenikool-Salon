"""Staff schemas for request/response validation."""

from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import date


class StaffCreate(BaseModel):
    """Schema for creating a staff member."""

    user_id: Optional[str] = Field(None, description="User ID of the staff member (optional, creates new user if not provided)")
    firstName: str = Field(..., description="First name of the staff member")
    lastName: str = Field(..., description="Last name of the staff member")
    email: str = Field(..., description="Email of the staff member")
    phone: Optional[str] = Field(None, description="Phone number of the staff member")
    role_ids: Optional[List[str]] = Field(None, description="List of role IDs to assign to the staff member")
    service_ids: Optional[List[str]] = Field(None, description="List of service IDs this staff member provides")
    specialties: List[str] = Field(default=[], description="List of specialties")
    certifications: List[str] = Field(default=[], description="List of certifications")
    certification_files: List[str] = Field(default=[], description="List of certification file URLs")
    payment_type: str = Field(default="hourly", description="Payment type: hourly, daily, weekly, monthly, or commission")
    payment_rate: float = Field(default=0, ge=0, description="Payment rate based on payment_type")
    hire_date: Optional[date] = Field(None, description="Date staff member was hired")
    bio: Optional[str] = Field(None, max_length=500, description="Staff bio/description")
    profile_image_url: Optional[str] = Field(None, max_length=500, description="Profile image URL")
    status: str = Field(default="active", description="Staff status")


class StaffUpdate(BaseModel):
    """Schema for updating a staff member."""

    service_ids: Optional[List[str]] = Field(None, description="List of service IDs this staff member provides")
    specialties: Optional[List[str]] = Field(None, description="List of specialties")
    certifications: Optional[List[str]] = Field(None, description="List of certifications")
    certification_files: Optional[List[str]] = Field(None, description="List of certification file URLs")
    payment_type: Optional[str] = Field(None, description="Payment type: hourly, daily, weekly, monthly, or commission")
    payment_rate: Optional[float] = Field(None, ge=0, description="Payment rate based on payment_type")
    hire_date: Optional[date] = Field(None, description="Date staff member was hired")
    bio: Optional[str] = Field(None, max_length=500, description="Staff bio/description")
    profile_image_url: Optional[str] = Field(None, max_length=500, description="Profile image URL")
    status: Optional[str] = Field(None, description="Staff status")


class StaffResponse(BaseModel):
    """Schema for staff response."""

    id: str = Field(..., description="Staff ID")
    user_id: str = Field(..., description="User ID")
    specialties: List[str] = Field(default=[], description="List of specialties")
    certifications: List[str] = Field(default=[], description="List of certifications")
    certification_files: List[str] = Field(default=[], description="List of certification file URLs")
    payment_type: str = Field(..., description="Payment type: hourly, daily, weekly, monthly, or commission")
    payment_rate: float = Field(..., description="Payment rate based on payment_type")
    hire_date: Optional[str] = Field(None, description="Date staff member was hired")
    bio: Optional[str] = Field(None, description="Staff bio/description")
    profile_image_url: Optional[str] = Field(None, description="Profile image URL")
    status: str = Field(..., description="Staff status")
    created_at: str = Field(..., description="Creation timestamp")
    updated_at: str = Field(..., description="Update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class StaffListResponse(BaseModel):
    """Schema for staff list response."""

    staff: List[StaffResponse] = Field(..., description="List of staff members")
    total: int = Field(..., description="Total number of staff members")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
