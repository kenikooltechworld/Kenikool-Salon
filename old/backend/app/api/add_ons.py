"""
Add-On Management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.api.dependencies import get_current_user, get_db
from app.services.add_on_service import AddOnService

router = APIRouter(prefix="/api/add-ons", tags=["add-ons"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_add_on(
    service_id: str = Query(...),
    name: str = Query(...),
    price: float = Query(...),
    duration_minutes: int = Query(...),
    description: Optional[str] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create an add-on"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = AddOnService.create_add_on(
            db=db,
            tenant_id=tenant_id,
            service_id=service_id,
            name=name,
            price=price,
            duration_minutes=duration_minutes,
            description=description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/service/{service_id}")
async def get_service_add_ons(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all add-ons for a service"""
    try:
        tenant_id = current_user.get("tenant_id")
        add_ons = AddOnService.get_service_add_ons(db, tenant_id, service_id)
        return {"service_id": service_id, "add_ons": add_ons}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{add_on_id}")
async def get_add_on(
    add_on_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific add-on"""
    try:
        tenant_id = current_user.get("tenant_id")
        add_on = AddOnService.get_add_on(db, tenant_id, add_on_id)
        if not add_on:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Add-on not found")
        return add_on
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate-cost")
async def calculate_add_ons_cost(
    add_on_ids: List[str] = Query(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Calculate total cost of add-ons"""
    try:
        tenant_id = current_user.get("tenant_id")
        cost = AddOnService.calculate_add_ons_cost(db, tenant_id, add_on_ids)
        return {"add_on_ids": add_on_ids, "total_cost": cost}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate-duration")
async def calculate_add_ons_duration(
    add_on_ids: List[str] = Query(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Calculate total duration of add-ons"""
    try:
        tenant_id = current_user.get("tenant_id")
        duration = AddOnService.calculate_add_ons_duration(db, tenant_id, add_on_ids)
        return {"add_on_ids": add_on_ids, "total_duration_minutes": duration}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
