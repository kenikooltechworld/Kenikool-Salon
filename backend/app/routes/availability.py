"""Availability management routes."""

import logging
from typing import Optional
from datetime import datetime, date, time, timedelta
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from mongoengine import Q
from app.models.availability import Availability
from app.models.service import Service
from app.schemas.availability import (
    AvailabilityCreateRequest,
    AvailabilityUpdateRequest,
    AvailabilityResponse,
    AvailabilityListResponse,
    AvailableSlotsResponse,
    AvailableSlot,
)
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/availability", tags=["availability"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def availability_to_response(availability: Availability) -> AvailabilityResponse:
    """Convert Availability model to response schema."""
    breaks = []
    if availability.breaks:
        for brk in availability.breaks:
            breaks.append({
                "start_time": brk.get("start_time"),
                "end_time": brk.get("end_time"),
            })
    
    return AvailabilityResponse(
        id=str(availability.id),
        staff_id=str(availability.staff_id),
        day_of_week=availability.day_of_week,
        start_time=availability.start_time,
        end_time=availability.end_time,
        is_recurring=availability.is_recurring,
        effective_from=availability.effective_from.isoformat(),
        effective_to=availability.effective_to.isoformat() if availability.effective_to else None,
        breaks=breaks,
        is_active=availability.is_active,
        notes=availability.notes,
        created_at=availability.created_at.isoformat(),
        updated_at=availability.updated_at.isoformat(),
    )


def validate_time_range(start_time: time, end_time: time) -> None:
    """Validate that start_time is before end_time."""
    # Convert time objects to comparable format
    start_seconds = start_time.hour * 3600 + start_time.minute * 60 + start_time.second
    end_seconds = end_time.hour * 3600 + end_time.minute * 60 + end_time.second
    
    if start_seconds >= end_seconds:
        raise HTTPException(
            status_code=400,
            detail="start_time must be before end_time"
        )


def validate_date_range(effective_from: date, effective_to: Optional[date]) -> None:
    """Validate that effective_from is before effective_to."""
    if effective_to and effective_from > effective_to:
        raise HTTPException(
            status_code=400,
            detail="effective_from must be before or equal to effective_to"
        )


