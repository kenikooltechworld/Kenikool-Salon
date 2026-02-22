"""
Campaign and Segmentation Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError(f"Invalid ObjectId: {v}")
        return str(v)


class ClientSegment(BaseModel):
    """Client segment model for targeting campaigns"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    tenant_id: str
    name: str
    description: Optional[str] = None
    
    # Segment criteria
    criteria: Dict[str, Any] = Field(default_factory=dict)
    
    # Cached metrics
    client_count: int = 0
    last_calculated_at: Optional[datetime] = None
    
    # Metadata
    is_dynamic: bool = True  # Recalculate on each use
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


class CampaignSend(BaseModel):
    """Record of a campaign message sent to a client"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
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
        populate_by_name = True
        arbitrary_types_allowed = True


class EnhancedCampaign(BaseModel):
    """Enhanced campaign model with multi-channel and segmentation support"""
    id: Optional[PyObjectId] = Field(None, alias="_id")
    tenant_id: str
    name: str
    description: Optional[str] = None
    campaign_type: str  # birthday, seasonal, custom, win_back, triggered
    
    # Targeting
    segment_id: Optional[str] = None
    segment_criteria: Optional[Dict[str, Any]] = None
    target_client_ids: Optional[List[str]] = None
    
    # Multi-channel support
    channels: List[str] = Field(default_factory=list)  # ['sms', 'whatsapp', 'email']
    message_templates: Dict[str, str] = Field(default_factory=dict)  # channel -> message content
    email_subject: Optional[str] = None
    
    # Personalization
    personalization_tokens: Dict[str, str] = Field(default_factory=dict)
    
    # Scheduling
    scheduled_at: Optional[datetime] = None
    recurrence: Optional[str] = None  # 'daily', 'weekly', 'monthly'
    trigger_event: Optional[str] = None  # 'post_booking', 'post_visit', 'anniversary'
    
    # Budget
    budget_limit: Optional[float] = None
    estimated_cost: float = 0.0
    actual_cost: float = 0.0
    
    # A/B Testing
    is_ab_test: bool = False
    ab_test_id: Optional[str] = None
    
    # Status and metrics
    status: str = "draft"  # draft, scheduled, sending, sent, cancelled, completed
    sent_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    recipients_count: int = 0
    delivered_count: int = 0
    failed_count: int = 0
    opened_count: int = 0
    clicked_count: int = 0
    converted_count: int = 0
    
    # Channel breakdown
    channel_stats: Dict[str, Dict[str, int]] = Field(default_factory=dict)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: str
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
