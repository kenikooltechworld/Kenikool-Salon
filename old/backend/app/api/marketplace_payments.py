"""
Marketplace Payments API

Endpoints for payment processing, webhook handling, and payment status tracking.
Integrates with Paystack for secure payment processing.
"""
from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from pydantic import BaseModel
import logging
import hmac
import hashlib

from app.database import Database
from app.services.payment_service import PaymentService
from app.services.commission_service import CommissionService
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/marketplace", tags=["marketplace-payments"])


# ============================================================================
# Pydantic Models
# ============================================================================

class PaymentInitialize(BaseModel):
    """Initialize payment request"""
    booking_reference: str
    payment_method: str  # "paystack", "bank_transfer"
    apply_discount: bool = True


class PaymentResponse(BaseModel):
    """Payment response"""
    booking_reference: str
    payment_url: Optional[str] = None
    amount: float
    discount_amount: float
    final_amount: float
    status: str


class PaymentStatusResponse(BaseModel):
    """Payment status response"""
    booking_reference: str
    payment_status: str
    amount: float
    timestamp: str


# ============================================================================
# Endpoints
# ============================================================================

@router.post("/payments/initialize", response_model=PaymentResponse)
async def initialize_payment(request_data: PaymentInitialize):
    """
    Initialize payment for a marketplace booking
    
    - Validates booking exists
    - Calculates discount if applicable
    - Initializes Paystack payment
    - Returns payment URL
    """
    try:
        db = Database.get_db()
        payment_service = PaymentService(db)
        
        # Get booking
        booking = db.marketplace_bookings.find_one({
            "booking_reference": request_data.booking_reference
        })
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking["payment_status"] != "pending":
            raise HTTPException(
                status_code=400,
                detail=f"Booking payment already {booking['payment_status']}"
            )
        
        # Calculate discount
        discount_amount = 0.0
        final_amount = booking["price"]
        
        if request_data.apply_discount and request_data.payment_method == "paystack":
            discount_percentage = 0.05  # 5% discount for online payment
            discount_amount = booking["price"] * discount_percentage
            final_amount = booking["price"] - discount_amount
        
        # Initialize Paystack payment
        if request_data.payment_method == "paystack":
            payment_url = await payment_service.initialize_paystack(
                amount=int(final_amount * 100),  # Paystack expects amount in kobo
                email=booking["guest_email"],
                reference=request_data.booking_reference,
                metadata={
                    "booking_type": "marketplace",
                    "booking_reference": request_data.booking_reference,
                    "tenant_id": booking["tenant_id"],
                    "guest_email": booking["guest_email"]
                }
            )
        else:
            payment_url = None
        
        # Update booking with payment info
        db.marketplace_bookings.update_one(
            {"_id": booking["_id"]},
            {
                "$set": {
                    "discount_amount": discount_amount,
                    "final_price": final_amount,
                    "payment_method": request_data.payment_method,
                    "payment_initialized_at": datetime.utcnow()
                }
            }
        )
        
        return PaymentResponse(
            booking_reference=request_data.booking_reference,
            payment_url=payment_url,
            amount=booking["price"],
            discount_amount=discount_amount,
            final_amount=final_amount,
            status="initialized"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error initializing payment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/payments/webhook")
async def payment_webhook(request: Request):
    """
    Handle Paystack webhook for payment confirmation
    
    - Verifies webhook signature
    - Updates booking payment status
    - Records commission
    - Sends confirmation emails
    """
    try:
        # Get request body
        body = await request.body()
        
        # Verify signature
        signature = request.headers.get("x-paystack-signature")
        if not signature:
            raise HTTPException(status_code=400, detail="Missing signature")
        
        # Verify signature matches
        hash_object = hmac.new(
            settings.PAYSTACK_SECRET_KEY.encode(),
            body,
            hashlib.sha512
        )
        computed_signature = hash_object.hexdigest()
        
        if signature != computed_signature:
            raise HTTPException(status_code=400, detail="Invalid signature")
        
        # Parse payload
        import json
        payload = json.loads(body)
        
        if payload["event"] == "charge.success":
            db = Database.get_db()
            commission_service = CommissionService(db)
            
            reference = payload["data"]["reference"]
            amount = payload["data"]["amount"] / 100  # Convert from kobo to naira
            
            # Get booking
            booking = db.marketplace_bookings.find_one({
                "booking_reference": reference
            })
            
            if not booking:
                logger.warning(f"Booking not found for reference: {reference}")
                return {"status": "error", "message": "Booking not found"}
            
            # Update booking payment status
            db.marketplace_bookings.update_one(
                {"_id": booking["_id"]},
                {
                    "$set": {
                        "payment_status": "paid",
                        "payment_reference": reference,
                        "payment_completed_at": datetime.utcnow()
                    }
                }
            )
            
            # Record commission
            tenant = db.tenants.find_one({"_id": booking["tenant_id"]})
            commission_rate = tenant.get("commission_rate", 0.10) if tenant else 0.10
            
            await commission_service.record_commission(
                tenant_id=str(booking["tenant_id"]),
                booking_id=str(booking["_id"]),
                booking_reference=reference,
                amount=booking["final_price"],
                commission_rate=commission_rate
            )
            
            # TODO: Send payment confirmation email
            # TODO: Send booking confirmation to salon
            
            logger.info(f"Payment confirmed for booking: {reference}")
            return {"status": "success", "message": "Payment processed"}
        
        elif payload["event"] == "charge.failed":
            reference = payload["data"]["reference"]
            
            # Update booking payment status
            db = Database.get_db()
            db.marketplace_bookings.update_one(
                {"booking_reference": reference},
                {
                    "$set": {
                        "payment_status": "failed",
                        "payment_failed_at": datetime.utcnow()
                    }
                }
            )
            
            logger.warning(f"Payment failed for booking: {reference}")
            return {"status": "success", "message": "Payment failure recorded"}
        
        return {"status": "success", "message": "Webhook processed"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return {"status": "error", "message": str(e)}


@router.get("/payments/{reference}/status", response_model=PaymentStatusResponse)
async def get_payment_status(reference: str):
    """
    Get payment status for a booking
    """
    try:
        db = Database.get_db()
        
        booking = db.marketplace_bookings.find_one({
            "booking_reference": reference
        })
        
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        return PaymentStatusResponse(
            booking_reference=reference,
            payment_status=booking["payment_status"],
            amount=booking["final_price"],
            timestamp=booking.get("payment_completed_at", booking["created_at"]).isoformat()
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting payment status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payments/history")
async def get_payment_history(
    tenant_id: str,
    skip: int = 0,
    limit: int = 50
):
    """
    Get payment history for a tenant
    """
    try:
        db = Database.get_db()
        
        payments = list(
            db.marketplace_bookings.find({
                "tenant_id": tenant_id,
                "payment_status": "paid"
            })
            .sort("payment_completed_at", -1)
            .skip(skip)
            .limit(limit)
        )
        
        # Convert ObjectId to string
        for payment in payments:
            payment["_id"] = str(payment["_id"])
        
        total = db.marketplace_bookings.count_documents({
            "tenant_id": tenant_id,
            "payment_status": "paid"
        })
        
        return {
            "payments": payments,
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    except Exception as e:
        logger.error(f"Error getting payment history: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Helper Functions
# ============================================================================

from datetime import datetime
