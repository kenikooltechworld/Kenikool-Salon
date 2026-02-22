"""
POS Package API endpoints - Package credit redemption at point of sale
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime

from app.schemas.service_credit import (
    ServiceCreditResponse,
    CreditBalanceResponse,
    RedemptionTransactionResponse
)
from app.services.pos_package_service import POSPackageService
from app.api.dependencies import get_current_user, get_db

router = APIRouter(prefix="/api/pos/packages", tags=["pos-packages"])


@router.get("/clients/{client_id}/packages")
async def get_client_packages_at_pos(
    client_id: str,
    include_expired: bool = False,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all active packages for a client at POS"""
    try:
        service = POSPackageService(db)
        
        packages = await service.get_client_packages(
            client_id=client_id,
            include_expired=include_expired
        )
        
        return {
            "packages": packages,
            "total": len(packages)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/clients/{client_id}/services/{service_id}/packages")
async def get_packages_with_service_credits(
    client_id: str,
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get packages that have available credits for a specific service"""
    try:
        service = POSPackageService(db)
        
        packages = await service.check_package_credits_for_service(
            client_id=client_id,
            service_id=service_id
        )
        
        return {
            "packages": packages,
            "total": len(packages)
        }
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/validate-redemption")
async def validate_package_redemption(
    purchase_id: str,
    service_id: str,
    client_id: str,
    stylist_id: Optional[str] = None,
    location_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Validate if a package credit can be redeemed at POS"""
    try:
        service = POSPackageService(db)
        
        result = await service.validate_pos_redemption(
            purchase_id=purchase_id,
            service_id=service_id,
            client_id=client_id,
            stylist_id=stylist_id,
            location_id=location_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.post("/redeem-credit", response_model=RedemptionTransactionResponse, status_code=status.HTTP_201_CREATED)
async def redeem_package_credit_at_pos(
    purchase_id: str,
    service_id: str,
    client_id: str,
    pos_transaction_id: str,
    quantity: int = 1,
    stylist_id: Optional[str] = None,
    location_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Redeem a package credit at POS"""
    try:
        service = POSPackageService(db)
        
        result = await service.redeem_package_credit_at_pos(
            purchase_id=purchase_id,
            service_id=service_id,
            client_id=client_id,
            staff_id=current_user.get("user_id"),
            pos_transaction_id=pos_transaction_id,
            quantity=quantity,
            stylist_id=stylist_id,
            location_id=location_id
        )
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


@router.get("/purchases/{purchase_id}/summary")
async def get_package_redemption_summary(
    purchase_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get summary of package redemptions for display at POS"""
    try:
        service = POSPackageService(db)
        
        result = await service.get_package_redemption_summary(purchase_id)
        
        return result
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
