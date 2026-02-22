"""Routes for appointment history endpoints."""

from datetime import datetime
from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.models.appointment_history import AppointmentHistory
from app.models.service import Service
from app.models.staff import Staff
from app.models.user import User
from app.schemas.appointment_history import (
    AppointmentHistoryResponse,
    AppointmentHistoryListResponse,
    AppointmentHistoryDetailResponse,
)
from app.middleware.tenant_context import get_tenant_id

router = APIRouter(prefix="/customers", tags=["appointment_history"])


def enrich_history_entries(
    entries: List[AppointmentHistory],
    tenant_id: ObjectId,
    services_cache: Optional[Dict] = None,
    staff_cache: Optional[Dict] = None,
    users_cache: Optional[Dict] = None,
) -> List[dict]:
    """Enrich history entries with service and staff names using batch queries."""
    if not entries:
        return []
    
    # Build caches if not provided
    if services_cache is None:
        service_ids = [e.service_id for e in entries]
        services_cache = {s.id: s for s in Service.objects(tenant_id=tenant_id, id__in=service_ids)}
    
    if staff_cache is None or users_cache is None:
        staff_ids = [e.staff_id for e in entries]
        staff_list = Staff.objects(tenant_id=tenant_id, id__in=staff_ids)
        staff_cache = {s.id: s for s in staff_list}
        
        user_ids = [s.user_id for s in staff_list if s.user_id]
        users_cache = {u.id: u for u in User.objects(id__in=user_ids)}
    
    # Enrich entries using caches
    enriched = []
    for entry in entries:
        service = services_cache.get(entry.service_id)
        staff = staff_cache.get(entry.staff_id)
        
        service_name = service.name if service else "Unknown Service"
        staff_name = "Unknown Staff"
        if staff and staff.user_id:
            user = users_cache.get(staff.user_id)
            if user:
                staff_name = f"{user.first_name} {user.last_name}"
        
        enriched.append({
            "id": str(entry.id),
            "customer_id": str(entry.customer_id),
            "appointment_id": str(entry.appointment_id),
            "service_id": str(entry.service_id),
            "staff_id": str(entry.staff_id),
            "service_name": service_name,
            "staff_name": staff_name,
            "appointment_date": entry.appointment_date.isoformat(),
            "appointment_time": entry.appointment_date.strftime("%H:%M"),
            "notes": entry.notes or "",
            "rating": 0,
            "feedback": "",
            "created_at": entry.created_at.isoformat(),
        })
    
    return enriched


@router.get("/{customer_id}/history", response_model=AppointmentHistoryListResponse)
async def get_customer_history(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Get customer appointment history with pagination.
    
    - **customer_id**: Customer ID
    - **page**: Page number (1-indexed)
    - **page_size**: Number of results per page
    """
    try:
        customer_id_obj = ObjectId(customer_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid customer ID")

    try:
        # Calculate skip for pagination
        skip = (page - 1) * page_size
        
        # Query appointment history
        query = AppointmentHistory.objects(
            tenant_id=tenant_id,
            customer_id=customer_id_obj
        )
        
        # Get total count
        total = query.count()
        
        # Get paginated results, sorted by appointment_date descending
        history_entries = list(query.order_by("-appointment_date").skip(skip).limit(page_size))
        
        # Batch fetch all related data
        service_ids = [e.service_id for e in history_entries]
        staff_ids = [e.staff_id for e in history_entries]
        
        services = {s.id: s for s in Service.objects(tenant_id=tenant_id, id__in=service_ids)}
        staff_list = Staff.objects(tenant_id=tenant_id, id__in=staff_ids)
        user_ids = [s.user_id for s in staff_list if s.user_id]
        users = {u.id: u for u in User.objects(id__in=user_ids)}
        staff_cache = {s.id: s for s in staff_list}
        
        return AppointmentHistoryListResponse(
            history=enrich_history_entries(
                history_entries,
                tenant_id,
                services_cache=services,
                staff_cache=staff_cache,
                users_cache=users,
            ),
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{customer_id}/history/{history_id}", response_model=AppointmentHistoryDetailResponse)
async def get_history_entry(
    customer_id: str,
    history_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """
    Get specific appointment history entry.
    
    - **customer_id**: Customer ID
    - **history_id**: History entry ID
    """
    try:
        customer_id_obj = ObjectId(customer_id)
        history_id_obj = ObjectId(history_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid customer ID or history ID")

    try:
        history_entry = AppointmentHistory.objects(
            tenant_id=tenant_id,
            id=history_id_obj,
            customer_id=customer_id_obj
        ).first()
        
        if not history_entry:
            raise HTTPException(status_code=404, detail="History entry not found")
        
        # Enrich with batch queries
        enriched = enrich_history_entries([history_entry], tenant_id)
        return enriched[0] if enriched else {}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
