"""Service category management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.models.service_category import ServiceCategory
from app.schemas.service_category import (
    ServiceCategoryCreateRequest,
    ServiceCategoryUpdateRequest,
    ServiceCategoryResponse,
    ServiceCategoryListResponse,
)
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/service-categories", tags=["service-categories"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def category_to_response(category: ServiceCategory) -> ServiceCategoryResponse:
    """Convert ServiceCategory model to response schema."""
    return ServiceCategoryResponse(
        id=str(category.id),
        name=category.name,
        description=category.description,
        color=category.color,
        icon=category.icon,
        is_active=category.is_active,
        created_at=category.created_at.isoformat(),
        updated_at=category.updated_at.isoformat(),
    )


@router.post("", response_model=ServiceCategoryResponse)
@tenant_isolated
async def create_category(
    request: ServiceCategoryCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Create a new service category.

    Creates a new service category for the tenant.
    """
    try:
        # Check if category with same name already exists
        existing = ServiceCategory.objects(
            tenant_id=tenant_id, name=request.name
        ).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="Category with this name already exists"
            )

        category = ServiceCategory(
            tenant_id=tenant_id,
            name=request.name,
            description=request.description,
            color=request.color,
            icon=request.icon,
            is_active=request.is_active,
        )
        category.save()
        logger.info(f"Service category created: {category.id} for tenant {tenant_id}")
        return category_to_response(category)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create service category: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to create service category")


@router.get("", response_model=ServiceCategoryListResponse)
@tenant_isolated
async def list_categories(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List all service categories for the tenant.

    Returns all service categories for the authenticated tenant.
    """
    try:
        categories = ServiceCategory.objects(tenant_id=tenant_id).order_by(
            "-created_at"
        )
        total = categories.count()

        return ServiceCategoryListResponse(
            categories=[category_to_response(c) for c in categories],
            total=total,
        )
    except Exception as e:
        logger.error(f"Failed to list service categories: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to list service categories")


@router.get("/{category_id}", response_model=ServiceCategoryResponse)
@tenant_isolated
async def get_category(
    category_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Get a specific service category.

    Returns the service category details for the given category ID.
    """
    try:
        category = ServiceCategory.objects(
            id=ObjectId(category_id), tenant_id=tenant_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")
        return category_to_response(category)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to get service category: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to get service category")


@router.put("/{category_id}", response_model=ServiceCategoryResponse)
@tenant_isolated
async def update_category(
    category_id: str,
    request: ServiceCategoryUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Update a service category.

    Updates the service category with the provided details.
    """
    try:
        category = ServiceCategory.objects(
            id=ObjectId(category_id), tenant_id=tenant_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Check if new name conflicts with existing category
        if request.name and request.name != category.name:
            existing = ServiceCategory.objects(
                tenant_id=tenant_id, name=request.name
            ).first()
            if existing:
                raise HTTPException(
                    status_code=400, detail="Category with this name already exists"
                )

        # Update only provided fields
        update_data = request.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(category, key, value)

        category.save()
        logger.info(f"Service category updated: {category_id} for tenant {tenant_id}")
        return category_to_response(category)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to update service category: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to update service category")


@router.delete("/{category_id}")
@tenant_isolated
async def delete_category(
    category_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    Delete a service category.

    Deletes the service category from the system.
    """
    try:
        category = ServiceCategory.objects(
            id=ObjectId(category_id), tenant_id=tenant_id
        ).first()
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

        # Check if any services use this category
        from app.models.service import Service

        services_count = Service.objects(
            tenant_id=tenant_id, category=category.name
        ).count()
        if services_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete category. {services_count} service(s) use this category.",
            )

        category.delete()
        logger.info(f"Service category deleted: {category_id} for tenant {tenant_id}")
        return {"message": "Service category deleted successfully"}
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        logger.error(f"Failed to delete service category: {str(e)}")
        raise HTTPException(status_code=400, detail="Failed to delete service category")
