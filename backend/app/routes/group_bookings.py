from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime

from app.schemas.group_booking import (
    GroupBookingCreate,
    GroupBookingUpdate,
    GroupBookingResponse
)
from app.services.group_booking_service import GroupBookingService
from app.middleware.tenant_context import get_tenant_id
from app.routes.auth import get_current_user_dependency as get_current_user

router = APIRouter(prefix="/group-bookings", tags=["Group Bookings"])


@router.post("", response_model=GroupBookingResponse)
async def create_group_booking(
    request: Request,
    booking_data: GroupBookingCreate,
    current_user = Depends(get_current_user)
):
    """Create a new group booking (staff/owner only)"""
    tenant_id = get_tenant_id(request)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    group_booking = GroupBookingService.create_group_booking(
        tenant_id=tenant_id,
        booking_data=booking_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    return GroupBookingResponse(
        id=str(group_booking.id),
        tenant_id=str(group_booking.tenant_id),
        **group_booking.to_mongo().to_dict()
    )


@router.get("", response_model=List[GroupBookingResponse])
async def get_group_bookings(
    request: Request,
    status: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user = Depends(get_current_user)
):
    """Get all group bookings with filters"""
    tenant_id = get_tenant_id(request)
    
    bookings = GroupBookingService.get_group_bookings(
        tenant_id=tenant_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return [
        GroupBookingResponse(
            id=str(booking.id),
            tenant_id=str(booking.tenant_id),
            **booking.to_mongo().to_dict()
        )
        for booking in bookings
    ]


@router.get("/{booking_id}", response_model=GroupBookingResponse)
async def get_group_booking(
    booking_id: str,
    current_user = Depends(get_current_user)
):
    """Get a specific group booking"""
    booking = GroupBookingService.get_group_booking(ObjectId(booking_id))
    
    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    return GroupBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        **booking.to_mongo().to_dict()
    )


@router.put("/{booking_id}", response_model=GroupBookingResponse)
async def update_group_booking(
    booking_id: str,
    update_data: GroupBookingUpdate,
    current_user = Depends(get_current_user)
):
    """Update a group booking"""
    booking = GroupBookingService.update_group_booking(
        ObjectId(booking_id),
        update_data
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    return GroupBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        **booking.to_mongo().to_dict()
    )


@router.post("/{booking_id}/confirm", response_model=GroupBookingResponse)
async def confirm_group_booking(
    booking_id: str,
    current_user = Depends(get_current_user)
):
    """Confirm a group booking and create individual appointments"""
    booking = GroupBookingService.confirm_group_booking(ObjectId(booking_id))
    
    if not booking:
        raise HTTPException(
            status_code=400,
            detail="Cannot confirm booking. Booking not found or already confirmed."
        )
    
    return GroupBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        **booking.to_mongo().to_dict()
    )


@router.post("/{booking_id}/cancel", response_model=GroupBookingResponse)
async def cancel_group_booking(
    booking_id: str,
    cancellation_reason: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Cancel a group booking and all associated appointments"""
    booking = GroupBookingService.cancel_group_booking(
        ObjectId(booking_id),
        cancellation_reason
    )
    
    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    return GroupBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        **booking.to_mongo().to_dict()
    )