@router.post("", response_model=AvailabilityResponse)
@tenant_isolated
async def create_availability(
    request: AvailabilityCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Create a new availability schedule.

    Creates a new availability schedule for a staff member with support for
    recurring weekly schedules or custom date ranges.
    """
    try:
        # Validate time range
        validate_time_range(request.start_time, request.end_time)
        
        # Validate date range
        validate_date_range(request.effective_from, request.effective_to)
        
        # Validate recurring schedule has day_of_week
        if request.is_recurring and request.day_of_week is None:
            raise HTTPException(
                status_code=400,
                detail="day_of_week is required for recurring schedules"
            )
        
        # Validate non-recurring schedule doesn't have day_of_week
        if not request.is_recurring and request.day_of_week is not None:
            raise HTTPException(
                status_code=400,
                detail="day_of_week should not be set for non-recurring schedules"
            )
        
        # Convert breaks to proper format
        breaks = []
        if request.breaks:
            for brk in request.breaks:
                brk_start_seconds = brk.start_time.hour * 3600 + brk.start_time.minute * 60 + brk.start_time.second
                brk_end_seconds = brk.end_time.hour * 3600 + brk.end_time.minute * 60 + brk.end_time.second
                
                if brk_start_seconds >= brk_end_seconds:
                    raise HTTPException(
                        status_code=400,
                        detail="Break start_time must be before end_time"
                    )
                breaks.append({
                    "start_time": brk.start_time.isoformat(),
                    "end_time": brk.end_time.isoformat(),
                })
        
        availability = Availability(
            tenant_id=tenant_id,
            staff_id=ObjectId(request.staff_id),
            day_of_week=request.day_of_week,
            start_time=request.start_time.isoformat(),
            end_time=request.end_time.isoformat(),
            is_recurring=request.is_recurring,
            effective_from=request.effective_from,
            effective_to=request.effective_to,
            breaks=breaks,
            is_active=request.is_active,
            notes=request.notes,
        )
        availability.save()
        logger.info(f"Availability created: {availability.id} for staff {request.staff_id}")
        return availability_to_response(availability)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create availability: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to create availability")


@router.get("/{availability_id}", response_model=AvailabilityResponse)
@tenant_isolated
async def get_availability(
    availability_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get a specific availability schedule.

    Returns the availability details for the given availability ID.
    """
    try:
        availability = Availability.objects(
            id=ObjectId(availability_id),
            tenant_id=tenant_id
        ).first()
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")
        return availability_to_response(availability)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get availability: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get availability")


@router.get("", response_model=AvailabilityListResponse)
@tenant_isolated
async def list_availability(
    staff_id: Optional[str] = Query(None),
    is_recurring: Optional[bool] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List availability schedules for the tenant.

    Returns a paginated list of availability schedules with optional filtering
    by staff member, recurring status, and active status.
    """
    try:
        query = Availability.objects(tenant_id=tenant_id)

        # Apply filters
        if staff_id:
            query = query(staff_id=ObjectId(staff_id))
        if is_recurring is not None:
            query = query(is_recurring=is_recurring)
        if is_active is not None:
            query = query(is_active=is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        availabilities = query.skip(skip).limit(page_size).order_by("-created_at")

        return AvailabilityListResponse(
            availabilities=[availability_to_response(a) for a in availabilities],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Failed to list availability: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list availability")


@router.put("/{availability_id}", response_model=AvailabilityResponse)
@tenant_isolated
async def update_availability(
    availability_id: str,
    request: AvailabilityUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update an availability schedule.

    Updates the availability schedule with the provided details.
    """
    try:
        availability = Availability.objects(
            id=ObjectId(availability_id),
            tenant_id=tenant_id
        ).first()
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")

        # Validate time range if both are provided
        start_time = request.start_time or availability.start_time
        end_time = request.end_time or availability.end_time
        validate_time_range(start_time, end_time)
        
        # Validate date range if both are provided
        effective_from = request.effective_from or availability.effective_from
        effective_to = request.effective_to or availability.effective_to
        validate_date_range(effective_from, effective_to)
        
        # Validate recurring schedule has day_of_week
        is_recurring = request.is_recurring if request.is_recurring is not None else availability.is_recurring
        day_of_week = request.day_of_week if request.day_of_week is not None else availability.day_of_week
        
        if is_recurring and day_of_week is None:
            raise HTTPException(
                status_code=400,
                detail="day_of_week is required for recurring schedules"
            )

        # Update only provided fields
        update_data = request.model_dump(exclude_unset=True)
        
        # Handle breaks specially
        if "breaks" in update_data and update_data["breaks"]:
            breaks = []
            for brk in update_data["breaks"]:
                if brk.start_time >= brk.end_time:
                    raise HTTPException(
                        status_code=400,
                        detail="Break start_time must be before end_time"
                    )
                breaks.append({
                    "start_time": brk.start_time,
                    "end_time": brk.end_time,
                })
            update_data["breaks"] = breaks
        
        for key, value in update_data.items():
            setattr(availability, key, value)

        availability.save()
        logger.info(f"Availability updated: {availability_id} for tenant {tenant_id}")
        return availability_to_response(availability)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update availability: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update availability")


@router.delete("/{availability_id}")
@tenant_isolated
async def delete_availability(
    availability_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Delete an availability schedule.

    Deletes the availability schedule from the system.
    """
    try:
        availability = Availability.objects(
            id=ObjectId(availability_id),
            tenant_id=tenant_id
        ).first()
        if not availability:
            raise HTTPException(status_code=404, detail="Availability not found")

        availability.delete()
        logger.info(f"Availability deleted: {availability_id} for tenant {tenant_id}")
        return {"message": "Availability deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete availability: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to delete availability")


@router.get("/slots/available", response_model=AvailableSlotsResponse)
@tenant_isolated
async def get_available_slots(
    staff_id: str = Query(..., description="Staff member ID"),
    service_id: str = Query(..., description="Service ID"),
    target_date: str = Query(..., description="Target date (YYYY-MM-DD format)"),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get available time slots for a staff member on a specific date.

    Returns available slots based on staff availability and service duration.
    """
    try:
        from app.utils.availability_calculator import AvailabilityCalculator
        
        logger.info(f"Getting available slots for staff={staff_id}, service={service_id}, date={target_date}")
        
        # Parse target date
        try:
            target_date_obj = datetime.strptime(target_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )
        
        # Validate and convert IDs
        try:
            staff_id_obj = ObjectId(staff_id)
            service_id_obj = ObjectId(service_id)
        except Exception:
            raise HTTPException(
                status_code=400,
                detail="Invalid staff_id or service_id format"
            )
        
        # Get service to determine duration
        service = Service.objects(
            id=service_id_obj,
            tenant_id=tenant_id
        ).first()
        if not service:
            logger.error(f"Service not found: {service_id}")
            raise HTTPException(status_code=404, detail="Service not found")
        
        logger.info(f"Service found: {service.name}, duration={service.duration_minutes} minutes")
        
        # Use AvailabilityCalculator to get slots
        calculator = AvailabilityCalculator()
        availability_slots = calculator.get_available_slots(
            tenant_id=tenant_id,
            staff_id=staff_id_obj,
            service_id=service_id_obj,
            booking_date=target_date_obj,
        )
        
        logger.info(f"Got {len(availability_slots)} available slots")
        
        # Convert AvailabilitySlot objects to response format
        slots = []
        for slot in availability_slots:
            slots.append(AvailableSlot(
                start_time=slot.time.strftime("%H:%M"),
                end_time=(datetime.combine(target_date_obj, slot.time) + timedelta(minutes=service.duration_minutes)).strftime("%H:%M"),
                staff_id=staff_id,
                duration_minutes=service.duration_minutes,
                isAvailable=slot.available,
            ))
        
        logger.info(f"Returning {len(slots)} slots in response")
        
        return AvailableSlotsResponse(
            date=target_date,
            slots=slots,
            staff_id=staff_id,
            total_slots=len(slots),
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get available slots: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail="Failed to get available slots")
