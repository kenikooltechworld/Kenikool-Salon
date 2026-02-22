"""Pydantic schemas for POS receipts."""

from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class ReceiptItemResponse(BaseModel):
    """Response schema for receipt item."""

    item_type: str
    item_id: str
    item_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    tax_amount: Decimal
    discount_amount: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class ReceiptResponse(BaseModel):
    """Response schema for a receipt."""

    id: str
    transaction_id: str
    customer_id: str
    receipt_number: str
    receipt_date: str
    customer_name: str
    customer_email: Optional[str]
    customer_phone: Optional[str]
    items: List[ReceiptItemResponse]
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    payment_method: str
    payment_reference: Optional[str]
    receipt_format: str
    printed_at: Optional[str]
    emailed_at: Optional[str]
    created_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class ReceiptPrintRequest(BaseModel):
    """Request schema for printing receipt."""

    printer_name: Optional[str] = Field(None, description="Printer name")


class ReceiptEmailRequest(BaseModel):
    """Request schema for emailing receipt."""

    email: str = Field(..., description="Email address")


class ReceiptListResponse(BaseModel):
    """Response schema for listing receipts."""

    receipts: List[ReceiptResponse]
    total: int
    page: int
    page_size: int
