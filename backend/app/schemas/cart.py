"""Pydantic schemas for POS cart."""

from typing import Optional, List
from pydantic import BaseModel, Field
from decimal import Decimal


class CartItemRequest(BaseModel):
    """Request schema for cart item."""

    item_type: str = Field(..., description="Item type: service, product, or package")
    item_id: str = Field(..., description="Item ID")
    item_name: str = Field(..., max_length=255, description="Item name")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")


class CartItemResponse(BaseModel):
    """Response schema for cart item."""

    item_type: str
    item_id: str
    item_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

    class Config:
        """Pydantic config."""

        from_attributes = True


class CartCreateRequest(BaseModel):
    """Request schema for creating a cart."""

    customer_id: Optional[str] = Field(None, description="Customer ID")
    staff_id: str = Field(..., description="Staff ID")


class CartUpdateRequest(BaseModel):
    """Request schema for updating a cart."""

    customer_id: Optional[str] = Field(None, description="Customer ID")
    status: Optional[str] = Field(None, description="Cart status")


class CartAddItemRequest(BaseModel):
    """Request schema for adding item to cart."""

    item_type: str = Field(..., description="Item type")
    item_id: str = Field(..., description="Item ID")
    item_name: str = Field(..., description="Item name")
    quantity: int = Field(..., ge=1, description="Quantity")
    unit_price: Decimal = Field(..., ge=0, description="Unit price")


class CartResponse(BaseModel):
    """Response schema for a cart."""

    id: str
    customer_id: Optional[str]
    staff_id: str
    items: List[CartItemResponse]
    subtotal: Decimal
    tax_amount: Decimal
    discount_amount: Decimal
    total: Decimal
    status: str
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class CartListResponse(BaseModel):
    """Response schema for listing carts."""

    carts: List[CartResponse]
    total: int
    page: int
    page_size: int
