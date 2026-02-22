"""Routes for time slot reservation management."""

from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId
from app.schemas.time_slot import (
    TimeSlotReserveRequest,
    TimeSlotConfirmRequest,
    TimeSlotReleaseRequest,
    TimeSlotResponse,
    TimeSlotListResponse,
)
from app.services.time_slot_service import TimeSlotService
from app.middleware.tenant_context import get_tenant_id


router = APIRouter(prefix="/time-slots", tags=["time-slots"])


@router.post("", response_model=TimeSlotResponse)
async def reserve_time_slot(
    request: TimeSlotReserveRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Reserve a time slot for a customer.
    
    - **staff_id**: Staff member ID
    - **service_id**: Service ID
    - **start_time**: Slot start time (UTC)
    - **end_time**: Slot end time (UTC)
    - **customer_id**: Optional customer ID
    """
    try:
        staff_id = ObjectId(request.staff_id)
        service_id = ObjectId(request.service_id)
        customer_id = ObjectId(request.customer_id) if request.customer_id else None
        
        time_slot = TimeSlotService.reserve_slot(
            tenant_id=tenant_id,
            staff_id=staff_id,
            service_id=service_id,
            start_time=request.start_time,
            end_time=request.end_time,
            customer_id=customer_id,
        )
        
        return TimeSlotResponse(
            id=str(time_slot.id),
            staff_id=str(time_slot.staff_id),
            service_id=str(time_slot.service_id),
            customer_id=str(time_slot.customer_id) if time_slot.customer_id else None,
            start_time=time_slot.start_time.isoformat(),
            end_time=time_slot.end_time.isoformat(),
            status=time_slot.status,
            reserved_at=time_slot.reserved_at.isoformat(),
            expires_at=time_slot.expires_at.isoformat(),
            appointment_id=str(time_slot.appointment_id) if time_slot.appointment_id else None,
            created_at=time_slot.created_at.isoformat(),
            updated_at=time_slot.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{time_slot_id}/confirm", response_model=TimeSlotResponse)
async def confirm_time_slot(
    time_slot_id: str,
    request: TimeSlotConfirmRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Confirm a time slot reservation by linking to appointment."""
    try:
        slot_id = ObjectId(time_slot_id)
        appointment_id = ObjectId(request.appointment_id)
        
        time_slot = TimeSlotService.confirm_reservation(
            tenant_id=tenant_id,
            time_slot_id=slot_id,
            appointment_id=appointment_id,
        )
        
        return TimeSlotResponse(
            id=str(time_slot.id),
            staff_id=str(time_slot.staff_id),
            service_id=str(time_slot.service_id),
            customer_id=str(time_slot.customer_id) if time_slot.customer_id else None,
            start_time=time_slot.start_time.isoformat(),
            end_time=time_slot.end_time.isoformat(),
            status=time_slot.status,
            reserved_at=time_slot.reserved_at.isoformat(),
            expires_at=time_slot.expires_at.isoformat(),
            appointment_id=str(time_slot.appointment_id) if time_slot.appointment_id else None,
            created_at=time_slot.created_at.isoformat(),
            updated_at=time_slot.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{time_slot_id}/release", response_model=TimeSlotResponse)
async def release_time_slot(
    time_slot_id: str,
    request: TimeSlotReleaseRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Release a time slot reservation."""
    try:
        slot_id = ObjectId(time_slot_id)
        
        time_slot = TimeSlotService.release_reservation(
            tenant_id=tenant_id,
            time_slot_id=slot_id,
        )
        
        return TimeSlotResponse(
            id=str(time_slot.id),
            staff_id=str(time_slot.staff_id),
            service_id=str(time_slot.service_id),
            customer_id=str(time_slot.customer_id) if time_slot.customer_id else None,
            start_time=time_slot.start_time.isoformat(),
            end_time=time_slot.end_time.isoformat(),
            status=time_slot.status,
            reserved_at=time_slot.reserved_at.isoformat(),
            expires_at=time_slot.expires_at.isoformat(),
            appointment_id=str(time_slot.appointment_id) if time_slot.appointment_id else None,
            created_at=time_slot.created_at.isoformat(),
            updated_at=time_slot.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=TimeSlotListResponse)
async def list_active_reservations(
    staff_id: str = None,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List active time slot reservations."""
    try:
        staff_id_obj = ObjectId(staff_id) if staff_id else None
        
        time_slots = TimeSlotService.list_active_reservations(
            tenant_id=tenant_id,
            staff_id=staff_id_obj,
        )
        
        return TimeSlotListResponse(
            time_slots=[
                TimeSlotResponse(
                    id=str(slot.id),
                    staff_id=str(slot.staff_id),
                    service_id=str(slot.service_id),
                    customer_id=str(slot.customer_id) if slot.customer_id else None,
                    start_time=slot.start_time.isoformat(),
                    end_time=slot.end_time.isoformat(),
                    status=slot.status,
                    reserved_at=slot.reserved_at.isoformat(),
                    expires_at=slot.expires_at.isoformat(),
                    appointment_id=str(slot.appointment_id) if slot.appointment_id else None,
                    created_at=slot.created_at.isoformat(),
                    updated_at=slot.updated_at.isoformat(),
                )
                for slot in time_slots
            ],
            total=len(time_slots),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
