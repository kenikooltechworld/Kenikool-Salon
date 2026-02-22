"""
Group booking schemas
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class GroupBookingMemberInput(BaseModel):
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    service_id: str

class GroupBookingMember(BaseModel):
    client_name: str
    client_phone: str
    client_email: Optional[str] = None
    service_id: str
    service_name: Optional[str] = None
    service_price: Optional[float] = None

class GroupBookingCreate(BaseModel):
    organizer_name: str
    organizer_phone: str
    organizer_email: Optional[str] = None
    booking_date: str
    members: List[GroupBookingMemberInput]
    notes: Optional[str] = None

class GroupBookingUpdate(BaseModel):
    organizer_name: Optional[str] = None
    organizer_phone: Optional[str] = None
    organizer_email: Optional[str] = None
    booking_date: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    members: Optional[List[GroupBookingMemberInput]] = None
    payment_status: Optional[str] = None
    payment_method: Optional[str] = None
    amount_paid: Optional[float] = None

class GroupBookingResponse(BaseModel):
    id: str = Field(..., alias="_id")
    tenant_id: str
    organizer_name: str
    organizer_phone: str
    organizer_email: Optional[str] = None
    booking_date: datetime
    total_members: int
    members: List[GroupBookingMember] = []
    notes: Optional[str] = None
    status: str
    total_price: float = 0.0
    payment_status: str = "unpaid"
    payment_method: Optional[str] = None
    created_at: datetime
    confirmed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    cancelled_at: Optional[datetime] = None
    
    class Config:
        populate_by_name = True
