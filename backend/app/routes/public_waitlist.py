"""Public waitlist routes for customer-facing waitlist features."""

from fastapi import APIRouter, HTTPException, Request, Query
from typing import Optional
from bson import ObjectId
from app.schemas.public_waitlist import (
    PublicWaitlistJoin,
    PublicWaitlistPosition,
    PublicWaitlistStatus,
)
from app.services.public_waitlist_service import PublicWaitlistService
from app.middleware.tenant_context import get_tenant_id

router = APIRouter(prefix="/public/waitlist", tags=["Public Waitlist"])


@router.get("/status", response_model=PublicWaitlistStatus)
async def get_waitlist_status(request: Request):
    """Get current waitlist status."""
    tenant_id = get_tenant_id(request)
    
    try:
        status = PublicWaitlistService.get_waitlist_status(tenant_id)
        return PublicWaitlistStatus(**status)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/join")
async def join_waitlist(request: Request, waitlist_data: PublicWaitlistJoin):
    """Join the public waitlist."""
    tenant_id = get_tenant_id(request)
    
    try:
        queue_entry = PublicWaitlistService.join_waitlist(
            tenant_id=tenant_id,
            service_id=waitlist_data.service_id,
            customer_name=waitlist_data.customer_name,
            customer_email=waitlist_data.customer_email,
            customer_phone=waitlist_data.customer_phone,
            staff_id=waitlist_data.staff_id,
            preferred_date=waitlist_data.preferred_date,
            notes=waitlist_data.notes,
        )
        
        return {
            "message": "Successfully joined waitlist",
            "position": queue_entry.position,
            "estimated_wait_time_minutes": queue_entry.estimated_wait_time_minutes,
            "queue_entry_id": str(queue_entry.id),
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/position", response_model=Optional[PublicWaitlistPosition])
async def get_position(
    request: Request,
    email: str = Query(..., description="Customer email"),
):
    """Get customer's position in waitlist."""
    tenant_id = get_tenant_id(request)
    
    try:
        position_data = PublicWaitlistService.get_customer_position(
            tenant_id=tenant_id, customer_email=email
        )
        
        if not position_data:
            return None
        
        return PublicWaitlistPosition(**position_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cancel")
async def cancel_waitlist(
    request: Request,
    email: str = Query(..., description="Customer email"),
):
    """Cancel waitlist entry."""
    tenant_id = get_tenant_id(request)
    
    try:
        success = PublicWaitlistService.cancel_waitlist_entry(
            tenant_id=tenant_id, customer_email=email
        )
        
        if not success:
            raise HTTPException(
                status_code=404, detail="Waitlist entry not found"
            )
        
        return {"message": "Waitlist entry cancelled successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
