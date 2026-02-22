"""
Communication Settings API endpoints - Email, SMS, and notification templates
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime
from bson import ObjectId
import logging

from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["communication"])


def get_db():
    """Get database instance"""
    return Database.get_db()


# ============================================================================
# EMAIL SETTINGS
# ============================================================================

@router.get("/email-settings", response_model=dict)
async def get_email_settings(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get email settings"""
    try:
        db = get_db()
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        email_settings = tenant.get("email_settings", {
            "smtpHost": "smtp.gmail.com",
            "smtpPort": 587,
            "smtpUsername": "",
            "smtpPassword": "",
            "fromEmail": "noreply@salon.com",
            "fromName": "Salon"
        })
        
        return email_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting email settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/email-settings", response_model=dict)
async def update_email_settings(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update email settings"""
    try:
        db = get_db()
        
        result = db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "email_settings": data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {
            "success": True,
            "message": "Email settings updated",
            "settings": data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# SMS SETTINGS
# ============================================================================

@router.get("/sms-settings", response_model=dict)
async def get_sms_settings(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get SMS settings"""
    try:
        db = get_db()
        tenant = db.tenants.find_one({"_id": ObjectId(tenant_id)})
        
        if not tenant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        sms_settings = tenant.get("sms_settings", {
            "provider": "twilio",
            "apiKey": "",
            "apiSecret": "",
            "fromNumber": ""
        })
        
        return sms_settings
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting SMS settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/sms-settings", response_model=dict)
async def update_sms_settings(
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update SMS settings"""
    try:
        db = get_db()
        
        result = db.tenants.update_one(
            {"_id": ObjectId(tenant_id)},
            {
                "$set": {
                    "sms_settings": data,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        
        return {
            "success": True,
            "message": "SMS settings updated",
            "settings": data
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating SMS settings: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# EMAIL TEMPLATES
# ============================================================================

@router.get("/email-templates", response_model=dict)
async def get_email_templates(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get email templates"""
    try:
        db = get_db()
        templates = list(
            db.email_templates.find({"tenant_id": tenant_id})
        )
        
        # Convert ObjectIds to strings
        for template in templates:
            if "_id" in template:
                template["_id"] = str(template["_id"])
        
        return {
            "templates": templates,
            "total": len(templates)
        }
    except Exception as e:
        logger.error(f"Error getting email templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/email-templates/{template_id}", response_model=dict)
async def update_email_template(
    template_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update email template"""
    try:
        db = get_db()
        
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        if "subject" in data:
            update_data["subject"] = data["subject"]
        if "body" in data:
            update_data["body"] = data["body"]
        if "isEnabled" in data:
            update_data["isEnabled"] = data["isEnabled"]
        
        result = db.email_templates.update_one(
            {
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            },
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        template = db.email_templates.find_one({
            "_id": ObjectId(template_id)
        })
        template["_id"] = str(template["_id"])
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating email template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


# ============================================================================
# SMS TEMPLATES
# ============================================================================

@router.get("/sms-templates", response_model=dict)
async def get_sms_templates(
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Get SMS templates"""
    try:
        db = get_db()
        templates = list(
            db.sms_templates.find({"tenant_id": tenant_id})
        )
        
        # Convert ObjectIds to strings
        for template in templates:
            if "_id" in template:
                template["_id"] = str(template["_id"])
        
        return {
            "templates": templates,
            "total": len(templates)
        }
    except Exception as e:
        logger.error(f"Error getting SMS templates: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.put("/sms-templates/{template_id}", response_model=dict)
async def update_sms_template(
    template_id: str,
    data: dict,
    tenant_id: str = Depends(get_tenant_id),
    current_user: dict = Depends(get_current_user),
):
    """Update SMS template"""
    try:
        db = get_db()
        
        update_data = {
            "updatedAt": datetime.utcnow()
        }
        
        if "message" in data:
            update_data["message"] = data["message"]
        if "isEnabled" in data:
            update_data["isEnabled"] = data["isEnabled"]
        
        result = db.sms_templates.update_one(
            {
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            },
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        template = db.sms_templates.find_one({
            "_id": ObjectId(template_id)
        })
        template["_id"] = str(template["_id"])
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating SMS template: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
