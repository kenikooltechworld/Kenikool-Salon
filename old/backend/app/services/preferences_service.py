"""
Preferences Service - User preferences management (language, timezone, currency, accessibility)
"""
import logging
from datetime import datetime
from typing import Dict, Optional
from bson import ObjectId

from app.database import Database

logger = logging.getLogger(__name__)


class PreferencesException(Exception):
    """Base exception for preferences operations"""
    pass


class BadRequestException(PreferencesException):
    """Raised when request is invalid"""
    pass


class NotFoundException(PreferencesException):
    """Raised when resource is not found"""
    pass


class PreferencesService:
    """Service for user preferences management"""

    # Valid values for preferences
    VALID_LANGUAGES = ["en", "fr", "es", "de", "pt", "yo"]
    VALID_TIME_FORMATS = ["12h", "24h"]
    VALID_FONT_SIZES = ["small", "medium", "large"]
    VALID_DATE_FORMATS = ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"]
    VALID_CURRENCIES = ["NGN", "USD", "EUR", "GBP", "JPY", "AUD", "CAD"]

    @staticmethod
    async def get_preferences(user_id: str, tenant_id: str) -> Dict:
        """
        Get user preferences
        
        Requirements: 8.1, 8.5, 17.1, 22.1
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            User preferences
        """
        db = Database.get_db()
        
        # Try to get from preferences collection
        prefs = db.user_preferences.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        if prefs:
            prefs["id"] = str(prefs.pop("_id"))
            return prefs
        
        # Return defaults if not found
        return {
            "user_id": user_id,
            "tenant_id": tenant_id,
            "language": "en",
            "timezone": "Africa/Lagos",
            "date_format": "DD/MM/YYYY",
            "time_format": "24h",
            "currency": "NGN",
            "font_size": "medium",
            "high_contrast": False,
            "reduce_motion": False,
            "screen_reader": False
        }

    @staticmethod
    async def update_preferences(
        user_id: str,
        tenant_id: str,
        preferences: Dict,
        request_info: Dict
    ) -> Dict:
        """
        Update user preferences
        
        Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 17.1, 17.2, 17.3, 17.4, 17.5, 22.1, 22.2, 22.6
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            preferences: Preferences to update
            request_info: Request metadata
            
        Returns:
            Updated preferences
            
        Raises:
            BadRequestException: If preferences are invalid
        """
        db = Database.get_db()
        
        # Validate preferences
        validated_prefs = PreferencesService._validate_preferences(preferences)
        
        # Get existing preferences
        existing = db.user_preferences.find_one({
            "user_id": user_id,
            "tenant_id": tenant_id
        })
        
        # Prepare update document
        update_doc = {
            **validated_prefs,
            "updated_at": datetime.utcnow()
        }
        
        if existing:
            # Update existing
            db.user_preferences.update_one(
                {"_id": existing["_id"]},
                {"$set": update_doc}
            )
            result = db.user_preferences.find_one({"_id": existing["_id"]})
        else:
            # Create new
            insert_doc = {
                "user_id": user_id,
                "tenant_id": tenant_id,
                **update_doc,
                "created_at": datetime.utcnow()
            }
            result = db.user_preferences.insert_one(insert_doc)
            result = db.user_preferences.find_one({"_id": result.inserted_id})
        
        # Log security event
        try:
            from app.services.audit_log_service import audit_log_service
            await audit_log_service.log_event(
                user_id=user_id,
                tenant_id=tenant_id,
                event_type="preferences_updated",
                request_info=request_info,
                success=True,
                details={"updated_fields": list(validated_prefs.keys())}
            )
        except Exception as e:
            logger.error(f"Failed to log audit event: {str(e)}")
        
        logger.info(f"Preferences updated for user {user_id}")
        
        result["id"] = str(result.pop("_id"))
        return result

    @staticmethod
    def _validate_preferences(preferences: Dict) -> Dict:
        """
        Validate preference values
        
        Args:
            preferences: Preferences to validate
            
        Returns:
            Validated preferences
            
        Raises:
            BadRequestException: If any preference is invalid
        """
        validated = {}
        
        # Validate language
        if "language" in preferences:
            if preferences["language"] not in PreferencesService.VALID_LANGUAGES:
                raise BadRequestException(
                    f"Invalid language. Valid options: {', '.join(PreferencesService.VALID_LANGUAGES)}"
                )
            validated["language"] = preferences["language"]
        
        # Validate timezone
        if "timezone" in preferences:
            # Basic validation - in production use pytz
            if not isinstance(preferences["timezone"], str) or len(preferences["timezone"]) < 3:
                raise BadRequestException("Invalid timezone format")
            validated["timezone"] = preferences["timezone"]
        
        # Validate date format
        if "date_format" in preferences:
            if preferences["date_format"] not in PreferencesService.VALID_DATE_FORMATS:
                raise BadRequestException(
                    f"Invalid date format. Valid options: {', '.join(PreferencesService.VALID_DATE_FORMATS)}"
                )
            validated["date_format"] = preferences["date_format"]
        
        # Validate time format
        if "time_format" in preferences:
            if preferences["time_format"] not in PreferencesService.VALID_TIME_FORMATS:
                raise BadRequestException(
                    f"Invalid time format. Valid options: {', '.join(PreferencesService.VALID_TIME_FORMATS)}"
                )
            validated["time_format"] = preferences["time_format"]
        
        # Validate currency
        if "currency" in preferences:
            if preferences["currency"] not in PreferencesService.VALID_CURRENCIES:
                raise BadRequestException(
                    f"Invalid currency. Valid options: {', '.join(PreferencesService.VALID_CURRENCIES)}"
                )
            validated["currency"] = preferences["currency"]
        
        # Validate font size
        if "font_size" in preferences:
            if preferences["font_size"] not in PreferencesService.VALID_FONT_SIZES:
                raise BadRequestException(
                    f"Invalid font size. Valid options: {', '.join(PreferencesService.VALID_FONT_SIZES)}"
                )
            validated["font_size"] = preferences["font_size"]
        
        # Validate accessibility settings
        if "high_contrast" in preferences:
            if not isinstance(preferences["high_contrast"], bool):
                raise BadRequestException("high_contrast must be a boolean")
            validated["high_contrast"] = preferences["high_contrast"]
        
        if "reduce_motion" in preferences:
            if not isinstance(preferences["reduce_motion"], bool):
                raise BadRequestException("reduce_motion must be a boolean")
            validated["reduce_motion"] = preferences["reduce_motion"]
        
        if "screen_reader" in preferences:
            if not isinstance(preferences["screen_reader"], bool):
                raise BadRequestException("screen_reader must be a boolean")
            validated["screen_reader"] = preferences["screen_reader"]
        
        return validated

    @staticmethod
    async def get_language_preference(user_id: str, tenant_id: str) -> str:
        """
        Get user's language preference
        
        Requirements: 8.1
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Language code
        """
        prefs = await PreferencesService.get_preferences(user_id, tenant_id)
        return prefs.get("language", "en")

    @staticmethod
    async def get_timezone_preference(user_id: str, tenant_id: str) -> str:
        """
        Get user's timezone preference
        
        Requirements: 8.4
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Timezone string
        """
        prefs = await PreferencesService.get_preferences(user_id, tenant_id)
        return prefs.get("timezone", "Africa/Lagos")

    @staticmethod
    async def get_currency_preference(user_id: str, tenant_id: str) -> str:
        """
        Get user's currency preference
        
        Requirements: 22.1, 22.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Currency code
        """
        prefs = await PreferencesService.get_preferences(user_id, tenant_id)
        return prefs.get("currency", "NGN")

    @staticmethod
    async def get_accessibility_settings(user_id: str, tenant_id: str) -> Dict:
        """
        Get user's accessibility settings
        
        Requirements: 17.1, 17.2, 17.3, 17.4, 17.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            
        Returns:
            Accessibility settings
        """
        prefs = await PreferencesService.get_preferences(user_id, tenant_id)
        
        return {
            "font_size": prefs.get("font_size", "medium"),
            "high_contrast": prefs.get("high_contrast", False),
            "reduce_motion": prefs.get("reduce_motion", False),
            "screen_reader": prefs.get("screen_reader", False)
        }

    @staticmethod
    async def update_language(
        user_id: str,
        tenant_id: str,
        language: str,
        request_info: Dict
    ) -> Dict:
        """
        Update language preference
        
        Requirements: 8.1, 8.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            language: Language code
            request_info: Request metadata
            
        Returns:
            Updated preferences
        """
        return await PreferencesService.update_preferences(
            user_id, tenant_id, {"language": language}, request_info
        )

    @staticmethod
    async def update_timezone(
        user_id: str,
        tenant_id: str,
        timezone: str,
        request_info: Dict
    ) -> Dict:
        """
        Update timezone preference
        
        Requirements: 8.4
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            timezone: Timezone string
            request_info: Request metadata
            
        Returns:
            Updated preferences
        """
        return await PreferencesService.update_preferences(
            user_id, tenant_id, {"timezone": timezone}, request_info
        )

    @staticmethod
    async def update_currency(
        user_id: str,
        tenant_id: str,
        currency: str,
        request_info: Dict
    ) -> Dict:
        """
        Update currency preference
        
        Requirements: 22.1, 22.2
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            currency: Currency code
            request_info: Request metadata
            
        Returns:
            Updated preferences
        """
        return await PreferencesService.update_preferences(
            user_id, tenant_id, {"currency": currency}, request_info
        )

    @staticmethod
    async def update_accessibility_settings(
        user_id: str,
        tenant_id: str,
        settings: Dict,
        request_info: Dict
    ) -> Dict:
        """
        Update accessibility settings
        
        Requirements: 17.1, 17.2, 17.3, 17.4, 17.5
        
        Args:
            user_id: User ID
            tenant_id: Tenant ID
            settings: Accessibility settings to update
            request_info: Request metadata
            
        Returns:
            Updated preferences
        """
        return await PreferencesService.update_preferences(
            user_id, tenant_id, settings, request_info
        )


# Create singleton instance
preferences_service = PreferencesService()
