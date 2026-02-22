from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class BrandingVersionSnapshot(BaseModel):
    """Snapshot of branding configuration at a point in time"""
    branding: Dict[str, Any] = Field(..., description="Branding configuration")
    domain: Dict[str, Any] = Field(..., description="Domain configuration")
    features: Dict[str, Any] = Field(..., description="Features configuration")
    is_active: bool = Field(..., description="Whether configuration was active")


class BrandingVersionCreate(BaseModel):
    """Schema for creating a branding version"""
    snapshot: BrandingVersionSnapshot = Field(..., description="Configuration snapshot")
    change_description: Optional[str] = Field(None, description="Description of changes made")


class BrandingVersion(BaseModel):
    """Branding version with metadata"""
    id: str = Field(..., alias="_id", description="Version ID")
    tenant_id: str = Field(..., description="Tenant ID")
    version_number: int = Field(..., description="Version number (1-based)")
    snapshot: BrandingVersionSnapshot = Field(..., description="Configuration snapshot")
    created_at: datetime = Field(..., description="Creation timestamp")
    created_by: Optional[str] = Field(None, description="User ID who created this version")
    change_description: Optional[str] = Field(None, description="Description of changes")
    is_current: bool = Field(default=False, description="Whether this is the current active version")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "bv_123",
                "tenant_id": "tenant_123",
                "version_number": 1,
                "snapshot": {
                    "branding": {
                        "logo_url": "https://example.com/logo.png",
                        "primary_color": "#FF6B6B",
                        "company_name": "My Salon"
                    },
                    "domain": {
                        "custom_domain": "booking.mysalon.com",
                        "ssl_enabled": True,
                        "dns_configured": True
                    },
                    "features": {
                        "hide_powered_by": True
                    },
                    "is_active": True
                },
                "created_at": "2024-01-01T00:00:00Z",
                "created_by": "user_123",
                "change_description": "Initial branding setup",
                "is_current": True
            }
        }


class BrandingVersionDiff(BaseModel):
    """Difference between two branding versions"""
    from_version: int = Field(..., description="Source version number")
    to_version: int = Field(..., description="Target version number")
    changes: Dict[str, Dict[str, Any]] = Field(..., description="Changes by section (branding, domain, features)")
    added_fields: Dict[str, Any] = Field(default_factory=dict, description="Fields added")
    removed_fields: Dict[str, Any] = Field(default_factory=dict, description="Fields removed")
    modified_fields: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="Fields modified with old and new values")


class BrandingVersionListResponse(BaseModel):
    """Response for listing branding versions"""
    versions: list[BrandingVersion] = Field(..., description="List of versions")
    total: int = Field(..., description="Total number of versions")
    current_version: int = Field(..., description="Current active version number")
