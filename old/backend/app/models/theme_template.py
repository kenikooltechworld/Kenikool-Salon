from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class ThemeTemplate(BaseModel):
    """Theme template model for white label branding"""
    id: str = Field(default_factory=lambda: str(datetime.utcnow().timestamp()))
    tenant_id: Optional[str] = Field(None, description="Tenant ID (None for system templates)")
    name: str = Field(..., description="Template name")
    description: Optional[str] = Field(None, description="Template description")
    category: str = Field(..., description="Template category: spa, barber, salon, modern, classic")
    
    # Branding configuration
    branding: Dict[str, Any] = Field(default_factory=dict, description="Branding configuration")
    
    # Preview image
    preview_image_url: Optional[str] = Field(None, description="URL to template preview image")
    
    # Template metadata
    is_system: bool = Field(default=False, description="Whether this is a system template")
    is_premium: bool = Field(default=False, description="Whether this is a premium template")
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    created_by: Optional[str] = Field(None, description="User who created the template")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Modern Spa",
                "category": "spa",
                "description": "Modern and elegant spa branding template",
                "branding": {
                    "primary_color": "#8B7355",
                    "secondary_color": "#D4A574",
                    "accent_color": "#E8D5C4",
                    "font_family": "Playfair Display",
                    "company_name": "Your Spa Name"
                },
                "preview_image_url": "https://example.com/preview.png",
                "is_system": True,
                "is_premium": False
            }
        }
