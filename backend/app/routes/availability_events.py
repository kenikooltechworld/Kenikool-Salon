"""Routes for real-time availability events."""

from fastapi import APIRouter, Request, HTTPException
from typing import List
from datetime import datetime
from bson import ObjectId
from app.schemas.availability_event import (
    AvailabilityEventResponse,
    SlotViewerUpdate,
    SlotViewerResponse,
)
from app.services.availability_event_service import AvailabilityEventService
from app.middleware.tenant_context import get_tenant_id

router = APIRouter(prefix="/public/availability-events", tags=["Availability Events"])


@router.get("/recent", response_model=List[AvailabilityEventResponse])
def get_recent_events(
    request: Request,
    service_id: str,
    date: str,  # ISO format: YYYY-MM-DD
    minutes: int = 30,
):
    """Get recent availability events for a service on a specific date."""
    tenant_id = get_tenant_id(request)
    
    try:
        date_obj = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    events = AvailabilityEventService.get_recent_events(
        tenant_id=tenant_id,
        service_id=ObjectId(service_id),
        date=date_obj,
        minutes=minutes,
    )
    
    return [
        AvailabilityEventResponse(
            id=str(event.id),
            tenant_id=str(event.tenant_id),
            service_id=str(event.service_id),
            staff_id=str(event.staff_id) if event.staff_id else None,
            date=event.date,
            time_slot=event.time_slot,
            event_type=event.event_type,
            viewer_count=event.viewer_count,
            created_at=event.created_at,
        )
        for event in events
    ]


@router.post("/viewer-update", response_model=SlotViewerResponse)
def update_slot_viewers(
    request: Request,
    update: SlotViewerUpdate,
):
    """Update viewer count for a specific time slot."""
    tenant_id = get_tenant_id(request)
    
    staff_id = ObjectId(update.staff_id) if update.staff_id else None
    
    if update.action == "join":
        viewer_count = AvailabilityEventService.increment_viewer_count(
            tenant_id=tenant_id,
            service_id=ObjectId(update.service_id),
            date=update.date,
            time_slot=update.time_slot,
            staff_id=staff_id,
        )
    elif update.action == "leave":
        viewer_count = AvailabilityEventService.decrement_viewer_count(
            tenant_id=tenant_id,
            service_id=ObjectId(update.service_id),
            date=update.date,
            time_slot=update.time_slot,
            staff_id=staff_id,
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid action. Use 'join' or 'leave'")
    
    return SlotViewerResponse(
        service_id=update.service_id,
        staff_id=update.staff_id,
        date=update.date,
        time_slot=update.time_slot,
        viewer_count=viewer_count,
    )


@router.get("/viewer-count", response_model=SlotViewerResponse)
def get_slot_viewer_count(
    request: Request,
    service_id: str,
    date: str,
    time_slot: str,
    staff_id: str = None,
):
    """Get current viewer count for a specific time slot."""
    tenant_id = get_tenant_id(request)
    
    try:
        date_obj = datetime.fromisoformat(date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    
    staff_obj_id = ObjectId(staff_id) if staff_id else None
    
    viewer_count = AvailabilityEventService.get_viewer_count(
        tenant_id=tenant_id,
        service_id=ObjectId(service_id),
        date=date_obj,
        time_slot=time_slot,
        staff_id=staff_obj_id,
    )
    
    return SlotViewerResponse(
        service_id=service_id,
        staff_id=staff_id,
        date=date_obj,
        time_slot=time_slot,
        viewer_count=viewer_count,
    )
