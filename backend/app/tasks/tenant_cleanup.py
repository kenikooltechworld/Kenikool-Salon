"""Background tasks for tenant cleanup."""

import logging
from app.services.tenant_deletion_service import TenantDeletionService
from app.config import settings

logger = logging.getLogger(__name__)


def cleanup_deleted_tenants():
    """Permanently delete tenants with expired recovery period."""
    try:
        deletion_service = TenantDeletionService(settings)
        result = deletion_service.cleanup_expired_tenants()

        logger.info(f"Cleanup task result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error in cleanup task: {e}")
        return {
            "success": False,
            "error": str(e),
        }
