from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class ThemeTemplateBase(BaseModel):
    """Base theme template configuration"""
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Template category: spa, barber, salon, modern, classic")
    config: Dict[str, Any] = Field(..., description="Branding configuration for this template")
    preview_image_url: Optional[str] = Field(None, description="URL to template preview image")


class ThemeTemplateCreate(ThemeTemplateBase):
    """Schema for creating theme template"""
    is_premium: bool = Field(default=False, description="Whether this is a premium template")


class ThemeTemplateUpdate(BaseModel):
    """Schema for updating theme template"""
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    preview_image_url: Optional[str] = None
    is_premium: Optional[bool] = None


class ThemeTemplate(ThemeTemplateBase):
    """Theme template with metadata"""
    id: str = Field(..., alias="_id", description="Template ID")
    tenant_id: Optional[str] = Field(None, description="Tenant ID (None for system templates)")
    is_system: bool = Field(default=False, description="Whether this is a system template")
    is_premium: bool = Field(default=False, description="Whether this is a premium template")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")
    created_by: Optional[str] = Field(None, description="User ID who created the template")
    usage_count: int = Field(default=0, description="Number of times this template has been applied")

    class Config:
        populate_by_name = True
        json_schema_extra = {
            "example": {
                "_id": "tpl_123",
                "tenant_id": None,
                "name": "Modern Spa",
                "description": "Modern and elegant spa branding template",
                "category": "spa",
                "config": {
                    "branding": {
                        "primary_color": "#8B7355",
                        "secondary_color": "#D4A574",
                        "accent_color": "#E8D5C4",
                        "font_family": "Playfair Display",
                        "company_name": "Your Spa Name"
                    }
                },
                "preview_image_url": "https://example.com/preview.png",
                "is_system": True,
                "is_premium": False,
                "created_at": "2024-01-01T00:00:00Z",
                "usage_count": 42
            }
        }


class ThemeTemplateListResponse(BaseModel):
    """Response for listing theme templates"""
    templates: list[ThemeTemplate] = Field(..., description="List of templates")
    total: int = Field(..., description="Total number of templates")
    categories: list[str] = Field(..., description="Available template categories")


class ThemeTemplateApply(BaseModel):
    """Request to apply a theme template"""
    template_id: str = Field(..., description="Template ID to apply")
    customize: bool = Field(default=False, description="Whether to allow customization after applying")
    custom_overrides: Optional[Dict[str, Any]] = Field(None, description="Custom overrides to apply after template")
