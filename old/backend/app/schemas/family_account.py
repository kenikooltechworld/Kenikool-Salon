"""
Family Account schemas
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.base import BaseSchema


class RelationshipType(str, Enum):
    """Family relationship types"""
    PARENT = "parent"
    CHILD = "child"
    SPOUSE = "spouse"
    SIBLING = "sibling"
    GRANDPARENT = "grandparent"
    GRANDCHILD = "grandchild"
    OTHER = "other"


class FamilyMember(BaseModel):
    """Family member model"""
    client_id: str = Field(..., description="Client ID")
    client_name: str = Field(..., min_length=2, max_length=100)
    client_phone: str = Field(..., min_length=10, max_length=20)
    client_email: Optional[EmailStr] = None
    relationship: RelationshipType = Field(..., description="Relationship to primary account holder")
    is_primary: bool = Field(False, description="Whether this is the primary account holder")
    added_at: datetime = Field(default_factory=datetime.now)


class FamilyAccountCreate(BaseModel):
    """Family account creation request"""
    primary_client_id: str = Field(..., description="Primary account holder client ID")
    family_name: Optional[str] = Field(None, max_length=100, description="Family name (e.g., 'The Johnsons')")
    credit_limit: Optional[float] = Field(None, ge=0, description="Credit limit for deferred payments in Naira")
    members: List[FamilyMember] = Field(default_factory=list, description="Initial family members")


class FamilyAccountUpdate(BaseModel):
    """Family account update request"""
    family_name: Optional[str] = Field(None, max_length=100)
    credit_limit: Optional[float] = Field(None, ge=0)


class FamilyMemberAdd(BaseModel):
    """Add family member request"""
    client_id: str = Field(..., description="Client ID to add")
    relationship: RelationshipType = Field(..., description="Relationship to primary account holder")


class FamilyAccount(BaseSchema):
    """Family account model"""
    id: str
    tenant_id: str
    family_account_id: str = Field(..., description="Unique family account identifier")
    primary_client_id: str
    family_name: Optional[str] = None
    members: List[FamilyMember]
    credit_limit: Optional[float] = None
    current_balance: float = Field(0.0, description="Current outstanding balance")
    total_bookings: int = Field(0, description="Total bookings across all family members")
    total_spent: float = Field(0.0, description="Total amount spent by family")
    loyalty_points: int = Field(0, description="Combined family loyalty points")
    is_active: bool = Field(True, description="Whether family account is active")
    created_at: datetime
    updated_at: datetime


class FamilyBookingCreate(BaseModel):
    """Family booking with deferred payment"""
    family_account_id: str = Field(..., description="Family account ID")
    client_id: str = Field(..., description="Family member client ID")
    service_id: str = Field(..., description="Service ID")
    stylist_id: str = Field(..., description="Stylist ID")
    booking_date: str = Field(..., description="Booking date/time in ISO format")
    notes: Optional[str] = Field(None, max_length=500)
    use_deferred_payment: bool = Field(True, description="Use deferred payment (pay later)")


class FamilyAccountFilter(BaseModel):
    """Family account filter parameters"""
    is_active: Optional[bool] = None
    has_outstanding_balance: Optional[bool] = None
    min_total_spent: Optional[float] = None
