"""Staff settings service for managing staff-specific preferences."""

from typing import Optional
from bson import ObjectId
from app.models.staff_settings import StaffSettings
from app.schemas.staff_settings import StaffSettingsCreate, StaffSettingsUpdate


class StaffSettingsService:
    """Service for managing staff settings."""

    @staticmethod
    def get_staff_settings(tenant_id: str, user_id: str) -> Optional[StaffSettings]:
        """Get staff settings for a user."""
        return StaffSettings.objects(
            tenant_id=ObjectId(tenant_id), user_id=ObjectId(user_id)
        ).first()

    @staticmethod
    def create_staff_settings(
        tenant_id: str, user_id: str, data: StaffSettingsCreate
    ) -> StaffSettings:
        """Create staff settings for a user."""
        settings = StaffSettings(
            tenant_id=ObjectId(tenant_id),
            user_id=ObjectId(user_id),
            **data.dict(),
        )
        settings.save()
        return settings

    @staticmethod
    def update_staff_settings(
        tenant_id: str, user_id: str, data: StaffSettingsUpdate
    ) -> Optional[StaffSettings]:
        """Update staff settings for a user."""
        settings = StaffSettingsService.get_staff_settings(tenant_id, user_id)
        if not settings:
            return None

        update_data = data.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(settings, key, value)

        settings.save()
        return settings

    @staticmethod
    def delete_staff_settings(tenant_id: str, user_id: str) -> bool:
        """Delete staff settings for a user."""
        settings = StaffSettingsService.get_staff_settings(tenant_id, user_id)
        if not settings:
            return False

        settings.delete()
        return True
