"""Tenant settings service."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.tenant import Tenant
from app.schemas.tenant_settings import TenantSettingsSchema

logger = logging.getLogger(__name__)


class TenantSettingsService:
    """Service for managing tenant settings."""

    @staticmethod
    def get_settings(tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant settings."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
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

            # Return settings with defaults
            settings = tenant.settings or {}
            return {
                "tenant_id": str(tenant.id),
                "subdomain": tenant.subdomain,
                "region": tenant.region,
                "subscription_tier": tenant.subscription_tier,
                "status": tenant.status,
                "salon_name": tenant.name,
                "email": settings.get("email", ""),
                "phone": settings.get("phone", ""),
                "address": tenant.address or "",
                "tax_rate": settings.get("tax_rate", 0.0),
                "currency": settings.get("currency", "NGN"),
                "timezone": settings.get("timezone", "Africa/Lagos"),
                "language": settings.get("language", "en"),
                "business_hours": settings.get("business_hours", default_business_hours),
                "notification_email": settings.get("notification_email", True),
                "notification_sms": settings.get("notification_sms", False),
                "notification_push": settings.get("notification_push", False),
                "logo_url": settings.get("logo_url"),
                "primary_color": settings.get("primary_color", "#000000"),
                "secondary_color": settings.get("secondary_color", "#FFFFFF"),
                "appointment_reminder_hours": settings.get("appointment_reminder_hours", 24),
                "allow_online_booking": settings.get("allow_online_booking", True),
                "require_customer_approval": settings.get("require_customer_approval", False),
                "auto_confirm_bookings": settings.get("auto_confirm_bookings", True),
            }
        except Exception as e:
            logger.error(f"Error getting tenant settings: {str(e)}")
            return None

    @staticmethod
    def update_settings(tenant_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update tenant settings."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
                return None

            # Validate settings using schema
            settings_data = TenantSettingsSchema(**updates)

            # Update tenant
            tenant.name = settings_data.salon_name
            tenant.address = settings_data.address
            tenant.updated_at = datetime.utcnow()

            # Update settings dict
            if not tenant.settings:
                tenant.settings = {}

            # Convert business_hours dict of objects to dict of dicts
            business_hours_dict = {}
            for day, hours in settings_data.business_hours.items():
                business_hours_dict[day] = hours.model_dump() if hasattr(hours, 'model_dump') else hours

            tenant.settings.update({
                "email": settings_data.email,
                "phone": settings_data.phone,
                "tax_rate": settings_data.tax_rate,
                "currency": settings_data.currency,
                "timezone": settings_data.timezone,
                "language": settings_data.language,
                "business_hours": business_hours_dict,
                "notification_email": settings_data.notification_email,
                "notification_sms": settings_data.notification_sms,
                "notification_push": settings_data.notification_push,
                "logo_url": settings_data.logo_url,
                "primary_color": settings_data.primary_color,
                "secondary_color": settings_data.secondary_color,
                "appointment_reminder_hours": settings_data.appointment_reminder_hours,
                "allow_online_booking": settings_data.allow_online_booking,
                "require_customer_approval": settings_data.require_customer_approval,
                "auto_confirm_bookings": settings_data.auto_confirm_bookings,
            })

            tenant.save()
            logger.info(f"Tenant settings updated: {tenant_id}")

            return TenantSettingsService.get_settings(tenant_id)
        except Exception as e:
            logger.error(f"Error updating tenant settings: {str(e)}")
            return None

    @staticmethod
    def reset_settings(tenant_id: str) -> Optional[Dict[str, Any]]:
        """Reset tenant settings to defaults."""
        try:
            tenant = Tenant.objects(id=tenant_id).first()
            if not tenant:
                logger.warning(f"Tenant not found: {tenant_id}")
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

            # Reset to defaults
            tenant.settings = {
                "email": "",
                "phone": "",
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
            tenant.updated_at = datetime.utcnow()
            tenant.save()

            logger.info(f"Tenant settings reset: {tenant_id}")
            return TenantSettingsService.get_settings(tenant_id)
        except Exception as e:
            logger.error(f"Error resetting tenant settings: {str(e)}")
            return None
