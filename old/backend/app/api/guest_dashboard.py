"""
Guest Dashboard API endpoints
Provides comprehensive guest dashboard data including bookings, loyalty, and family account info
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import Optional, List
from datetime import datetime, timedelta
from bson import ObjectId

from app.api.dependencies import get_current_user, get_db
from app.services.booking_service import BookingService

router = APIRouter(prefix="/api/guest", tags=["guest-dashboard"])


@router.get("/dashboard")
async def get_guest_dashboard(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get comprehensive guest dashboard data
    Includes upcoming bookings, recent bookings, loyalty points, and family account info
    """
    try:
        guest_id = current_user.get("id") or current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        if not guest_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        # Get upcoming bookings (next 7 days)
        today = datetime.utcnow()
        next_week = today + timedelta(days=7)
        
        upcoming_bookings = list(db["bookings"].find({
            "client_id": guest_id,
            "booking_date": {
                "$gte": today.isoformat(),
                "$lte": next_week.isoformat()
            },
            "status": {"$in": ["confirmed", "pending"]}
        }).sort("booking_date", 1).limit(10))
        
        # Get recent bookings (last 30 days)
        thirty_days_ago = today - timedelta(days=30)
        
        recent_bookings = list(db["bookings"].find({
            "client_id": guest_id,
            "booking_date": {
                "$gte": thirty_days_ago.isoformat(),
                "$lte": today.isoformat()
            }
        }).sort("booking_date", -1).limit(10))
        
        # Get loyalty points
        loyalty_data = db["loyalty_accounts"].find_one({
            "client_id": guest_id
        }) or {
            "current_points": 0,
            "tier": "bronze",
            "total_points_earned": 0
        }
        
        # Get family account info
        family_data = db["family_accounts"].find_one({
            "primary_member_id": guest_id
        }) or {
            "total_members": [],
            "primary_member_id": guest_id
        }
        
        # Get booking templates
        templates = list(db["booking_templates"].find({
            "client_id": guest_id
        }).limit(5))
        
        # Get waitlist entries
        waitlist = list(db["waitlist"].find({
            "client_id": guest_id,
            "status": "active"
        }).limit(5))
        
        # Format response
        return {
            "upcomingBookingsCount": len(upcoming_bookings),
            "upcomingBookings": [
                {
                    "id": str(booking.get("_id", "")),
                    "serviceName": booking.get("service_name", ""),
                    "salonName": booking.get("salon_name", ""),
                    "dateTime": booking.get("booking_date", ""),
                    "status": booking.get("status", ""),
                    "duration": booking.get("duration", 0),
                    "price": booking.get("price", 0),
                    "staffName": booking.get("stylist_name", ""),
                    "type": booking.get("booking_type", "regular")
                }
                for booking in upcoming_bookings
            ],
            "recentBookings": [
                {
                    "id": str(booking.get("_id", "")),
                    "serviceName": booking.get("service_name", ""),
                    "salonName": booking.get("salon_name", ""),
                    "dateTime": booking.get("booking_date", ""),
                    "status": booking.get("status", ""),
                    "duration": booking.get("duration", 0),
                    "price": booking.get("price", 0),
                    "staffName": booking.get("stylist_name", ""),
                    "type": booking.get("booking_type", "regular")
                }
                for booking in recent_bookings
            ],
            "loyaltyPoints": loyalty_data.get("current_points", 0),
            "loyaltyTier": loyalty_data.get("tier", "bronze"),
            "familyMembers": len(family_data.get("total_members", [])),
            "savedTemplates": len(templates),
            "activeWaitlist": len(waitlist)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load dashboard: {str(e)}"
        )


