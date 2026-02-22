"""
Flutterwave payment gateway integration
"""
import httpx
from app.config import settings
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def initialize_payment(
    email: str,
    amount: float,
    tx_ref: str,
    customer_name: str,
    customer_phone: str,
    redirect_url: Optional[str] = None,
    metadata: Optional[Dict] = None
) -> Dict:
    """
    Initialize Flutterwave payment
    """
    try:
        payload = {
            "tx_ref": tx_ref,
            "amount": amount,
            "currency": "NGN",
            "redirect_url": redirect_url or f"{settings.FRONTEND_URL}/payment/callback",
            "payment_options": "card,banktransfer,ussd",
            "customer": {
                "email": email,
                "name": customer_name,
                "phonenumber": customer_phone
            },
            "customizations": {
                "title": settings.APP_NAME,
                "description": "Payment for salon services",
                "logo": ""
            }
        }
        
        if metadata:
            payload["meta"] = metadata
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.flutterwave.com/v3/payments",
                json=payload,
                headers={
                    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY_TEST}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                logger.info(f"Flutterwave payment initialized: {tx_ref}")
                return {
                    "success": True,
                    "payment_link": result["data"]["link"],
                    "tx_ref": tx_ref
                }
            else:
                logger.error(f"Flutterwave initialization failed: {result.get('message')}")
                return {
                    "success": False,
                    "error": result.get("message", "Payment initialization failed")
                }
    
    except Exception as e:
        logger.error(f"Error initializing Flutterwave payment: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def verify_payment(transaction_id: str) -> Dict:
    """
    Verify Flutterwave payment
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify",
                headers={
                    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY_TEST}"
                },
                timeout=30.0
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                data = result["data"]
                logger.info(f"Flutterwave payment verified: {transaction_id}")
                return {
                    "success": True,
                    "status": data["status"],
                    "amount": data["amount"],
                    "currency": data["currency"],
                    "tx_ref": data["tx_ref"],
                    "transaction_id": data["id"],
                    "charged_amount": data.get("charged_amount"),
                    "payment_type": data.get("payment_type"),
                    "customer": data.get("customer")
                }
            else:
                logger.error(f"Flutterwave verification failed: {result.get('message')}")
                return {
                    "success": False,
                    "error": result.get("message", "Payment verification failed")
                }
    
    except Exception as e:
        logger.error(f"Error verifying Flutterwave payment: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_transaction(transaction_id: str) -> Dict:
    """
    Get transaction details
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.flutterwave.com/v3/transactions/{transaction_id}",
                headers={
                    "Authorization": f"Bearer {settings.FLUTTERWAVE_SECRET_KEY_TEST}"
                },
                timeout=30.0
            )
            
            result = response.json()
            
            if response.status_code == 200 and result.get("status") == "success":
                return {
                    "success": True,
                    "data": result["data"]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("message", "Failed to get transaction")
                }
    
    except Exception as e:
        logger.error(f"Error getting Flutterwave transaction: {e}")
        return {
            "success": False,
            "error": str(e)
        }
