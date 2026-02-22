"""
Dashboard schemas
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime


class DashboardMetricsResponse(BaseModel):
    """Enhanced dashboard metrics with trends"""
    total_revenue: float
    revenue_trend: Optional[float]
    total_bookings: int
    booking_trend: Optional[float]
    total_clients: int
    client_trend: Optional[float]
    new_clients: int
    returning_client_percentage: float
    retention_rate: float
    period: str
    # Additional fields for Quick Stats
    completed_bookings: Optional[int] = 0
    pending_bookings: Optional[int] = 0
    total_services: Optional[int] = 0


class RevenueDataPoint(BaseModel):
    """Single data point for revenue chart"""
    date: str
    revenue: float


class RevenueChartResponse(BaseModel):
    """Revenue chart data"""
    data: List[RevenueDataPoint]
    period: str


class TopServiceItem(BaseModel):
    """Top service performance item"""
    id: str
    name: str
    booking_count: int
    revenue: float
    trend: float


class TopServicesResponse(BaseModel):
    """Top services list"""
    services: List[TopServiceItem]


class StaffPerformanceItem(BaseModel):
    """Staff performance metrics"""
    id: str
    name: str
    revenue: float
    booking_count: int
    rating: float
    utilization: float


class StaffPerformanceResponse(BaseModel):
    """Staff performance list"""
    staff: List[StaffPerformanceItem]


class ActivityItem(BaseModel):
    """Activity feed item"""
    id: str
    type: str
    message: str
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None


class ActivityFeedResponse(BaseModel):
    """Activity feed"""
    activities: List[ActivityItem]


class AlertItem(BaseModel):
    """Alert item"""
    id: str
    type: str
    severity: str
    message: str
    action_url: Optional[str] = None


class AlertsResponse(BaseModel):
    """Alerts list"""
    alerts: List[AlertItem]


class UpcomingEventItem(BaseModel):
    """Upcoming event item"""
    date: str
    appointment_count: int
    is_fully_booked: bool


class UpcomingEventsResponse(BaseModel):
    """Upcoming events list"""
    events: List[UpcomingEventItem]


class ExpenseBreakdownItem(BaseModel):
    """Expense breakdown by category"""
    category: str
    amount: float


class ExpenseSummaryResponse(BaseModel):
    """Expense summary"""
    total_expenses: float
    expense_trend: float
    breakdown: List[ExpenseBreakdownItem]
    profit_margin: Optional[float]


class WaitlistServiceItem(BaseModel):
    """Waitlist by service"""
    service_name: str
    count: int


class WaitlistSummaryResponse(BaseModel):
    """Waitlist summary"""
    total_count: int
    by_service: List[WaitlistServiceItem]
    urgent_count: int


class QuickStatsResponse(BaseModel):
    """Quick stats"""
    avg_booking_value: float
    cancellation_rate: float
    no_show_rate: float
    online_booking_percentage: float
    gift_card_sales: float
    loyalty_points_redeemed: int
