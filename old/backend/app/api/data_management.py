"""
Data Management API endpoints - Data export, account deletion, audit logs
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict

from app.schemas.settings import (
    DataExportRequest, DataExportResponse, AccountDeletionRequest,
    AccountDeletionResponse, SecurityLogEntry
)
from app.services.data_export_service import (
    data_export_service, BadRequestException as ExportBadRequest, NotFoundException as ExportNotFound
)
from app.services.account_deletion_service import (
    account_deletion_service, UnauthorizedException, BadRequestException, NotFoundException
)
from app.services.audit_log_service import audit_log_service
from app.api.dependencies import get_current_user, get_request_info

router = APIRouter(prefix="/api/users", tags=["data-management"])


# ==================== DATA EXPORT ENDPOINTS ====================

@router.post("/export", response_model=DataExportResponse, status_code=201)
async def request_data_export(
    request: DataExportRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Request data export
    
    Requirements: 5.1, 5.5
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        export_id = await data_export_service.request_export(
            user_id, tenant_id, request.dict(), request_info
        )
        
        return {
            "id": export_id,
            "status": "pending",
            "file_url": None,
            "file_size": None,
            "requested_at": __import__("datetime").datetime.utcnow(),
            "completed_at": None,
            "expires_at": None
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/exports", response_model=List[DataExportResponse])
async def list_exports(
    current_user: Dict = Depends(get_current_user)
):
    """
    List export history
    
    Requirements: 5.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        exports = await data_export_service.list_exports(user_id, tenant_id)
        return exports
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/exports/{export_id}", response_model=DataExportResponse)
async def get_export(
    export_id: str,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get export details
    
    Requirements: 5.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        export = await data_export_service.get_export(user_id, tenant_id, export_id)
        return export
    except ExportNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== ACCOUNT DELETION ENDPOINTS ====================

@router.post("/delete-account", response_model=AccountDeletionResponse, status_code=201)
async def request_account_deletion(
    request: AccountDeletionRequest,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Request account deletion
    
    Requirements: 6.1, 6.2, 6.3
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        result = await account_deletion_service.request_deletion(
            user_id, tenant_id, request.password, request_info
        )
        
        return result
    except UnauthorizedException as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/cancel-deletion", status_code=200)
async def cancel_account_deletion(
    cancellation_token: str,
    current_user: Dict = Depends(get_current_user),
    request_info: Dict = Depends(get_request_info)
):
    """
    Cancel account deletion
    
    Requirements: 6.3
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        await account_deletion_service.cancel_deletion(
            user_id, tenant_id, cancellation_token, request_info
        )
        
        return {"message": "Account deletion cancelled successfully"}
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/deletion-status", response_model=AccountDeletionResponse)
async def get_deletion_status(
    current_user: Dict = Depends(get_current_user)
):
    """
    Get account deletion status
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        status_info = await account_deletion_service.get_deletion_status(user_id, tenant_id)
        
        if not status_info:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No pending deletion")
        
        return status_info
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# ==================== AUDIT LOG ENDPOINTS ====================

@router.get("/audit-log", response_model=List[SecurityLogEntry])
async def get_audit_log(
    limit: int = 100,
    event_type: str = None,
    current_user: Dict = Depends(get_current_user)
):
    """
    Get audit log
    
    Requirements: 12.1, 12.4
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        logs = await audit_log_service.get_audit_log(user_id, tenant_id, limit, event_type)
        return logs
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/audit-log/export")
async def export_audit_log(
    current_user: Dict = Depends(get_current_user)
):
    """
    Export audit log as CSV
    
    Requirements: 12.6
    """
    try:
        user_id = current_user.get("user_id")
        tenant_id = current_user.get("tenant_id")
        
        csv_content = await audit_log_service.export_audit_log(user_id, tenant_id)
        
        return {
            "content": csv_content,
            "filename": f"audit_log_{user_id}.csv"
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
