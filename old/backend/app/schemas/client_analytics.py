"""
Client Analytics schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime, date


class ClientAnalyticsResponse(BaseModel):
    """Client analytics response"""
    id: str
    client_id: str
    tenant_id: str
    
    # Visit metrics
    total_visits: int = Field(default=0, description="Total number of visits")
    first_visit_date: Optional[datetime] = Field(default=None, description="Date of first visit")
    last_visit_date: Optional[datetime] = Field(default=None, description="Date of last visit")
    average_days_between_visits: Optional[float] = Field(default=None, description="Average days between visits")
    predicted_next_visit: Optional[date] = Field(default=None, description="Predicted next visit date")
    
    # Financial metrics
    total_spent: float = Field(default=0.0, description="Total amount spent")
    average_transaction_value: float = Field(default=0.0, description="Average transaction value")
    lifetime_value: float = Field(default=0.0, description="Customer lifetime value")
    
    # Engagement metrics
    no_show_count: int = Field(default=0, description="Number of no-shows")
    cancellation_count: int = Field(default=0, description="Number of cancellations")
    attendance_rate: float = Field(default=100.0, description="Attendance rate percentage")
    
    # Retention metrics
    is_at_risk: bool = Field(default=False, description="Is client at risk of churning")
    churn_risk_score: float = Field(default=0.0, ge=0, le=1, description="Churn risk score (0-1)")
    days_since_last_visit: int = Field(default=0, description="Days since last visit")
    
    # Service preferences
    favorite_services: List[str] = Field(default=[], description="List of favorite service IDs")
    favorite_stylists: List[str] = Field(default=[], description="List of favorite stylist IDs")
    
    # Timestamps
    calculated_at: datetime = Field(default_factory=datetime.utcnow, description="When analytics were calculated")
    updated_at: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    
    class Config:
        populate_by_name = True


class ClientAnalyticsSummary(BaseModel):
    """Simplified client analytics summary"""
    lifetime_value: float = Field(alias="lifetimeValue")
    average_spend: float = Field(alias="averageSpend")
    visit_frequency_days: Optional[int] = Field(alias="visitFrequencyDays")
    predicted_next_visit: Optional[date] = Field(alias="predictedNextVisit")
    churn_risk_score: float = Field(alias="churnRiskScore")
    is_at_risk: bool = Field(alias="isAtRisk")
    attendance_rate: float = Field(alias="attendanceRate")
    
    class Config:
        populate_by_name = True
        by_alias = True


class GlobalAnalyticsResponse(BaseModel):
    """Global client analytics response"""
    total_clients: int = Field(alias="totalClients")
    active_clients: int = Field(alias="activeClients")
    at_risk_clients: int = Field(alias="atRiskClients")
    new_clients_this_month: int = Field(alias="newClientsThisMonth")
    average_lifetime_value: float = Field(alias="averageLifetimeValue")
    average_visit_frequency: float = Field(alias="averageVisitFrequency")
    total_revenue: float = Field(alias="totalRevenue")
    segment_distribution: Dict[str, int] = Field(alias="segmentDistribution")
    
    class Config:
        populate_by_name = True
        by_alias = True
