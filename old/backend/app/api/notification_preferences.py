"""
Notification Preferences API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Optional
import logging

from app.services.notification_preferences_service import NotificationPreferencesService
from app.schemas.notification_preferences import (
    NotificationPreferences,
    NotificationPreferencesUpdate
)
from app.api.dependencies import get_current_user, get_current_tenant_id

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/notification-preferences", tags=["notification-preferences"])


@router.get("", response_model=Dict)
async def get_notification_preferences(
    current_user: Dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Get user's notification preferences
    
    Returns the current notification preferences for the authenticated user.
    If no preferences exist, returns default preferences.
    
    Args:
        current_user: Current authenticated user
        tenant_id: Current tenant ID
    
    Returns:
        Dict containing notification preferences
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        logger.info(f"Fetching notification preferences for user {user_id}")
        
        preferences = await NotificationPreferencesService.get_preferences(
            user_id=user_id,
            tenant_id=tenant_id
        )
        
        return preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching notification preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch notification preferences"
        )


@router.put("", response_model=Dict)
async def update_notification_preferences(
    update_data: NotificationPreferencesUpdate,
    current_user: Dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Update user's notification preferences
    
    Updates one or more notification preference settings for the authenticated user.
    
    Args:
        update_data: Notification preferences to update
        current_user: Current authenticated user
        tenant_id: Current tenant ID
    
    Returns:
        Dict containing updated notification preferences
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        logger.info(f"Updating notification preferences for user {user_id}")
        
        # Convert update data to dict, excluding None values
        preferences_dict = update_data.dict(exclude_none=True)
        
        updated_preferences = await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences=preferences_dict
        )
        
        logger.info(f"Successfully updated notification preferences for user {user_id}")
        
        return updated_preferences
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating notification preferences: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update notification preferences"
        )


@router.post("/opt-in", response_model=Dict)
async def opt_in_notifications(
    channel: str,
    current_user: Dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Opt in to a specific notification channel
    
    Enables notifications for a specific channel (email, sms, push, etc.)
    
    Args:
        channel: Notification channel to opt in to (email, sms, push)
        current_user: Current authenticated user
        tenant_id: Current tenant ID
    
    Returns:
        Dict containing updated notification preferences
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        # Validate channel
        valid_channels = ["email", "sms", "push", "in_app"]
        if channel not in valid_channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid channel. Must be one of: {', '.join(valid_channels)}"
            )
        
        logger.info(f"Opting in user {user_id} to {channel} notifications")
        
        # Build preferences dict based on channel
        preferences_dict = {f"{channel}_notifications": True}
        
        updated_preferences = await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences=preferences_dict
        )
        
        logger.info(f"User {user_id} opted in to {channel} notifications")
        
        return {
            "message": f"Successfully opted in to {channel} notifications",
            **updated_preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error opting in to notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to opt in to notifications"
        )


@router.post("/opt-out", response_model=Dict)
async def opt_out_notifications(
    channel: str,
    current_user: Dict = Depends(get_current_user),
    tenant_id: str = Depends(get_current_tenant_id)
) -> Dict:
    """
    Opt out of a specific notification channel
    
    Disables notifications for a specific channel (email, sms, push, etc.)
    
    Args:
        channel: Notification channel to opt out of (email, sms, push)
        current_user: Current authenticated user
        tenant_id: Current tenant ID
    
    Returns:
        Dict containing updated notification preferences
    """
    try:
        user_id = current_user.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not authenticated"
            )
        
        # Validate channel
        valid_channels = ["email", "sms", "push", "in_app"]
        if channel not in valid_channels:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid channel. Must be one of: {', '.join(valid_channels)}"
            )
        
        logger.info(f"Opting out user {user_id} from {channel} notifications")
        
        # Build preferences dict based on channel
        preferences_dict = {f"{channel}_notifications": False}
        
        updated_preferences = await NotificationPreferencesService.update_preferences(
            user_id=user_id,
            tenant_id=tenant_id,
            preferences=preferences_dict
        )
        
        logger.info(f"User {user_id} opted out of {channel} notifications")
        
        return {
            "message": f"Successfully opted out of {channel} notifications",
            **updated_preferences
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error opting out of notifications: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to opt out of notifications"
        )
