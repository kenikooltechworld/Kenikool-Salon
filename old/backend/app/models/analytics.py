from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CampaignSend(BaseModel):
    """Record of a campaign message sent to a client"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    campaign_id: str
    tenant_id: str
    client_id: str
    
    channel: str  # sms, whatsapp, email
    message_content: str
    
    # Delivery tracking
    status: str = "pending"  # pending, sent, delivered, failed, bounced
    sent_at: Optional[datetime] = None
    delivered_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    clicked_at: Optional[datetime] = None
    
    # Error handling
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    
    # Cost tracking
    cost: float = 0.0
    
    # Attribution
    booking_id: Optional[str] = None
    transaction_id: Optional[str] = None
    revenue_attributed: float = 0.0
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "tenant_id": "tenant_1",
                "client_id": "client_456",
                "channel": "sms",
                "message_content": "Hello! Check out our new services",
                "status": "delivered",
                "cost": 0.05,
                "revenue_attributed": 50.0
            }
        }


class CampaignAnalytics(BaseModel):
    """Campaign performance analytics"""
    campaign_id: str
    campaign_name: str
    
    # Delivery metrics
    total_recipients: int
    delivered: int
    failed: int
    delivery_rate: float
    
    # Engagement metrics
    opened: int
    open_rate: float
    clicked: int
    click_rate: float
    
    # Conversion metrics
    conversions: int
    conversion_rate: float
    revenue_generated: float
    roi: float
    
    # Channel breakdown
    channel_stats: Dict[str, Dict[str, Any]] = Field(default_factory=dict)
    
    # Time series data
    daily_stats: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Cost tracking
    total_cost: float
    cost_per_conversion: float
    budget_used: float
    budget_remaining: float
    
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "campaign_name": "Summer Sale",
                "total_recipients": 1000,
                "delivered": 950,
                "failed": 50,
                "delivery_rate": 95.0,
                "opened": 450,
                "open_rate": 45.0,
                "clicked": 150,
                "click_rate": 15.0,
                "conversions": 45,
                "conversion_rate": 4.5,
                "revenue_generated": 2250.0,
                "roi": 225.0,
                "total_cost": 10.0,
                "cost_per_conversion": 0.22
            }
        }
