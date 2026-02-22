"""Pydantic schemas for payment operations."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class PaymentBase(BaseModel):
    """Base payment schema with common fields."""

    amount: Decimal = Field(..., gt=0, description="Payment amount")
    customer_id: str = Field(..., description="Customer ID")
    invoice_id: str = Field(..., description="Invoice ID")
    gateway: str = Field(default="paystack", description="Payment gateway")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")


class PaymentCreate(PaymentBase):
    """Schema for creating a payment."""

    reference: str = Field(..., description="Payment reference from gateway")


class PaymentUpdate(BaseModel):
    """Schema for updating a payment."""

    status: Optional[str] = Field(None, description="Payment status")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


class PaymentResponse(PaymentBase):
    """Schema for payment response."""

    id: str = Field(..., description="Payment ID")
    reference: str = Field(..., description="Payment reference")
    status: str = Field(..., description="Payment status")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        """Pydantic config."""

        from_attributes = True


class PaymentListResponse(BaseModel):
    """Schema for payment list response."""

    total: int = Field(..., description="Total number of payments")
    page: int = Field(..., description="Current page")
    page_size: int = Field(..., description="Page size")
    payments: list[PaymentResponse] = Field(..., description="List of payments")


class PaymentInitializeRequest(BaseModel):
    """Schema for payment initialization request."""

    amount: Decimal = Field(..., gt=0, description="Payment amount")
    customer_id: str = Field(..., description="Customer ID")
    invoice_id: str = Field(..., description="Invoice ID")
    email: str = Field(..., description="Customer email for payment")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    idempotency_key: Optional[str] = Field(None, description="Unique key for idempotency (prevents duplicate payments)")


class PaymentInitializeResponse(BaseModel):
    """Schema for payment initialization response."""

    payment_id: str = Field(..., description="Payment ID")
    authorization_url: str = Field(..., description="URL for customer to complete payment")
    access_code: str = Field(..., description="Paystack access code")
    reference: str = Field(..., description="Paystack reference")
