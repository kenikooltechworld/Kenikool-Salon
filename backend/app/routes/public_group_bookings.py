from fastapi import APIRouter, HTTPException, Request
from bson import ObjectId

from app.schemas.group_booking import PublicGroupBookingCreate, GroupBookingResponse
from app.services.group_booking_service import GroupBookingService
from app.middleware.tenant_context import get_tenant_id

router = APIRouter(prefix="/public/group-bookings", tags=["Public Group Bookings"])


@router.post("", response_model=GroupBookingResponse)
async def create_public_group_booking(
    request: Request,
    booking_data: PublicGroupBookingCreate
):
    """Create a new group booking from public booking page"""
    tenant_id = get_tenant_id(request)
    
    # Get client info
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")
    
    # Validate minimum participants
    if len(booking_data.participants) < 2:
        raise HTTPException(
            status_code=400,
            detail="Group bookings require at least 2 participants"
        )
    
    # Validate maximum participants
    if len(booking_data.participants) > 20:
        raise HTTPException(
            status_code=400,
            detail="Group bookings are limited to 20 participants. Please contact us for larger groups."
        )
    
    group_booking = GroupBookingService.create_group_booking(
        tenant_id=tenant_id,
        booking_data=booking_data,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    # TODO: Send confirmation email to organizer
    # TODO: Send notification to staff
    
    return GroupBookingResponse(
        id=str(group_booking.id),
        tenant_id=str(group_booking.tenant_id),
        **group_booking.to_mongo().to_dict()
    )


@router.get("/{booking_id}", response_model=GroupBookingResponse)
async def get_public_group_booking(
    request: Request,
    booking_id: str,
    email: str = None
):
    """Get group booking details (email optional for confirmation page)"""
    tenant_id = get_tenant_id(request)
    
    booking = GroupBookingService.get_group_booking(ObjectId(booking_id))
    
    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    # Verify organizer email if provided (for security)
    if email and booking.organizer_email != email:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Verify tenant
    if booking.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    return GroupBookingResponse(
        id=str(booking.id),
        tenant_id=str(booking.tenant_id),
        **booking.to_mongo().to_dict()
    )


@router.post("/{booking_id}/cancel")
async def cancel_public_group_booking(
    request: Request,
    booking_id: str,
    email: str,
    cancellation_reason: str = None
):
    """Cancel a group booking (requires organizer email for verification)"""
    tenant_id = get_tenant_id(request)
    
    booking = GroupBookingService.get_group_booking(ObjectId(booking_id))
    
    if not booking:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    # Verify organizer email
    if booking.organizer_email != email:
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    # Verify tenant
    if booking.tenant_id != tenant_id:
        raise HTTPException(status_code=404, detail="Group booking not found")
    
    # Check if booking can be cancelled
    if booking.status in ["completed", "cancelled"]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel booking with status: {booking.status}"
        )
    
    booking = GroupBookingService.cancel_group_booking(
        ObjectId(booking_id),
        cancellation_reason
    )
    
    # TODO: Send cancellation confirmation email
    # TODO: Send notification to staff
    
    return {"message": "Group booking cancelled successfully"}
