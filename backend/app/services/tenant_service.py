"""Tenant provisioning and management service."""

import logging
import secrets
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.services.auth_service import AuthenticationService
from app.services.rbac_service import RBACService
from app.config import Settings

logger = logging.getLogger(__name__)


class TenantProvisioningService:
    """Service for provisioning and managing tenants."""

    def __init__(self, settings: Settings):
        """Initialize tenant provisioning service."""
        self.settings = settings
        self.auth_service = AuthenticationService(settings)
        self.rbac_service = RBACService()

    def provision_tenant(
        self,
        name: str,
        email: str,
        phone: str,
        subscription_tier: str = "starter",
        region: str = "us-east-1",
    ) -> Optional[Dict[str, Any]]:
        """Provision a new tenant with all required setup."""
        try:
            # Check if tenant already exists
            existing_tenant = Tenant.objects(name=name).first()
            if existing_tenant:
                logger.warning(f"Tenant already exists: {name}")
                return None

            # Default business hours
            default_business_hours = {
                "monday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                "tuesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                "wednesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                "thursday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                "friday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
                "saturday": {"open_time": "10:00", "close_time": "16:00", "is_closed": False},
                "sunday": {"open_time": "00:00", "close_time": "00:00", "is_closed": True},
            }

            # Create tenant with default settings
            tenant = Tenant(
                name=name,
                subscription_tier=subscription_tier,
                status="active",
                region=region,
                settings={
                    "email": email,
                    "phone": phone,
                    "tax_rate": 0.0,
                    "currency": "NGN",
                    "timezone": "Africa/Lagos",
                    "language": "en",
                    "business_hours": default_business_hours,
                    "notification_email": True,
                    "notification_sms": False,
                    "notification_push": False,
                    "logo_url": None,
                    "primary_color": "#000000",
                    "secondary_color": "#FFFFFF",
                    "appointment_reminder_hours": 24,
                    "allow_online_booking": True,
                    "require_customer_approval": False,
                    "auto_confirm_bookings": True,
                }
            )
            tenant.save()
            logger.info(f"Tenant created: {name} (ID: {tenant.id})")

            # Create default roles and permissions
            self.rbac_service.create_default_roles(str(tenant.id))

            # Get Owner role
            owner_role = Role.objects(
                tenant_id=tenant.id, name="Owner"
            ).first()
            if not owner_role:
                logger.error(f"Failed to create Owner role for tenant: {tenant.id}")
                return None

            # Create admin user
            admin_password = secrets.token_urlsafe(16)
            admin_user = User(
                tenant_id=tenant.id,
                email=email,
                password_hash=self.auth_service.hash_password(admin_password),
                first_name="Admin",
                last_name="User",
                phone=phone,
                role_ids=[owner_role.id],  # Multiple roles per user
                status="active",
            )
            admin_user.save()
            logger.info(f"Admin user created: {email} (ID: {admin_user.id})")

            # Generate API key
            api_key = self._generate_api_key()

            return {
                "tenant_id": str(tenant.id),
                "admin_user_id": str(admin_user.id),
                "admin_email": email,
                "admin_password": admin_password,
                "api_key": api_key,
                "subscription_tier": subscription_tier,
                "status": "active",
                "created_at": tenant.created_at.isoformat(),
            }
        except Exception as e:
            logger.error(f"Error provisioning tenant: {e}")
            return None

    def _generate_api_key(self) -> str:
        """Generate a random API key."""
        return secrets.token_urlsafe(32)

    def get_tenant(self, tenant_id: str) -> Optional[Tenant]:
        """Get a tenant by ID."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            return tenant
        except Exception as e:
            logger.error(f"Error getting tenant: {e}")
            return None

    def update_tenant(
        self, tenant_id: str, **kwargs
    ) -> Optional[Tenant]:
        """Update tenant settings."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return None

            for key, value in kwargs.items():
                if hasattr(tenant, key):
                    setattr(tenant, key, value)

            tenant.updated_at = datetime.utcnow()
            tenant.save()
            logger.info(f"Tenant updated: {tenant_id}")
            return tenant
        except Exception as e:
            logger.error(f"Error updating tenant: {e}")
            return None

    def suspend_tenant(self, tenant_id: str) -> bool:
        """Suspend a tenant."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return False

            tenant.status = "suspended"
            tenant.updated_at = datetime.utcnow()
            tenant.save()
            logger.info(f"Tenant suspended: {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Error suspending tenant: {e}")
            return False

    def delete_tenant(self, tenant_id: str) -> bool:
        """Delete a tenant (soft delete)."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return False

            tenant.status = "deleted"
            tenant.deleted_at = datetime.utcnow()
            tenant.updated_at = datetime.utcnow()
            tenant.save()
            logger.info(f"Tenant deleted: {tenant_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting tenant: {e}")
            return False

    def list_tenants(self, status: str = "active") -> list:
        """List all tenants with a specific status."""
        try:
            tenants = Tenant.objects(status=status)
            return list(tenants)
        except Exception as e:
            logger.error(f"Error listing tenants: {e}")
            return []
