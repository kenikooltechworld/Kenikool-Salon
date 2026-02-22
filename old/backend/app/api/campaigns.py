"""
Campaigns API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
import logging

from app.api.dependencies import get_tenant_id
from app.services.campaign_service import CampaignService
from app.services.sms_credit_service import SMSCreditService
from app.models.sms_credit import SMSCreditPurchase

logger = logging.getLogger(__name__)

router = APIRouter(tags=["campaigns"])


# ============================================================================
# Campaign Endpoints
# ============================================================================

@router.post("/campaigns")
async def create_campaign(
    name: str,
    campaign_type: str,
    message_template: str,
    channels: List[str],
    target_segment: Optional[dict] = None,
    discount_code: Optional[str] = None,
    discount_value: Optional[float] = None,
    scheduled_at: Optional[str] = None,
    auto_send: bool = False,
    tenant_id: str = Depends(get_tenant_id)
):
    """Create a new campaign"""
    try:
        campaign = CampaignService.create_campaign(
            tenant_id=tenant_id,
            name=name,
            campaign_type=campaign_type,
            message_template=message_template,
            channels=channels,
            target_segment=target_segment,
            discount_code=discount_code,
            discount_value=discount_value,
            scheduled_at=scheduled_at,
            auto_send=auto_send
        )
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating campaign: {e}")
        raise HTTPException(status_code=500, detail="Error creating campaign")


@router.get("/campaigns")
async def list_campaigns(
    status: Optional[str] = Query(None),
    campaign_type: Optional[str] = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """List campaigns for tenant"""
    try:
        campaigns = CampaignService.list_campaigns(
            tenant_id=tenant_id,
            status=status,
            campaign_type=campaign_type,
            offset=offset,
            limit=limit
        )
        return {"campaigns": campaigns}
    except Exception as e:
        logger.error(f"Error listing campaigns: {e}")
        raise HTTPException(status_code=500, detail="Error listing campaigns")


@router.get("/campaigns/{campaign_id}")
async def get_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get campaign details"""
    try:
        campaign = CampaignService.get_campaign(campaign_id, tenant_id)
        return campaign
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting campaign: {e}")
        raise HTTPException(status_code=500, detail="Error getting campaign")


@router.post("/campaigns/{campaign_id}/send")
async def send_campaign(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Send campaign"""
    try:
        result = await CampaignService.send_campaign(campaign_id, tenant_id)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error sending campaign: {e}")
        raise HTTPException(status_code=500, detail="Error sending campaign")


@router.get("/campaigns/{campaign_id}/analytics")
async def get_campaign_analytics(
    campaign_id: str,
    tenant_id: str = Depends(get_tenant_id)
):
    """Get campaign analytics"""
    try:
        analytics = CampaignService.get_campaign_analytics(campaign_id, tenant_id)
        return analytics
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting campaign analytics: {e}")
        raise HTTPException(status_code=500, detail="Error getting campaign analytics")


# ============================================================================
# SMS Credit Endpoints
# ============================================================================

@router.get("/sms-credits/balance")
async def get_sms_balance(tenant_id: str = Depends(get_tenant_id)):
    """Get SMS credit balance"""
    try:
        balance = SMSCreditService.get_balance(tenant_id)
        return balance
    except Exception as e:
        logger.error(f"Error getting SMS balance: {e}")
        raise HTTPException(status_code=500, detail="Error getting SMS balance")


@router.get("/sms-credits/history")
async def get_sms_history(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    tenant_id: str = Depends(get_tenant_id)
):
    """Get SMS credit transaction history"""
    try:
        history = SMSCreditService.get_transaction_history(tenant_id, offset, limit)
        return {"transactions": history}
    except Exception as e:
        logger.error(f"Error getting SMS history: {e}")
        raise HTTPException(status_code=500, detail="Error getting SMS history")


@router.post("/sms-credits/purchase")
async def purchase_sms_credits(
    purchase: SMSCreditPurchase,
    tenant_id: str = Depends(get_tenant_id)
):
    """Purchase SMS credits"""
    try:
        # In production, integrate with payment provider
        # For now, just add credits
        transaction = SMSCreditService.add_credits(
            tenant_id=tenant_id,
            amount=purchase.amount,
            reason="purchase",
            reference_id=purchase.reference_id
        )
        return transaction
    except Exception as e:
        logger.error(f"Error purchasing SMS credits: {e}")
        raise HTTPException(status_code=500, detail="Error purchasing SMS credits")


@router.put("/sms-credits/threshold")
async def set_low_balance_threshold(
    threshold: int,
    tenant_id: str = Depends(get_tenant_id)
):
    """Set low balance alert threshold"""
    try:
        result = SMSCreditService.set_low_balance_threshold(tenant_id, threshold)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting threshold: {e}")
        raise HTTPException(status_code=500, detail="Error setting threshold")


@router.post("/bookings/{booking_id}/send-confirmation")
async def send_booking_confirmation(
    booking_id: str,
    channel: str = Query("sms", enum=["sms", "whatsapp"]),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send booking confirmation message"""
    from app.services.booking_notification_service import BookingNotificationService
    
    try:
        result = await BookingNotificationService.send_booking_confirmation(
            booking_id=booking_id,
            tenant_id=tenant_id,
            channel=channel
        )
        if result:
            return {"success": True, "message": f"Booking confirmation sent via {channel}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send booking confirmation")
    except Exception as e:
        logger.error(f"Error sending booking confirmation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/bookings/{booking_id}/send-reminder")
async def send_booking_reminder(
    booking_id: str,
    hours_before: int = Query(24, ge=1, le=168),
    channel: str = Query("sms", enum=["sms", "whatsapp"]),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send booking reminder message"""
    from app.services.booking_notification_service import BookingNotificationService
    
    try:
        result = await BookingNotificationService.send_booking_reminder(
            booking_id=booking_id,
            tenant_id=tenant_id,
            hours_before=hours_before,
            channel=channel
        )
        if result:
            return {"success": True, "message": f"Booking reminder sent via {channel}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send booking reminder")
    except Exception as e:
        logger.error(f"Error sending booking reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clients/{client_id}/send-review-request")
async def send_review_request(
    client_id: str,
    booking_id: Optional[str] = Query(None),
    channel: str = Query("sms", enum=["sms", "whatsapp"]),
    tenant_id: str = Depends(get_tenant_id)
):
    """Send review request message"""
    from app.services.booking_notification_service import BookingNotificationService
    
    try:
        result = await BookingNotificationService.send_review_request(
            client_id=client_id,
            tenant_id=tenant_id,
            booking_id=booking_id,
            channel=channel
        )
        if result:
            return {"success": True, "message": f"Review request sent via {channel}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send review request")
    except Exception as e:
        logger.error(f"Error sending review request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "ok"}
