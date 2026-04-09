"""Gift card routes - Admin/Owner management"""
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional
from bson import ObjectId

from app.middleware.tenant_context import get_tenant_id
from app.services.gift_card_service import GiftCardService
from app.schemas.gift_card import (
    GiftCardResponse,
    GiftCardListResponse,
    GiftCardTransactionResponse
)


router = APIRouter(prefix="/gift-cards", tags=["Gift Cards - Admin"])


@router.get("", response_model=GiftCardListResponse)
async def list_gift_cards(
    request: Request,
    status: Optional[str] = Query(None, pattern="^(active|redeemed|expired|cancelled)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100)
):
    """List all gift cards (admin only)"""
    tenant_id = get_tenant_id(request)
    
    skip = (page - 1) * page_size
    gift_cards, total = await GiftCardService.list_gift_cards(
        tenant_id=tenant_id,
        status=status,
        skip=skip,
        limit=page_size
    )
    
    return GiftCardListResponse(
        gift_cards=[
            GiftCardResponse(
                id=str(gc.id),
                code=gc.code,
                initial_amount=float(gc.initial_amount.to_decimal()),
                current_balance=float(gc.current_balance.to_decimal()),
                currency=gc.currency,
                purchased_by_name=gc.purchased_by_name,
                purchased_by_email=gc.purchased_by_email,
                purchase_date=gc.purchase_date,
                recipient_name=gc.recipient_name,
                recipient_email=gc.recipient_email,
                status=gc.status,
                expiry_date=gc.expiry_date,
                is_active=gc.is_active,
                delivery_method=gc.delivery_method,
                is_delivered=gc.is_delivered,
                delivered_at=gc.delivered_at,
                personal_message=gc.personal_message,
                created_at=gc.created_at,
                updated_at=gc.updated_at
            )
            for gc in gift_cards
        ],
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{gift_card_id}", response_model=GiftCardResponse)
async def get_gift_card(
    request: Request,
    gift_card_id: str
):
    """Get gift card details (admin only)"""
    tenant_id = get_tenant_id(request)
    
    from app.models.gift_card import GiftCard
    gift_card = await GiftCard.find_one({
        "tenant_id": tenant_id,
        "_id": ObjectId(gift_card_id)
    })
    
    if not gift_card:
        raise HTTPException(status_code=404, detail="Gift card not found")
    
    return GiftCardResponse(
        id=str(gift_card.id),
        code=gift_card.code,
        initial_amount=float(gift_card.initial_amount.to_decimal()),
        current_balance=float(gift_card.current_balance.to_decimal()),
        currency=gift_card.currency,
        purchased_by_name=gift_card.purchased_by_name,
        purchased_by_email=gift_card.purchased_by_email,
        purchase_date=gift_card.purchase_date,
        recipient_name=gift_card.recipient_name,
        recipient_email=gift_card.recipient_email,
        status=gift_card.status,
        expiry_date=gift_card.expiry_date,
        is_active=gift_card.is_active,
        delivery_method=gift_card.delivery_method,
        is_delivered=gift_card.is_delivered,
        delivered_at=gift_card.delivered_at,
        personal_message=gift_card.personal_message,
        created_at=gift_card.created_at,
        updated_at=gift_card.updated_at
    )


@router.get("/{gift_card_id}/transactions", response_model=list[GiftCardTransactionResponse])
async def get_gift_card_transactions(
    request: Request,
    gift_card_id: str
):
    """Get transaction history for a gift card (admin only)"""
    tenant_id = get_tenant_id(request)
    
    transactions = await GiftCardService.get_gift_card_transactions(
        tenant_id=tenant_id,
        gift_card_id=ObjectId(gift_card_id)
    )
    
    return [
        GiftCardTransactionResponse(
            id=str(t.id),
            gift_card_code=t.gift_card_code,
            transaction_type=t.transaction_type,
            amount=float(t.amount.to_decimal()),
            balance_before=float(t.balance_before.to_decimal()),
            balance_after=float(t.balance_after.to_decimal()),
            description=t.description,
            created_at=t.created_at
        )
        for t in transactions
    ]


@router.post("/{gift_card_id}/cancel")
async def cancel_gift_card(
    request: Request,
    gift_card_id: str,
    reason: str = Query(..., min_length=10, max_length=500)
):
    """Cancel a gift card (admin only)"""
    tenant_id = get_tenant_id(request)
    
    try:
        gift_card = await GiftCardService.cancel_gift_card(
            tenant_id=tenant_id,
            gift_card_id=ObjectId(gift_card_id),
            reason=reason
        )
        
        return {
            "message": "Gift card cancelled successfully",
            "gift_card_code": gift_card.code
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
