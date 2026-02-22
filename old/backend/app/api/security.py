"""
Security API endpoints - Password, 2FA, sessions, and security monitoring
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from datetime import datetime

from app.schemas.settings import (
    PasswordChangeRequest, TwoFactorSetupResponse, TwoFactorVerifyRequest,
    TwoFactorDisableRequest, SessionInfo, SecurityLogEntry, SecurityScoreResponse
)
from app.services.security_service import (
    security_service, UnauthorizedException, BadRequestException, NotFoundException
)
from app.api.dependencies import get_current_user, get_request_info

router = APIRouter(prefix="/api/users", tags=["security"])


@router.post("/change-password", status_code=200)
async def change_password(
    request: PasswordChangeRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Change user password
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await security_service.change_password(
            user_id, tenant_id,
            request.current_password,
            request.new_password,
            request_info
        )
        
        return {"message": "Password changed successfully"}
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/2fa/setup", response_model=TwoFactorSetupResponse)
async def setup_2fa(
    current_user: Dict = Depends(get_current_user)
):
    """
    Initialize 2FA setup
    
    Requirements: 2.1, 2.2, 2.3
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        result = await security_service.setup_2fa(user_id, tenant_id)
        return result
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/2fa/verify", status_code=200)
async def verify_2fa(
    request: TwoFactorVerifyRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Verify and enable 2FA
    
    Requirements: 2.1, 2.3, 2.5, 2.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await security_service.verify_and_enable_2fa(
            user_id, tenant_id, request.code, request_info
        )
        
        return {"message": "2FA enabled successfully"}
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/2fa", status_code=200)
async def disable_2fa(
    request: TwoFactorDisableRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Disable 2FA
    
    Requirements: 2.5, 2.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await security_service.disable_2fa(
            user_id, tenant_id, request.password, request.code, request_info
        )
        
        return {"message": "2FA disabled successfully"}
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/sessions", response_model=List[SessionInfo])
async def get_sessions(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get active sessions
    
    Requirements: 3.2
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        current_session_id = current_user.get("session_id")
        
        sessions = await security_service.get_active_sessions(user_id, tenant_id)
        
        # Mark current session
        for session in sessions:
            session["is_current"] = session["id"] == current_session_id
        
        return sessions
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/sessions/{session_id}", status_code=200)
async def revoke_session(
    session_id: str,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Revoke specific session
    
    Requirements: 3.3, 3.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await security_service.revoke_session(user_id, tenant_id, session_id)
        
        return {"message": "Session revoked successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/sessions", status_code=200)
async def revoke_all_other_sessions(
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Revoke all other sessions
    
    Requirements: 3.4, 3.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        current_session_id = current_user.get("session_id")
        
        count = await security_service.revoke_all_other_sessions(
            user_id, tenant_id, current_session_id
        )
        
        return {"message": f"Revoked {count} sessions"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/security-score", response_model=SecurityScoreResponse)
async def get_security_score(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get security score
    
    Requirements: 11.1, 11.2, 11.3, 11.4
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        score = await security_service.calculate_security_score(user_id, tenant_id)
        
        # Determine level
        if score >= 75:
            level = "high"
        elif score >= 50:
            level = "medium"
        else:
            level = "low"
        
        # Generate recommendations
        recommendations = []
        if score < 30:
            recommendations.append("Enable two-factor authentication")
        if score < 50:
            recommendations.append("Update your password")
        if score < 75:
            recommendations.append("Verify your email address")
        
        return {
            "score": score,
            "level": level,
            "recommendations": recommendations,
            "last_updated": datetime.utcnow()
        }
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/login-activity", response_model=List[SecurityLogEntry])
async def get_login_activity(
    limit: int = 50,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get login activity
    
    Requirements: 23.2
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        logs = await security_service.get_login_activity(user_id, tenant_id, limit)
        return logs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
