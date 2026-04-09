"""Tenant recovery endpoints."""

import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.tenant_deletion_service import TenantDeletionService
from app.config import settings
from app.context import get_tenant_id

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tenants", tags=["tenant-recovery"])


class RecoveryTokenRequest(BaseModel):
    """Recovery token request."""

    recovery_token: str


class RecoveryStatusResponse(BaseModel):
    """Recovery status response."""

    is_deleted: bool
    days_remaining: int = None
    can_recover: bool
    recovery_expires_at: str = None


@router.post("/recover")
async def recover_account(request: RecoveryTokenRequest):
    """Recover a deleted account using recovery token."""
    try:
        deletion_service = TenantDeletionService(settings)
        result = deletion_service.reactivate_tenant(request.recovery_token)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid recovery token",
            )

        if not result.get("success"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result.get("error", "Recovery failed"),
            )

        return {
            "success": True,
            "message": "Account recovered successfully",
            "tenant_id": result.get("tenant_id"),
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error recovering account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to recover account",
        )


@router.get("/recovery-status/{tenant_id}")
async def get_recovery_status(tenant_id: str):
    """Get recovery status for a tenant."""
    try:
        deletion_service = TenantDeletionService(settings)
        status_info = deletion_service.get_recovery_status(tenant_id)

        if not status_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found",
            )

        return status_info
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting recovery status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recovery status",
        )
