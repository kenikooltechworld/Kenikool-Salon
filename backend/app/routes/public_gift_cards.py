"""Public gift card routes - Customer-facing"""
from fastapi import APIRouter, Depends, HTTPException, Request
from bson import ObjectId

from app.middleware.tenant_context import get_tenant_id
from app.services.gift_card_service import GiftCardService
from app.schemas.gift_card import (
    GiftCardPurchaseRequest,
    GiftCardPurchaseResponse,
    GiftCardBalanceCheck,
    GiftCardBalanceResponse,
    GiftCardRedemptionRequest,
    GiftCardResponse
)


router = APIRouter(prefix="/public/gift-cards", tags=["Gift Cards - Public"])


@router.post("/purchase", response_model=GiftCardPurchaseResponse)
async def purchase_gift_card(
    request: Request,
    purchase_data: GiftCardPurchaseRequest
):
    """Purchase a gift card (public endpoint)"""
    tenant_id = get_tenant_id(request)
    
    try:
        gift_card = await GiftCardService.purchase_gift_card(
            tenant_id=tenant_id,
            purchase_data=purchase_data
        )
        
        # TODO: If payment_method is paystack, create payment and return payment_url
        payment_url = None
        if purchase_data.payment_method == "paystack":
            # Integrate with PaystackService to create payment
            # payment_url = await PaystackService.initialize_payment(...)
            pass
        
        return GiftCardPurchaseResponse(
            gift_card=GiftCardResponse(
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
            ),
            payment_url=payment_url,
            message="Gift card purchased successfully. Delivery will be sent shortly."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/check-balance", response_model=GiftCardBalanceResponse)
async def check_gift_card_balance(
    request: Request,
    balance_check: GiftCardBalanceCheck
):
    """Check gift card balance (public endpoint)"""
    tenant_id = get_tenant_id(request)
    
    gift_card = await GiftCardService.check_balance(
        tenant_id=tenant_id,
        code=balance_check.code
    )
    
    if not gift_card:
        raise HTTPException(status_code=404, detail="Gift card not found")
    
    return GiftCardBalanceResponse(
        code=gift_card.code,
        current_balance=float(gift_card.current_balance.to_decimal()),
        currency=gift_card.currency,
        status=gift_card.status,
        expiry_date=gift_card.expiry_date,
        is_active=gift_card.is_active
    )


@router.post("/redeem")
async def redeem_gift_card(
    request: Request,
    redemption_data: GiftCardRedemptionRequest
):
    """Redeem a gift card (public endpoint)"""
    tenant_id = get_tenant_id(request)
    
    try:
        booking_id = ObjectId(redemption_data.booking_id) if redemption_data.booking_id else None
        
        result = await GiftCardService.redeem_gift_card(
            tenant_id=tenant_id,
            redemption_data=redemption_data,
            booking_id=booking_id
        )
        
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to redeem gift card")
