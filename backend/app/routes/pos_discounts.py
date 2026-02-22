"""API routes for POS discounts."""

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from app.context import get_tenant_id
from app.schemas.discount import (
    DiscountCreateRequest,
    DiscountUpdateRequest,
    DiscountValidateRequest,
    DiscountResponse,
    DiscountValidateResponse,
    DiscountListResponse,
)
from app.services.discount_service import DiscountService

router = APIRouter(prefix="/discounts", tags=["discounts"])


@router.post("", response_model=DiscountResponse)
async def create_discount(
    request: DiscountCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Create a new discount."""
    try:
        discount = DiscountService.create_discount(
            tenant_id=tenant_id,
            discount_code=request.discount_code,
            discount_type=request.discount_type,
            discount_value=request.discount_value,
            applicable_to=request.applicable_to,
            conditions=request.conditions,
            max_discount=request.max_discount,
            valid_from=None,  # Parse from request if needed
            valid_until=None,  # Parse from request if needed
            usage_limit=request.usage_limit,
        )

        return DiscountResponse(
            id=str(discount.id),
            discount_code=discount.discount_code,
            discount_type=discount.discount_type,
            discount_value=discount.discount_value,
            applicable_to=discount.applicable_to,
            conditions=discount.conditions,
            max_discount=discount.max_discount,
            active=discount.active,
            valid_from=discount.valid_from.isoformat() if discount.valid_from else None,
            valid_until=discount.valid_until.isoformat() if discount.valid_until else None,
            usage_count=discount.usage_count,
            usage_limit=discount.usage_limit,
            created_at=discount.created_at.isoformat(),
            updated_at=discount.updated_at.isoformat(),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=DiscountListResponse)
async def list_discounts(
    active_only: bool = Query(False),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """List discounts."""
    try:
        discounts, total = DiscountService.list_discounts(
            tenant_id=tenant_id,
            active_only=active_only,
            page=page,
            page_size=page_size,
        )

        return DiscountListResponse(
            discounts=[
                DiscountResponse(
                    id=str(d.id),
                    discount_code=d.discount_code,
                    discount_type=d.discount_type,
                    discount_value=d.discount_value,
                    applicable_to=d.applicable_to,
                    conditions=d.conditions,
                    max_discount=d.max_discount,
                    active=d.active,
                    valid_from=d.valid_from.isoformat() if d.valid_from else None,
                    valid_until=d.valid_until.isoformat() if d.valid_until else None,
                    usage_count=d.usage_count,
                    usage_limit=d.usage_limit,
                    created_at=d.created_at.isoformat(),
                    updated_at=d.updated_at.isoformat(),
                )
                for d in discounts
            ],
            total=total,
            page=page,
            page_size=page_size,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/validate", response_model=DiscountValidateResponse)
async def validate_discount(
    request: DiscountValidateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Validate a discount code."""
    try:
        is_valid, discount_amount, message = DiscountService.validate_discount_code(
            tenant_id=tenant_id,
            discount_code=request.discount_code,
            subtotal=request.subtotal,
        )

        return DiscountValidateResponse(
            valid=is_valid,
            discount_amount=discount_amount,
            message=message,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{discount_id}", response_model=DiscountResponse)
async def update_discount(
    discount_id: str,
    request: DiscountUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Update a discount."""
    try:
        discount = DiscountService.update_discount(
            tenant_id=tenant_id,
            discount_id=ObjectId(discount_id),
            discount_value=request.discount_value,
            active=request.active,
            valid_until=None,  # Parse from request if needed
            usage_limit=request.usage_limit,
        )

        if not discount:
            raise HTTPException(status_code=404, detail="Discount not found")

        return DiscountResponse(
            id=str(discount.id),
            discount_code=discount.discount_code,
            discount_type=discount.discount_type,
            discount_value=discount.discount_value,
            applicable_to=discount.applicable_to,
            conditions=discount.conditions,
            max_discount=discount.max_discount,
            active=discount.active,
            valid_from=discount.valid_from.isoformat() if discount.valid_from else None,
            valid_until=discount.valid_until.isoformat() if discount.valid_until else None,
            usage_count=discount.usage_count,
            usage_limit=discount.usage_limit,
            created_at=discount.created_at.isoformat(),
            updated_at=discount.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
