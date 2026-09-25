"""Roles management routes."""

import logging
from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from app.models.role import Role
from app.context import get_tenant_id
from app.decorators.tenant_isolated import tenant_isolated

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/roles", tags=["roles"])


def get_tenant_id_from_context() -> ObjectId:
    """Get tenant_id from context."""
    tenant_id = get_tenant_id()
    if not tenant_id:
        raise HTTPException(status_code=401, detail="Tenant context not found")
    return tenant_id


def role_to_response(role: Role) -> dict:
    """Convert Role model to response."""
    return {
        "id": str(role.id),
        "name": role.name,
        "description": role.description,
        "isCustom": role.is_custom,
    }


@router.get("", response_model=dict)
async def list_roles(
    tenant_id: ObjectId = Depends(get_tenant_id_from_context),
):
    """
    List all roles for the tenant.

    Returns all available roles for the current tenant.
    """
    try:
        roles = Role.objects(tenant_id=tenant_id).order_by("name")
        total = roles.count()
        
        if total == 0:
            from app.services.rbac_service import RBACService
            rbac_service = RBACService()
            rbac_service.create_default_roles(str(tenant_id))
            roles = Role.objects(tenant_id=tenant_id).order_by("name")
        
        response_roles = [role_to_response(r) for r in roles]
        return {"roles": response_roles}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list roles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=f"Failed to list roles: {str(e)}")
