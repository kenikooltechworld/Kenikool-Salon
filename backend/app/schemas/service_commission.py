"""Schemas for service commission API."""

from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ServiceCommissionBase(BaseModel):
    """Base schema for service commission."""

    staff_id: str
    appointment_id: str
    service_id: str
    service_price: Decimal
    commission_percentage: Decimal
    commission_amount: Decimal


class ServiceCommissionCreate(ServiceCommissionBase):
    """Schema for creating a service commission."""

    pass


class ServiceCommissionUpdate(BaseModel):
    """Schema for updating a service commission."""

    status: str = Field(..., description="Commission status (pending/paid)")


class ServiceCommissionResponse(ServiceCommissionBase):
    """Schema for service commission response."""

    id: str
    status: str
    earned_date: datetime
    paid_date: datetime | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ServiceCommissionSummary(BaseModel):
    """Schema for commission summary."""

    total_earned: Decimal
    total_pending: Decimal
    total_paid: Decimal
    total_services: int
    average_commission: Decimal


class ServiceCommissionBreakdown(BaseModel):
    """Schema for commission breakdown by service."""

    service_id: str
    service_name: str | None = None
    total_commission: Decimal
    count: int


class CommissionListResponse(BaseModel):
    """Schema for commission list response."""

    commissions: list[ServiceCommissionResponse]
    total: int
    page: int
    page_size: int


class CommissionSummaryResponse(BaseModel):
    """Schema for commission summary response."""

    summary: ServiceCommissionSummary
    breakdown: list[ServiceCommissionBreakdown]
