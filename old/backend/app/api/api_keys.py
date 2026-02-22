"""
API Keys API endpoints - API key management
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict
from datetime import datetime

from app.schemas.settings import APIKeyCreate, APIKeyResponse, APIKeyDisplayResponse
from app.services.api_key_service import (
    api_key_service, UnauthorizedException, BadRequestException, NotFoundException
)
from app.api.dependencies import get_current_user, get_request_info

router = APIRouter(prefix="/api/users", tags=["api-keys"])


@router.post("/api-keys", response_model=APIKeyDisplayResponse, status_code=201)
async def create_api_key(
    request: APIKeyCreate,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Create new API key
    
    Requirements: 4.1, 4.2, 4.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        plain_key, metadata = await api_key_service.create_api_key(
            user_id, tenant_id, request.name, request.expires_at, request.permissions
        )
        
        return metadata
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/api-keys", response_model=List[APIKeyResponse])
async def list_api_keys(
    current_user: Dict = Depends(get_current_user)
):
    """
    List API keys
    
    Requirements: 4.3, 4.5
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        keys = await api_key_service.list_api_keys(user_id, tenant_id)
        return keys
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/api-keys/{key_id}", response_model=APIKeyResponse)
async def get_api_key(
    key_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get API key details
    
    Requirements: 4.3
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        key = await api_key_service.get_api_key_by_id(user_id, tenant_id, key_id)
        return key
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.delete("/api-keys/{key_id}", status_code=200)
async def revoke_api_key(
    key_id: str,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Revoke API key
    
    Requirements: 4.4
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await api_key_service.revoke_api_key(user_id, tenant_id, key_id)
        
        return {"message": "API key revoked successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.patch("/api-keys/{key_id}", response_model=APIKeyResponse)
async def update_api_key(
    key_id: str,
    request: APIKeyCreate,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Update API key metadata
    
    Requirements: 4.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        key = await api_key_service.update_api_key_metadata(
            user_id, tenant_id, key_id,
            name=request.name,
            expires_at=request.expires_at,
            permissions=request.permissions
        )
        
        return key
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
