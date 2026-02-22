"""Refund schemas for request/response validation."""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class RefundCreateRequest(BaseModel):
    """Request schema for creating a refund."""

    payment_id: str = Field(..., description="Payment ID to refund")
    amount: Decimal = Field(..., gt=0, description="Refund amount")
    reason: str = Field(..., min_length=1, max_length=500, description="Reason for refund")


class RefundResponse(BaseModel):
    """Response schema for refund."""

    id: str = Field(..., description="Refund ID")
    payment_id: str = Field(..., description="Payment ID")
    amount: Decimal = Field(..., description="Refund amount")
    reason: str = Field(..., description="Reason for refund")
    status: str = Field(..., description="Refund status (pending, success, failed)")
    reference: str = Field(..., description="Paystack refund reference")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")


class RefundListResponse(BaseModel):
    """Response schema for listing refunds."""

    total: int = Field(..., description="Total number of refunds")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Page size")
    refunds: list[RefundResponse] = Field(..., description="List of refunds")
