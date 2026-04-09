"""Tenant soft delete and recovery service."""

import logging
import secrets
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from app.models.tenant import Tenant
from app.config import Settings

logger = logging.getLogger(__name__)


class TenantDeletionService:
    """Service for managing tenant soft delete and recovery."""

    def __init__(self, settings: Settings):
        """Initialize tenant deletion service."""
        self.settings = settings
        self.grace_period_days = int(
            getattr(settings, "TENANT_DELETION_GRACE_PERIOD_DAYS", 14)
        )

    def soft_delete_tenant(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Soft delete a tenant with recovery token."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return None

            # Generate recovery token
            recovery_token = secrets.token_urlsafe(32)
            recovery_expires = datetime.utcnow() + timedelta(days=self.grace_period_days)

            # Update tenant
            tenant.deletion_status = "soft_deleted"
            tenant.deleted_at = datetime.utcnow()
            tenant.recovery_token = recovery_token
            tenant.recovery_token_expires_at = recovery_expires
            tenant.status = "deleted"
            tenant.save()

            logger.info(f"Tenant soft deleted: {tenant_id}")
            return {
                "tenant_id": str(tenant.id),
                "deleted_at": tenant.deleted_at.isoformat(),
                "recovery_token": recovery_token,
                "recovery_expires_at": recovery_expires.isoformat(),
                "grace_period_days": self.grace_period_days,
            }
        except Exception as e:
            logger.error(f"Error soft deleting tenant: {e}")
            return None

    def reactivate_tenant(self, recovery_token: str) -> Optional[Dict[str, Any]]:
        """Reactivate a tenant using recovery token."""
        try:
            tenant = Tenant.objects(recovery_token=recovery_token).first()
            if not tenant:
                logger.warning(f"Invalid recovery token")
                return None

            # Check if token is expired
            if tenant.recovery_token_expires_at < datetime.utcnow():
                logger.warning(f"Recovery token expired for tenant: {tenant.id}")
                return {
                    "success": False,
                    "error": "Recovery token expired",
                    "tenant_id": str(tenant.id),
                }

            # Reactivate tenant
            tenant.deletion_status = "active"
            tenant.status = "active"
            tenant.deleted_at = None
            tenant.recovery_token = None
            tenant.recovery_token_expires_at = None
            tenant.save()

            logger.info(f"Tenant reactivated: {tenant.id}")
            return {
                "success": True,
                "tenant_id": str(tenant.id),
                "message": "Account recovered successfully",
            }
        except Exception as e:
            logger.error(f"Error reactivating tenant: {e}")
            return None

    def permanently_delete_tenant(self, tenant_id: str) -> bool:
        """Permanently delete a tenant (hard delete)."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return False

            # Mark as permanently deleted before hard delete
            tenant.deletion_status = "permanently_deleted"
            tenant.save()

            # Hard delete
            tenant.delete()
            logger.info(f"Tenant permanently deleted: {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Error permanently deleting tenant: {e}")
            return False

    def is_deleted(self, tenant_id: str) -> bool:
        """Check if tenant is soft deleted."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                return False
            return tenant.deletion_status == "soft_deleted"
        except Exception as e:
            logger.error(f"Error checking deletion status: {e}")
            return False

    def is_recovery_expired(self, tenant_id: str) -> bool:
        """Check if recovery period has expired."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant or not tenant.recovery_token_expires_at:
                return False
            return tenant.recovery_token_expires_at < datetime.utcnow()
        except Exception as e:
            logger.error(f"Error checking recovery expiry: {e}")
            return False

    def get_recovery_status(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get recovery status for a tenant."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                return None

            if tenant.deletion_status != "soft_deleted":
                return {
                    "is_deleted": False,
                    "days_remaining": None,
                    "can_recover": False,
                }

            days_remaining = (
                tenant.recovery_token_expires_at - datetime.utcnow()
            ).days
            can_recover = days_remaining > 0

            return {
                "is_deleted": True,
                "deleted_at": tenant.deleted_at.isoformat(),
                "days_remaining": max(0, days_remaining),
                "can_recover": can_recover,
                "recovery_expires_at": tenant.recovery_token_expires_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error getting recovery status: {e}")
            return None

    def cleanup_expired_tenants(self) -> Dict[str, Any]:
        """Permanently delete tenants with expired recovery period."""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=self.grace_period_days)
            expired_tenants = Tenant.objects(
                deletion_status="soft_deleted", deleted_at__lt=cutoff_date
            )

            deleted_count = 0
            for tenant in expired_tenants:
                if self.permanently_delete_tenant(str(tenant.id)):
                    deleted_count += 1

            logger.info(f"Cleanup task completed: {deleted_count} tenants deleted")
            return {
                "success": True,
                "deleted_count": deleted_count,
                "timestamp": datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
