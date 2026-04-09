"""Routes for staff settings management."""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from app.context import get_tenant_id
from app.services.staff_settings_service import StaffSettingsService
from app.schemas.staff_settings import (
    StaffSettingsCreate,
    StaffSettingsUpdate,
    StaffSettingsResponse,
)
from app.routes.auth import get_current_user_dependency

router = APIRouter(prefix="/staff/settings", tags=["staff-settings"])


@router.get("", response_model=StaffSettingsResponse)
async def get_staff_settings(
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Get current staff member's settings."""
    from app.models.user import User
    from bson import ObjectId
    
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("id")
    
    settings = StaffSettingsService.get_staff_settings(
        tenant_id, user_id
    )

    if not settings:
        # Auto-create settings if they don't exist
        try:
            user = User.objects(id=ObjectId(user_id), tenant_id=ObjectId(tenant_id)).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )
            
            # Create default settings
            from app.schemas.staff_settings import StaffSettingsCreate
            default_settings = StaffSettingsCreate(
                first_name=user.first_name,
                last_name=user.last_name,
                phone=user.phone or "",
                email_bookings=True,
                email_reminders=True,
                email_messages=True,
                sms_bookings=False,
                sms_reminders=False,
                push_bookings=True,
                push_reminders=True,
            )
            settings = StaffSettingsService.create_staff_settings(
                tenant_id, user_id, default_settings
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create staff settings: {str(e)}",
            )

    return settings.to_dict()


@router.put("", response_model=StaffSettingsResponse)
async def update_staff_settings(
    data: StaffSettingsUpdate,
    request: Request,
    response: Response,
    current_user: dict = Depends(get_current_user_dependency),
):
    """Update current staff member's settings."""
    tenant_id = current_user.get("tenant_id")
    user_id = current_user.get("id")
    
    settings = StaffSettingsService.update_staff_settings(
        tenant_id, user_id, data
    )

    if not settings:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Staff settings not found",
        )

    return settings.to_dict()
