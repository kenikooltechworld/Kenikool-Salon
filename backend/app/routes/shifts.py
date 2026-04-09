"""Shift management routes."""

from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, HTTPException, Query, Depends
from bson import ObjectId
from app.models.shift import Shift
from app.models.staff import Staff
from app.schemas.shift import ShiftCreate, ShiftUpdate, ShiftResponse, ShiftListResponse
from app.context import get_tenant_id

router = APIRouter(prefix="/shifts", tags=["shifts"])


def check_shift_conflicts(staff_id: str, start_time: datetime, end_time: datetime, exclude_shift_id: str = None, tenant_id: ObjectId = None) -> bool:
    """Check if a shift conflicts with existing shifts for the same staff.
    
    Args:
        staff_id: Staff member ID
        start_time: Shift start time
        end_time: Shift end time
        exclude_shift_id: Shift ID to exclude from conflict check (for updates)
        tenant_id: Tenant ID for filtering
        
    Returns:
        True if conflict exists, False otherwise
    """
    query = {
        "staff_id": ObjectId(staff_id),
        "status": {"$in": ["scheduled", "in_progress"]},
        "tenant_id": ObjectId(tenant_id),
    }
    
    # Exclude the current shift if updating
    if exclude_shift_id:
        query["_id"] = {"$ne": ObjectId(exclude_shift_id)}
    
    # Check for overlapping shifts
    # Conflict occurs if: new_start < existing_end AND new_end > existing_start
    conflicting_shifts = Shift.objects(
        **query,
        start_time__lt=end_time,
        end_time__gt=start_time
    )
    
    return len(conflicting_shifts) > 0


@router.get("", response_model=ShiftListResponse)
async def list_shifts(
    staff_id: str = Query(None, description="Filter by staff ID"),
    status: str = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Page size"),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List shifts with optional filtering."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    query = {"tenant_id": tenant_id}
    
    if staff_id:
        query["staff_id"] = ObjectId(staff_id)
    
    if status:
        query["status"] = status
    
    total = Shift.objects(**query).count()
    shifts = Shift.objects(**query).skip((page - 1) * page_size).limit(page_size).order_by("-created_at")
    
    shift_responses = []
    for shift in shifts:
        shift_dict = shift.to_mongo().to_dict()
        shift_dict["_id"] = str(shift.id)
        shift_dict["staff_id"] = str(shift.staff_id)
        shift_responses.append(ShiftResponse(**shift_dict))
    
    return ShiftListResponse(
        shifts=shift_responses,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{shift_id}", response_model=ShiftResponse)
async def get_shift(shift_id: str, tenant_id: ObjectId = Depends(get_tenant_id)):
    """Get a specific shift by ID."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        shift = Shift.objects(id=ObjectId(shift_id), tenant_id=tenant_id).first()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid shift ID")
    
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    shift_dict = shift.to_mongo().to_dict()
    shift_dict["_id"] = str(shift.id)
    shift_dict["staff_id"] = str(shift.staff_id)
    
    return ShiftResponse(**shift_dict)


@router.post("", response_model=ShiftResponse)
async def create_shift(
    shift_data: ShiftCreate,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Create a new shift with conflict detection."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    # Verify staff exists
    try:
        staff = Staff.objects(id=ObjectId(shift_data.staff_id), tenant_id=tenant_id).first()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid staff ID")
    
    if not staff:
        raise HTTPException(status_code=404, detail="Staff member not found")
    
    # Check for conflicts
    if check_shift_conflicts(shift_data.staff_id, shift_data.start_time, shift_data.end_time, tenant_id=tenant_id):
        raise HTTPException(
            status_code=409,
            detail="Shift conflicts with existing shift for this staff member"
        )
    
    # Create shift
    shift = Shift(
        tenant_id=tenant_id,
        staff_id=ObjectId(shift_data.staff_id),
        start_time=shift_data.start_time,
        end_time=shift_data.end_time,
        status=shift_data.status,
    )
    
    # Calculate labor cost
    labor_cost = shift.calculate_labor_cost(staff.hourly_rate)
    shift.labor_cost = labor_cost
    
    shift.save()
    
    shift_dict = shift.to_mongo().to_dict()
    shift_dict["_id"] = str(shift.id)
    shift_dict["staff_id"] = str(shift.staff_id)
    
    return ShiftResponse(**shift_dict)


@router.put("/{shift_id}", response_model=ShiftResponse)
async def update_shift(
    shift_id: str,
    shift_data: ShiftUpdate,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Update a shift."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        shift = Shift.objects(id=ObjectId(shift_id), tenant_id=tenant_id).first()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid shift ID")
    
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    # Update fields if provided
    if shift_data.status is not None:
        shift.status = shift_data.status
    
    if shift_data.start_time is not None or shift_data.end_time is not None:
        new_start = shift_data.start_time or shift.start_time
        new_end = shift_data.end_time or shift.end_time
        
        # Check for conflicts with new times
        if check_shift_conflicts(str(shift.staff_id), new_start, new_end, exclude_shift_id=shift_id, tenant_id=tenant_id):
            raise HTTPException(
                status_code=409,
                detail="Updated shift conflicts with existing shift for this staff member"
            )
        
        shift.start_time = new_start
        shift.end_time = new_end
        
        # Recalculate labor cost
        staff = Staff.objects(id=shift.staff_id).first()
        if staff:
            labor_cost = shift.calculate_labor_cost(staff.hourly_rate)
            shift.labor_cost = labor_cost
    
    shift.save()
    
    shift_dict = shift.to_mongo().to_dict()
    shift_dict["_id"] = str(shift.id)
    shift_dict["staff_id"] = str(shift.staff_id)
    
    return ShiftResponse(**shift_dict)


@router.delete("/{shift_id}")
async def delete_shift(shift_id: str, tenant_id: ObjectId = Depends(get_tenant_id)):
    """Delete a shift."""
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    
    try:
        shift = Shift.objects(id=ObjectId(shift_id), tenant_id=tenant_id).first()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid shift ID")
    
    if not shift:
        raise HTTPException(status_code=404, detail="Shift not found")
    
    shift.delete()
    
    return {"message": "Shift deleted successfully"}
