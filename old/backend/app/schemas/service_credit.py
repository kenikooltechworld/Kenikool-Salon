"""
Service credit schemas
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ServiceCreditBase(BaseModel):
    """Base service credit schema"""
    purchase_id: str = Field(..., description="Package purchase ID")
    service_id: str = Field(..., description="Service ID")
    service_name: str = Field(..., description="Service name")
    service_price: float = Field(..., description="Service price")
    initial_quantity: int = Field(..., gt=0, description="Initial quantity of credits")
    remaining_quantity: int = Field(..., ge=0, description="Remaining quantity of credits")
    reserved_quantity: int = Field(default=0, ge=0, description="Quantity reserved for bookings")
    status: str = Field(default="available", description="available, reserved, redeemed, expired")


class ServiceCreditResponse(ServiceCreditBase):
    """Service credit response schema"""
    id: str = Field(..., alias="_id")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True


class CreditReservationBase(BaseModel):
    """Base credit reservation schema"""
    credit_id: str = Field(..., description="Service credit ID")
    booking_id: str = Field(..., description="Booking ID")
    reserved_at: datetime = Field(..., description="Reservation timestamp")
    expires_at: datetime = Field(..., description="Reservation expiration time")
    status: str = Field(default="active", description="active, released, redeemed")


class CreditReservationResponse(CreditReservationBase):
    """Credit reservation response schema"""
    id: str = Field(..., alias="_id")
    
    class Config:
        populate_by_name = True


class CreditBalanceResponse(BaseModel):
    """Credit balance response schema"""
    purchase_id: str
    credits: dict = Field(..., description="Service ID -> remaining quantity mapping")
    total_remaining: int = Field(..., description="Total remaining credits across all services")
    total_reserved: int = Field(..., description="Total reserved credits across all services")


class RedemptionTransactionBase(BaseModel):
    """Base redemption transaction schema"""
    purchase_id: str = Field(..., description="Package purchase ID")
    credit_id: str = Field(..., description="Service credit ID")
    service_id: str = Field(..., description="Service ID")
    client_id: str = Field(..., description="Client ID")
    redeemed_by_staff_id: str = Field(..., description="Staff member who processed redemption")
    redemption_date: datetime = Field(..., description="Redemption timestamp")
    service_value: float = Field(..., description="Value of redeemed service")
    pos_transaction_id: Optional[str] = Field(None, description="POS transaction ID if redeemed at POS")
    booking_id: Optional[str] = Field(None, description="Booking ID if redeemed for booking")


class RedemptionTransactionResponse(RedemptionTransactionBase):
    """Redemption transaction response schema"""
    id: str = Field(..., alias="_id")
    created_at: datetime
    
    class Config:
        populate_by_name = True
