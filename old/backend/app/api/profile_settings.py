"""
Profile Settings API endpoints - Profile picture, email change, phone verification
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from typing import Dict

from app.schemas.settings import (
    EmailChangeRequest, PhoneVerificationRequest, PhoneVerificationConfirmRequest
)
from app.services.profile_enhancement_service import (
    profile_enhancement_service, BadRequestException, NotFoundException, ConflictException
)
from app.api.dependencies import get_current_user, get_request_info

router = APIRouter(prefix="/api/users", tags=["profile"])


# ==================== PROFILE PICTURE ENDPOINTS ====================

@router.post("/profile-picture", status_code=201)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Upload profile picture
    
    Requirements: 13.1, 13.2, 13.4, 13.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        # Read file content
        content = await file.read()
        
        result = await profile_enhancement_service.upload_profile_picture(
            user_id, tenant_id, content, file.filename, request_info
        )
        
        return result
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/profile-picture", status_code=200)
async def delete_profile_picture(
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Delete profile picture
    
    Requirements: 13.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await profile_enhancement_service.delete_profile_picture(user_id, tenant_id, request_info)
        
        return {"message": "Profile picture deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== EMAIL CHANGE ENDPOINTS ====================

@router.post("/change-email", status_code=200)
async def initiate_email_change(
    request: EmailChangeRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Initiate email change
    
    Requirements: 9.1, 9.2, 9.4, 9.5
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        token = await profile_enhancement_service.initiate_email_change(
            user_id, tenant_id, request.new_email, request_info
        )
        
        return {
            "message": "Verification email sent",
            "verification_token": token
        }
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/change-email/verify", status_code=200)
async def verify_email_change(
    token: str,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Verify email change
    
    Requirements: 9.2, 9.3, 9.5
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await profile_enhancement_service.verify_email_change(
            user_id, tenant_id, token, request_info
        )
        
        return {"message": "Email changed successfully"}
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== PHONE VERIFICATION ENDPOINTS ====================

@router.post("/verify-phone", status_code=200)
async def initiate_phone_verification(
    request: PhoneVerificationRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Send phone verification SMS
    
    Requirements: 10.1, 10.5
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await profile_enhancement_service.initiate_phone_verification(
            user_id, tenant_id, request.phone_number, request_info
        )
        
        return {"message": "Verification code sent to phone"}
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/verify-phone/confirm", status_code=200)
async def confirm_phone_verification(
    request: PhoneVerificationConfirmRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Confirm phone verification
    
    Requirements: 10.2, 10.3, 10.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await profile_enhancement_service.verify_phone(
            user_id, tenant_id, request.code, request_info
        )
        
        return {"message": "Phone verified successfully"}
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
