"""Email template management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends, Body
from bson import ObjectId
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated
from app.services.email_template_service import EmailTemplateService
from app.models.tenant import Tenant

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/email-templates", tags=["email-templates"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


@router.get("/customer-welcome", response_model=dict)
@tenant_isolated
async def get_customer_welcome_template(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get customer welcome email template.
    
    Returns the custom template if set, otherwise returns the default template.
    """
    try:
        tenant = Tenant.objects(id=tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant_settings = tenant.settings or {}
        custom_template = tenant_settings.get("customer_welcome_email_template", "").strip()
        
        return {
            "template": custom_template if custom_template else EmailTemplateService.get_default_customer_welcome_template(),
            "is_custom": bool(custom_template),
            "available_variables": EmailTemplateService.get_available_variables(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get customer welcome template: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get template")


@router.put("/customer-welcome", response_model=dict)
@tenant_isolated
async def update_customer_welcome_template(
    template_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update customer welcome email template.
    
    Validates and saves the custom template.
    """
    try:
        tenant = Tenant.objects(id=tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        template_str = template_data.get("template", "").strip()
        
        # Validate template syntax
        is_valid, error_message = EmailTemplateService.validate_template(template_str)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Update tenant settings
        if not tenant.settings:
            tenant.settings = {}
        
        tenant.settings["customer_welcome_email_template"] = template_str
        tenant.save()
        
        logger.info(f"Customer welcome template updated for tenant: {tenant_id}")
        
        return {
            "success": True,
            "message": "Template updated successfully",
            "template": template_str,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update customer welcome template: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update template")


@router.post("/customer-welcome/reset", response_model=dict)
@tenant_isolated
async def reset_customer_welcome_template(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Reset customer welcome email template to default.
    """
    try:
        tenant = Tenant.objects(id=tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        # Remove custom template
        if tenant.settings and "customer_welcome_email_template" in tenant.settings:
            tenant.settings["customer_welcome_email_template"] = ""
            tenant.save()
        
        logger.info(f"Customer welcome template reset for tenant: {tenant_id}")
        
        return {
            "success": True,
            "message": "Template reset to default",
            "template": EmailTemplateService.get_default_customer_welcome_template(),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset customer welcome template: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to reset template")


@router.post("/customer-welcome/preview", response_model=dict)
@tenant_isolated
async def preview_customer_welcome_template(
    preview_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Preview customer welcome email template with sample data.
    """
    try:
        from jinja2 import Template, TemplateSyntaxError
        
        template_str = preview_data.get("template", "").strip()
        if not template_str:
            raise HTTPException(status_code=400, detail="Template is required")
        
        # Validate template
        is_valid, error_message = EmailTemplateService.validate_template(template_str)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_message)
        
        # Get tenant for sample data
        tenant = Tenant.objects(id=tenant_id).first()
        if not tenant:
            raise HTTPException(status_code=404, detail="Tenant not found")
        
        tenant_settings = tenant.settings or {}
        
        # Sample context data
        sample_context = {
            "customer_name": "John Doe",
            "customer_email": "john.doe@example.com",
            "customer_phone": "+1234567890",
            "business_name": tenant.name,
            "business_address": tenant.address or "123 Main Street, City, State",
            "business_phone": tenant_settings.get("phone", "+1234567890"),
            "business_email": tenant_settings.get("email", "info@business.com"),
            "logo_url": tenant.logo_url,
            "primary_color": tenant.primary_color or "#6366f1",
            "secondary_color": tenant.secondary_color or "#8b5cf6",
            "booking_url": f"https://{tenant.subdomain}.example.com/book",
        }
        
        # Render template
        template = Template(template_str)
        rendered_html = template.render(**sample_context)
        
        return {
            "success": True,
            "html": rendered_html,
            "sample_data": sample_context,
        }
    except HTTPException:
        raise
    except TemplateSyntaxError as e:
        raise HTTPException(status_code=400, detail=f"Template syntax error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to preview template: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to preview template")


@router.post("/customer-welcome/validate", response_model=dict)
@tenant_isolated
async def validate_customer_welcome_template(
    template_data: dict = Body(...),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Validate customer welcome email template syntax.
    """
    try:
        template_str = template_data.get("template", "").strip()
        if not template_str:
            raise HTTPException(status_code=400, detail="Template is required")
        
        is_valid, error_message = EmailTemplateService.validate_template(template_str)
        
        return {
            "valid": is_valid,
            "error": error_message if not is_valid else None,
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to validate template: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to validate template")
