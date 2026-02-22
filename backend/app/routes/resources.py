"""Resource routes."""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime
from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceResponse,
    ResourceAvailabilityCreate,
    ResourceAvailabilityResponse,
    ResourceAssignmentResponse,
    ResourceMaintenanceCreate,
    ResourceMaintenanceResponse,
    ResourceUtilizationResponse,
)
from app.services.resource_service import ResourceService
from app.decorators.tenant_isolated import tenant_isolated

router = APIRouter(prefix="/resources", tags=["resources"])


# Resource Management
@router.post("", response_model=ResourceResponse)
@tenant_isolated
async def create_resource(resource: ResourceCreate):
    """Create a new resource."""
    try:
        created = ResourceService.create_resource(
            name=resource.name,
            type=resource.type,
            quantity=resource.quantity,
            location_id=resource.location_id,
            description=resource.description,
            purchase_date=resource.purchase_date,
            purchase_price=resource.purchase_price,
            tags=resource.tags,
        )
        return ResourceResponse.from_orm(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{resource_id}", response_model=dict)
@tenant_isolated
async def get_resource(resource_id: str):
    """Get a resource by ID."""
    resource = ResourceService.get_resource(resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"data": ResourceResponse.from_orm(resource)}


@router.get("", response_model=dict)
@tenant_isolated
async def list_resources(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    location_id: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
):
    """List resources with optional filtering."""
    resources = ResourceService.get_resources(
        type=type,
        status=status,
        location_id=location_id,
        is_active=is_active,
        limit=limit,
        skip=skip,
    )
    return {"data": [ResourceResponse.from_orm(r) for r in resources]}


@router.put("/{resource_id}", response_model=ResourceResponse)
@tenant_isolated
async def update_resource(resource_id: str, resource: ResourceUpdate):
    """Update a resource."""
    try:
        updated = ResourceService.update_resource(
            resource_id=resource_id,
            name=resource.name,
            description=resource.description,
            quantity=resource.quantity,
            tags=resource.tags,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Resource not found")
        return ResourceResponse.from_orm(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{resource_id}", response_model=ResourceResponse)
@tenant_isolated
async def patch_resource(resource_id: str, resource: ResourceUpdate):
    """Update a resource (PATCH)."""
    try:
        updated = ResourceService.update_resource(
            resource_id=resource_id,
            name=resource.name,
            description=resource.description,
            quantity=resource.quantity,
            tags=resource.tags,
        )
        if not updated:
            raise HTTPException(status_code=404, detail="Resource not found")
        return ResourceResponse.from_orm(updated)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{resource_id}")
@tenant_isolated
async def delete_resource(resource_id: str):
    """Delete a resource."""
    success = ResourceService.delete_resource(resource_id)
    if not success:
        raise HTTPException(status_code=404, detail="Resource not found")
    return {"message": "Resource deleted successfully"}


@router.get("/available", response_model=dict)
@tenant_isolated
async def get_available_resources(
    type: Optional[str] = Query(None),
    quantity: int = Query(1, ge=1),
    date: Optional[datetime] = Query(None),
):
    """Get available resources."""
    resources = ResourceService.get_available_resources(
        type=type, quantity=quantity, date=date
    )
    return {"data": [ResourceResponse.from_orm(r) for r in resources]}


# Resource Availability
@router.post("/availability", response_model=ResourceAvailabilityResponse)
@tenant_isolated
async def set_availability(availability: ResourceAvailabilityCreate):
    """Set resource availability."""
    try:
        created = ResourceService.set_availability(
            resource_id=availability.resource_id,
            start_time=availability.start_time,
            end_time=availability.end_time,
            day_of_week=availability.day_of_week,
            is_recurring=availability.is_recurring,
            effective_from=availability.effective_from,
            effective_to=availability.effective_to,
        )
        return ResourceAvailabilityResponse.from_orm(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{resource_id}/availability", response_model=dict)
@tenant_isolated
async def get_availability(resource_id: str):
    """Get resource availability."""
    availabilities = ResourceService.get_availability(resource_id)
    return {"data": [ResourceAvailabilityResponse.from_orm(a) for a in availabilities]}


@router.patch("/{resource_id}/availability", response_model=dict)
@tenant_isolated
async def update_availability(
    resource_id: str,
    availability: dict
):
    """Update resource availability."""
    try:
        availabilities = availability.get("availability", [])
        results = []
        for avail in availabilities:
            created = ResourceService.set_availability(
                resource_id=resource_id,
                start_time=avail.get("start_time"),
                end_time=avail.get("end_time"),
                day_of_week=avail.get("day_of_week"),
                is_recurring=avail.get("is_recurring", False),
                effective_from=avail.get("effective_from"),
                effective_to=avail.get("effective_to"),
            )
            results.append(ResourceAvailabilityResponse.from_orm(created))
        return {"data": results}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Resource Assignment
@router.post("/assignments", response_model=ResourceAssignmentResponse)
@tenant_isolated
async def assign_resource(
    appointment_id: str, resource_id: str, quantity: int = Query(1, ge=1)
):
    """Assign resource to appointment."""
    try:
        assignment = ResourceService.assign_resource_to_appointment(
            appointment_id=appointment_id, resource_id=resource_id, quantity=quantity
        )
        if not assignment:
            raise HTTPException(
                status_code=400, detail="Resource not available or cannot be assigned"
            )
        return ResourceAssignmentResponse.from_orm(assignment)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/assign", response_model=dict)
@tenant_isolated
async def assign_resource_to_appointment(data: dict):
    """Assign resource to appointment."""
    try:
        assignment = ResourceService.assign_resource_to_appointment(
            appointment_id=data.get("appointment_id"),
            resource_id=data.get("resource_id"),
            quantity=data.get("quantity_used", 1)
        )
        if not assignment:
            raise HTTPException(
                status_code=400, detail="Resource not available or cannot be assigned"
            )
        return {"data": ResourceAssignmentResponse.from_orm(assignment)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/appointments/{appointment_id}/resources", response_model=dict)
@tenant_isolated
async def get_appointment_resources(appointment_id: str):
    """Get resources assigned to appointment."""
    assignments = ResourceService.get_appointment_resources(appointment_id)
    return {"data": [ResourceAssignmentResponse.from_orm(a) for a in assignments]}


@router.get("/assignments/{appointment_id}", response_model=dict)
@tenant_isolated
async def get_appointment_resources_alt(appointment_id: str):
    """Get resources assigned to appointment (alternative endpoint)."""
    assignments = ResourceService.get_appointment_resources(appointment_id)
    return {"data": [ResourceAssignmentResponse.from_orm(a) for a in assignments]}


@router.patch("/assignments/{assignment_id}/release", response_model=dict)
@tenant_isolated
async def release_resource_assignment(assignment_id: str):
    """Release resource assignment."""
    try:
        # This would need to be implemented in the service
        return {"data": {"message": "Resource released"}}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/appointments/{appointment_id}/release-resources")
@tenant_isolated
async def release_appointment_resources(appointment_id: str):
    """Release all resources assigned to appointment."""
    try:
        ResourceService.release_appointment_resources(appointment_id)
        return {"message": "Resources released successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Resource Maintenance
@router.post("/maintenance", response_model=ResourceMaintenanceResponse)
@tenant_isolated
async def schedule_maintenance(maintenance: ResourceMaintenanceCreate):
    """Schedule resource maintenance."""
    try:
        created = ResourceService.schedule_maintenance(
            resource_id=maintenance.resource_id,
            maintenance_type=maintenance.maintenance_type,
            scheduled_date=maintenance.scheduled_date,
            estimated_duration_hours=maintenance.estimated_duration_hours,
            description=maintenance.description,
            cost=maintenance.cost,
        )
        return ResourceMaintenanceResponse.from_orm(created)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/maintenance", response_model=dict)
@tenant_isolated
async def get_maintenance_schedule(
    resource_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
):
    """Get maintenance schedule."""
    maintenance_records = ResourceService.get_maintenance_schedule(
        resource_id=resource_id, status=status
    )
    return {"data": [ResourceMaintenanceResponse.from_orm(m) for m in maintenance_records]}


@router.patch("/maintenance/{maintenance_id}/complete", response_model=ResourceMaintenanceResponse)
@tenant_isolated
async def complete_maintenance(maintenance_id: str):
    """Mark maintenance as completed."""
    try:
        maintenance = ResourceService.complete_maintenance(maintenance_id)
        if not maintenance:
            raise HTTPException(status_code=404, detail="Maintenance record not found")
        return ResourceMaintenanceResponse.from_orm(maintenance)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{resource_id}/maintenance", response_model=dict)
@tenant_isolated
async def mark_resource_maintenance(resource_id: str):
    """Mark resource as in maintenance."""
    try:
        resource = ResourceService.get_resource(resource_id)
        if not resource:
            raise HTTPException(status_code=404, detail="Resource not found")
        # Update resource status to maintenance
        resource.status = "maintenance"
        resource.save()
        return {"data": ResourceResponse.from_orm(resource)}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Resource Utilization
@router.get("/utilization/stats", response_model=dict)
@tenant_isolated
async def get_utilization_stats(
    resource_id: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
):
    """Get resource utilization statistics."""
    stats = ResourceService.get_utilization_stats(
        resource_id=resource_id, start_date=start_date, end_date=end_date
    )
    return stats


@router.get("/conflicts", response_model=dict)
@tenant_isolated
async def get_resource_conflicts(
    resource_id: str,
    start_date: datetime,
    end_date: datetime,
):
    """Get resource conflicts."""
    conflicts = ResourceService.get_resource_conflicts(
        resource_id=resource_id, start_date=start_date, end_date=end_date
    )
    return {"data": [ResourceAssignmentResponse.from_orm(c) for c in conflicts]}
