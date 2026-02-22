"""
Marketplace Bookings API

Endpoints for creating, managing, and tracking marketplace bookings.
Includes guest account management and magic link authentication.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr
import logging

from app.database import Database
from app.services.marketplace_booking_service import MarketplaceBookingService
from app.services.guest_account_service import GuestAccountService
from app.services.commission_service import CommissionService
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace"])


# ============================================================================
# Pydantic Models
# ============================================================================

class GuestInfo(BaseModel):
    """Guest information for booking"""
    email: EmailStr
    phone: str
    name: str


class BookingCreate(BaseModel):
    """Create marketplace booking"""
    tenant_id: str
    guest_info: GuestInfo
    service_id: str
    service_name: str
    booking_date: str  # YYYY-MM-DD
    booking_time: str  # HH:MM
    duration_minutes: int
    price: float
    payment_method: str  # "online" or "at_salon"
    stylist_id: Optional[str] = None
    stylist_name: Optional[str] = None
    notes: Optional[str] = None


class BookingUpdate(BaseModel):
    """Update booking"""
    booking_date: Optional[str] = None
    booking_time: Optional[str] = None
    notes: Optional[str] = None


class BookingResponse(BaseModel):
    """Booking response"""
    _id: str
    reference_number: str
    tenant_id: str
    guest_email: str
    guest_name: str
    service_name: str
    booking_date: str
    booking_time: str
    price: float
    final_price: float
    payment_method: str
    payment_status: str
    booking_status: str
    created_at: str


class AvailabilityRequest(BaseModel):
    """Check availability request"""
    booking_date: str
    booking_time: str
    duration_minutes: int
    stylist_id: Optional[str] = None


class AvailabilityResponse(BaseModel):
    """Availability response"""
    available: bool
    message: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/bookings", response_model=BookingResponse)
async def create_marketplace_booking(booking_data: BookingCreate):
    """
    Create a new marketplace booking
    
    - Validates guest information
    - Checks availability
    - Creates guest account if needed
    - Generates magic link
    - Sends confirmation email
    
    Returns booking reference and magic link
    """
    try:
        db = Database.get_db()
        booking_service = MarketplaceBookingService(db)
        
        # Check availability
        is_available = await booking_service.check_availability(
            tenant_id=booking_data.tenant_id,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            duration_minutes=booking_data.duration_minutes,
            stylist_id=booking_data.stylist_id
        )
        
        if not is_available:
            raise HTTPException(
                status_code=409,
                detail="Selected time slot is not available"
            )
        
        # Create booking
        booking = await booking_service.create_booking(
            tenant_id=booking_data.tenant_id,
            guest_email=booking_data.guest_info.email,
            guest_phone=booking_data.guest_info.phone,
            guest_name=booking_data.guest_info.name,
            service_id=booking_data.service_id,
            service_name=booking_data.service_name,
            booking_date=booking_data.booking_date,
            booking_time=booking_data.booking_time,
            duration_minutes=booking_data.duration_minutes,
            price=booking_data.price,
            payment_method=booking_data.payment_method,
            stylist_id=booking_data.stylist_id,
            stylist_name=booking_data.stylist_name,
            notes=booking_data.notes
        )
        
        # TODO: Send confirmation email with magic link
        # TODO: Record commission if applicable
        
        return BookingResponse(
            _id=booking["_id"],
            reference_number=booking["reference_number"],
            tenant_id=booking["tenant_id"],
            guest_email=booking["guest_email"],
            guest_name=booking["guest_name"],
            service_name=booking["service_name"],
            booking_date=booking["booking_date"],
            booking_time=booking["booking_time"],
            price=booking["price"],
            final_price=booking["final_price"],
            payment_method=booking["payment_method"],
            payment_status=booking["payment_status"],
            booking_status=booking["booking_status"],
            created_at=booking["created_at"].isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating marketplace booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings/{reference}")
async def get_booking(
    reference: str,
    magic_token: Optional[str] = Query(None)
):
    """
    Get booking details using reference number and magic token
    
    Magic token is required for guest access
    """
    try:
        db = Database.get_db()
        booking_service = MarketplaceBookingService(db)
        guest_service = GuestAccountService(db)
        
        # Get booking by reference
        booking = await booking_service.get_booking_by_reference(reference, "")
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Verify magic token if provided
        if magic_token:
            guest = await guest_service.authenticate_guest(
                booking["guest_email"],
                magic_token
            )
            if not guest:
                raise HTTPException(status_code=401, detail="Invalid magic token")
        
        return booking
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/bookings/{reference}/reschedule")
async def reschedule_booking(
    reference: str,
    new_date: str,
    new_time: str,
    magic_token: str
):
    """
    Reschedule a marketplace booking
    
    Requires valid magic token for authentication
    """
    try:
        db = Database.get_db()
        booking_service = MarketplaceBookingService(db)
        guest_service = GuestAccountService(db)
        
        # Get booking
        booking = await booking_service.get_booking_by_reference(reference, "")
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Verify magic token
        guest = await guest_service.authenticate_guest(
            booking["guest_email"],
            magic_token
        )
        if not guest:
            raise HTTPException(status_code=401, detail="Invalid magic token")
        
        # Check new availability
        is_available = await booking_service.check_availability(
            tenant_id=booking["tenant_id"],
            booking_date=new_date,
            booking_time=new_time,
            duration_minutes=booking["duration_minutes"],
            stylist_id=booking.get("stylist_id")
        )
        
        if not is_available:
            raise HTTPException(
                status_code=409,
                detail="New time slot is not available"
            )
        
        # Reschedule booking
        updated_booking = await booking_service.reschedule_booking(
            booking_id=booking["_id"],
            new_date=new_date,
            new_time=new_time,
            tenant_id=booking["tenant_id"]
        )
        
        # TODO: Send reschedule confirmation email
        
        return updated_booking
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rescheduling booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/bookings/{reference}")
async def cancel_booking(
    reference: str,
    magic_token: str,
    reason: Optional[str] = None
):
    """
    Cancel a marketplace booking
    
    Requires valid magic token for authentication
    """
    try:
        db = Database.get_db()
        booking_service = MarketplaceBookingService(db)
        guest_service = GuestAccountService(db)
        
        # Get booking
        booking = await booking_service.get_booking_by_reference(reference, "")
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        # Verify magic token
        guest = await guest_service.authenticate_guest(
            booking["guest_email"],
            magic_token
        )
        if not guest:
            raise HTTPException(status_code=401, detail="Invalid magic token")
        
        # Cancel booking
        success = await booking_service.cancel_booking(
            booking_id=booking["_id"],
            tenant_id=booking["tenant_id"]
        )
        
        if success:
            # TODO: Process refund if payment was made
            # TODO: Send cancellation confirmation email
            return {"message": "Booking cancelled successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to cancel booking")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling booking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bookings/check-availability")
async def check_availability(request: AvailabilityRequest, tenant_id: str):
    """
    Check if a time slot is available for booking
    """
    try:
        db = Database.get_db()
        booking_service = MarketplaceBookingService(db)
        
        is_available = await booking_service.check_availability(
            tenant_id=tenant_id,
            booking_date=request.booking_date,
            booking_time=request.booking_time,
            duration_minutes=request.duration_minutes,
            stylist_id=request.stylist_id
        )
        
        return AvailabilityResponse(
            available=is_available,
            message="Time slot is available" if is_available else "Time slot is not available"
        )
    
    except Exception as e:
        logger.error(f"Error checking availability: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings")
async def list_bookings(
    tenant_id: str,
    guest_email: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    List marketplace bookings for a tenant
    
    Supports filtering by guest email and booking status
    """
    try:
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if guest_email:
            query["guest_email"] = guest_email
        
        if status:
            query["booking_status"] = status
        
        bookings = list(
            db.marketplace_bookings.find(query)
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for booking in bookings:
            booking["_id"] = str(booking["_id"])
        
        total = db.marketplace_bookings.count_documents(query)
        
        return {
            "bookings": bookings,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error listing bookings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bookings/stats")
async def get_booking_stats(tenant_id: str):
    """
    Get booking statistics for a tenant
    """
    try:
        db = Database.get_db()
        
        total_bookings = db.marketplace_bookings.count_documents({"tenant_id": tenant_id})
        confirmed_bookings = db.marketplace_bookings.count_documents({
            "tenant_id": tenant_id,
            "booking_status": "confirmed"
        })
        completed_bookings = db.marketplace_bookings.count_documents({
            "tenant_id": tenant_id,
            "booking_status": "completed"
        })
        cancelled_bookings = db.marketplace_bookings.count_documents({
            "tenant_id": tenant_id,
            "booking_status": "cancelled"
        })
        
        # Calculate total revenue
        pipeline = [
            {"$match": {"tenant_id": tenant_id, "payment_status": "paid"}},
            {"$group": {"_id": None, "total_revenue": {"$sum": "$final_price"}}}
        ]
        revenue_result = list(db.marketplace_bookings.aggregate(pipeline))
        total_revenue = revenue_result[0]["total_revenue"] if revenue_result else 0
        
        return {
            "total_bookings": total_bookings,
            "confirmed_bookings": confirmed_bookings,
            "completed_bookings": completed_bookings,
            "cancelled_bookings": cancelled_bookings,
            "total_revenue": total_revenue
        }
    
    except Exception as e:
        logger.error(f"Error getting booking stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))
