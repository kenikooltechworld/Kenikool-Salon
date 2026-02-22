from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CampaignTemplate(BaseModel):
    """Campaign template model"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    tenant_id: str
    name: str
    description: Optional[str] = None
    category: str  # promotional, seasonal, retention, birthday, custom
    
    # Channel support
    channels: List[str] = Field(default_factory=list)
    
    # Message templates
    message_templates: Dict[str, str] = Field(default_factory=dict)
    email_subject: Optional[str] = None
    
    # Variables/tokens
    variables: List[str] = Field(default_factory=list)
    
    # Metadata
    is_system: bool = False
    created_by: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Birthday Special",
                "category": "birthday",
                "channels": ["sms", "email"],
                "message_templates": {
                    "sms": "Happy Birthday {{client_name}}! Enjoy {{discount_percentage}}% off",
                    "email": "Special Birthday Offer"
                },
                "variables": ["client_name", "discount_percentage"],
                "is_system": True
            }
        }


class ABTest(BaseModel):
    """A/B test model"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    campaign_id: str
    tenant_id: str
    name: str
    status: str = "draft"  # draft, running, completed
    
    # Variants
    variants: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Test configuration
    traffic_split: Dict[str, float] = Field(default_factory=dict)
    
    # Results
    winner_variant_id: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "campaign_id": "camp_123",
                "name": "Subject Line Test",
                "status": "running",
                "variants": [
                    {
                        "id": "var_1",
                        "name": "Variant A",
                        "message_content": "Limited time offer",
                        "recipients_count": 500
                    },
                    {
                        "id": "var_2",
                        "name": "Variant B",
                        "message_content": "Exclusive deal for you",
                        "recipients_count": 500
                    }
                ],
                "traffic_split": {"var_1": 50, "var_2": 50}
            }
        }
