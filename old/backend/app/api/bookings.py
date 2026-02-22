"""
Booking API endpoints with location support
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Optional, List
from datetime import datetime

from app.api.dependencies import get_current_user
from app.services.booking_service import BookingService
from app.schemas.booking import (
    BookingCreate,
    BookingEdit,
    BookingResponse,
    BookingStatusUpdate,
)

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.get("", response_model=List[BookingResponse])
async def get_bookings(
    location_id: Optional[str] = Query(None, description="Filter by single location"),
    location_ids: Optional[List[str]] = Query(None, description="Filter by multiple locations"),
    status_filter: Optional[str] = Query(None, description="Filter by booking status"),
    stylist_id: Optional[str] = Query(None, description="Filter by stylist"),
    client_id: Optional[str] = Query(None, description="Filter by client"),
    date_from: Optional[str] = Query(None, description="Filter from date (YYYY-MM-DD)"),
    date_to: Optional[str] = Query(None, description="Filter to date (YYYY-MM-DD)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=1000),
    current_user: dict = Depends(get_current_user)
):
    """Get bookings with optional location filtering - Requirements: 6.3.1, 6.3.2, 6.3.3, 6.3.4"""
    try:
        tenant_id = current_user.get("tenant_id")
        bookings = BookingService.filter_bookings_by_location(
            tenant_id=tenant_id,
            location_id=location_id,
            location_ids=location_ids,
            status=status_filter,
            stylist_id=stylist_id,
            client_id=client_id,
            date_from=date_from,
            date_to=date_to,
            offset=skip,
            limit=limit
        )
        return bookings
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get single booking with location information - Requirements: 6.3.4"""
    try:
        tenant_id = current_user.get("tenant_id")
        booking = BookingService.get_booking(booking_id, tenant_id)
        return booking
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post("", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new booking with location validation - Requirements: 6.1, 6.2, 6.3.5"""
    try:
        tenant_id = current_user.get("tenant_id")
        if not booking.location_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="location_id is required for booking creation"
            )
        result = await BookingService.create_booking(
            tenant_id=tenant_id,
            location_id=booking.location_id,
            client_name=booking.client_name,
            client_phone=booking.client_phone,
            service_id=booking.service_id,
            stylist_id=booking.stylist_id,
            booking_date=booking.booking_date,
            client_email=booking.client_email,
            notes=booking.notes,
            variant_id=None
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking: BookingEdit,
    current_user: dict = Depends(get_current_user)
):
    """Update a booking (location_id cannot be changed after creation) - Requirements: 6.1.5"""
    try:
        tenant_id = current_user.get("tenant_id")
        user_id = current_user.get("user_id")
        user_name = current_user.get("name")
        if booking.location_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="location_id cannot be changed after booking creation"
            )
        updates = booking.dict(exclude_unset=True)
        result = BookingService.edit_booking(
            booking_id=booking_id,
            tenant_id=tenant_id,
            updates=updates,
            user_id=user_id,
            user_name=user_name
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{booking_id}/status", response_model=BookingResponse)
async def update_booking_status(
    booking_id: str,
    status_update: BookingStatusUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update booking status"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = BookingService.update_booking_status(
            booking_id=booking_id,
            tenant_id=tenant_id,
            status=status_update.status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{booking_id}/reschedule", response_model=BookingResponse)
async def reschedule_booking(
    booking_id: str,
    new_date: str = Query(..., description="New booking date (YYYY-MM-DD HH:MM)"),
    current_user: dict = Depends(get_current_user)
):
    """Reschedule a booking to a new date"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = BookingService.reschedule_booking(
            booking_id=booking_id,
            tenant_id=tenant_id,
            new_date=new_date
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bulk-actions", response_model=dict)
async def bulk_booking_actions(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Perform bulk actions on multiple bookings"""
    try:
        tenant_id = current_user.get("tenant_id")
        action = data.get("action")
        booking_ids = data.get("booking_ids", [])
        
        if not action or not booking_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="action and booking_ids are required"
            )
        
        result = BookingService.bulk_actions(
            tenant_id=tenant_id,
            action=action,
            booking_ids=booking_ids,
            data=data
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/recurring", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_recurring_booking(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a recurring booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = BookingService.create_recurring_booking(
            tenant_id=tenant_id,
            data=data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/recurring/{template_id}", response_model=dict)
async def update_recurring_booking(
    template_id: str,
    data: dict,
    update_type: str = Query("single", description="single|future|all"),
    booking_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Update a recurring booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = BookingService.update_recurring_booking(
            tenant_id=tenant_id,
            template_id=template_id,
            update_type=update_type,
            booking_id=booking_id,
            data=data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/recurring/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_recurring_booking(
    template_id: str,
    update_type: str = Query("single", description="single|future|all"),
    booking_id: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Delete a recurring booking template"""
    try:
        tenant_id = current_user.get("tenant_id")
        BookingService.delete_recurring_booking(
            tenant_id=tenant_id,
            template_id=template_id,
            update_type=update_type,
            booking_id=booking_id
        )
        return None
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/analytics", response_model=dict)
async def get_booking_analytics(
    date_from: str = Query(..., description="Start date (YYYY-MM-DD)"),
    date_to: str = Query(..., description="End date (YYYY-MM-DD)"),
    group_subtype: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user)
):
    """Get booking analytics for a date range"""
    try:
        tenant_id = current_user.get("tenant_id")
        analytics = BookingService.get_booking_analytics(
            tenant_id=tenant_id,
            date_from=date_from,
            date_to=date_to,
            group_subtype=group_subtype
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{booking_id}/audit-log", response_model=dict)
async def get_booking_audit_log(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get audit log for a booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        audit_log = BookingService.get_booking_audit_log(
            booking_id=booking_id,
            tenant_id=tenant_id
        )
        return audit_log
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.get("/{booking_id}/payment-methods")
async def get_payment_methods(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get available payment methods for a booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        methods = BookingService.get_payment_methods(
            booking_id=booking_id,
            tenant_id=tenant_id
        )
        return {
            "methods": methods.get("methods", []),
            "available_credits": methods.get("available_credits", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/calculate-cost")
async def calculate_booking_cost(
    booking_id: Optional[str] = Query(None),
    service_id: Optional[str] = Query(None),
    variant_ids: Optional[List[str]] = Query(None),
    add_on_ids: Optional[List[str]] = Query(None),
    credits_to_apply: float = Query(0),
    current_user: dict = Depends(get_current_user)
):
    """Calculate booking cost with variants, add-ons, and credits"""
    try:
        tenant_id = current_user.get("tenant_id")
        cost = BookingService.calculate_cost(
            tenant_id=tenant_id,
            booking_id=booking_id,
            service_id=service_id,
            variant_ids=variant_ids or [],
            add_on_ids=add_on_ids or [],
            credits_to_apply=credits_to_apply
        )
        return cost
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/bulk/status")
async def bulk_update_status(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Bulk update booking status"""
    try:
        tenant_id = current_user.get("tenant_id")
        booking_ids = data.get("booking_ids", [])
        new_status = data.get("status")
        
        if not booking_ids or not new_status:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_ids and status are required"
            )
        
        result = BookingService.bulk_update_status(
            tenant_id=tenant_id,
            booking_ids=booking_ids,
            status=new_status
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/bulk/cancel")
async def bulk_cancel_bookings(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Bulk cancel bookings"""
    try:
        tenant_id = current_user.get("tenant_id")
        booking_ids = data.get("booking_ids", [])
        reason = data.get("reason", "")
        
        if not booking_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_ids are required"
            )
        
        result = BookingService.bulk_cancel(
            tenant_id=tenant_id,
            booking_ids=booking_ids,
            reason=reason
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/bulk/reschedule")
async def bulk_reschedule_bookings(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Bulk reschedule bookings"""
    try:
        tenant_id = current_user.get("tenant_id")
        booking_ids = data.get("booking_ids", [])
        new_date = data.get("new_date")
        new_time = data.get("new_time")
        
        if not booking_ids or not new_date or not new_time:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="booking_ids, new_date, and new_time are required"
            )
        
        result = BookingService.bulk_reschedule(
            tenant_id=tenant_id,
            booking_ids=booking_ids,
            new_date=new_date,
            new_time=new_time
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/check-conflict", response_model=dict)
async def check_booking_conflict(
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Check for booking conflicts and suggest alternatives - Requirements: 2.1, 2.2, 2.3"""
    try:
        tenant_id = current_user.get("tenant_id")
        stylist_id = data.get("stylist_id")
        service_id = data.get("service_id")
        start_time = data.get("start_time")
        end_time = data.get("end_time")
        
        if not all([stylist_id, service_id, start_time, end_time]):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="stylist_id, service_id, start_time, and end_time are required"
            )
        
        result = BookingService.check_conflict(
            tenant_id=tenant_id,
            stylist_id=stylist_id,
            service_id=service_id,
            start_time=start_time,
            end_time=end_time
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{booking_id}/cancel", response_model=dict)
async def cancel_booking(
    booking_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Cancel a booking with reason and refund calculation - Requirements: 3.1, 3.2, 3.3"""
    try:
        tenant_id = current_user.get("tenant_id")
        reason = data.get("reason", "")
        
        result = BookingService.cancel_booking(
            booking_id=booking_id,
            tenant_id=tenant_id,
            reason=reason
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{booking_id}/payment-method", response_model=BookingResponse)
async def update_booking_payment_method(
    booking_id: str,
    data: dict,
    current_user: dict = Depends(get_current_user)
):
    """Update payment method for a booking"""
    try:
        tenant_id = current_user.get("tenant_id")
        payment_method = data.get("payment_method")
        
        if not payment_method:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="payment_method is required"
            )
        
        result = BookingService.update_payment_method(
            booking_id=booking_id,
            tenant_id=tenant_id,
            payment_method=payment_method
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
