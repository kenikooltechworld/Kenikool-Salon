"""Service management routes."""

import logging
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from bson import ObjectId
from app.models.service import Service
from app.schemas.service import (
    ServiceCreateRequest,
    ServiceUpdateRequest,
    ServiceResponse,
    ServiceListResponse,
)
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/services", tags=["services"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def service_to_response(service: Service) -> ServiceResponse:
    """Convert Service model to response schema."""
    return ServiceResponse(
        id=str(service.id),
        name=service.name,
        description=service.description,
        duration_minutes=service.duration_minutes,
        price=float(service.price),
        category=service.category,
        color=service.color,
        icon=service.icon,
        is_active=service.is_active,
        is_published=service.is_published,
        public_description=service.public_description,
        public_image_url=service.public_image_url,
        allow_public_booking=service.allow_public_booking,
        tags=service.tags,
        created_at=service.created_at.isoformat(),
        updated_at=service.updated_at.isoformat(),
    )


@router.post("", response_model=ServiceResponse)
@tenant_isolated
async def create_service(
    request: ServiceCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Create a new service.

    Creates a new service for the tenant with the provided details.
    """
    try:
        service = Service(
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            duration_minutes=request.duration_minutes,
            price=request.price,
            category=request.category,
            is_active=request.is_active,
            is_published=request.is_published,
            public_description=request.public_description,
            public_image_url=request.public_image_url,
            allow_public_booking=request.allow_public_booking,
            tags=request.tags,
        )
        service.save()
        logger.info(f"Service created: {service.id} for tenant {tenant_id}")
        return service_to_response(service)
    except Exception as e:
        logger.error(f"Failed to create service: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to create service")


@router.get("/{service_id}", response_model=ServiceResponse)
@tenant_isolated
async def get_service(
    service_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get a specific service.

    Returns the service details for the given service ID.
    """
    try:
        service = Service.objects(id=ObjectId(service_id), tenant_id=tenant_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        return service_to_response(service)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to get service: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get service")


@router.get("", response_model=ServiceListResponse)
@tenant_isolated
async def list_services(
    category: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List services for the tenant.

    Returns a paginated list of services with optional filtering by category and status.
    """
    try:
        query = Service.objects(tenant_id=tenant_id)

        # Apply filters
        if category:
            query = query(category=category)
        if is_active is not None:
            query = query(is_active=is_active)

        # Get total count
        total = query.count()

        # Apply pagination
        skip = (page - 1) * page_size
        services = query.skip(skip).limit(page_size).order_by("-created_at")

        return ServiceListResponse(
            services=[service_to_response(s) for s in services],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        logger.error(f"Failed to list services: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list services")


@router.put("/{service_id}", response_model=ServiceResponse)
@tenant_isolated
async def update_service(
    service_id: str,
    request: ServiceUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update a service.

    Updates the service with the provided details.
    """
    try:
        service = Service.objects(id=ObjectId(service_id), tenant_id=tenant_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        # Update only provided fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(service, key, value)

        service.save()
        logger.info(f"Service updated: {service_id} for tenant {tenant_id}")
        return service_to_response(service)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to update service: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update service")


@router.delete("/{service_id}")
@tenant_isolated
async def delete_service(
    service_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Delete a service.

    Deletes the service from the system.
    """
    try:
        service = Service.objects(id=ObjectId(service_id), tenant_id=tenant_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")

        service.delete()
        logger.info(f"Service deleted: {service_id} for tenant {tenant_id}")
        return {"message": "Service deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to delete service: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to delete service")
