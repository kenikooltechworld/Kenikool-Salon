"""Pydantic schemas for POS discounts."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from decimal import Decimal


class DiscountCreateRequest(BaseModel):
    """Request schema for creating a discount."""

    discount_code: str = Field(..., max_length=50, description="Discount code")
    discount_type: str = Field(..., description="Discount type: percentage, fixed, loyalty, or bulk")
    discount_value: Decimal = Field(..., ge=0, description="Discount value")
    applicable_to: str = Field(default="transaction", description="Applicable to: transaction, item, service, or product")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Discount conditions")
    max_discount: Optional[Decimal] = Field(None, ge=0, description="Maximum discount amount")
    valid_from: Optional[str] = Field(None, description="Valid from date")
    valid_until: Optional[str] = Field(None, description="Valid until date")
    usage_limit: Optional[int] = Field(None, ge=1, description="Usage limit")


class DiscountUpdateRequest(BaseModel):
    """Request schema for updating a discount."""

    discount_value: Optional[Decimal] = Field(None, ge=0, description="Discount value")
    applicable_to: Optional[str] = Field(None, description="Applicable to")
    conditions: Optional[Dict[str, Any]] = Field(None, description="Discount conditions")
    max_discount: Optional[Decimal] = Field(None, ge=0, description="Maximum discount amount")
    active: Optional[bool] = Field(None, description="Active status")
    valid_from: Optional[str] = Field(None, description="Valid from date")
    valid_until: Optional[str] = Field(None, description="Valid until date")
    usage_limit: Optional[int] = Field(None, ge=1, description="Usage limit")


class DiscountValidateRequest(BaseModel):
    """Request schema for validating a discount."""

    discount_code: str = Field(..., description="Discount code")
    subtotal: Decimal = Field(..., ge=0, description="Transaction subtotal")


class DiscountResponse(BaseModel):
    """Response schema for a discount."""

    id: str
    discount_code: str
    discount_type: str
    discount_value: Decimal
    applicable_to: str
    conditions: Dict[str, Any]
    max_discount: Optional[Decimal]
    active: bool
    valid_from: Optional[str]
    valid_until: Optional[str]
    usage_count: int
    usage_limit: Optional[int]
    created_at: str
    updated_at: str

    class Config:
        """Pydantic config."""

        from_attributes = True


class DiscountValidateResponse(BaseModel):
    """Response schema for discount validation."""

    valid: bool
    discount_amount: Decimal
    message: str


class DiscountListResponse(BaseModel):
    """Response schema for listing discounts."""

    discounts: List[DiscountResponse]
    total: int
    page: int
    page_size: int
