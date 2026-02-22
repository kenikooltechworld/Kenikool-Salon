"""
Service Variants API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional

from app.api.dependencies import get_current_user, get_db
from app.services.service_variant_service import ServiceVariantService

router = APIRouter(prefix="/api/variants", tags=["variants"])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_variant(
    service_id: str = Query(...),
    name: str = Query(...),
    price_adjustment: float = Query(...),
    price_adjustment_type: str = Query(...),
    duration_adjustment: int = Query(...),
    base_price: float = Query(...),
    base_duration: int = Query(...),
    description: Optional[str] = Query(None),
    is_active: bool = Query(True),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Create a service variant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        result = service.create_variant(
            service_id=service_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            price_adjustment=price_adjustment,
            price_adjustment_type=price_adjustment_type,
            duration_adjustment=duration_adjustment,
            is_active=is_active,
            base_price=base_price,
            base_duration=base_duration
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/service/{service_id}")
async def get_service_variants(
    service_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get all variants for a service"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        variants = service.get_variants(service_id, tenant_id)
        return {"service_id": service_id, "variants": variants}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/{variant_id}")
async def get_variant(
    variant_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Get a specific variant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        variant = service.get_variant(variant_id, tenant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        return variant
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.put("/{variant_id}")
async def update_variant(
    variant_id: str,
    name: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    price_adjustment: Optional[float] = Query(None),
    duration_adjustment: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Update a service variant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        result = service.update_variant(
            variant_id=variant_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
            price_adjustment=price_adjustment,
            duration_adjustment=duration_adjustment,
            is_active=is_active
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete("/{variant_id}")
async def delete_variant(
    variant_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Delete a service variant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        await service.delete_variant(variant_id, tenant_id)
        return {"message": "Variant deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate-price")
async def calculate_variant_price(
    variant_id: str = Query(...),
    base_price: float = Query(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Calculate final price for a variant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        variant = service.get_variant(variant_id, tenant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        
        # Calculate final price based on adjustment
        if variant.get("price_adjustment_type") == "fixed":
            final_price = base_price + variant.get("price_adjustment", 0)
        else:  # percentage
            final_price = base_price * (1 + variant.get("price_adjustment", 0) / 100)
        
        return {"variant_id": variant_id, "base_price": base_price, "final_price": final_price}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/calculate-duration")
async def calculate_variant_duration(
    variant_id: str = Query(...),
    base_duration: int = Query(...),
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    """Calculate final duration for a variant"""
    try:
        tenant_id = current_user.get("tenant_id")
        service = ServiceVariantService(db)
        variant = service.get_variant(variant_id, tenant_id)
        if not variant:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Variant not found")
        
        # Calculate final duration
        final_duration = base_duration + variant.get("duration_adjustment", 0)
        
        return {"variant_id": variant_id, "base_duration": base_duration, "final_duration": final_duration}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
