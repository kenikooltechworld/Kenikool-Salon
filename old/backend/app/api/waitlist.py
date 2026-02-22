"""
Waitlist API endpoints
"""
from fastapi import APIRouter, HTTPException, Query, Depends, status
from typing import Optional, List
from datetime import datetime
from app.services.waitlist_service import WaitlistService
from app.services.notification_service import NotificationService
from app.services.waitlist_analytics_service import WaitlistAnalyticsService
from app.services.booking_integration_service import WaitlistBookingIntegration
from app.schemas.waitlist import WaitlistCreate, WaitlistUpdate, WaitlistResponse
from app.api.dependencies import get_current_user
from app.database import Database
from bson import ObjectId

router = APIRouter(prefix="/api/waitlist", tags=["waitlist"])

# Initialize services
waitlist_service = WaitlistService()
notification_service = NotificationService()
analytics_service = WaitlistAnalyticsService()
booking_integration = WaitlistBookingIntegration()


@router.post("/", response_model=dict)
async def create_waitlist_entry(
    request: WaitlistCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new waitlist entry"""
    try:
        entry = waitlist_service.add_to_waitlist(
            tenant_id=current_user.get("tenant_id"),
            client_name=request.client_name,
            client_email=request.client_email,
            client_phone=request.client_phone,
            service_id=request.service_id,
            preferred_date=request.preferred_date,
            location_id=request.location_id,
            notes=request.notes
        )
        return entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def get_waitlist_entries(
    current_user: dict = Depends(get_current_user),
    status: Optional[str] = Query(None, description="Filter by status"),
    service_id: Optional[str] = Query(None, description="Filter by service ID"),
    stylist_id: Optional[str] = Query(None, description="Filter by stylist ID"),
    location_id: Optional[str] = Query(None, description="Filter by location ID"),
    search_query: Optional[str] = Query(None, description="Search by client name or phone"),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)"),
    sort_by: str = Query("priority", description="Sort by: priority, created_at, updated_at"),
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """Get waitlist entries with advanced filtering"""
    try:
        # Parse dates if provided
        date_from_dt = None
        date_to_dt = None
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
        
        result = waitlist_service.get_waitlist_entries(
            tenant_id=current_user.get("tenant_id"),
            status=status,
            service_id=service_id,
            stylist_id=stylist_id,
            location_id=location_id,
            search_query=search_query,
            date_from=date_from_dt,
            date_to=date_to_dt,
            sort_by=sort_by,
            limit=limit,
            offset=offset
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-update")
async def bulk_update_status(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Bulk update status for multiple waitlist entries"""
    try:
        waitlist_ids = request.get("waitlist_ids", [])
        status = request.get("status")
        
        if not waitlist_ids:
            raise ValueError("waitlist_ids is required")
        if not status:
            raise ValueError("status is required")
        
        result = waitlist_service.bulk_update_status(
            waitlist_ids=waitlist_ids,
            tenant_id=current_user.get("tenant_id"),
            status=status
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-delete")
async def bulk_delete_entries(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Bulk delete multiple waitlist entries"""
    try:
        waitlist_ids = request.get("waitlist_ids", [])
        
        if not waitlist_ids:
            raise ValueError("waitlist_ids is required")
        
        result = waitlist_service.bulk_delete(
            waitlist_ids=waitlist_ids,
            tenant_id=current_user.get("tenant_id")
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bulk-notify")
async def bulk_notify_entries(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Bulk notify multiple waitlist entries"""
    try:
        waitlist_ids = request.get("waitlist_ids", [])
        template_id = request.get("template_id")
        
        if not waitlist_ids:
            raise ValueError("waitlist_ids is required")
        
        result = notification_service.bulk_notify(
            waitlist_ids=waitlist_ids,
            tenant_id=current_user.get("tenant_id"),
            template_id=template_id
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/analytics")
async def get_analytics(
    current_user: dict = Depends(get_current_user),
    date_from: Optional[str] = Query(None, description="Filter from date (ISO format)"),
    date_to: Optional[str] = Query(None, description="Filter to date (ISO format)")
):
    """Get waitlist analytics"""
    try:
        # Parse dates if provided
        date_from_dt = None
        date_to_dt = None
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
        
        stats = analytics_service.get_waitlist_stats(
            tenant_id=current_user.get("tenant_id"),
            date_from=date_from_dt,
            date_to=date_to_dt
        )
        
        service_demand = analytics_service.get_service_demand(
            tenant_id=current_user.get("tenant_id"),
            date_from=date_from_dt,
            date_to=date_to_dt
        )
        
        stylist_demand = analytics_service.get_stylist_demand(
            tenant_id=current_user.get("tenant_id"),
            date_from=date_from_dt,
            date_to=date_to_dt
        )
        
        conversion_metrics = analytics_service.get_conversion_metrics(
            tenant_id=current_user.get("tenant_id"),
            date_from=date_from_dt,
            date_to=date_to_dt
        )
        
        return {
            "stats": stats,
            "service_demand": service_demand,
            "stylist_demand": stylist_demand,
            "conversion_metrics": conversion_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{waitlist_id}/create-booking")
async def create_booking_from_waitlist(
    waitlist_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Create a booking from a waitlist entry"""
    try:
        booking_date = request.get("booking_date")
        booking_time = request.get("booking_time")
        
        if not booking_date or not booking_time:
            raise ValueError("booking_date and booking_time are required")
        
        # Get the waitlist entry
        db = Database.get_db()
        entry = db.waitlist.find_one({
            "_id": ObjectId(waitlist_id),
            "tenant_id": current_user.get("tenant_id")
        })
        
        if not entry:
            raise ValueError("Waitlist entry not found")
        
        # Create booking
        booking = booking_integration.create_booking_from_waitlist(
            waitlist_entry=entry,
            booking_date=booking_date,
            booking_time=booking_time
        )
        
        return booking
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
