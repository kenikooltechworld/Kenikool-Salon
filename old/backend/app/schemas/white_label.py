from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Dict, Any
from datetime import datetime


class WhiteLabelBranding(BaseModel):
    """White-label branding configuration"""
    logo_url: Optional[str] = Field(None, description="Custom logo URL")
    logo_file: Optional[str] = Field(None, description="Custom logo file path in storage")
    logo_file_path: Optional[str] = Field(None, description="Logo file path in MinIO/S3 storage")
    favicon_url: Optional[str] = Field(None, description="Custom favicon URL")
    favicon_file: Optional[str] = Field(None, description="Custom favicon file path in storage")
    favicon_file_path: Optional[str] = Field(None, description="Favicon file path in MinIO/S3 storage")
    primary_color: Optional[str] = Field(None, description="Primary brand color (hex)")
    secondary_color: Optional[str] = Field(None, description="Secondary brand color (hex)")
    accent_color: Optional[str] = Field(None, description="Accent color (hex)")
    font_family: Optional[str] = Field(None, description="Custom font family")
    company_name: Optional[str] = Field(None, description="Company name")
    tagline: Optional[str] = Field(None, description="Company tagline")


class WhiteLabelDomain(BaseModel):
    """Custom domain configuration"""
    custom_domain: Optional[str] = Field(None, description="Custom domain (e.g., booking.yoursalon.com)")
    ssl_enabled: bool = Field(default=True, description="Whether SSL is enabled")
    dns_configured: bool = Field(default=False, description="Whether DNS is properly configured")


class WhiteLabelFeatures(BaseModel):
    """Feature toggles for white-label"""
    hide_powered_by: bool = Field(default=False, description="Hide 'Powered by' branding")
    custom_email_domain: Optional[str] = Field(None, description="Custom email domain")
    custom_support_email: Optional[str] = Field(None, description="Custom support email")
    custom_support_phone: Optional[str] = Field(None, description="Custom support phone")
    custom_terms_url: Optional[str] = Field(None, description="Custom terms of service URL")
    custom_privacy_url: Optional[str] = Field(None, description="Custom privacy policy URL")
    enable_custom_css: bool = Field(default=False, description="Allow custom CSS")
    custom_css: Optional[str] = Field(None, description="Custom CSS code")


class WhiteLabelConfigBase(BaseModel):
    """Base white-label configuration"""
    branding: WhiteLabelBranding = Field(default_factory=WhiteLabelBranding, description="Branding settings")
    domain: WhiteLabelDomain = Field(default_factory=WhiteLabelDomain, description="Domain settings")
    features: WhiteLabelFeatures = Field(default_factory=WhiteLabelFeatures, description="Feature settings")
    asset_storage_urls: Dict[str, str] = Field(default_factory=dict, description="Mapping of asset types to their storage URLs")
    is_active: bool = Field(default=False, description="Whether white-label is active")


class WhiteLabelConfigCreate(WhiteLabelConfigBase):
    """Schema for creating white-label config"""
    pass


class WhiteLabelConfigUpdate(BaseModel):
    """Schema for updating white-label config"""
    branding: Optional[WhiteLabelBranding] = None
    domain: Optional[WhiteLabelDomain] = None
    features: Optional[WhiteLabelFeatures] = None
    is_active: Optional[bool] = None


class WhiteLabelConfig(WhiteLabelConfigBase):
    """White-label configuration with metadata"""
    id: str = Field(..., alias="_id", description="Configuration ID")
    tenant_id: str = Field(..., description="Tenant ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "wl_123",
                "tenant_id": "tenant_123",
                "branding": {
                    "logo_url": "https://example.com/logo.png",
                    "primary_color": "#FF6B6B",
                    "company_name": "My Salon Brand"
                },
                "domain": {
                    "custom_domain": "booking.mysalon.com",
                    "ssl_enabled": True,
                    "dns_configured": True
                },
                "features": {
                    "hide_powered_by": True,
                    "custom_support_email": "support@mysalon.com"
                },
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z"
            }
        }


class DNSInstructions(BaseModel):
    """DNS configuration instructions"""
    record_type: str = Field(..., description="DNS record type (CNAME, A, etc.)")
    host: str = Field(..., description="Host/Name field")
    value: str = Field(..., description="Value/Points to field")
    ttl: int = Field(default=3600, description="TTL in seconds")
    instructions: str = Field(..., description="Human-readable instructions")


class WhiteLabelStatus(BaseModel):
    """White-label configuration status"""
    is_configured: bool = Field(..., description="Whether white-label is configured")
    is_active: bool = Field(..., description="Whether white-label is active")
    has_custom_domain: bool = Field(..., description="Whether custom domain is set")
    domain_verified: bool = Field(..., description="Whether domain is verified")
    ssl_enabled: bool = Field(..., description="Whether SSL is enabled")
    branding_complete: bool = Field(..., description="Whether branding is complete")
    issues: list[str] = Field(default_factory=list, description="List of configuration issues")
