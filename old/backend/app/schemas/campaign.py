"""
Campaign schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class CampaignCreate(BaseModel):
    """Create marketing campaign"""
    name: str = Field(..., max_length=200)
    campaign_type: str = Field(..., description="birthday, seasonal, promotional, custom")
    message_template: str = Field(..., description="Message template with placeholders")
    discount_code: Optional[str] = None
    discount_value: Optional[float] = None
    target_segment: Dict[str, Any] = Field(default_factory=dict, description="Segmentation criteria")
    scheduled_at: Optional[datetime] = None
    auto_send: bool = Field(default=False, description="Auto-send when scheduled")


class CampaignUpdate(BaseModel):
    """Update campaign"""
    name: Optional[str] = Field(None, max_length=200)
    message_template: Optional[str] = None
    discount_code: Optional[str] = None
    discount_value: Optional[float] = None
    target_segment: Optional[Dict[str, Any]] = None
    scheduled_at: Optional[datetime] = None
    auto_send: Optional[bool] = None


class CampaignResponse(BaseModel):
    """Campaign response"""
    id: str
    tenant_id: str
    name: str
    campaign_type: str
    message_template: str
    discount_code: Optional[str]
    discount_value: Optional[float]
    target_segment: Dict[str, Any]
    status: str  # draft, scheduled, sending, sent, failed
    scheduled_at: Optional[datetime]
    sent_at: Optional[datetime]
    recipients_count: int
    delivered_count: int
    opened_count: int
    clicked_count: int
    converted_count: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CampaignAnalyticsResponse(BaseModel):
    """Campaign analytics"""
    campaign_id: str
    campaign_name: str
    recipients_count: int
    delivered_count: int
    delivery_rate: float
    opened_count: int
    open_rate: float
    clicked_count: int
    click_rate: float
    converted_count: int
    conversion_rate: float
    revenue_generated: float
    roi: float


class ClientSegmentRequest(BaseModel):
    """Client segmentation criteria"""
    criteria: Dict[str, Any] = Field(..., description="Segmentation filters")


class ClientSegmentResponse(BaseModel):
    """Client segment preview"""
    total_clients: int
    segment_size: int
    percentage: float
    sample_clients: List[Dict[str, Any]]


# Campaign Templates
class CampaignTemplateCreate(BaseModel):
    """Create campaign template"""
    name: str = Field(..., max_length=200)
    category: str = Field(..., description="promotional, seasonal, retention, birthday, custom")
    channels: List[str] = Field(default_factory=list, description="sms, whatsapp, email")
    message_templates: Dict[str, str] = Field(default_factory=dict)
    email_subject: Optional[str] = None
    variables: List[str] = Field(default_factory=list)
    description: Optional[str] = None


class CampaignTemplateResponse(BaseModel):
    """Campaign template response"""
    id: str
    tenant_id: str
    name: str
    category: str
    channels: List[str]
    message_templates: Dict[str, str]
    email_subject: Optional[str]
    variables: List[str]
    description: Optional[str]
    is_system: bool
    created_by: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# A/B Testing
class ABTestVariant(BaseModel):
    """A/B test variant"""
    id: str
    name: str
    message_content: str
    traffic_percentage: float
    recipients_count: Optional[int] = 0


class ABTestCreate(BaseModel):
    """Create A/B test"""
    name: str = Field(..., max_length=200)
    variants: List[ABTestVariant]
    traffic_split: Dict[str, float] = Field(..., description="variant_id -> percentage")


class ABTestResponse(BaseModel):
    """A/B test response"""
    id: str
    campaign_id: str
    tenant_id: str
    name: str
    status: str  # draft, running, completed
    variants: List[ABTestVariant]
    traffic_split: Dict[str, float]
    winner_variant_id: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ABTestResultsResponse(BaseModel):
    """A/B test results"""
    test_id: str
    campaign_id: str
    name: str
    status: str
    variants: List[ABTestVariant]
    traffic_split: Dict[str, float]
    variant_performance: Dict[str, Dict[str, Any]]
    winner_variant_id: Optional[str]


# Opt-Out Management
class OptOutPreferenceCreate(BaseModel):
    """Create opt-out preference"""
    client_id: str
    channels: Dict[str, bool] = Field(..., description="sms, whatsapp, email")
    reason: Optional[str] = None


class OptOutPreferenceResponse(BaseModel):
    """Opt-out preference response"""
    client_id: str
    tenant_id: str
    channels: Dict[str, bool]
    reason: Optional[str]
    opted_out_via: str
    opted_out_at: datetime
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Advanced Scheduling
class RecurrenceConfig(BaseModel):
    """Recurrence configuration"""
    type: str = Field(..., description="daily, weekly, monthly")
    day_of_week: Optional[int] = None  # 0-6 for weekly
    day_of_month: Optional[int] = None  # 1-31 for monthly


class TriggerConfig(BaseModel):
    """Trigger configuration"""
    event: str = Field(..., description="post_booking, post_visit, anniversary")
    delay_days: Optional[int] = None


class AdvancedSchedulingUpdate(BaseModel):
    """Update advanced scheduling"""
    recurrence: Optional[RecurrenceConfig] = None
    trigger: Optional[TriggerConfig] = None
    use_optimal_send_time: Optional[bool] = None
    optimal_send_time: Optional[str] = None
