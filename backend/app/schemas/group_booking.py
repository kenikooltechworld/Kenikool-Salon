from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class GroupBookingParticipantBase(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    service_id: str
    staff_id: Optional[str] = None
    notes: Optional[str] = None


class GroupBookingParticipantResponse(GroupBookingParticipantBase):
    appointment_id: Optional[str] = None
    status: str = "pending"


class GroupBookingCreate(BaseModel):
    group_name: str
    group_type: str = "other"
    organizer_name: str
    organizer_email: EmailStr
    organizer_phone: str
    booking_date: datetime
    participants: List[GroupBookingParticipantBase]
    payment_option: str = "pay_later"
    special_requests: Optional[str] = None


class GroupBookingUpdate(BaseModel):
    group_name: Optional[str] = None
    booking_date: Optional[datetime] = None
    status: Optional[str] = None
    payment_status: Optional[str] = None
    special_requests: Optional[str] = None
    internal_notes: Optional[str] = None


class GroupBookingResponse(BaseModel):
    id: str
    tenant_id: str
    group_name: str
    group_type: str
    organizer_name: str
    organizer_email: str
    organizer_phone: str
    booking_date: datetime
    participants: List[GroupBookingParticipantResponse]
    total_participants: int
    base_total: Decimal
    discount_percentage: float
    discount_amount: Decimal
    final_total: Decimal
    payment_option: str
    payment_status: str
    amount_paid: Decimal
    status: str
    special_requests: Optional[str] = None
    internal_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PublicGroupBookingCreate(BaseModel):
    """Public-facing group booking creation schema"""
    group_name: str
    group_type: str = "other"
    organizer_name: str
    organizer_email: EmailStr
    organizer_phone: str
    booking_date: datetime
    participants: List[GroupBookingParticipantBase]
    payment_option: str = "pay_later"
    special_requests: Optional[str] = None
