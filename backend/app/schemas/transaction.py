"""Pydantic schemas for POS transactions."""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal
from datetime import datetime


class TransactionItemRequest(BaseModel):
    """Request schema for transaction item."""

    item_type: str = Field(..., description="Item type: service, product, or package")
    item_id: str = Field(..., description="Item ID")
    item_name: str = Field(..., max_length=255, description="Item name")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: Union[Decimal, float, int] = Field(..., description="Unit price")
    tax_rate: Union[Decimal, float, int] = Field(default=Decimal("0"), description="Tax rate percentage")
    discount_rate: Union[Decimal, float, int] = Field(default=Decimal("0"), description="Discount rate percentage")

    @field_validator("unit_price", "tax_rate", "discount_rate", mode="before")
    @classmethod
    def convert_to_decimal(cls, v):
        """Convert numeric values to Decimal."""
        if v is None:
            return Decimal("0")
        if isinstance(v, Decimal):
            return v
        try:
            decimal_val = Decimal(str(v))
            if decimal_val < 0:
                raise ValueError(f"Value must be non-negative: {v}")
            return decimal_val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid decimal value: {v}") from e


class TransactionItemResponse(BaseModel):
    """Response schema for transaction item."""

    item_type: str
    item_id: str
    item_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal
    tax_rate: Decimal
    tax_amount: Decimal
    discount_rate: Decimal
    discount_amount: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class TransactionCreateRequest(BaseModel):
    """Request schema for creating a transaction."""

    customer_id: str = Field(..., description="Customer ID")
    staff_id: str = Field(..., description="Staff ID")
    appointment_id: Optional[str] = Field(None, description="Appointment ID")
    transaction_type: str = Field(default="service", description="Transaction type")
    items: List[TransactionItemRequest] = Field(..., description="Transaction items")
    payment_method: str = Field(..., description="Payment method")
    discount_amount: Union[Decimal, float, int] = Field(default=Decimal("0"), description="Discount amount")
    notes: Optional[str] = Field(None, max_length=1000, description="Transaction notes")

    @field_validator("discount_amount", mode="before")
    @classmethod
    def convert_discount_to_decimal(cls, v):
        """Convert discount amount to Decimal."""
        if v is None:
            return Decimal("0")
        if isinstance(v, Decimal):
            return v
        try:
            decimal_val = Decimal(str(v))
            if decimal_val < 0:
                raise ValueError(f"Discount amount must be non-negative: {v}")
            return decimal_val
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid decimal value: {v}") from e


class TransactionUpdateRequest(BaseModel):
    """Request schema for updating a transaction."""

    payment_status: Optional[str] = Field(None, description="Payment status")
    notes: Optional[str] = Field(None, max_length=1000, description="Transaction notes")


class TransactionResponse(BaseModel):
    """Response schema for a transaction."""

    id: str
    customer_id: str
    staff_id: str
    appointment_id: Optional[str]
    transaction_type: str
    items: List[TransactionItemResponse]
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    payment_method: str
    payment_status: str
    reference_number: str
    paystack_reference: Optional[str]
    notes: Optional[str]
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class TransactionListResponse(BaseModel):
    """Response schema for listing transactions."""

    transactions: List[TransactionResponse]
    total: int
    page: int
    page_size: int
