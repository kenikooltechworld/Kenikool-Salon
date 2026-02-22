"""White Label System API Endpoints"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status, Query, Path
from fastapi.responses import JSONResponse, HTMLResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.white_label_asset_manager import AssetManagerService
from app.services.ssl_manager_service import SSLManagerService
from app.services.preview_engine_service import PreviewEngineService
from app.services.email_branding_service import EmailBrandingService
from app.services.theme_template_service import ThemeTemplateService
from app.services.white_label_service import WhiteLabelService
from app.utils.auth import get_current_user
from app.database import get_db

router = APIRouter(prefix="/api/white-label", tags=["white-label"])
asset_manager = AssetManagerService()
ssl_manager = SSLManagerService()
preview_engine = PreviewEngineService()
email_branding_service = EmailBrandingService()


# SSL Certificate Request/Response Models
class ProvisionSSLRequest(BaseModel):
    """Request to provision SSL certificate"""
    domain: str
    email: Optional[str] = "admin@platform.com"


class ACMEChallengeResponse(BaseModel):
    """ACME challenge response"""
    challenge_type: str
    token: str
    key_authorization: str
    instructions: str
    domain: str


class ValidateChallengeRequest(BaseModel):
    """Request to validate ACME challenge"""
    domain: str
    challenge_type: str
    token: str


class SSLCertificateResponse(BaseModel):
    """SSL certificate response"""
    domain: str
    status: str
    issued_at: Optional[str]
    expires_at: Optional[str]
    issuer: str


@router.post("/upload-logo")
async def upload_logo(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload logo for white label branding

    - **file**: Logo image file (PNG, JPG, SVG, max 5MB)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        result = await asset_manager.upload_asset(tenant_id, file, "logo")
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/upload-favicon")
async def upload_favicon(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload favicon for white label branding

    - **file**: Favicon image file (PNG, JPG, SVG, 16x16/32x32/64x64, max 1MB)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        result = await asset_manager.upload_asset(tenant_id, file, "favicon")
        return JSONResponse(status_code=status.HTTP_200_OK, content=result)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/delete-asset")
async def delete_asset(
    asset_url: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete an uploaded asset

    - **asset_url**: URL of the asset to delete
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        success = await asset_manager.delete_asset(tenant_id, asset_url)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Asset not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Asset deleted successfully"},
        )

    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# SSL Certificate Endpoints

@router.post("/provision-ssl")
async def provision_ssl(
    request: ProvisionSSLRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Provision SSL certificate for custom domain

    - **domain**: Domain to provision certificate for
    - **email**: Email for Let's Encrypt account (optional)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate domain format
        if not request.domain or "." not in request.domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid domain format",
            )

        # Provision certificate
        success, error, cert = await ssl_manager.provision_certificate(
            tenant_id=tenant_id,
            domain=request.domain,
            email=request.email
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error or "Failed to provision SSL certificate",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "SSL certificate provisioned successfully",
                "domain": cert.domain,
                "expires_at": cert.expires_at.isoformat() if cert else None,
                "nginx_configured": True,
                "note": "Nginx has been configured for this domain with SSL"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/acme-challenge")
async def get_acme_challenge(
    domain: str = Query(..., description="Domain to generate challenge for"),
    challenge_type: str = Query("dns-01", description="Challenge type: dns-01 or http-01"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get ACME challenge for domain verification

    - **domain**: Domain to generate challenge for
    - **challenge_type**: Type of challenge (dns-01 or http-01)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate challenge type
        if challenge_type not in ["dns-01", "http-01"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge type must be 'dns-01' or 'http-01'",
            )

        # Generate challenge
        success, error, challenge = await ssl_manager.get_acme_challenge(
            domain=domain,
            challenge_type=challenge_type
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error or "Failed to generate ACME challenge",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "challenge_type": challenge.challenge_type,
                "token": challenge.token,
                "key_authorization": challenge.key_authorization,
                "instructions": challenge.instructions,
                "domain": challenge.domain,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/validate-challenge")
async def validate_challenge(
    request: ValidateChallengeRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Validate ACME challenge response

    - **domain**: Domain being validated
    - **challenge_type**: Type of challenge (dns-01 or http-01)
    - **token**: Challenge token
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate challenge type
        if request.challenge_type not in ["dns-01", "http-01"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Challenge type must be 'dns-01' or 'http-01'",
            )

        # Validate challenge
        success, error = await ssl_manager.validate_acme_challenge(
            domain=request.domain,
            challenge_type=request.challenge_type,
            token=request.token
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error or "Failed to validate ACME challenge",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "ACME challenge validated successfully",
                "domain": request.domain,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )



# Preview Endpoints

class PreviewRequest(BaseModel):
    """Request to generate preview"""
    branding_config: Dict[str, Any] = {}
    page_type: str = "home"


@router.post("/preview")
async def generate_preview(
    request: PreviewRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate preview of white label branding

    - **branding_config**: Branding configuration to preview
    - **page_type**: Type of page to preview (home, booking, checkout)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate page type
        valid_page_types = ["home", "booking", "checkout"]
        if request.page_type not in valid_page_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid page type. Must be one of: {', '.join(valid_page_types)}",
            )

        # Generate preview
        preview = await preview_engine.generate_preview(
            branding_config=request.branding_config,
            page_type=request.page_type,
            tenant_id=tenant_id,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "html": preview.html,
                "page_type": preview.page_type,
                "generated_at": preview.generated_at.isoformat(),
                "accessibility_warnings": [
                    {
                        "type": w.type,
                        "severity": w.severity,
                        "message": w.message,
                        "suggestion": w.suggestion,
                    }
                    for w in preview.accessibility_warnings
                ],
                "branding_applied": preview.branding_applied,
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/preview-html")
async def generate_preview_html(
    request: PreviewRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Generate preview HTML (returns raw HTML for iframe embedding)

    - **branding_config**: Branding configuration to preview
    - **page_type**: Type of page to preview (home, booking, checkout)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate page type
        valid_page_types = ["home", "booking", "checkout"]
        if request.page_type not in valid_page_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid page type. Must be one of: {', '.join(valid_page_types)}",
            )

        # Generate preview
        preview = await preview_engine.generate_preview(
            branding_config=request.branding_config,
            page_type=request.page_type,
            tenant_id=tenant_id,
        )

        return HTMLResponse(content=preview.html, status_code=status.HTTP_200_OK)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/preview-component")
async def preview_component(
    component: str = Query(..., description="Component name (header, button, card, footer)"),
    branding_config: Dict[str, Any] = {},
    current_user: dict = Depends(get_current_user),
):
    """
    Generate preview of a specific component

    - **component**: Component name (header, button, card, footer)
    - **branding_config**: Branding configuration to apply
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate component
        valid_components = ["header", "button", "card", "footer"]
        if component not in valid_components:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid component. Must be one of: {', '.join(valid_components)}",
            )

        # Generate component preview
        html = await preview_engine.render_preview_component(
            component=component,
            branding_config=branding_config,
            tenant_id=tenant_id,
        )

        return HTMLResponse(content=html, status_code=status.HTTP_200_OK)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/validate-preview")
