"""
POS API endpoints
"""
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

from app.services.pos_service import POSService
from app.services.membership_service import MembershipService
from app.api.dependencies import get_current_user, get_tenant_id
from app.database import Database

router = APIRouter(prefix="/api/pos", tags=["pos"])


class CreateGiftCardRequest(BaseModel):
    amount: float
    card_type: str = "physical"
    recipient_name: Optional[str] = None
    recipient_email: Optional[str] = None
    message: Optional[str] = None
    expiration_months: int = 12
    design_theme: str = "default"
    activation_required: bool = False
    pin: Optional[str] = None


class SendDigitalGiftCardRequest(BaseModel):
    card_id: str
    recipient_email: str
    recipient_name: Optional[str] = None
    message: Optional[str] = None
    scheduled_delivery: Optional[datetime] = None


class ResendGiftCardEmailRequest(BaseModel):
    card_id: str
    new_recipient_email: Optional[str] = None


class UpdateDeliveryStatusRequest(BaseModel):
    card_id: str
    status: str


class ApplyMembershipDiscountRequest(BaseModel):
    client_id: str
    items: List[dict]  # List of items with type, price, quantity
    promo_code: Optional[str] = None


@router.post("/gift-cards")
async def create_gift_card(
    request: CreateGiftCardRequest,
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new gift card"""
    try:
        gift_card = POSService.create_gift_card(
            tenant_id=tenant_id,
            amount=request.amount,
            card_type=request.card_type,
            recipient_name=request.recipient_name,
            recipient_email=request.recipient_email,
            message=request.message,
            expiration_months=request.expiration_months,
            created_by=current_user.get("id"),
            design_theme=request.design_theme,
            activation_required=request.activation_required,
            pin=request.pin
        )
        return gift_card
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/gift-cards/{card_id}/send")
async def send_digital_gift_card(
    card_id: str,
    request: SendDigitalGiftCardRequest,
    background_tasks: BackgroundTasks,
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send digital gift card via email"""
    try:
        # If scheduled, add to background tasks
        if request.scheduled_delivery:
            background_tasks.add_task(
                POSService.send_digital_gift_card,
                tenant_id=tenant_id,
                card_id=card_id,
                recipient_email=request.recipient_email,
                recipient_name=request.recipient_name,
                message=request.message,
                scheduled_delivery=request.scheduled_delivery
            )
            return {"success": True, "status": "scheduled"}
        
        # Send immediately
        result = await POSService.send_digital_gift_card(
            tenant_id=tenant_id,
            card_id=card_id,
            recipient_email=request.recipient_email,
            recipient_name=request.recipient_name,
            message=request.message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/gift-cards/{card_id}/resend")
async def resend_gift_card_email(
    card_id: str,
    request: ResendGiftCardEmailRequest,
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Resend gift card email"""
    try:
        result = await POSService.resend_gift_card_email(
            tenant_id=tenant_id,
            card_id=card_id,
            new_recipient_email=request.new_recipient_email
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/gift-cards/{card_id}/delivery-status")
async def update_delivery_status(
    card_id: str,
    request: UpdateDeliveryStatusRequest,
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Update gift card delivery status"""
    try:
        result = await POSService.update_delivery_status(
            tenant_id=tenant_id,
            card_id=card_id,
            status=request.status
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gift-cards/{card_id}/balance")
async def get_gift_card_balance(
    card_id: str,
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get gift card balance"""
    try:
        from bson import ObjectId
        from app.database import Database
        
        db = Database.get_db()
        gift_card = db.gift_cards.find_one({
            "_id": ObjectId(card_id),
            "tenant_id": tenant_id
        })
        
        if not gift_card:
            raise HTTPException(status_code=404, detail="Gift card not found")
        
        return {
            "card_number": gift_card.get("card_number"),
            "balance": gift_card.get("balance"),
            "status": gift_card.get("status"),
            "expires_at": gift_card.get("expires_at")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class BulkCreateGiftCardsRequest(BaseModel):
    csv_content: str
    amount: float
    design_theme: str = "default"
    expiration_months: int = 12


@router.post("/gift-cards/bulk")
async def bulk_create_gift_cards(
    request: BulkCreateGiftCardsRequest,
    current_user = Depends(get_current_user),
    tenant_id: str = Depends(get_tenant_id)
):
    """Bulk create gift cards from CSV"""
    try:
        from app.services.gift_card_bulk_operations_service import GiftCardBulkOperationsService
        
        result = await GiftCardBulkOperationsService.bulk_create(
            tenant_id=tenant_id,
            csv_content=request.csv_content,
            created_by=current_user.get("id"),
            design_theme=request.design_theme,
            expiration_months=request.expiration_months
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gift-cards/analytics")
async def get_gift_card_analytics(
    tenant_id: str = Depends(get_tenant_id),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    card_type: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Get gift card analytics"""
    try:
        from app.services.gift_card_analytics_service import GiftCardAnalyticsService
        from datetime import datetime
        
        date_from_dt = None
        date_to_dt = None
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
        
        analytics = GiftCardAnalyticsService.get_analytics(
            tenant_id=tenant_id,
            date_from=date_from_dt,
            date_to=date_to_dt,
            card_type=card_type
        )
        return analytics
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gift-cards/analytics/export")
async def export_gift_card_analytics(
    tenant_id: str = Depends(get_tenant_id),
    format: str = "csv",
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Export gift card analytics"""
    try:
        from app.services.gift_card_analytics_service import GiftCardAnalyticsService
        from datetime import datetime
        from fastapi.responses import StreamingResponse
        import io
        
        date_from_dt = None
        date_to_dt = None
        
        if date_from:
            date_from_dt = datetime.fromisoformat(date_from)
        if date_to:
            date_to_dt = datetime.fromisoformat(date_to)
        
        if format == "csv":
            csv_content = GiftCardAnalyticsService.export_csv(
                tenant_id=tenant_id,
                date_from=date_from_dt,
                date_to=date_to_dt
            )
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=analytics.csv"}
            )
        elif format == "pdf":
            pdf_content = GiftCardAnalyticsService.export_pdf(
                tenant_id=tenant_id,
                date_from=date_from_dt,
                date_to=date_to_dt
            )
            return StreamingResponse(
                iter([pdf_content]),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=analytics.pdf"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/gift-cards/export")
async def export_gift_cards(
    tenant_id: str = Depends(get_tenant_id),
    format: str = "csv",
    status: Optional[str] = None,
    card_type: Optional[str] = None,
    current_user = Depends(get_current_user)
):
    """Export gift cards list"""
    try:
        from app.services.gift_card_export_service import GiftCardExportService
        from fastapi.responses import StreamingResponse
        
        if format == "csv":
            csv_content = GiftCardExportService.export_csv(
                tenant_id=tenant_id,
                status=status,
                card_type=card_type
            )
            return StreamingResponse(
                iter([csv_content]),
                media_type="text/csv",
                headers={"Content-Disposition": "attachment; filename=gift-cards.csv"}
            )
        elif format == "pdf":
            pdf_content = GiftCardExportService.export_pdf(
                tenant_id=tenant_id,
                status=status,
                card_type=card_type
            )
            return StreamingResponse(
                iter([pdf_content]),
                media_type="application/pdf",
                headers={"Content-Disposition": "attachment; filename=gift-cards.pdf"}
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid format")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/apply-membership-discount")
async def apply_membership_discount(
    request: ApplyMembershipDiscountRequest,
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user)
):
    """
    Apply membership discount to POS transaction items.
    
    Only applies discount to services, not products.
    Does not combine with promo codes.
    """
    try:
        db = Database.get_db()
        membership_service = MembershipService(db)
        
        result = await membership_service.apply_membership_discount(
            tenant_id=tenant_id,
            client_id=request.client_id,
            items=request.items,
            promo_code=request.promo_code
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/client-discount/{client_id}")
async def get_client_discount(
    client_id: str,
    tenant_id: str = Depends(get_tenant_id),
    current_user = Depends(get_current_user)
):
    """
    Get active membership discount for a client.
    
    Returns discount information if client has an active subscription.
    """
    try:
        db = Database.get_db()
        membership_service = MembershipService(db)
        
        result = await membership_service.get_client_discount(
            tenant_id=tenant_id,
            client_id=client_id
        )
        
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
