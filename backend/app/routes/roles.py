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
    logger.info(f"[ROLES] ========== ENDPOINT CALLED ==========")
    logger.info(f"[ROLES] tenant_id: {tenant_id}")
    logger.info(f"[ROLES] tenant_id type: {type(tenant_id)}")
    try:
        logger.info(f"[ROLES] Querying roles for tenant: {tenant_id}")
        roles = Role.objects(tenant_id=tenant_id).order_by("name")
        logger.info(f"[ROLES] Query executed. Found {roles.count()} roles")
        
        # If no roles exist, create default roles
        if roles.count() == 0:
            logger.info(f"[ROLES] No roles found, creating default roles...")
            try:
                from app.services.rbac_service import RBACService
                rbac_service = RBACService()
                rbac_service.create_default_roles(str(tenant_id))
                logger.info(f"[ROLES] Default roles created successfully")
                roles = Role.objects(tenant_id=tenant_id).order_by("name")
                logger.info(f"[ROLES] After creation: {roles.count()} roles")
            except Exception as create_error:
                logger.error(f"[ROLES] Error creating default roles: {str(create_error)}", exc_info=True)
                raise
        
        response_roles = [role_to_response(r) for r in roles]
        logger.info(f"[ROLES] Converting {len(response_roles)} roles to response format")
        for r in response_roles:
            logger.info(f"[ROLES]   - {r['name']} (id: {r['id']})")
        
        result = {"roles": response_roles}
        logger.info(f"[ROLES] Returning response with {len(response_roles)} roles")
        logger.info(f"[ROLES] ========== ENDPOINT COMPLETE ==========")
        return result
    except HTTPException:
        logger.error(f"[ROLES] HTTPException raised")
        raise
    except Exception as e:
        logger.error(f"[ROLES] Exception: {str(e)}", exc_info=True)
        logger.error(f"[ROLES] ========== ENDPOINT FAILED ==========")
        raise HTTPException(status_code=400, detail=f"Failed to list roles: {str(e)}")