async def validate_preview(
    branding_config: Dict[str, Any] = {},
    current_user: dict = Depends(get_current_user),
):
    """
    Validate preview configuration for issues

    - **branding_config**: Branding configuration to validate
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate configuration
        warnings = await preview_engine.validate_preview_config(branding_config)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "warnings": [
                    {
                        "type": w.type,
                        "severity": w.severity,
                        "message": w.message,
                        "suggestion": w.suggestion,
                    }
                    for w in warnings
                ],
                "has_errors": any(w.severity == "error" for w in warnings),
                "has_warnings": any(w.severity == "warning" for w in warnings),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Email Domain Validation Endpoints

class ValidateEmailDomainRequest(BaseModel):
    """Request to validate email domain"""
    domain: str


@router.post("/validate-email-domain")
async def validate_email_domain(
    request: ValidateEmailDomainRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Validate email domain configuration for SPF, DKIM, and DMARC records

    - **domain**: Email domain to validate (e.g., example.com)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate domain format
        if not request.domain or "." not in request.domain:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid domain format. Please provide a valid domain (e.g., example.com)",
            )

        # Validate email domain
        result = await email_branding_service.validate_email_domain(request.domain)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )



# Theme Template Endpoints

class TemplateResponse(BaseModel):
    """Template response model"""
    id: str
    name: str
    category: str
    description: Optional[str]
    branding: Dict[str, Any]
    preview_image_url: Optional[str]
    is_system: bool
    is_premium: bool
    created_at: str


class ApplyTemplateRequest(BaseModel):
    """Request to apply a template"""
    template_id: str
    customize: bool = True  # Allow customization after application


class TemplateListResponse(BaseModel):
    """Template list response"""
    templates: List[TemplateResponse]
    total: int
    skip: int
    limit: int


@router.get("/templates")
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category: spa, barber, salon, modern, classic"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get available theme templates

    - **category**: Optional category filter (spa, barber, salon, modern, classic)
    - **skip**: Number of templates to skip
    - **limit**: Maximum number of templates to return
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        template_service = ThemeTemplateService(db)
        
        # Get templates for tenant (includes system templates)
        templates = await template_service.get_templates(
            category=category,
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )
        
        # Get total count
        total = await template_service.count_templates(
            category=category,
            tenant_id=tenant_id,
        )
        
        template_responses = [
            TemplateResponse(
                id=t.id,
                name=t.name,
                category=t.category,
                description=t.description,
                branding=t.branding,
                preview_image_url=t.preview_image_url,
                is_system=t.is_system,
                is_premium=t.is_premium,
                created_at=t.created_at.isoformat(),
            )
            for t in templates
        ]
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "templates": [t.model_dump() for t in template_responses],
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/apply-template")
async def apply_template(
    request: ApplyTemplateRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Apply a theme template to white label configuration

    - **template_id**: ID of the template to apply
    - **customize**: Whether to allow customization after application
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        template_service = ThemeTemplateService(db)
        white_label_service = WhiteLabelService(db)
        
        # Get the template
        template = await template_service.get_template(request.template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        
        # Get or create white label config
        config = await white_label_service.get_config(tenant_id)
        if not config:
            # Create new config with template branding
            from app.schemas.white_label import WhiteLabelConfigCreate
            config_data = WhiteLabelConfigCreate(
                branding=template.branding,
            )
            config = await white_label_service.create_config(tenant_id, config_data)
        else:
            # Update existing config with template branding
            from app.schemas.white_label import WhiteLabelConfigUpdate
            update_data = WhiteLabelConfigUpdate(
                branding=template.branding,
            )
            config = await white_label_service.update_config(tenant_id, update_data)
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Template applied successfully",
                "template_id": request.template_id,
                "template_name": template.name,
                "branding_applied": template.branding,
                "customize_enabled": request.customize,
                "config_id": config.id if config else None,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/templates/{template_id}")
async def get_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get a specific template by ID

    - **template_id**: ID of the template to retrieve
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        template_service = ThemeTemplateService(db)
        template = await template_service.get_template(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        
        # Check access: user can access system templates or their own templates
        if not template.is_system and template.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this template",
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "id": template.id,
                "name": template.name,
                "category": template.category,
                "description": template.description,
                "branding": template.branding,
                "preview_image_url": template.preview_image_url,
                "is_system": template.is_system,
                "is_premium": template.is_premium,
                "created_at": template.created_at.isoformat(),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/templates/save-custom")
async def save_custom_template(
    name: str = Query(..., description="Template name"),
    category: str = Query(..., description="Template category"),
    branding: Dict[str, Any] = {},
    description: Optional[str] = Query(None, description="Template description"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Save current branding as a custom template

    - **name**: Name for the custom template
    - **category**: Category for the template
    - **branding**: Branding configuration to save
    - **description**: Optional description
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate category
        valid_categories = ["spa", "barber", "salon", "modern", "classic"]
        if category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
            )

        template_service = ThemeTemplateService(db)
        
        # Create custom template
        template = await template_service.create_template(
            name=name,
            category=category,
            branding=branding,
            description=description,
            tenant_id=tenant_id,
            is_system=False,
            is_premium=False,
            created_by=current_user.get("user_id"),
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Custom template saved successfully",
                "template_id": template.id,
                "template_name": template.name,
                "category": template.category,
            }
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Delete a custom template

    - **template_id**: ID of the template to delete
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        template_service = ThemeTemplateService(db)
        
        # Get template to verify ownership
        template = await template_service.get_template(template_id)
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        
        # Check ownership: cannot delete system templates
        if template.is_system:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system templates",
            )
        
        if template.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this template",
            )
        
        # Delete template
        success = await template_service.delete_template(template_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete template",
            )
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Template deleted successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )



# Template Import/Export Endpoints

class ExportConfigRequest(BaseModel):
    """Request to export configuration"""
    include_assets: bool = False


class ImportConfigRequest(BaseModel):
    """Request to import configuration"""
    config_json: Dict[str, Any]
    save_as_template: bool = False
    template_name: Optional[str] = None
    template_category: Optional[str] = None


@router.post("/export-config")
async def export_config(
    request: ExportConfigRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Export white label configuration as JSON

    - **include_assets**: Whether to include asset URLs in export
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        white_label_service = WhiteLabelService(db)
        config = await white_label_service.get_config(tenant_id)
        
        if not config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="White label configuration not found",
            )
        
        # Build export data
        export_data = {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "branding": config.branding.model_dump(),
            "domain": config.domain.model_dump(),
            "features": config.features.model_dump(),
        }
        
        # Optionally include asset URLs
        if request.include_assets:
            export_data["assets"] = {
                "logo_url": config.branding.logo_url,
                "favicon_url": config.branding.favicon_url,
            }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Configuration exported successfully",
                "config": export_data,
                "filename": f"white-label-config-{tenant_id}.json",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/import-config")
async def import_config(
    request: ImportConfigRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Import white label configuration from JSON

    - **config_json**: Configuration JSON to import
    - **save_as_template**: Whether to save as a template
    - **template_name**: Name for saved template (if save_as_template=True)
    - **template_category**: Category for saved template (if save_as_template=True)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate config structure
        if not isinstance(request.config_json, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuration must be a JSON object",
            )
        
        # Extract branding configuration
        branding_data = request.config_json.get("branding", {})
        domain_data = request.config_json.get("domain", {})
        features_data = request.config_json.get("features", {})
        
        if not branding_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuration must include branding data",
            )
        
        white_label_service = WhiteLabelService(db)
        
        # Get or create config
        config = await white_label_service.get_config(tenant_id)
        
        if not config:
            # Create new config
            from app.schemas.white_label import WhiteLabelConfigCreate
            config_data = WhiteLabelConfigCreate(
                branding=branding_data,
                domain=domain_data,
                features=features_data,
            )
            config = await white_label_service.create_config(tenant_id, config_data)
        else:
            # Update existing config
            from app.schemas.white_label import WhiteLabelConfigUpdate
            update_data = WhiteLabelConfigUpdate(
                branding=branding_data,
                domain=domain_data,
                features=features_data,
            )
            config = await white_label_service.update_config(tenant_id, update_data)
        
        response_data = {
            "message": "Configuration imported successfully",
            "config_id": config.id if config else None,
        }
        
        # Optionally save as template
        if request.save_as_template:
            if not request.template_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="template_name is required when save_as_template=True",
                )
            
            if not request.template_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="template_category is required when save_as_template=True",
                )
            
            # Validate category
            valid_categories = ["spa", "barber", "salon", "modern", "classic"]
            if request.template_category not in valid_categories:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
                )
            
            template_service = ThemeTemplateService(db)
            template = await template_service.create_template(
                name=request.template_name,
                category=request.template_category,
                branding=branding_data,
                tenant_id=tenant_id,
                is_system=False,
                is_premium=False,
                created_by=current_user.get("user_id"),
            )
            
            response_data["template_saved"] = True
            response_data["template_id"] = template.id
            response_data["template_name"] = template.name
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response_data
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/export-template/{template_id}")
async def export_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Export a template as JSON

    - **template_id**: ID of the template to export
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        template_service = ThemeTemplateService(db)
        template = await template_service.get_template(template_id)
        
        if not template:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found",
            )
        
        # Check access
        if not template.is_system and template.tenant_id != tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this template",
            )
        
        # Build export data
        export_data = {
            "version": "1.0",
            "exported_at": datetime.utcnow().isoformat(),
            "template_name": template.name,
            "template_category": template.category,
            "template_description": template.description,
            "branding": template.branding,
        }
        
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Template exported successfully",
                "template": export_data,
                "filename": f"template-{template.name.lower().replace(' ', '-')}.json",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/import-template")
async def import_template(
    template_json: Dict[str, Any],
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Import a template from JSON

    - **template_json**: Template JSON to import
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate template structure
        if not isinstance(template_json, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Template must be a JSON object",
            )
        
        # Extract required fields
        template_name = template_json.get("template_name")
        template_category = template_json.get("template_category")
        branding = template_json.get("branding", {})
        description = template_json.get("template_description")
        
        if not template_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="template_name is required",
            )
        
        if not template_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="template_category is required",
            )
        
        if not branding:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="branding configuration is required",
            )
        
        # Validate category
        valid_categories = ["spa", "barber", "salon", "modern", "classic"]
        if template_category not in valid_categories:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
            )
        
        template_service = ThemeTemplateService(db)
        
        # Create template
        template = await template_service.create_template(
            name=template_name,
            category=template_category,
            branding=branding,
            description=description,
            tenant_id=tenant_id,
            is_system=False,
            is_premium=False,
            created_by=current_user.get("user_id"),
        )
        
        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Template imported successfully",
                "template_id": template.id,
                "template_name": template.name,
                "category": template.category,
            }
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Add datetime import at the top if not already present

# White Label Analytics Endpoints

from app.services.white_label_analytics_service import WhiteLabelAnalyticsService


class TrackDomainVisitRequest(BaseModel):
    """Request to track domain visit"""
    domain: str
    page_type: str
    user_agent: str
    ip_address: str
    referrer: Optional[str] = None
    session_id: Optional[str] = None


class TrackConversionRequest(BaseModel):
    """Request to track conversion"""
    domain: str
    session_id: str
    conversion_type: str
    conversion_value: float
    booking_id: Optional[str] = None


class TrackEmailOpenRequest(BaseModel):
    """Request to track email open"""
    email_id: str
    recipient_email: str
    campaign_id: Optional[str] = None


class TrackPageLoadRequest(BaseModel):
    """Request to track page load time"""
    domain: str
    page_type: str
    load_time_ms: float
    resource_timing: Optional[Dict[str, float]] = None


@router.post("/analytics/track-visit")
async def track_domain_visit(
    request: TrackDomainVisitRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Track a visit to white-labeled domain

    - **domain**: Custom domain visited
    - **page_type**: Type of page (home, booking, checkout, etc.)
    - **user_agent**: User agent string
    - **ip_address**: Visitor IP address
    - **referrer**: HTTP referrer (optional)
    - **session_id**: Session ID for tracking user journey (optional)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        result = await analytics_service.track_domain_visit(
            tenant_id=tenant_id,
            domain=request.domain,
            page_type=request.page_type,
            user_agent=request.user_agent,
            ip_address=request.ip_address,
            referrer=request.referrer,
            session_id=request.session_id,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Visit tracked successfully",
                "session_id": result["session_id"],
                "timestamp": result["timestamp"].isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/analytics/track-conversion")
async def track_conversion(
    request: TrackConversionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Track a conversion on white-labeled site

    - **domain**: Custom domain
    - **session_id**: Session ID
    - **conversion_type**: Type of conversion (booking, purchase, signup, etc.)
    - **conversion_value**: Value of conversion
    - **booking_id**: Associated booking ID (optional)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        result = await analytics_service.track_conversion(
            tenant_id=tenant_id,
            domain=request.domain,
            session_id=request.session_id,
            conversion_type=request.conversion_type,
            conversion_value=request.conversion_value,
            booking_id=request.booking_id,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Conversion tracked successfully",
                "conversion_type": result["conversion_type"],
                "conversion_value": result["conversion_value"],
                "timestamp": result["timestamp"].isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/analytics/track-email-open")
async def track_email_open(
    request: TrackEmailOpenRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Track email open for branded emails

    - **email_id**: Email message ID
    - **recipient_email**: Recipient email address
    - **campaign_id**: Associated campaign ID (optional)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        result = await analytics_service.track_email_open(
            tenant_id=tenant_id,
            email_id=request.email_id,
            recipient_email=request.recipient_email,
            campaign_id=request.campaign_id,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Email open tracked successfully",
                "email_id": result["email_id"],
                "opened_at": result["opened_at"].isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/analytics/track-page-load")
async def track_page_load(
    request: TrackPageLoadRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Track page load time for white-labeled site

    - **domain**: Custom domain
    - **page_type**: Type of page
    - **load_time_ms**: Total page load time in milliseconds
    - **resource_timing**: Breakdown of resource load times (optional)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        result = await analytics_service.track_page_load_time(
            tenant_id=tenant_id,
            domain=request.domain,
            page_type=request.page_type,
            load_time_ms=request.load_time_ms,
            resource_timing=request.resource_timing,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Page load time tracked successfully",
                "load_time_ms": result["load_time_ms"],
                "timestamp": result["timestamp"].isoformat(),
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/traffic")
async def get_traffic_analytics(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    domain: Optional[str] = Query(None, description="Optional specific domain to filter"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get traffic analytics for white-labeled site

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **domain**: Optional specific domain to filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        result = await analytics_service.get_traffic_analytics(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            domain=domain,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/performance")
async def get_performance_analytics(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    domain: Optional[str] = Query(None, description="Optional specific domain to filter"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get performance analytics for white-labeled site

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **domain**: Optional specific domain to filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        result = await analytics_service.get_performance_analytics(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            domain=domain,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/reports")
async def get_analytics_reports(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    report_type: str = Query("comprehensive", description="Report type: comprehensive, traffic, conversion, email, performance, branding, comparison"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get comprehensive analytics reports

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **report_type**: Type of report (comprehensive, traffic, conversion, email, performance, branding, comparison)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        # Validate report type
        valid_report_types = ["comprehensive", "traffic", "conversion", "email", "performance", "branding", "comparison"]
        if report_type not in valid_report_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid report type. Must be one of: {', '.join(valid_report_types)}",
            )

        analytics_service = WhiteLabelAnalyticsService(db)
        report_data = {}

        # Build report based on type
        if report_type in ["comprehensive", "traffic"]:
            report_data["traffic"] = await analytics_service.get_traffic_analytics(
                tenant_id=tenant_id,
                start_date=start,
                end_date=end,
            )

        if report_type in ["comprehensive", "conversion"]:
            report_data["conversion"] = await analytics_service.get_conversion_analytics(
                tenant_id=tenant_id,
                start_date=start,
                end_date=end,
            )

        if report_type in ["comprehensive", "email"]:
            report_data["email"] = await analytics_service.get_email_analytics(
                tenant_id=tenant_id,
                start_date=start,
                end_date=end,
            )

        if report_type in ["comprehensive", "performance"]:
            report_data["performance"] = await analytics_service.get_performance_analytics(
                tenant_id=tenant_id,
                start_date=start,
                end_date=end,
            )

        if report_type in ["comprehensive", "branding"]:
            report_data["branding_effectiveness"] = await analytics_service.get_branding_effectiveness(
                tenant_id=tenant_id,
                start_date=start,
                end_date=end,
            )

        if report_type in ["comprehensive", "comparison"]:
            report_data["branded_vs_default"] = await analytics_service.compare_branded_vs_default(
                tenant_id=tenant_id,
                start_date=start,
                end_date=end,
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "report_type": report_type,
                "generated_at": datetime.utcnow().isoformat(),
                "date_range": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
                "data": report_data,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# White Label Performance Monitoring Endpoints

from app.services.white_label_performance_monitoring import WhiteLabelPerformanceMonitoring


@router.get("/analytics/page-load-metrics")
async def get_page_load_metrics(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    domain: Optional[str] = Query(None, description="Optional specific domain to filter"),
    page_type: Optional[str] = Query(None, description="Optional specific page type to filter"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get detailed page load time metrics for white-labeled site

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **domain**: Optional specific domain to filter
    - **page_type**: Optional specific page type to filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        monitoring_service = WhiteLabelPerformanceMonitoring(db)
        result = await monitoring_service.get_page_load_metrics(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            domain=domain,
            page_type=page_type,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/resource-timing")
async def get_resource_timing_analysis(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    domain: Optional[str] = Query(None, description="Optional specific domain to filter"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get resource timing analysis for white-labeled site

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **domain**: Optional specific domain to filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        monitoring_service = WhiteLabelPerformanceMonitoring(db)
        result = await monitoring_service.get_resource_timing_analysis(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            domain=domain,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/email-performance")
async def get_email_performance_metrics(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    campaign_id: Optional[str] = Query(None, description="Optional specific campaign to filter"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get email performance metrics for branded emails

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **campaign_id**: Optional specific campaign to filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        monitoring_service = WhiteLabelPerformanceMonitoring(db)
        result = await monitoring_service.get_email_performance_metrics(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            campaign_id=campaign_id,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/performance-comparison")
async def get_performance_comparison(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Compare performance between branded and default sites

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        monitoring_service = WhiteLabelPerformanceMonitoring(db)
        result = await monitoring_service.compare_performance_metrics(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=result
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/analytics/performance-alerts")
async def get_performance_alerts(
    start_date: str = Query(..., description="Start date (ISO format: YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (ISO format: YYYY-MM-DD)"),
    severity: Optional[str] = Query(None, description="Optional severity filter (info, warning, critical)"),
    acknowledged: Optional[bool] = Query(None, description="Optional acknowledged status filter"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get performance alerts

    - **start_date**: Start date (ISO format: YYYY-MM-DD)
    - **end_date**: End date (ISO format: YYYY-MM-DD)
    - **severity**: Optional severity filter (info, warning, critical)
    - **acknowledged**: Optional acknowledged status filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse dates
        try:
            start = datetime.fromisoformat(start_date)
            end = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date format. Use ISO format: YYYY-MM-DD",
            )

        # Validate severity
        if severity and severity not in ["info", "warning", "critical"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid severity. Must be one of: info, warning, critical",
            )

        monitoring_service = WhiteLabelPerformanceMonitoring(db)
        alerts = await monitoring_service.get_performance_alerts(
            tenant_id=tenant_id,
            start_date=start,
            end_date=end,
            severity=severity,
            acknowledged=acknowledged,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "total_alerts": len(alerts),
                "alerts": alerts,
                "date_range": {
                    "start": start.isoformat(),
                    "end": end.isoformat(),
                },
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


class AcknowledgeAlertRequest(BaseModel):
    """Request to acknowledge an alert"""
    alert_id: str


@router.post("/analytics/acknowledge-alert")
async def acknowledge_alert(
    request: AcknowledgeAlertRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Acknowledge a performance alert

    - **alert_id**: ID of the alert to acknowledge
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        monitoring_service = WhiteLabelPerformanceMonitoring(db)
        success = await monitoring_service.acknowledge_alert(
            alert_id=request.alert_id,
            tenant_id=tenant_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Alert acknowledged successfully",
                "alert_id": request.alert_id,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Branding Version Management Endpoints

from app.services.branding_version_service import BrandingVersionService
from app.schemas.branding_version import BrandingVersionListResponse


class RollbackRequest(BaseModel):
    """Request to rollback to a previous version"""
    version_number: int = Field(..., description="Version number to rollback to")


class VersionDiffRequest(BaseModel):
    """Request to get diff between versions"""
    from_version: int = Field(..., description="Source version number")
    to_version: int = Field(..., description="Target version number")


@router.get("/versions")
async def get_branding_versions(
    skip: int = Query(0, ge=0, description="Number of versions to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of versions to return"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get all branding versions for the tenant

    - **skip**: Number of versions to skip (for pagination)
    - **limit**: Maximum number of versions to return
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        versions, total = await version_service.list_versions(
            tenant_id=tenant_id,
            skip=skip,
            limit=limit,
        )

        # Get current version
        current_version = await version_service.get_current_version(tenant_id)
        current_version_number = current_version.version_number if current_version else None

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "versions": [
                    {
                        "id": v.id,
                        "version_number": v.version_number,
                        "created_at": v.created_at.isoformat(),
                        "created_by": v.created_by,
                        "change_description": v.change_description,
                        "is_current": v.is_current,
                    }
                    for v in versions
                ],
                "total": total,
                "current_version": current_version_number,
                "skip": skip,
                "limit": limit,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/versions/{version_number}")
async def get_branding_version(
    version_number: int = Path(..., ge=1, description="Version number to retrieve"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get a specific branding version

    - **version_number**: Version number to retrieve
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        version = await version_service.get_version(tenant_id, version_number)

        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "id": version.id,
                "version_number": version.version_number,
                "snapshot": version.snapshot.model_dump(),
                "created_at": version.created_at.isoformat(),
                "created_by": version.created_by,
                "change_description": version.change_description,
                "is_current": version.is_current,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/rollback")
async def rollback_branding(
    request: RollbackRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Rollback branding configuration to a previous version

    - **version_number**: Version number to rollback to
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        
        # Check if version exists
        version = await version_service.get_version(tenant_id, request.version_number)
        if not version:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {request.version_number} not found",
            )

        # Perform rollback
        new_version = await version_service.rollback_to_version(
            tenant_id=tenant_id,
            version_number=request.version_number,
            created_by=current_user.get("user_id"),
        )

        # Update white label config with rolled-back configuration
        white_label_service = WhiteLabelService(db)
        from app.schemas.white_label import WhiteLabelConfigUpdate
        
        update_data = WhiteLabelConfigUpdate(
            branding=new_version.snapshot.branding,
            domain=new_version.snapshot.domain,
            features=new_version.snapshot.features,
            is_active=new_version.snapshot.is_active,
        )
        
        config = await white_label_service.update_config(tenant_id, update_data)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": f"Successfully rolled back to version {request.version_number}",
                "new_version_number": new_version.version_number,
                "rolled_back_from": request.version_number,
                "created_at": new_version.created_at.isoformat(),
                "config_id": config.id if config else None,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/version-diff")
async def get_version_diff(
    request: VersionDiffRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get differences between two branding versions

    - **from_version**: Source version number
    - **to_version**: Target version number
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        
        # Get both versions to verify they exist
        from_v = await version_service.get_version(tenant_id, request.from_version)
        to_v = await version_service.get_version(tenant_id, request.to_version)

        if not from_v:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {request.from_version} not found",
            )

        if not to_v:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {request.to_version} not found",
            )

        # Get diff
        diff = await version_service.get_version_diff(
            tenant_id=tenant_id,
            from_version=request.from_version,
            to_version=request.to_version,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "from_version": diff.from_version,
                "to_version": diff.to_version,
                "changes": diff.changes,
                "added_fields": diff.added_fields,
                "removed_fields": diff.removed_fields,
                "modified_fields": diff.modified_fields,
                "has_changes": bool(diff.changes or diff.added_fields or diff.removed_fields),
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/version-count")
async def get_version_count(
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get total number of versions for the tenant
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        count = await version_service.get_version_count(tenant_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "total_versions": count,
                "max_versions_stored": 10,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/export-version/{version_number}")
async def export_version(
    version_number: int = Path(..., ge=1, description="Version number to export"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Export a specific version as JSON

    - **version_number**: Version number to export
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        version_data = await version_service.export_version(tenant_id, version_number)

        if not version_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Version {version_number} not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Version exported successfully",
                "version": version_data,
                "filename": f"branding-version-{version_number}.json",
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


class ImportVersionRequest(BaseModel):
    """Request to import a version"""
    version_data: Dict[str, Any] = Field(..., description="Version data to import")
    change_description: Optional[str] = Field(None, description="Description of the import")


@router.post("/import-version")
async def import_version(
    request: ImportVersionRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Import a version from JSON

    - **version_data**: Version data to import
    - **change_description**: Optional description of the import
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        version_service = BrandingVersionService(db)
        
        # Import version
        new_version = await version_service.import_version(
            tenant_id=tenant_id,
            version_data=request.version_data,
            created_by=current_user.get("user_id"),
        )

        # Update white label config with imported configuration
        white_label_service = WhiteLabelService(db)
        from app.schemas.white_label import WhiteLabelConfigUpdate
        
        update_data = WhiteLabelConfigUpdate(
            branding=new_version.snapshot.branding,
            domain=new_version.snapshot.domain,
            features=new_version.snapshot.features,
            is_active=new_version.snapshot.is_active,
        )
        
        config = await white_label_service.update_config(tenant_id, update_data)

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Version imported successfully",
                "version_number": new_version.version_number,
                "created_at": new_version.created_at.isoformat(),
                "config_id": config.id if config else None,
            }
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# Scheduled Branding Changes and A/B Testing Endpoints

from app.services.scheduled_branding_service import ScheduledBrandingService


class ScheduleBrandingChangeRequest(BaseModel):
    """Request to schedule a branding change"""
    scheduled_for: str = Field(..., description="ISO format datetime when change should be applied")
    branding_config: Dict[str, Any] = Field(..., description="Branding configuration to apply")
    description: Optional[str] = Field(None, description="Description of the change")


class CreateABTestRequest(BaseModel):
    """Request to create an A/B test"""
    test_name: str = Field(..., description="Name of the A/B test")
    variant_a: Dict[str, Any] = Field(..., description="Branding configuration for variant A")
    variant_b: Dict[str, Any] = Field(..., description="Branding configuration for variant B")
    split_percentage: float = Field(default=50.0, ge=1, le=99, description="Percentage of users to see variant A")
    duration_days: int = Field(default=7, ge=1, description="Duration of the test in days")
    description: Optional[str] = Field(None, description="Description of the test")


class EndABTestRequest(BaseModel):
    """Request to end an A/B test"""
    winning_variant: Optional[str] = Field(None, description="Winning variant to apply (variant_a or variant_b)")


@router.post("/schedule-branding-change")
async def schedule_branding_change(
    request: ScheduleBrandingChangeRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Schedule a branding change for a future date

    - **scheduled_for**: ISO format datetime when change should be applied
    - **branding_config**: Branding configuration to apply
    - **description**: Optional description of the change
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Parse scheduled time
        try:
            scheduled_for = datetime.fromisoformat(request.scheduled_for)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid datetime format. Use ISO format: YYYY-MM-DDTHH:MM:SS",
            )

        scheduled_service = ScheduledBrandingService(db)
        result = await scheduled_service.schedule_branding_change(
            tenant_id=tenant_id,
            scheduled_for=scheduled_for,
            branding_config=request.branding_config,
            description=request.description,
            created_by=current_user.get("user_id"),
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "Branding change scheduled successfully",
                "change_id": result["id"],
                "scheduled_for": result["scheduled_for"],
                "status": result["status"],
            }
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/scheduled-changes")
async def get_scheduled_changes(
    status_filter: Optional[str] = Query(None, description="Filter by status: pending, executed, failed, cancelled"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get scheduled branding changes for the tenant

    - **status_filter**: Optional status filter
    - **skip**: Number of changes to skip
    - **limit**: Maximum number of changes to return
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        changes, total = await scheduled_service.list_scheduled_changes(
            tenant_id=tenant_id,
            status=status_filter,
            skip=skip,
            limit=limit,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "changes": changes,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/scheduled-changes/{change_id}")
async def get_scheduled_change(
    change_id: str = Path(..., description="ID of the scheduled change"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get a specific scheduled branding change

    - **change_id**: ID of the scheduled change
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        change = await scheduled_service.get_scheduled_change(tenant_id, change_id)

        if not change:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled change not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=change
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/scheduled-changes/{change_id}/cancel")
async def cancel_scheduled_change(
    change_id: str = Path(..., description="ID of the scheduled change to cancel"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Cancel a scheduled branding change

    - **change_id**: ID of the scheduled change to cancel
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        success = await scheduled_service.cancel_scheduled_change(tenant_id, change_id)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Scheduled change not found or cannot be cancelled",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Scheduled change cancelled successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/scheduled-changes/{change_id}/execute")
async def execute_scheduled_change(
    change_id: str = Path(..., description="ID of the scheduled change to execute"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Execute a scheduled branding change immediately

    - **change_id**: ID of the scheduled change to execute
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        success = await scheduled_service.execute_scheduled_change(tenant_id, change_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Scheduled change executed successfully"}
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# A/B Testing Endpoints

@router.post("/ab-tests")
async def create_ab_test(
    request: CreateABTestRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Create an A/B test for branding configurations

    - **test_name**: Name of the A/B test
    - **variant_a**: Branding configuration for variant A
    - **variant_b**: Branding configuration for variant B
    - **split_percentage**: Percentage of users to see variant A (default: 50)
    - **duration_days**: Duration of the test in days (default: 7)
    - **description**: Optional description of the test
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        result = await scheduled_service.create_ab_test(
            tenant_id=tenant_id,
            test_name=request.test_name,
            variant_a=request.variant_a,
            variant_b=request.variant_b,
            split_percentage=request.split_percentage,
            duration_days=request.duration_days,
            description=request.description,
            created_by=current_user.get("user_id"),
        )

        return JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "message": "A/B test created successfully",
                "test_id": result["test_id"],
                "test_name": result["test_name"],
                "status": result["status"],
                "start_date": result["start_date"],
                "end_date": result["end_date"],
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/ab-tests")
async def get_ab_tests(
    status_filter: Optional[str] = Query(None, description="Filter by status: active, completed"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get A/B tests for the tenant

    - **status_filter**: Optional status filter (active, completed)
    - **skip**: Number of tests to skip
    - **limit**: Maximum number of tests to return
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        tests, total = await scheduled_service.list_ab_tests(
            tenant_id=tenant_id,
            status=status_filter,
            skip=skip,
            limit=limit,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "tests": tests,
                "total": total,
                "skip": skip,
                "limit": limit,
            }
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/ab-tests/{test_id}")
async def get_ab_test(
    test_id: str = Path(..., description="ID of the A/B test"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get a specific A/B test

    - **test_id**: ID of the A/B test
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        test = await scheduled_service.get_ab_test(tenant_id, test_id)

        if not test:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=test
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/ab-tests/{test_id}/results")
async def get_ab_test_results(
    test_id: str = Path(..., description="ID of the A/B test"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get results and statistics for an A/B test

    - **test_id**: ID of the A/B test
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        results = await scheduled_service.get_ab_test_results(tenant_id, test_id)

        if not results:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=results
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ab-tests/{test_id}/end")
async def end_ab_test(
    test_id: str = Path(..., description="ID of the A/B test to end"),
    request: EndABTestRequest = None,
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    End an A/B test and optionally apply the winning variant

    - **test_id**: ID of the A/B test to end
    - **winning_variant**: Optional winning variant to apply (variant_a or variant_b)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        if request is None:
            request = EndABTestRequest()

        scheduled_service = ScheduledBrandingService(db)
        success = await scheduled_service.end_ab_test(
            tenant_id=tenant_id,
            test_id=test_id,
            winning_variant=request.winning_variant,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "A/B test ended successfully",
                "winning_variant_applied": request.winning_variant is not None,
            }
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/ab-tests/{test_id}/variant")
async def get_user_variant(
    test_id: str = Path(..., description="ID of the A/B test"),
    user_id: str = Query(..., description="User ID to determine variant for"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Get which variant a user should see in an A/B test

    - **test_id**: ID of the A/B test
    - **user_id**: User ID to determine variant for
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        scheduled_service = ScheduledBrandingService(db)
        variant = await scheduled_service.get_variant_for_user(tenant_id, test_id, user_id)

        if not variant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found or not active",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "test_id": test_id,
                "user_id": user_id,
                "variant": variant,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ab-tests/{test_id}/track-visit")
async def track_ab_test_visit(
    test_id: str = Path(..., description="ID of the A/B test"),
    variant: str = Query(..., description="Variant (variant_a or variant_b)"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Track a visit for an A/B test variant

    - **test_id**: ID of the A/B test
    - **variant**: Variant (variant_a or variant_b)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        if variant not in ["variant_a", "variant_b"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid variant. Must be variant_a or variant_b",
            )

        scheduled_service = ScheduledBrandingService(db)
        success = await scheduled_service.track_ab_test_visit(tenant_id, test_id, variant)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Visit tracked successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post("/ab-tests/{test_id}/track-conversion")
async def track_ab_test_conversion(
    test_id: str = Path(..., description="ID of the A/B test"),
    variant: str = Query(..., description="Variant (variant_a or variant_b)"),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_db),
):
    """
    Track a conversion for an A/B test variant

    - **test_id**: ID of the A/B test
    - **variant**: Variant (variant_a or variant_b)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        if variant not in ["variant_a", "variant_b"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid variant. Must be variant_a or variant_b",
            )

        scheduled_service = ScheduledBrandingService(db)
        success = await scheduled_service.track_ab_test_conversion(tenant_id, test_id, variant)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="A/B test not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={"message": "Conversion tracked successfully"}
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# White Label Health Monitoring Endpoints

