"""Tenant settings service."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.tenant import Tenant
from app.schemas.tenant_settings import TenantSettingsSchema
from app.config import get_settings

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
            
            # Get platform domain and environment from config
            config = get_settings()
            platform_domain = config.platform_domain
            environment = config.environment.lower()
            
            # Generate subdomain URL based on environment
            # For development, use http with port 3000
            # For production, use https without port
            if tenant.subdomain:
                if environment == "development":
                    # Development: http://subdomain.localhost:3000
                    subdomain_url = f"http://{tenant.subdomain}.{platform_domain}:3000"
                else:
                    # Production/Staging: https://subdomain.domain.com
                    subdomain_url = f"https://{tenant.subdomain}.{platform_domain}"
            else:
                subdomain_url = ""
            
            # Default configs
            default_system_config = {
                "rate_limit_enabled": True,
                "rate_limit_requests": 100,
                "rate_limit_window": 60,
                "ddos_protection_enabled": True,
                "ddos_threshold": 1000,
                "waf_enabled": True,
                "intrusion_detection_enabled": True,
                "audit_logging_enabled": True,
                "feature_flags": {},
            }
            
            default_integration_config = {
                "termii": {"apiKey": "", "senderId": "", "enabled": False},
                "paystack": {"publicKey": "", "secretKey": "", "webhookUrl": "", "enabled": False},
            }
            
            default_financial_config = {
                "balance_enforcement_enabled": True,
                "minimum_balance_threshold": 0,
                "refund_policy_enabled": True,
                "refund_window_days": 30,
                "commission_tracking_enabled": True,
                "staff_commission_percentage": 10,
                "service_commission_percentage": 5,
                "invoice_numbering_prefix": "INV",
                "invoice_numbering_start": 1000,
            }
            
            default_operational_config = {
                "inventory_tracking_enabled": True,
                "low_stock_threshold": 10,
                "waiting_room_enabled": True,
                "waiting_room_max_capacity": 50,
                "resource_management_enabled": True,
                "notification_preferences_enabled": True,
                "sms_provider": "termii",
                "email_provider": "smtp",
                "backup_enabled": True,
                "backup_frequency": "daily",
                "cache_optimization_enabled": True,
                "cache_ttl_minutes": 60,
            }
            
            return {
                "tenant_id": str(tenant.id),
                "tenant_name": tenant.name,
                "subdomain": tenant.subdomain,
                "subdomain_url": subdomain_url,
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
                "customer_welcome_email_template": settings.get("customer_welcome_email_template", ""),
                "system_config": settings.get("system_config", default_system_config),
                "integration_config": settings.get("integration_config", default_integration_config),
                "financial_config": settings.get("financial_config", default_financial_config),
                "operational_config": settings.get("operational_config", default_operational_config),
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

            # Preserve existing config sections if not provided in updates
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
            
            # Handle customer_welcome_email_template if provided
            if "customer_welcome_email_template" in updates:
                tenant.settings["customer_welcome_email_template"] = updates["customer_welcome_email_template"]
            
            # Handle config sections if provided in updates
            if "system_config" in updates:
                tenant.settings["system_config"] = updates["system_config"]
            if "integration_config" in updates:
                tenant.settings["integration_config"] = updates["integration_config"]
            if "financial_config" in updates:
                tenant.settings["financial_config"] = updates["financial_config"]
            if "operational_config" in updates:
                tenant.settings["operational_config"] = updates["operational_config"]

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
