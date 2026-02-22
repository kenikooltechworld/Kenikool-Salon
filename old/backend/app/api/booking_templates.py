"""
Booking Templates API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.api.dependencies import get_current_user, get_db
from app.services.booking_template_service import BookingTemplateService

router = APIRouter(prefix="/api/booking-templates", tags=["booking-templates"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_template(
    name: str = Query(...),
    client_id: str = Query(...),
    service_id: str = Query(...),
    stylist_id: str = Query(...),
    notes: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    duration: Optional[int] = Query(None),
    pricing: Optional[float] = Query(None),
    category: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a new booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = await BookingTemplateService.create_template(
            tenant_id=tenant_id,
            name=name,
            client_id=client_id,
            service_id=service_id,
            stylist_id=stylist_id,
            notes=notes,
            description=description,
            duration=duration,
            pricing=pricing,
            category=category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/from-booking/{booking_id}")
async def create_template_from_booking(
    booking_id: str,
    template_name: str = Query(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a template from an existing booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = await BookingTemplateService.create_template_from_booking(
            booking_id=booking_id,
            tenant_id=tenant_id,
            template_name=template_name
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("")
async def list_templates(
    skip: int = Query(0),
    limit: int = Query(10),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """List all booking templates for the tenant"""
    try:
        tenant_id = current_user.get("tenant_id")
        templates = await BookingTemplateService.get_templates(
            tenant_id=tenant_id,
            offset=skip,
            limit=limit
        )
        return templates
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{template_id}")
async def get_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        template = await BookingTemplateService.get_template(
            template_id=template_id,
            tenant_id=tenant_id
        )
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        return template
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{template_id}")
async def update_template(
    template_id: str,
    name: Optional[str] = Query(None),
    notes: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update a booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = await BookingTemplateService.update_template(
            template_id=template_id,
            tenant_id=tenant_id,
            name=name,
            notes=notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{template_id}")
async def delete_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        await BookingTemplateService.delete_template(
            template_id=template_id,
            tenant_id=tenant_id
        )
        return {"message": "Template deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{template_id}/use")
async def use_template(
    template_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Mark template as used (increment usage count)"""
    try:
        tenant_id = current_user.get("tenant_id")
        # Get template and update usage
        template = await BookingTemplateService.get_template(template_id, tenant_id)
        if not template:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found")
        
        # Update usage count in database
        from bson import ObjectId
        db.booking_templates.update_one(
            {"_id": ObjectId(template_id), "tenant_id": ObjectId(tenant_id)},
            {
                "$inc": {"usage_count": 1},
                "$set": {"last_used_at": __import__("datetime").datetime.utcnow()}
            }
        )
        
        # Return updated template
        updated = await BookingTemplateService.get_template(template_id, tenant_id)
        return updated
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
