"""
Membership analytics model for storing aggregated membership data.
Used for tracking MRR, ARR, churn rate, and other key metrics.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class RevenueByPlan(BaseModel):
    """Revenue breakdown by plan"""
    revenue: float
    subscribers: int


class StatusDistribution(BaseModel):
    """Distribution of subscriptions by status"""
    active: int = 0
    paused: int = 0
    cancelled: int = 0
    expired: int = 0
    trial: int = 0
    grace_period: int = 0


class MembershipAnalytics(BaseModel):
    """Daily membership analytics snapshot"""
    id: Optional[str] = Field(None, alias="_id")
    tenant_id: str
    date: datetime
    mrr: float  # Monthly Recurring Revenue
    arr: float  # Annual Recurring Revenue
    active_subscribers: int
    churn_rate: float  # Percentage
    revenue_by_plan: Dict[str, RevenueByPlan]
    status_distribution: StatusDistribution
    total_subscriptions: int
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True
