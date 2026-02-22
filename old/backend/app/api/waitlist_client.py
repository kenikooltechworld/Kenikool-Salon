"""
Waitlist client self-service API endpoints (public)
"""
from fastapi import APIRouter, HTTPException, Path
from app.services.waitlist_service import WaitlistService
from app.database import Database

router = APIRouter(prefix="/api/waitlist/client", tags=["waitlist-client"])

waitlist_service = WaitlistService()


@router.get("/{token}")
async def get_entry_by_token(token: str = Path(..., description="Access token")):
    """Get waitlist entry by access token (public endpoint)"""
    try:
        entry = waitlist_service.get_entry_by_token(token)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return entry
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{token}")
async def update_client_info(
    token: str = Path(..., description="Access token"),
    request: dict = None
):
    """Update client information via access token (public endpoint)"""
    try:
        if not request:
            raise ValueError("Request body is required")
        
        client_name = request.get("client_name")
        client_phone = request.get("client_phone")
        client_email = request.get("client_email")
        
        updated_entry = waitlist_service.update_client_info(
            token=token,
            client_name=client_name,
            client_phone=client_phone,
            client_email=client_email
        )
        
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return updated_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{token}/cancel")
async def cancel_by_token(token: str = Path(..., description="Access token")):
    """Cancel waitlist entry via access token (public endpoint)"""
    try:
        cancelled_entry = waitlist_service.cancel_by_token(token)
        
        if not cancelled_entry:
            raise HTTPException(status_code=404, detail="Entry not found")
        
        return cancelled_entry
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
