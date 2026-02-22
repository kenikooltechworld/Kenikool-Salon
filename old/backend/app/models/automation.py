from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AutomationSettings(BaseModel):
    """Automation settings for campaigns"""
    tenant_id: str
    
    # Birthday campaigns
    birthday_campaigns: Dict[str, Any] = Field(default_factory=dict)
    
    # Win-back campaigns
    winback_campaigns: Dict[str, Any] = Field(default_factory=dict)
    
    # Post-visit campaigns
    post_visit_campaigns: Dict[str, Any] = Field(default_factory=dict)
    
    # Global settings
    enabled: bool = True
    daily_send_limit: Optional[int] = None
    monthly_budget_limit: Optional[float] = None
    
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    updated_by: str

    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_1",
                "birthday_campaigns": {
                    "enabled": True,
                    "discount_percentage": 10,
                    "message_template": "Happy Birthday! Enjoy {{discount_percentage}}% off",
                    "channels": ["sms", "email"],
                    "send_time": "09:00"
                },
                "enabled": True
            }
        }


class AutomationHistory(BaseModel):
    """Record of automation execution"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    tenant_id: str
    automation_type: str  # birthday, winback, post_visit
    campaign_id: str
    
    # Execution details
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    recipients_count: int
    sent_count: int
    failed_count: int
    
    # Status
    status: str  # success, partial, failed
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "tenant_id": "tenant_1",
                "automation_type": "birthday",
                "campaign_id": "camp_123",
                "recipients_count": 5,
                "sent_count": 5,
                "failed_count": 0,
                "status": "success"
            }
        }
