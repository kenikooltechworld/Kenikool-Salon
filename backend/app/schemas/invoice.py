"""Pydantic schemas for invoice management."""

from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import datetime


class InvoiceLineItemRequest(BaseModel):
    """Request schema for invoice line item."""

    service_id: str = Field(..., description="Service ID")
    service_name: str = Field(..., max_length=255, description="Service name")
    quantity: Decimal = Field(default=Decimal("1"), ge=1, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")


class InvoiceLineItemResponse(BaseModel):
    """Response schema for invoice line item."""

    service_id: str
    service_name: str
    quantity: Decimal
    unit_price: Decimal
    total: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class InvoiceCreateRequest(BaseModel):
    """Request schema for creating an invoice."""

    appointment_id: Optional[str] = Field(None, description="Appointment ID")
    customer_id: str = Field(..., description="Customer ID")
    line_items: List[InvoiceLineItemRequest] = Field(..., description="Line items")
    discount: Decimal = Field(default=Decimal("0"), ge=0, description="Discount amount")
    tax: Decimal = Field(default=Decimal("0"), ge=0, description="Tax amount")
    notes: Optional[str] = Field(None, max_length=1000, description="Invoice notes")


class InvoiceUpdateRequest(BaseModel):
    """Request schema for updating an invoice."""

    status: Optional[str] = Field(None, description="Invoice status")
    discount: Optional[Decimal] = Field(None, ge=0, description="Discount amount")
    tax: Optional[Decimal] = Field(None, ge=0, description="Tax amount")
    notes: Optional[str] = Field(None, max_length=1000, description="Invoice notes")


class InvoiceMarkPaidRequest(BaseModel):
    """Request schema for marking invoice as paid."""

    paid_at: Optional[datetime] = Field(None, description="Payment date")


class InvoiceResponse(BaseModel):
    """Response schema for an invoice."""

    id: str
    appointment_id: Optional[str]
    customer_id: str
    line_items: List[InvoiceLineItemResponse]
    subtotal: Decimal
    discount: Decimal
    tax: Decimal
    total: Decimal
    status: str
    due_date: Optional[str]
    paid_at: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class InvoiceListResponse(BaseModel):
    """Response schema for listing invoices."""

    invoices: List[InvoiceResponse]
    total: int
    page: int
    page_size: int
