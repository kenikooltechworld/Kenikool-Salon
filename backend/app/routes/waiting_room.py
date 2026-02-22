"""Waiting room routes."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from app.schemas.waiting_room import (
    QueueEntryCheckIn,
    QueueEntryResponse,
    WaitingRoomResponse,
    QueueHistoryResponse,
    QueueStatsResponse,
)
from app.services.waiting_room_service import WaitingRoomService
from app.decorators.tenant_isolated import tenant_isolated

router = APIRouter(prefix="/waiting-room", tags=["waiting-room"])


# Queue Management
@router.post("/check-in", response_model=QueueEntryResponse)
@tenant_isolated
async def check_in_customer(check_in: QueueEntryCheckIn):
    """Check in a customer to the waiting room."""
    try:
        entry = WaitingRoomService.check_in_customer(
            appointment_id=check_in.appointment_id,
            customer_id=check_in.customer_id,
            customer_name=check_in.customer_name,
            customer_phone=check_in.customer_phone,
            service_id=check_in.service_id,
            service_name=check_in.service_name,
            staff_id=check_in.staff_id,
            staff_name=check_in.staff_name,
            estimated_wait_time=check_in.estimated_wait_time,
        )
        if not entry:
            raise HTTPException(status_code=400, detail="Failed to check in customer")
        return QueueEntryResponse.from_orm(entry)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/queue", response_model=dict)
@tenant_isolated
async def get_current_queue(
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """Get current queue."""
    entries = WaitingRoomService.get_current_queue(
        status=status, limit=limit, skip=skip
    )
    return {"data": [QueueEntryResponse.from_orm(e) for e in entries]}


@router.get("/queue/next", response_model=Optional[QueueEntryResponse])
@tenant_isolated
async def get_next_customer():
    """Get next customer in queue."""
    entry = WaitingRoomService.get_next_customer()
    if not entry:
        return None
    return QueueEntryResponse.from_orm(entry)


@router.get("/queue/{entry_id}", response_model=QueueEntryResponse)
@tenant_isolated
async def get_queue_entry(entry_id: str):
    """Get queue entry by ID."""
    entry = WaitingRoomService.get_queue_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.patch("/queue/{entry_id}/call", response_model=QueueEntryResponse)
@tenant_isolated
async def call_customer(entry_id: str):
    """Call next customer in queue."""
    entry = WaitingRoomService.call_customer(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.post("/call-next", response_model=QueueEntryResponse)
@tenant_isolated
async def call_next_customer():
    """Call next customer in queue."""
    entry = WaitingRoomService.get_next_customer()
    if not entry:
        raise HTTPException(status_code=400, detail="No customers in queue")
    entry = WaitingRoomService.call_customer(entry.id)
    return QueueEntryResponse.from_orm(entry)


@router.patch("/queue/{entry_id}/start-service", response_model=QueueEntryResponse)
@tenant_isolated
async def start_service(entry_id: str):
    """Mark customer as in service."""
    entry = WaitingRoomService.start_service(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.patch("/{entry_id}/in-service", response_model=QueueEntryResponse)
@tenant_isolated
async def mark_in_service(entry_id: str):
    """Mark customer as in service (alternative endpoint)."""
    entry = WaitingRoomService.start_service(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.patch("/queue/{entry_id}/complete", response_model=QueueEntryResponse)
@tenant_isolated
async def complete_service(entry_id: str):
    """Mark service as completed."""
    entry = WaitingRoomService.complete_service(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.patch("/{entry_id}/completed", response_model=QueueEntryResponse)
@tenant_isolated
async def mark_completed(entry_id: str):
    """Mark service as completed (alternative endpoint)."""
    entry = WaitingRoomService.complete_service(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.patch("/queue/{entry_id}/no-show", response_model=QueueEntryResponse)
@tenant_isolated
async def mark_no_show(entry_id: str, reason: Optional[str] = Query(None)):
    """Mark customer as no-show."""
    entry = WaitingRoomService.mark_no_show(entry_id, reason)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.patch("/{entry_id}/no-show", response_model=QueueEntryResponse)
@tenant_isolated
async def mark_no_show_alt(entry_id: str, reason: Optional[str] = Query(None)):
    """Mark customer as no-show (alternative endpoint)."""
    entry = WaitingRoomService.mark_no_show(entry_id, reason)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return QueueEntryResponse.from_orm(entry)


@router.delete("/queue/{entry_id}")
@tenant_isolated
async def cancel_queue_entry(entry_id: str):
    """Cancel queue entry."""
    entry = WaitingRoomService.cancel_queue_entry(entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    return {"message": "Queue entry cancelled"}


# Customer Information
@router.get("/position/{customer_id}", response_model=dict)
@tenant_isolated
async def get_customer_position(customer_id: str):
    """Get customer's position in queue."""
    position = WaitingRoomService.get_customer_position(customer_id)
    if position is None:
        raise HTTPException(status_code=404, detail="Customer not in queue")
    return {"position": position, "estimated_wait_time_minutes": 0}


@router.get("/customer/{customer_id}/position", response_model=Optional[int])
@tenant_isolated
async def get_customer_position_alt(customer_id: str):
    """Get customer's position in queue (alternative endpoint)."""
    position = WaitingRoomService.get_customer_position(customer_id)
    return position


@router.get("/customer/{customer_id}/wait-time", response_model=Optional[int])
@tenant_isolated
async def get_estimated_wait_time(customer_id: str):
    """Get estimated wait time for customer."""
    wait_time = WaitingRoomService.get_estimated_wait_time(customer_id)
    return wait_time


# Queue Statistics
@router.get("/stats", response_model=dict)
@tenant_isolated
async def get_queue_stats():
    """Get queue statistics."""
    stats = WaitingRoomService.get_queue_stats()
    return {"data": stats}


# Queue History
@router.get("/history", response_model=dict)
@tenant_isolated
async def get_queue_history(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    skip: int = Query(0, ge=0),
):
    """Get queue history."""
    history = WaitingRoomService.get_queue_history(
        start_date=start_date,
        end_date=end_date,
        status=status,
        limit=limit,
        skip=skip,
    )
    return {"data": [QueueHistoryResponse.from_orm(h) for h in history]}


# Waiting Room Management
@router.get("/rooms", response_model=Optional[WaitingRoomResponse])
@tenant_isolated
async def get_waiting_room(location_id: Optional[str] = Query(None)):
    """Get waiting room."""
    room = WaitingRoomService.get_waiting_room(location_id)
    if not room:
        raise HTTPException(status_code=404, detail="Waiting room not found")
    return WaitingRoomResponse.from_orm(room)


@router.post("/rooms", response_model=WaitingRoomResponse)
@tenant_isolated
async def create_waiting_room(
    name: str,
    location_id: Optional[str] = Query(None),
    max_queue_length: Optional[int] = Query(None),
):
    """Create a waiting room."""
    try:
        room = WaitingRoomService.create_waiting_room(
            name=name,
            location_id=location_id,
            max_queue_length=max_queue_length,
        )
        return WaitingRoomResponse.from_orm(room)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