from app.services.white_label_health_monitoring import WhiteLabelHealthMonitoring
from app.services.white_label_alerting_service import WhiteLabelAlertingService


@router.get("/health/status")
async def get_health_status(
    current_user: dict = Depends(get_current_user),
):
    """
    Get current health status for the tenant's white label configuration
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        monitoring_service = WhiteLabelHealthMonitoring()
        health = await monitoring_service.get_health_status(tenant_id)

        if not health:
            return JSONResponse(
                status_code=status.HTTP_200_OK,
                content={
                    "status": "unknown",
                    "message": "No health check data available yet",
                    "checked_at": None,
                }
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "status": health.get("status"),
                "domain": health.get("domain"),
                "checks": health.get("checks"),
                "issues": health.get("issues"),
                "checked_at": health.get("checked_at").isoformat() if health.get("checked_at") else None,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health/history")
async def get_health_history(
    limit: int = Query(30, ge=1, le=100, description="Maximum number of records to return"),
    days: int = Query(7, ge=1, le=90, description="Number of days to look back"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get health check history for the tenant

    - **limit**: Maximum number of records to return (default: 30)
    - **days**: Number of days to look back (default: 7)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        monitoring_service = WhiteLabelHealthMonitoring()
        history = await monitoring_service.get_health_history(
            tenant_id=tenant_id,
            limit=limit,
            days=days,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "total_records": len(history),
                "limit": limit,
                "days": days,
                "history": [
                    {
                        "status": h.get("status"),
                        "domain": h.get("domain"),
                        "issues_count": len(h.get("issues", [])),
                        "checked_at": h.get("checked_at").isoformat() if h.get("checked_at") else None,
                    }
                    for h in history
                ],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health/uptime")
async def get_uptime_metrics(
    days: int = Query(30, ge=1, le=365, description="Number of days to analyze"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get uptime metrics for the tenant's white label configuration

    - **days**: Number of days to analyze (default: 30)
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        monitoring_service = WhiteLabelHealthMonitoring()
        metrics = await monitoring_service.get_uptime_metrics(
            tenant_id=tenant_id,
            days=days,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=metrics
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health/dashboard")
async def get_health_dashboard(
    current_user: dict = Depends(get_current_user),
):
    """
    Get comprehensive health dashboard for the tenant's white label configuration
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        monitoring_service = WhiteLabelHealthMonitoring()
        alerting_service = WhiteLabelAlertingService()

        # Get current health status
        health = await monitoring_service.get_health_status(tenant_id)

        # Get uptime metrics
        uptime_30d = await monitoring_service.get_uptime_metrics(tenant_id, days=30)
        uptime_7d = await monitoring_service.get_uptime_metrics(tenant_id, days=7)

        # Get alert summary
        alert_summary = await alerting_service.get_alert_summary(tenant_id)

        # Get recent health history
        history = await monitoring_service.get_health_history(tenant_id, limit=10, days=7)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "current_status": {
                    "status": health.get("status") if health else "unknown",
                    "domain": health.get("domain") if health else None,
                    "issues": health.get("issues", []) if health else [],
                    "checked_at": health.get("checked_at").isoformat() if health and health.get("checked_at") else None,
                },
                "uptime": {
                    "last_7_days": uptime_7d,
                    "last_30_days": uptime_30d,
                },
                "alerts": alert_summary,
                "recent_checks": [
                    {
                        "status": h.get("status"),
                        "issues_count": len(h.get("issues", [])),
                        "checked_at": h.get("checked_at").isoformat() if h.get("checked_at") else None,
                    }
                    for h in history
                ],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/health/all-tenants")