@router.get("/bookings")
async def get_guest_bookings(
    booking_type: Optional[str] = Query(None, description="Filter by booking type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search: Optional[str] = Query(None, description="Search by service name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get guest bookings with optional filtering
    """
    try:
        guest_id = current_user.get("id") or current_user.get("user_id")
        
        if not guest_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        # Build query
        query = {"client_id": guest_id}
        
        if booking_type and booking_type != "all":
            query["booking_type"] = booking_type
        
        if status and status != "all":
            query["status"] = status
        
        if search:
            query["service_name"] = {"$regex": search, "$options": "i"}
        
        # Get bookings
        bookings = list(db["bookings"].find(query)
            .sort("booking_date", -1)
            .skip(skip)
            .limit(limit))
        
        return [
            {
                "id": str(booking.get("_id", "")),
                "serviceName": booking.get("service_name", ""),
                "salonName": booking.get("salon_name", ""),
                "dateTime": booking.get("booking_date", ""),
                "status": booking.get("status", ""),
                "duration": booking.get("duration", 0),
                "price": booking.get("price", 0),
                "staffName": booking.get("stylist_name", ""),
                "type": booking.get("booking_type", "regular"),
                "notes": booking.get("notes", ""),
                "recurringPattern": booking.get("recurring_pattern", ""),
                "occurrencesRemaining": booking.get("occurrences_remaining", 0),
                "groupSize": booking.get("group_size", 1),
                "sessionsUsed": booking.get("sessions_used", 0),
                "totalSessions": booking.get("total_sessions", 0)
            }
            for booking in bookings
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load bookings: {str(e)}"
        )


@router.get("/bookings/{booking_id}")
async def get_guest_booking_details(
    booking_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get detailed information about a specific guest booking
    """
    try:
        guest_id = current_user.get("id") or current_user.get("user_id")
        
        if not guest_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        # Get booking
        booking = db["bookings"].find_one({
            "_id": ObjectId(booking_id),
            "client_id": guest_id
        })
        
        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Booking not found"
            )
        
        return {
            "id": str(booking.get("_id", "")),
            "serviceName": booking.get("service_name", ""),
            "salonName": booking.get("salon_name", ""),
            "dateTime": booking.get("booking_date", ""),
            "status": booking.get("status", ""),
            "duration": booking.get("duration", 0),
            "price": booking.get("price", 0),
            "staffName": booking.get("stylist_name", ""),
            "type": booking.get("booking_type", "regular"),
            "notes": booking.get("notes", ""),
            "location": booking.get("location", ""),
            "phone": booking.get("phone", ""),
            "email": booking.get("email", "")
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load booking details: {str(e)}"
        )


@router.get("/booking-templates")
async def get_guest_booking_templates(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get guest's saved booking templates
    """
    try:
        guest_id = current_user.get("id") or current_user.get("user_id")
        
        if not guest_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        templates = list(db["booking_templates"].find({
            "client_id": guest_id
        }).sort("created_at", -1))
        
        return [
            {
                "id": str(template.get("_id", "")),
                "name": template.get("name", ""),
                "serviceName": template.get("service_name", ""),
                "salonName": template.get("salon_name", ""),
                "duration": template.get("duration", 0),
                "price": template.get("price", 0),
                "staffName": template.get("stylist_name", ""),
                "createdAt": template.get("created_at", "")
            }
            for template in templates
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load templates: {str(e)}"
        )


@router.get("/waitlist")
async def get_guest_waitlist(
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """
    Get guest's waitlist entries
    """
    try:
        guest_id = current_user.get("id") or current_user.get("user_id")
        
        if not guest_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User ID not found in token"
            )
        
        waitlist_entries = list(db["waitlist"].find({
            "client_id": guest_id,
            "status": "active"
        }).sort("created_at", -1))
        
        return [
            {
                "id": str(entry.get("_id", "")),
                "serviceName": entry.get("service_name", ""),
                "salonName": entry.get("salon_name", ""),
                "preferredDate": entry.get("preferred_date", ""),
                "preferredTime": entry.get("preferred_time", ""),
                "status": entry.get("status", "active"),
                "createdAt": entry.get("created_at", ""),
                "position": entry.get("position", 0)
            }
            for entry in waitlist_entries
        ]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load waitlist: {str(e)}"
        )
