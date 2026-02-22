from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class IntegrationCategory(str, Enum):
    """Integration categories"""
    PAYMENT = "payment"
    MARKETING = "marketing"
    ACCOUNTING = "accounting"
    COMMUNICATION = "communication"
    ANALYTICS = "analytics"
    SCHEDULING = "scheduling"
    INVENTORY = "inventory"
    OTHER = "other"


class IntegrationStatus(str, Enum):
    """Integration installation status"""
    AVAILABLE = "available"
    INSTALLED = "installed"
    CONFIGURED = "configured"
    ACTIVE = "active"
    INACTIVE = "inactive"
    ERROR = "error"


class IntegrationBase(BaseModel):
    """Base integration schema"""
    name: str = Field(..., description="Integration name")
    description: str = Field(..., description="Integration description")
    category: IntegrationCategory = Field(..., description="Integration category")
    icon_url: Optional[str] = Field(None, description="Integration icon URL")
    provider: str = Field(..., description="Integration provider")
    version: str = Field(default="1.0.0", description="Integration version")
    documentation_url: Optional[str] = Field(None, description="Documentation URL")
    support_url: Optional[str] = Field(None, description="Support URL")
    pricing: Optional[str] = Field(None, description="Pricing information")
    features: List[str] = Field(default_factory=list, description="List of features")
    required_fields: List[str] = Field(default_factory=list, description="Required configuration fields")
    is_premium: bool = Field(default=False, description="Whether integration requires premium plan")


class IntegrationCreate(IntegrationBase):
    """Schema for creating integration"""
    pass


class Integration(IntegrationBase):
    """Integration schema with ID"""
    id: str = Field(..., alias="_id", description="Integration ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "int_123",
                "name": "Stripe Payment Gateway",
                "description": "Accept payments with Stripe",
                "category": "payment",
                "provider": "Stripe",
                "version": "1.0.0",
                "features": ["Credit card processing", "Subscription billing", "Refunds"],
                "required_fields": ["api_key", "webhook_secret"],
                "is_premium": False,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class IntegrationInstallationBase(BaseModel):
    """Base installation schema"""
    integration_id: str = Field(..., description="Integration ID")
    configuration: Dict[str, Any] = Field(default_factory=dict, description="Integration configuration")
    is_active: bool = Field(default=True, description="Whether integration is active")


class IntegrationInstallationCreate(IntegrationInstallationBase):
    """Schema for installing integration"""
    pass


class IntegrationInstallationUpdate(BaseModel):
    """Schema for updating installation"""
    configuration: Optional[Dict[str, Any]] = Field(None, description="Updated configuration")
    is_active: Optional[bool] = Field(None, description="Active status")


class IntegrationInstallation(IntegrationInstallationBase):
    """Installation schema with metadata"""
    id: str = Field(..., alias="_id", description="Installation ID")
    tenant_id: str = Field(..., description="Tenant ID")
    status: IntegrationStatus = Field(default=IntegrationStatus.INSTALLED, description="Installation status")
    installed_at: datetime = Field(..., description="Installation timestamp")
    last_sync: Optional[datetime] = Field(None, description="Last sync timestamp")
    error_message: Optional[str] = Field(None, description="Error message if status is error")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "inst_123",
                "tenant_id": "tenant_123",
                "integration_id": "int_123",
                "configuration": {"api_key": "sk_test_***"},
                "status": "active",
                "is_active": True,
                "installed_at": "2024-01-01T00:00:00Z"
            }
        }


class IntegrationWithInstallation(Integration):
    """Integration with installation status"""
    installation: Optional[IntegrationInstallation] = Field(None, description="Installation details if installed")
    is_installed: bool = Field(default=False, description="Whether integration is installed")


class IntegrationTestResult(BaseModel):
    """Result of integration test"""
    success: bool = Field(..., description="Whether test was successful")
    message: str = Field(..., description="Test result message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional details")
