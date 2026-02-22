"""
Public Gift Card API Endpoints
Rate-limited endpoints for customer self-service gift card operations
"""

from fastapi import APIRouter, HTTPException, Request, Query, Body
from typing import Optional, Dict, List
from datetime import datetime, timezone
import logging
from app.database import Database
from app.services.pos_service import POSService
from app.services.fraud_detection_service import FraudDetectionService
from app.api.exceptions import BadRequestException, NotFoundException

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/public/gift-cards", tags=["public-gift-cards"])

# Rate limiting storage (in production, use Redis)
rate_limit_store = {}
ip_block_store = {}


def check_rate_limit(ip_address: str, endpoint: str, limit: int = 10, window: int = 60) -> bool:
    """
    Check if IP has exceeded rate limit
    
    Args:
        ip_address: Client IP address
        endpoint: API endpoint
        limit: Max requests per window
        window: Time window in seconds
        
    Returns:
        True if within limit, False if exceeded
    """
    key = f"{ip_address}:{endpoint}"
    now = datetime.now(timezone.utc).timestamp()
    
    if key not in rate_limit_store:
        rate_limit_store[key] = []
    
    # Remove old requests outside window
    rate_limit_store[key] = [
        ts for ts in rate_limit_store[key]
        if now - ts < window
    ]
    
    if len(rate_limit_store[key]) >= limit:
        return False
    
    rate_limit_store[key].append(now)
    return True


def check_ip_block(ip_address: str) -> bool:
    """
    Check if IP is blocked
    
    Args:
        ip_address: Client IP address
        
    Returns:
        True if blocked, False if not
    """
    if ip_address not in ip_block_store:
        return False
    
    block_until = ip_block_store[ip_address]
    now = datetime.now(timezone.utc).timestamp()
    
    if now > block_until:
        del ip_block_store[ip_address]
        return False
    
    return True


def block_ip(ip_address: str, duration_seconds: int = 900):
    """
    Block an IP address temporarily
    
    Args:
        ip_address: IP to block
        duration_seconds: Block duration in seconds (default 15 minutes)
    """
    now = datetime.now(timezone.utc).timestamp()
    ip_block_store[ip_address] = now + duration_seconds


@router.get("/balance")
async def check_balance(
    request: Request,
    card_number: str = Query(..., description="Gift card number"),
    tenant_id: str = Query(..., description="Tenant ID")
) -> Dict:
    """
    Check gift card balance (public endpoint, rate limited)
    
    Args:
        card_number: Gift card number
        tenant_id: Tenant ID
        
    Returns:
        Gift card balance and details
    """
    ip_address = request.client.host
    
    # Check if IP is blocked
    if check_ip_block(ip_address):
        logger.warning(f"Blocked IP attempted balance check: {ip_address}")
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    
    # Check rate limit (10 per minute per IP)
    if not check_rate_limit(ip_address, "balance_check", limit=10, window=60):
        logger.warning(f"Rate limit exceeded for IP {ip_address}")
        
        # Block IP for 15 minutes
        block_ip(ip_address, duration_seconds=900)
        
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Please try again later.")
    
    try:
        db = Database.get_db()
        
        # Record balance check attempt
        FraudDetectionService.record_balance_check(
            card_number=card_number,
            ip_address=ip_address,
            tenant_id=tenant_id,
            success=True
        )
        
        # Check for suspicious activity
        rate_check = FraudDetectionService.check_balance_check_rate(
            ip_address=ip_address,
            card_number=card_number,
            tenant_id=tenant_id
        )
        
        if rate_check.get("suspicious"):
            logger.warning(f"Suspicious balance check activity from {ip_address}")
            
            if rate_check.get("action") == "block_ip":
                block_ip(ip_address, duration_seconds=900)
            elif rate_check.get("action") == "block_ip_extended":
                block_ip(ip_address, duration_seconds=3600)
            
            raise HTTPException(status_code=429, detail="Suspicious activity detected. Please try again later.")
        
        # Get balance
        balance_info = POSService.get_gift_card_balance(tenant_id, card_number)
        
        return {
            "success": True,
            "card_number": balance_info["card_number"],
            "balance": balance_info["balance"],
            "status": balance_info["status"],
            "expires_at": balance_info["expires_at"].isoformat()
        }
        
    except NotFoundException as e:
        logger.warning(f"Gift card not found: {card_number}")
        raise HTTPException(status_code=404, detail="Gift card not found")
    except Exception as e:
        logger.error(f"Error checking balance: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/purchase")
