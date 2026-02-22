"""
Booking Cancellation API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional

from app.api.dependencies import get_current_user, get_db

router = APIRouter(prefix="/api/cancellations", tags=["cancellations"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def record_cancellation(
    booking_id: str = Query(...),
    reason: str = Query(...),
    category: str = Query(...),
    notes: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Record a booking cancellation"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        cancellation_data = {
            "tenant_id": tenant_id,
            "booking_id": booking_id,
            "reason": reason,
            "category": category,
            "notes": notes,
            "created_at": __import__("datetime").datetime.utcnow()
        }
        result = db["cancellations"].insert_one(cancellation_data)
        return {"id": str(result.inserted_id), **cancellation_data}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/booking/{booking_id}")
async def get_booking_cancellation(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get cancellation record for a booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        cancellation = db["cancellations"].find_one({
            "tenant_id": tenant_id,
            "booking_id": booking_id
        })
        if not cancellation:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cancellation not found")
        return cancellation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/client/{client_id}")
async def get_client_cancellations(
    client_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all cancellations for a client"""
    try:
        tenant_id = current_user.get("tenant_id")
        
        # Get all bookings for client
        bookings = db["bookings"].find({
            "tenant_id": tenant_id,
            "client_id": client_id
        })
        booking_ids = [b["_id"] for b in bookings]
        
        # Get cancellations for those bookings
        cancellations = list(db["cancellations"].find({
            "tenant_id": tenant_id,
            "booking_id": {"$in": booking_ids}
        }))
        
        return {"client_id": client_id, "cancellations": cancellations, "count": len(cancellations)}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
