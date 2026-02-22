"""
Prerequisite Service API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List

from app.api.dependencies import get_current_user, get_db
from app.services.prerequisite_service import PrerequisiteService

router = APIRouter(prefix="/api/prerequisites", tags=["prerequisites"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def add_prerequisite(
    service_id: str = Query(...),
    prerequisite_service_id: str = Query(...),
    is_required: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Add a prerequisite to a service"""
    try:
        tenant_id = current_user.get("tenant_id")
        result = PrerequisiteService.add_prerequisite(
            db=db,
            tenant_id=tenant_id,
            service_id=service_id,
            prerequisite_service_id=prerequisite_service_id,
            is_required=is_required
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/service/{service_id}")
async def get_service_prerequisites(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all prerequisites for a service"""
    try:
        tenant_id = current_user.get("tenant_id")
        prerequisites = PrerequisiteService.get_service_prerequisites(db, tenant_id, service_id)
        return {"service_id": service_id, "prerequisites": prerequisites}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/check/{client_id}/{service_id}")
async def check_prerequisites_completed(
    client_id: str,
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Check if client has completed all prerequisites for a service"""
    try:
        tenant_id = current_user.get("tenant_id")
        completed = PrerequisiteService.check_prerequisites_completed(
            db=db,
            tenant_id=tenant_id,
            client_id=client_id,
            service_id=service_id
        )
        return {"client_id": client_id, "service_id": service_id, "prerequisites_completed": completed}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/client/{client_id}/completed")
async def get_client_completed_services(
    client_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get list of services completed by client"""
    try:
        tenant_id = current_user.get("tenant_id")
        services = PrerequisiteService.get_client_completed_services(db, tenant_id, client_id)
        return {"client_id": client_id, "completed_services": services}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
