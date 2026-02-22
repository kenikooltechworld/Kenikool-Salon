"""
Waitlist notification templates API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional
from app.services.notification_template_service import NotificationTemplateService
from app.api.dependencies import get_current_user
from app.database import Database
from bson import ObjectId

router = APIRouter(prefix="/api/waitlist/templates", tags=["waitlist-templates"])

template_service = NotificationTemplateService()


@router.get("/")
async def get_templates(
    current_user: dict = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000)
):
    """Get all notification templates for tenant"""
    try:
        templates = template_service.get_notification_templates(
            tenant_id=current_user.get("tenant_id"),
            skip=skip,
            limit=limit
        )
        return templates
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/")
async def create_template(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a new notification template"""
    try:
        name = request.get("name")
        message = request.get("message")
        variables = request.get("variables", [])
        is_default = request.get("is_default", False)
        
        if not name or not message:
            raise ValueError("name and message are required")
        
        template = template_service.create_notification_template(
            tenant_id=current_user.get("tenant_id"),
            name=name,
            message=message,
            variables=variables,
            is_default=is_default
        )
        return template
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{template_id}")
async def update_template(
    template_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update a notification template"""
    try:
        name = request.get("name")
        message = request.get("message")
        variables = request.get("variables")
        is_default = request.get("is_default")
        
        db = Database.get_db()
        
        # Verify template belongs to tenant
        template = db.notification_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": current_user.get("tenant_id")
        })
        
        if not template:
            raise ValueError("Template not found")
        
        # Build update dict
        update_dict = {}
        if name:
            update_dict["name"] = name
        if message:
            update_dict["message"] = message
        if variables is not None:
            update_dict["variables"] = variables
        if is_default is not None:
            update_dict["is_default"] = is_default
        
        if not update_dict:
            raise ValueError("No fields to update")
        
        updated = template_service.update_notification_template(
            template_id=template_id,
            tenant_id=current_user.get("tenant_id"),
            **update_dict
        )
        return updated
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Delete a notification template"""
    try:
        db = Database.get_db()
        
        # Verify template belongs to tenant
        template = db.notification_templates.find_one({
            "_id": ObjectId(template_id),
            "tenant_id": current_user.get("tenant_id")
        })
        
        if not template:
            raise ValueError("Template not found")
        
        result = template_service.delete_notification_template(
            template_id=template_id,
            tenant_id=current_user.get("tenant_id")
        )
        return {"success": result}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
