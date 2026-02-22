"""
Privacy Service - Privacy settings management
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId

from app.database import Database

logger = logging.getLogger(__name__)


class PrivacyException(Exception):
    """Base exception for privacy operations"""
    pass


class BadRequestException(PrivacyException):
    """Raised when request is invalid"""
    pass


class NotFoundException(PrivacyException):
    """Raised when resource is not found"""
    pass


class PrivacyService:
    """Service for privacy settings management"""

    @staticmethod
    async def get_privacy_settings(user_id: str, tenant_id: str) -> Dict:
        """
        Get user privacy settings
        
        Requirements: 7.1
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Privacy settings
        """
        db = Database.get_db()
        
        # Try to get from privacy_settings collection
        privacy = db.privacy_settings.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if privacy:
            privacy["id"] = str(privacy.pop("_id"))
            return privacy
        
        # Return defaults if not found
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "analytics_enabled": True,
            "marketing_emails": True,
            "third_party_sharing": False,
            "data_retention_days": 365
        }

    @staticmethod
    async def update_privacy_settings(
        user_id: str,
        tenant_id: str,
        settings: Dict,
        request_info: Dict
    ) -> Dict:
        """
        Update privacy settings
        
        Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            settings: Privacy settings to update
            request_info: Request metadata
            
        Returns:
            Updated privacy settings
            
        Raises:
            BadRequestException: If settings are invalid
        """
        db = Database.get_db()
        
        # Validate settings
        validated_settings = PrivacyService._validate_settings(settings)
        
        # Get existing settings
        existing = db.privacy_settings.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        # Prepare update document
        update_doc = {
            **validated_settings,
            "updated_at": datetime.utcnow()
        }
        
        if existing:
            # Update existing
            db.privacy_settings.update_one(
                {"_id": existing["_id"]},
                {"$set": update_doc}
            )
            result = db.privacy_settings.find_one({"_id": existing["_id"]})
        else:
            # Create new
            insert_doc = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                **update_doc,
                "created_at": datetime.utcnow()
            }
            result = db.privacy_settings.insert_one(insert_doc)
            result = db.privacy_settings.find_one({"_id": result.inserted_id})
        
        # Log the change (Requirement 7.4, 7.5)
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="privacy_settings_updated",
                request_info=request_info,
                success=True,
                details={"updated_fields": list(validated_settings.keys())}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Privacy settings updated for user {user_id}")
        
        result["id"] = str(result.pop("_id"))
        return result

    @staticmethod
    def _validate_settings(settings: Dict) -> Dict:
        """
        Validate privacy settings
        
        Args:
            settings: Settings to validate
            
        Returns:
            Validated settings
            
        Raises:
            BadRequestException: If any setting is invalid
        """
        validated = {}
        
        # Validate analytics_enabled
        if "analytics_enabled" in settings:
            if not isinstance(settings["analytics_enabled"], bool):
                raise BadRequestException("analytics_enabled must be a boolean")
            validated["analytics_enabled"] = settings["analytics_enabled"]
        
        # Validate marketing_emails
        if "marketing_emails" in settings:
            if not isinstance(settings["marketing_emails"], bool):
                raise BadRequestException("marketing_emails must be a boolean")
            validated["marketing_emails"] = settings["marketing_emails"]
        
        # Validate third_party_sharing
        if "third_party_sharing" in settings:
            if not isinstance(settings["third_party_sharing"], bool):
                raise BadRequestException("third_party_sharing must be a boolean")
            validated["third_party_sharing"] = settings["third_party_sharing"]
        
        # Validate data_retention_days
        if "data_retention_days" in settings:
            if not isinstance(settings["data_retention_days"], int):
                raise BadRequestException("data_retention_days must be an integer")
            if settings["data_retention_days"] < 30 or settings["data_retention_days"] > 2555:
                raise BadRequestException("data_retention_days must be between 30 and 2555")
            validated["data_retention_days"] = settings["data_retention_days"]
        
        return validated

    @staticmethod
    async def opt_out_analytics(
        user_id: str,
        tenant_id: str,
        request_info: Dict
    ) -> Dict:
        """
        Opt out of analytics
        
        Requirements: 7.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            request_info: Request metadata
            
        Returns:
            Updated privacy settings
        """
        return await PrivacyService.update_privacy_settings(
            user_id, tenant_id, {"analytics_enabled": False}, request_info
        )

    @staticmethod
    async def opt_out_marketing(
        user_id: str,
        tenant_id: str,
        request_info: Dict
    ) -> Dict:
        """
        Opt out of marketing emails
        
        Requirements: 7.3
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            request_info: Request metadata
            
        Returns:
            Updated privacy settings
        """
        return await PrivacyService.update_privacy_settings(
            user_id, tenant_id, {"marketing_emails": False}, request_info
        )

    @staticmethod
    async def opt_out_third_party_sharing(
        user_id: str,
        tenant_id: str,
        request_info: Dict
    ) -> Dict:
        """
        Opt out of third-party sharing
        
        Requirements: 7.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            request_info: Request metadata
            
        Returns:
            Updated privacy settings
        """
        return await PrivacyService.update_privacy_settings(
            user_id, tenant_id, {"third_party_sharing": False}, request_info
        )

    @staticmethod
    async def is_analytics_enabled(user_id: str, tenant_id: str) -> bool:
        """
        Check if analytics is enabled
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            True if analytics is enabled
        """
        settings = await PrivacyService.get_privacy_settings(user_id, tenant_id)
        return settings.get("analytics_enabled", True)

    @staticmethod
    async def is_marketing_enabled(user_id: str, tenant_id: str) -> bool:
        """
        Check if marketing emails are enabled
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            True if marketing emails are enabled
        """
        settings = await PrivacyService.get_privacy_settings(user_id, tenant_id)
        return settings.get("marketing_emails", True)

    @staticmethod
    async def is_third_party_sharing_enabled(user_id: str, tenant_id: str) -> bool:
        """
        Check if third-party sharing is enabled
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            True if third-party sharing is enabled
        """
        settings = await PrivacyService.get_privacy_settings(user_id, tenant_id)
        return settings.get("third_party_sharing", False)

    @staticmethod
    async def get_data_retention_days(user_id: str, tenant_id: str) -> int:
        """
        Get data retention period
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Number of days to retain data
        """
        settings = await PrivacyService.get_privacy_settings(user_id, tenant_id)
        return settings.get("data_retention_days", 365)


# Create singleton instance
privacy_service = PrivacyService()
