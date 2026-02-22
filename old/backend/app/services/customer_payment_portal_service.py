"""
Customer Payment Portal Service - Customer-facing payment operations
Handles customer payment history, payment links, and payment status
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
import secrets
import hashlib

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException, UnauthorizedException

logger = logging.getLogger(__name__)


class CustomerPaymentPortalService:
    """Service for customer-facing payment portal operations"""
    
    @staticmethod
    def get_customer_payments(
        tenant_id: str,
        customer_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> Dict:
        """
        Get payments for a customer's bookings
        
        Args:
            tenant_id: Tenant ID for isolation
            customer_id: Customer ID to fetch payments for
            limit: Maximum number of payments to return
            skip: Number of payments to skip (for pagination)
            
        Returns:
            Dict with customer payments and pagination info
            
        Raises:
            NotFoundException: If customer not found
        """
        db = Database.get_db()
        
        try:
            customer_oid = ObjectId(customer_id)
        except Exception:
            raise BadRequestException("Invalid customer ID format")
        
        # Verify customer exists
        customer = db.clients.find_one({
            "_id": customer_oid,
            "tenant_id": tenant_id
        })
        
        if not customer:
            raise NotFoundException("Customer not found")
        
        # Find all bookings for this customer
        bookings = list(db.bookings.find({
            "client_id": customer_id,
            "tenant_id": tenant_id
        }).project({"_id": 1}))
        
        booking_ids = [str(b["_id"]) for b in bookings]
        
        # Find all payments for these bookings
        total_count = db.payments.count_documents({
            "tenant_id": tenant_id,
            "booking_id": {"$in": booking_ids}
        })
        
        payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "booking_id": {"$in": booking_ids}
        }).sort("created_at", -1).skip(skip).limit(limit))
        
        # Format payment data
        payment_data = []
        for payment in payments:
            # Fetch related booking
            booking_data = None
            if payment.get("booking_id"):
                try:
                    booking_oid = ObjectId(payment["booking_id"])
                    booking = db.bookings.find_one({
                        "_id": booking_oid,
                        "tenant_id": tenant_id
                    })
                    if booking:
                        booking_data = {
                            "id": str(booking["_id"]),
                            "reference": booking.get("reference"),
                            "service": booking.get("service"),
                            "start_time": booking.get("start_time"),
                            "status": booking.get("status")
                        }
                except Exception as e:
                    logger.warning(f"Failed to fetch booking {payment.get('booking_id')}: {str(e)}")
            
            payment_data.append({
                "id": str(payment["_id"]),
                "amount": payment.get("amount"),
                "status": payment.get("status"),
                "payment_type": payment.get("payment_type"),
                "gateway": payment.get("gateway"),
                "reference": payment.get("reference"),
                "created_at": payment.get("created_at"),
                "verified_at": payment.get("verified_at"),
                "receipt_url": payment.get("receipt_url"),
                "receipt_generated_at": payment.get("receipt_generated_at"),
                "booking_data": booking_data
            })
        
        return {
            "customer_id": customer_id,
            "customer_name": customer.get("name"),
            "customer_email": customer.get("email"),
            "total_count": total_count,
            "limit": limit,
            "skip": skip,
            "payments": payment_data,
            "has_more": (skip + limit) < total_count
        }
    
    @staticmethod
    def generate_payment_link(
        tenant_id: str,
        customer_id: str,
        payment_id: str,
        expires_in_days: int = 30
    ) -> Dict:
        """
        Generate a shareable payment link for a pending payment
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            payment_id: Payment ID to generate link for
            expires_in_days: Number of days until link expires
            
        Returns:
            Dict with payment link and token
            
        Raises:
            NotFoundException: If payment not found
            BadRequestException: If payment is not pending
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Verify payment belongs to customer
        if payment.get("client_id") != customer_id:
            raise UnauthorizedException("Payment does not belong to this customer")
        
        # Check payment status
        if payment.get("status") not in ["pending", "failed"]:
            raise BadRequestException(
                f"Cannot generate link for payment with status: {payment.get('status')}"
            )
        
        # Generate secure token
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Store payment link in database
        link_data = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "customer_id": customer_id,
            "token_hash": token_hash,
            "created_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=expires_in_days),
            "accessed_at": None,
            "access_count": 0
        }
        
        result = db.payment_links.insert_one(link_data)
        link_id = str(result.inserted_id)
        
        # Generate payment link URL
        payment_link = f"/customer/payments/link/{token}"
        
        logger.info(f"Payment link generated for payment {payment_id}, customer {customer_id}")
        
        return {
            "link_id": link_id,
            "payment_id": payment_id,
            "payment_link": payment_link,
            "token": token,
            "expires_at": link_data["expires_at"],
            "message": "Payment link generated successfully"
        }
    
    @staticmethod
    def validate_payment_link(
        tenant_id: str,
        token: str
    ) -> Dict:
        """
        Validate a payment link token and get payment details
        
        Args:
            tenant_id: Tenant ID
            token: Payment link token
            
        Returns:
            Dict with payment details and link info
            
        Raises:
            NotFoundException: If link not found or expired
            BadRequestException: If link is invalid
        """
        db = Database.get_db()
        
        # Hash the token
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find payment link
        link = db.payment_links.find_one({
            "tenant_id": tenant_id,
            "token_hash": token_hash
        })
        
        if not link:
            raise NotFoundException("Payment link not found")
        
        # Check if link is expired
        if link.get("expires_at") < datetime.utcnow():
            raise BadRequestException("Payment link has expired")
        
        # Fetch payment
        try:
            payment_oid = ObjectId(link["payment_id"])
        except Exception:
            raise BadRequestException("Invalid payment ID in link")
        
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Update link access info
        db.payment_links.update_one(
            {"_id": link["_id"]},
            {
                "$set": {
                    "accessed_at": datetime.utcnow()
                },
                "$inc": {
                    "access_count": 1
                }
            }
        )
        
        # Fetch customer info
        customer_data = None
        if payment.get("client_id"):
            try:
                customer_oid = ObjectId(payment["client_id"])
                customer = db.clients.find_one({
                    "_id": customer_oid,
                    "tenant_id": tenant_id
                })
                if customer:
                    customer_data = {
                        "id": str(customer["_id"]),
                        "name": customer.get("name"),
                        "email": customer.get("email")
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch customer: {str(e)}")
        
        # Fetch booking info
        booking_data = None
        if payment.get("booking_id"):
            try:
                booking_oid = ObjectId(payment["booking_id"])
                booking = db.bookings.find_one({
                    "_id": booking_oid,
                    "tenant_id": tenant_id
                })
                if booking:
                    booking_data = {
                        "id": str(booking["_id"]),
                        "reference": booking.get("reference"),
                        "service": booking.get("service"),
                        "start_time": booking.get("start_time"),
                        "status": booking.get("status")
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch booking: {str(e)}")
        
        return {
            "link_id": str(link["_id"]),
            "payment_id": str(payment["_id"]),
            "customer_data": customer_data,
            "payment": {
                "amount": payment.get("amount"),
                "status": payment.get("status"),
                "payment_type": payment.get("payment_type"),
                "gateway": payment.get("gateway"),
                "reference": payment.get("reference"),
                "created_at": payment.get("created_at")
            },
            "booking_data": booking_data,
            "link_expires_at": link.get("expires_at"),
            "link_accessed_count": link.get("access_count", 0)
        }
    
    @staticmethod
    def get_payment_status(
        tenant_id: str,
        customer_id: str,
        payment_id: str
    ) -> Dict:
        """
        Get real-time payment status for a customer
        
        Args:
            tenant_id: Tenant ID
            customer_id: Customer ID
            payment_id: Payment ID
            
        Returns:
            Dict with payment status and details
            
        Raises:
            NotFoundException: If payment not found
            UnauthorizedException: If payment doesn't belong to customer
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Verify payment belongs to customer
        if payment.get("client_id") != customer_id:
            raise UnauthorizedException("Payment does not belong to this customer")
        
        # Fetch booking info
        booking_data = None
        if payment.get("booking_id"):
            try:
                booking_oid = ObjectId(payment["booking_id"])
                booking = db.bookings.find_one({
                    "_id": booking_oid,
                    "tenant_id": tenant_id
                })
                if booking:
                    booking_data = {
                        "id": str(booking["_id"]),
                        "reference": booking.get("reference"),
                        "service": booking.get("service"),
                        "start_time": booking.get("start_time"),
                        "status": booking.get("status")
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch booking: {str(e)}")
        
        return {
            "payment_id": str(payment["_id"]),
            "amount": payment.get("amount"),
            "status": payment.get("status"),
            "payment_type": payment.get("payment_type"),
            "gateway": payment.get("gateway"),
            "reference": payment.get("reference"),
            "created_at": payment.get("created_at"),
            "verified_at": payment.get("verified_at"),
            "receipt_url": payment.get("receipt_url"),
            "receipt_generated_at": payment.get("receipt_generated_at"),
            "booking_data": booking_data,
            "status_message": CustomerPaymentPortalService._get_status_message(payment.get("status"))
        }
    
    @staticmethod
    def _get_status_message(status: str) -> str:
        """
        Get human-readable status message
        
        Args:
            status: Payment status
            
        Returns:
            Status message
        """
        messages = {
            "pending": "Payment is pending. Please complete the payment.",
            "completed": "Payment has been completed successfully.",
            "failed": "Payment failed. Please try again.",
            "refunded": "Payment has been fully refunded.",
            "partially_refunded": "Payment has been partially refunded.",
            "cancelled": "Payment has been cancelled."
        }
        return messages.get(status, f"Payment status: {status}")


# Singleton instance
customer_payment_portal_service = CustomerPaymentPortalService()
