from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum


class TimeGranularity(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class MetricType(str, Enum):
    BOOKINGS = "bookings"
    REVENUE = "revenue"
    CLIENTS = "clients"
    INVENTORY = "inventory"
    STAFF = "staff"


# Peak Hours Analytics
class PeakHourMetric(BaseModel):
    hour: int
    day_of_week: int
    bookings_count: int
    revenue: float
    capacity_utilization: float
    staff_count: int


class PeakHoursAnalytics(BaseModel):
    metrics: List[PeakHourMetric]
    peak_hour: int
    peak_day: int
    average_utilization: float
    recommendations: List[str]


# Inventory Analytics
class InventoryTurnover(BaseModel):
    product_id: str
    product_name: str
    turnover_rate: float
    days_inventory_outstanding: int
    stock_level: int
    reorder_point: int


class InventoryAnalytics(BaseModel):
    turnovers: List[InventoryTurnover]
    fast_moving_items: List[str]
    slow_moving_items: List[str]
    total_inventory_value: float
    forecast_accuracy: float


# Financial Analytics
class FinancialMetric(BaseModel):
    date: datetime
    revenue: float
    expenses: float
    profit: float
    margin_percentage: float


class FinancialAnalytics(BaseModel):
    metrics: List[FinancialMetric]
    total_revenue: float
    total_expenses: float
    total_profit: float
    average_margin: float
    cash_flow_trend: str


# Client Analytics
class ClientSegment(BaseModel):
    segment_id: str
    name: str
    client_count: int
    average_ltv: float
    churn_risk: float
    retention_rate: float


class ClientAnalytics(BaseModel):
    segments: List[ClientSegment]
    total_clients: int
    new_clients: int
    churned_clients: int
    average_ltv: float
    at_risk_count: int


# Campaign Analytics
class CampaignMetric(BaseModel):
    campaign_id: str
    campaign_name: str
    impressions: int
    clicks: int
    conversions: int
    roi: float
    cost: float
    revenue: float


class CampaignAnalytics(BaseModel):
    campaigns: List[CampaignMetric]
    total_roi: float
    total_cost: float
    total_revenue: float
    best_performing: str
    worst_performing: str


# Predictive Analytics
class PredictionResult(BaseModel):
    predicted_value: float
    confidence_score: float
    lower_bound: float
    upper_bound: float
    trend: str
    anomalies: List[Dict[str, Any]]


class DemandPrediction(BaseModel):
    predictions: List[float]
    dates: List[datetime]
    confidence: float
    trend: str


class ChurnPrediction(BaseModel):
    client_id: str
    churn_probability: float
    risk_level: str
    retention_strategies: List[str]


# Real-Time Analytics
class RealTimeMetric(BaseModel):
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    timestamp: datetime
    status: str


class RealTimeAnalytics(BaseModel):
    metrics: List[RealTimeMetric]
    active_bookings: int
    current_revenue: float
    staff_utilization: float
    queue_length: int


# Custom Reports
class ReportFilter(BaseModel):
    field: str
    operator: str
    value: Any


class CustomReport(BaseModel):
    report_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    metrics: List[str]
    filters: List[ReportFilter]
    date_range: Dict[str, datetime]
    granularity: TimeGranularity
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Goal Tracking
class Goal(BaseModel):
    goal_id: Optional[str] = None
    name: str
    goal_type: str
    target_value: float
    current_value: float
    start_date: datetime
    end_date: datetime
    status: str
    progress_percentage: float


class KPIMetric(BaseModel):
    kpi_id: str
    name: str
    current_value: float
    target_value: float
    status: str
    trend: str
    last_updated: datetime


# Data Export
class ExportRequest(BaseModel):
    report_id: Optional[str] = None
    format: str  # csv, excel, json, pdf
    filters: Optional[List[ReportFilter]] = None
    date_range: Optional[Dict[str, datetime]] = None


class ExportResponse(BaseModel):
    export_id: str
    status: str
    download_url: Optional[str] = None
    created_at: datetime
    expires_at: datetime