async def get_all_tenants_health_summary(
    current_user: dict = Depends(get_current_user),
):
    """
    Get health summary for all white label configurations (admin only)
    """
    try:
        # Check if user is admin
        user_role = current_user.get("role")
        if user_role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only administrators can view all tenants health",
            )

        monitoring_service = WhiteLabelHealthMonitoring()
        summary = await monitoring_service.get_all_tenants_health_summary()

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


# White Label Alerts Endpoints

@router.get("/alerts")
async def get_alerts(
    limit: int = Query(50, ge=1, le=500, description="Maximum number of alerts to return"),
    skip: int = Query(0, ge=0, description="Number of alerts to skip"),
    severity: Optional[str] = Query(None, description="Filter by severity: info, warning, critical"),
    acknowledged: Optional[bool] = Query(None, description="Filter by acknowledged status"),
    current_user: dict = Depends(get_current_user),
):
    """
    Get alerts for the tenant

    - **limit**: Maximum number of alerts to return (default: 50)
    - **skip**: Number of alerts to skip (default: 0)
    - **severity**: Optional severity filter (info, warning, critical)
    - **acknowledged**: Optional acknowledged status filter
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        # Validate severity
        if severity and severity not in ["info", "warning", "critical"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid severity. Must be one of: info, warning, critical",
            )

        alerting_service = WhiteLabelAlertingService()
        alerts, total = await alerting_service.get_alerts(
            tenant_id=tenant_id,
            limit=limit,
            skip=skip,
            severity=severity,
            acknowledged=acknowledged,
        )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "total": total,
                "limit": limit,
                "skip": skip,
                "alerts": [
                    {
                        "id": str(a.get("_id")),
                        "alert_type": a.get("alert_type"),
                        "severity": a.get("severity"),
                        "message": a.get("message"),
                        "domain": a.get("domain"),
                        "acknowledged": a.get("acknowledged"),
                        "created_at": a.get("created_at").isoformat() if a.get("created_at") else None,
                        "acknowledged_at": a.get("acknowledged_at").isoformat() if a.get("acknowledged_at") else None,
                    }
                    for a in alerts
                ],
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


class AcknowledgeHealthAlertRequest(BaseModel):
    """Request to acknowledge a health alert"""
    alert_id: str


@router.post("/alerts/acknowledge")
async def acknowledge_health_alert(
    request: AcknowledgeHealthAlertRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Acknowledge a health alert

    - **alert_id**: ID of the alert to acknowledge
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        user_id = current_user.get("user_id")
        alerting_service = WhiteLabelAlertingService()
        success = await alerting_service.acknowledge_alert(
            alert_id=request.alert_id,
            tenant_id=tenant_id,
            user_id=user_id,
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alert not found",
            )

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "Alert acknowledged successfully",
                "alert_id": request.alert_id,
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get("/alerts/summary")
async def get_alert_summary(
    current_user: dict = Depends(get_current_user),
):
    """
    Get alert summary for the tenant
    """
    try:
        tenant_id = current_user.get("tenant_id")
        if not tenant_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Tenant ID not found",
            )

        alerting_service = WhiteLabelAlertingService()
        summary = await alerting_service.get_alert_summary(tenant_id)

        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=summary
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