async def purchase_gift_card(
    request: Request,
    tenant_id: str = Query(...),
    amount: float = Body(...),
    card_type: str = Body(..., description="physical or digital"),
    recipient_name: Optional[str] = Body(None),
    recipient_email: Optional[str] = Body(None),
    message: Optional[str] = Body(None),
    design_theme: str = Body("default"),
    payment_method: str = Body(...)
) -> Dict:
    """
    Purchase a gift card online
    
    Args:
        tenant_id: Tenant ID
        amount: Card amount
        card_type: physical or digital
        recipient_name: Recipient name
        recipient_email: Recipient email
        message: Personal message
        design_theme: Design theme
        payment_method: Payment method (paystack, etc.)
        
    Returns:
        Purchase confirmation with payment details
    """
    ip_address = request.client.host
    
    # Check rate limit (5 per minute per IP)
    if not check_rate_limit(ip_address, "purchase", limit=5, window=60):
        logger.warning(f"Purchase rate limit exceeded for IP {ip_address}")
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        db = Database.get_db()
        
        # Validate amount
        if amount < 1000 or amount > 500000:
            raise BadRequestException("Amount must be between ₦1,000 and ₦500,000")
        
        # Validate email for digital cards
        if card_type == "digital" and not recipient_email:
            raise BadRequestException("Email required for digital gift cards")
        
        # Create gift card (initially inactive until payment confirmed)
        gift_card = POSService.create_gift_card(
            tenant_id=tenant_id,
            amount=amount,
            card_type=card_type,
            recipient_name=recipient_name,
            recipient_email=recipient_email,
            message=message,
            design_theme=design_theme,
            created_by="public_api",
            activation_required=True  # Require activation after payment
        )
        
        logger.info(f"Gift card created for purchase: {gift_card['card_number']}, amount: {amount}")
        
        # Return card details for payment processing
        return {
            "success": True,
            "card_number": gift_card["card_number"],
            "card_id": str(gift_card.get("_id", "")),
            "amount": amount,
            "card_type": card_type,
            "recipient_email": recipient_email,
            "status": "pending_payment",
            "message": "Gift card created. Please proceed with payment."
        }
        
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error purchasing gift card: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/transfer")
async def transfer_balance(
    request: Request,
    tenant_id: str = Query(...),
    source_card: str = Body(...),
    destination_card: Optional[str] = Body(None),
    amount: float = Body(...)
) -> Dict:
    """
    Transfer balance between gift cards
    
    Args:
        tenant_id: Tenant ID
        source_card: Source card number
        destination_card: Destination card number (optional, creates new if not provided)
        amount: Amount to transfer
        
    Returns:
        Transfer confirmation
    """
    ip_address = request.client.host
    
    # Check rate limit (1 per day per IP)
    if not check_rate_limit(ip_address, "transfer", limit=1, window=86400):
        logger.warning(f"Transfer rate limit exceeded for IP {ip_address}")
        raise HTTPException(status_code=429, detail="Transfer limit exceeded. Try again tomorrow.")
    
    try:
        db = Database.get_db()
        
        # Validate amount
        if amount <= 0:
            raise BadRequestException("Amount must be greater than 0")
        
        # Check velocity
        velocity_check = FraudDetectionService.check_redemption_velocity(
            card_number=source_card,
            tenant_id=tenant_id
        )
        
        if velocity_check.get("suspicious"):
            logger.warning(f"Suspicious transfer velocity for card {source_card}")
            raise HTTPException(status_code=429, detail="Too many transfers. Please try again later.")
        
        # Transfer balance
        result = POSService.transfer_gift_card_balance(
            tenant_id=tenant_id,
            source_card=source_card,
            destination_card=destination_card,
            amount=amount,
            transferred_by="public_api"
        )
        
        logger.info(f"Transfer completed: {source_card} -> {result['destination_card']}, amount: {amount}")
        
        return {
            "success": True,
            "source_card": result["source_card"],
            "destination_card": result["destination_card"],
            "amount": amount,
            "source_balance": result["source_balance"],
            "destination_balance": result["destination_balance"]
        }
        
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error transferring balance: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/set-pin")
async def set_pin(
    request: Request,
    tenant_id: str = Query(...),
    card_number: str = Body(...),
    pin: str = Body(...)
) -> Dict:
    """
    Set or change PIN for a gift card
    
    Args:
        tenant_id: Tenant ID
        card_number: Gift card number
        pin: 4-6 digit PIN
        
    Returns:
        PIN set confirmation
    """
    ip_address = request.client.host
    
    # Check rate limit
    if not check_rate_limit(ip_address, "set_pin", limit=5, window=60):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    try:
        # Validate PIN
        if not pin or len(pin) < 4 or len(pin) > 6 or not pin.isdigit():
            raise BadRequestException("PIN must be 4-6 digits")
        
        # Set PIN
        result = POSService.set_gift_card_pin(
            tenant_id=tenant_id,
            card_number=card_number,
            pin=pin
        )
        
        logger.info(f"PIN set for card {card_number}")
        
        return {
            "success": True,
            "card_number": card_number,
            "pin_enabled": True
        }
        
    except BadRequestException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error setting PIN: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/terms")
async def get_terms(
    tenant_id: str = Query(...)
) -> Dict:
    """
    Get current gift card terms and conditions
    
    Args:
        tenant_id: Tenant ID
        
    Returns:
        Terms and conditions
    """
    try:
        db = Database.get_db()
        
        # Get active terms
        terms = db.gift_card_terms.find_one({
            "is_active": True
        })
        
        if not terms:
            # Return default terms
            terms = {
                "version": "1.0",
                "content": "Default terms and conditions"
            }
        
        return {
            "success": True,
            "version": terms.get("version"),
            "content": terms.get("content"),
            "effective_date": terms.get("effective_date", datetime.now(timezone.utc)).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error getting terms: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
