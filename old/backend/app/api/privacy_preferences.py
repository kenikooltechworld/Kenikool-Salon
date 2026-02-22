"""
Privacy and Preferences API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict

from app.schemas.settings import PrivacySettings, UserPreferences
from app.services.privacy_service import privacy_service, BadRequestException
from app.services.preferences_service import preferences_service
from app.api.dependencies import get_current_user, get_request_info

router = APIRouter(prefix="/api/users", tags=["privacy-preferences"])


# ==================== PRIVACY ENDPOINTS ====================

@router.get("/privacy", response_model=PrivacySettings)
async def get_privacy_settings(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get privacy settings
    
    Requirements: 7.1
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        settings = await privacy_service.get_privacy_settings(user_id, tenant_id)
        return settings
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/privacy", response_model=PrivacySettings)
async def update_privacy_settings(
    request: PrivacySettings,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Update privacy settings
    
    Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        settings = await privacy_service.update_privacy_settings(
            user_id, tenant_id, request.dict(exclude_unset=True), request_info
        )
        
        return settings
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== PREFERENCES ENDPOINTS ====================

@router.get("/preferences", response_model=UserPreferences)
async def get_preferences(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get user preferences
    
    Requirements: 8.1, 8.5, 17.1, 22.1
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        prefs = await preferences_service.get_preferences(user_id, tenant_id)
        return prefs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/preferences", response_model=UserPreferences)
async def update_preferences(
    request: UserPreferences,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Update user preferences
    
    Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 17.1, 17.2, 17.3, 17.4, 17.5, 22.1, 22.2, 22.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        prefs = await preferences_service.update_preferences(
            user_id, tenant_id, request.dict(exclude_unset=True), request_info
        )
        
        return prefs
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
