"""
No-Show Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime

from app.api.dependencies import get_current_user, get_db
from app.services.no_show_service import NoShowService

router = APIRouter(prefix="/api/no-shows", tags=["no-shows"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def record_no_show(
    booking_id: str = Query(...),
    client_id: str = Query(...),
    fee_charged: Optional[float] = Query(None),
    notes: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Record a no-show for a booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("user_id")
        
        result = NoShowService.create_no_show(
            db=db,
            tenant_id=tenant_id,
            booking_id=booking_id,
            client_id=client_id,
            recorded_by=user_id,
            fee_charged=fee_charged,
            notes=notes
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/client/{client_id}")
async def get_client_no_shows(
    client_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all no-shows for a client"""
    try:
        tenant_id = current_user.get("tenant_id")
        no_shows = NoShowService.get_client_no_shows(db, tenant_id, client_id)
        return {"no_shows": no_shows, "count": len(no_shows)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/booking/{booking_id}")
async def get_booking_no_show(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get no-show record for a booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        no_show = NoShowService.get_booking_no_show(db, tenant_id, booking_id)
        if not no_show:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No-show not found")
        return no_show
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/fee/{client_id}")
async def calculate_no_show_fee(
    client_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Calculate no-show fee for a client"""
    try:
        tenant_id = current_user.get("tenant_id")
        fee = NoShowService.calculate_no_show_fee(db, tenant_id, client_id)
        return {"client_id": client_id, "no_show_fee": fee}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
