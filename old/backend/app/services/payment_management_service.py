"""
Payment Management Service - Enhanced payment operations
Handles payment details, refunds, and related operations
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException, UnauthorizedException

logger = logging.getLogger(__name__)


class PaymentManagementService:
    """Service for enhanced payment management operations"""
    
    @staticmethod
    def get_payment_detail(
        tenant_id: str,
        payment_id: str
    ) -> Dict:
        """
        Get detailed payment information including related booking and customer data
        
        Args:
            tenant_id: Tenant ID for isolation
            payment_id: Payment ID to retrieve
            
        Returns:
            Dict with complete payment information including related data
            
        Raises:
            NotFoundException: If payment not found
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
                        "stylist": booking.get("stylist"),
                        "client_id": booking.get("client_id"),
                        "start_time": booking.get("start_time"),
                        "end_time": booking.get("end_time"),
                        "status": booking.get("status")
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch booking {payment.get('booking_id')}: {str(e)}")
        
        # Fetch related client/customer data
        client_data = None
        client_id = payment.get("client_id") or (booking_data.get("client_id") if booking_data else None)
        if client_id:
            try:
                client_oid = ObjectId(client_id)
                client = db.clients.find_one({
                    "_id": client_oid,
                    "tenant_id": tenant_id
                })
                if client:
                    client_data = {
                        "id": str(client["_id"]),
                        "name": client.get("name"),
                        "email": client.get("email"),
                        "phone": client.get("phone")
                    }
            except Exception as e:
                logger.warning(f"Failed to fetch client {client_id}: {str(e)}")
        
        # Fetch refund history if payment has been refunded
        refund_history = []
        if payment.get("refund_amount") or payment.get("status") in ["refunded", "partially_refunded"]:
            refunds = list(db.payment_refunds.find({
                "payment_id": payment_id,
                "tenant_id": tenant_id
            }).sort("created_at", -1))
            
            refund_history = [
                {
                    "id": str(r["_id"]),
                    "amount": r.get("refund_amount"),
                    "type": r.get("refund_type"),
                    "reason": r.get("reason"),
                    "status": r.get("status"),
                    "processed_by": r.get("processed_by"),
                    "created_at": r.get("created_at"),
                    "completed_at": r.get("completed_at")
                }
                for r in refunds
            ]
        
        # Format and return response
        return {
            "id": str(payment["_id"]),
            "tenant_id": payment["tenant_id"],
            "booking_id": payment.get("booking_id"),
            "client_id": payment.get("client_id"),
            "amount": payment.get("amount"),
            "gateway": payment.get("gateway"),
            "reference": payment.get("reference"),
            "status": payment.get("status"),
            "payment_type": payment.get("payment_type"),
            "metadata": payment.get("metadata"),
            "created_at": payment.get("created_at"),
            "updated_at": payment.get("updated_at"),
            "verified_at": payment.get("verified_at"),
            
            # Refund fields
            "refund_amount": payment.get("refund_amount"),
            "refund_reason": payment.get("refund_reason"),
            "refunded_at": payment.get("refunded_at"),
            "refund_type": payment.get("refund_type"),
            "refunded_by": payment.get("refunded_by"),
            
            # Receipt fields
            "receipt_generated_at": payment.get("receipt_generated_at"),
            "receipt_url": payment.get("receipt_url"),
            "receipt_emailed_at": payment.get("receipt_emailed_at"),
            
            # Manual payment fields
            "recorded_by": payment.get("recorded_by"),
            "is_manual": payment.get("is_manual", False),
            
            # Gateway sync fields
            "gateway_sync_status": payment.get("gateway_sync_status", "synced"),
            "last_synced_at": payment.get("last_synced_at"),
            
            # Related data
            "booking_data": booking_data,
            "client_data": client_data,
            "refund_history": refund_history
        }
    
    @staticmethod
    def validate_refund_amount(
        payment_id: str,
        tenant_id: str,
        refund_amount: float
    ) -> Dict:
        """
        Validate refund amount against payment
        
        Args:
            payment_id: Payment ID to refund
            tenant_id: Tenant ID
            refund_amount: Amount to refund
            
        Returns:
            Dict with validation result and available refund amount
            
        Raises:
            NotFoundException: If payment not found
            BadRequestException: If refund validation fails
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
        
        # Check payment status
        if payment.get("status") == "refunded":
            raise BadRequestException("Payment has already been fully refunded")
        
        if payment.get("status") not in ["completed", "partially_refunded"]:
            raise BadRequestException(f"Cannot refund payment with status: {payment.get('status')}")
        
        # Calculate available refund amount
        original_amount = payment.get("amount", 0)
        already_refunded = payment.get("refund_amount", 0)
        available_for_refund = original_amount - already_refunded
        
        # Validate refund amount
        if refund_amount <= 0:
            raise BadRequestException("Refund amount must be greater than zero")
        
        if refund_amount > available_for_refund:
            raise BadRequestException(
                f"Refund amount (₦{refund_amount}) exceeds available amount (₦{available_for_refund})"
            )
        
        return {
            "valid": True,
            "original_amount": original_amount,
            "already_refunded": already_refunded,
            "available_for_refund": available_for_refund,
            "requested_refund": refund_amount,
            "will_be_fully_refunded": refund_amount == available_for_refund
        }
    
    @staticmethod
    def process_refund(
        tenant_id: str,
        payment_id: str,
        refund_amount: float,
        reason: str,
        refund_type: str,
        processed_by: str,
        gateway_refund_id: Optional[str] = None
    ) -> Dict:
        """
        Process a refund for a payment
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID to refund
            refund_amount: Amount to refund
            reason: Reason for refund
            refund_type: "full" or "partial"
            processed_by: User ID who processed the refund
            gateway_refund_id: Optional gateway refund ID
            
        Returns:
            Dict with refund details
            
        Raises:
            NotFoundException: If payment not found
            BadRequestException: If refund validation fails
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
        except Exception:
            raise BadRequestException("Invalid payment ID format")
        
        # Validate refund
        validation = PaymentManagementService.validate_refund_amount(
            payment_id, tenant_id, refund_amount
        )
        
        # Fetch payment for update
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        # Create refund record
        refund_data = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "refund_amount": refund_amount,
            "refund_type": refund_type,
            "reason": reason,
            "status": "completed",
            "gateway_refund_id": gateway_refund_id,
            "processed_by": processed_by,
            "created_at": datetime.utcnow(),
            "completed_at": datetime.utcnow()
        }
        
        result = db.payment_refunds.insert_one(refund_data)
        refund_id = str(result.inserted_id)
        
        # Update payment record
        new_refund_amount = (payment.get("refund_amount", 0) or 0) + refund_amount
        new_status = "refunded" if validation["will_be_fully_refunded"] else "partially_refunded"
        
        db.payments.update_one(
            {"_id": payment_oid},
            {
                "$set": {
                    "refund_amount": new_refund_amount,
                    "refund_reason": reason,
                    "refund_type": refund_type,
                    "refunded_at": datetime.utcnow(),
                    "refunded_by": processed_by,
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update related booking payment status if applicable
        if payment.get("booking_id"):
            try:
                booking_oid = ObjectId(payment["booking_id"])
                if new_status == "refunded":
                    db.bookings.update_one(
                        {"_id": booking_oid},
                        {
                            "$set": {
                                "payment_status": "refunded",
                                "updated_at": datetime.utcnow()
                            }
                        }
                    )
            except Exception as e:
                logger.warning(f"Failed to update booking payment status: {str(e)}")
        
        logger.info(
            f"Refund processed: {refund_id} for payment {payment_id}, "
            f"amount: ₦{refund_amount}, type: {refund_type}"
        )
        
        return {
            "refund_id": refund_id,
            "payment_id": payment_id,
            "refund_amount": refund_amount,
            "refund_type": refund_type,
            "status": "completed",
            "processed_at": datetime.utcnow(),
            "message": f"Refund of ₦{refund_amount} processed successfully"
        }
    
    @staticmethod
    def get_refund_history(
        tenant_id: str,
        payment_id: str
    ) -> List[Dict]:
        """
        Get refund history for a payment
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID
            
        Returns:
            List of refund records
        """
        db = Database.get_db()
        
        refunds = list(db.payment_refunds.find({
            "payment_id": payment_id,
            "tenant_id": tenant_id
        }).sort("created_at", -1))
        
        return [
            {
                "id": str(r["_id"]),
                "payment_id": r["payment_id"],
                "refund_amount": r.get("refund_amount"),
                "refund_type": r.get("refund_type"),
                "reason": r.get("reason"),
                "status": r.get("status"),
                "gateway_refund_id": r.get("gateway_refund_id"),
                "processed_by": r.get("processed_by"),
                "created_at": r.get("created_at"),
                "completed_at": r.get("completed_at"),
                "error_message": r.get("error_message")
            }
            for r in refunds
        ]
    
    @staticmethod
    def record_manual_payment(
        tenant_id: str,
        booking_id: str,
        amount: float,
        payment_method: str,
        recorded_by: str,
        reference: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Record a manual payment (cash, check, bank transfer, etc.)
        
        Args:
            tenant_id: Tenant ID
            booking_id: Booking ID for the payment
            amount: Payment amount
            payment_method: Payment method (cash, bank_transfer, check, other)
            recorded_by: User ID who recorded the payment
            reference: Optional reference number
            notes: Optional notes
            
        Returns:
            Dict with created payment details
            
        Raises:
            NotFoundException: If booking not found
            BadRequestException: If validation fails
        """
        db = Database.get_db()
        
        # Validate booking exists
        try:
            booking_oid = ObjectId(booking_id)
        except Exception:
            raise BadRequestException("Invalid booking ID format")
        
        booking = db.bookings.find_one({
            "_id": booking_oid,
            "tenant_id": tenant_id
        })
        
        if not booking:
            raise NotFoundException("Booking not found")
        
        # Validate payment amount
        if amount <= 0:
            raise BadRequestException("Payment amount must be greater than zero")
        
        # Validate payment method
        valid_methods = ["cash", "bank_transfer", "check", "other"]
        if payment_method not in valid_methods:
            raise BadRequestException(
                f"Invalid payment method. Must be one of: {', '.join(valid_methods)}"
            )
        
        # Create payment record
        payment_data = {
            "tenant_id": tenant_id,
            "booking_id": booking_id,
            "client_id": booking.get("client_id"),
            "amount": amount,
            "gateway": "manual",
            "reference": reference or f"MANUAL-{datetime.utcnow().timestamp()}",
            "status": "completed",
            "payment_type": "full",
            "payment_method": payment_method,
            "is_manual": True,
            "recorded_by": recorded_by,
            "notes": notes,
            "metadata": {
                "payment_method": payment_method,
                "recorded_by": recorded_by,
                "notes": notes
            },
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "verified_at": datetime.utcnow(),
            "gateway_sync_status": "synced",
            "last_synced_at": datetime.utcnow()
        }
        
        result = db.payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Update booking payment status
        db.bookings.update_one(
            {"_id": booking_oid},
            {
                "$set": {
                    "payment_status": "paid",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(
            f"Manual payment recorded: {payment_id} for booking {booking_id}, "
            f"amount: ₦{amount}, method: {payment_method}, recorded by: {recorded_by}"
        )
        
        return {
            "id": payment_id,
            "tenant_id": tenant_id,
            "booking_id": booking_id,
            "client_id": booking.get("client_id"),
            "amount": amount,
            "gateway": "manual",
            "reference": payment_data["reference"],
            "status": "completed",
            "payment_type": "full",
            "payment_method": payment_method,
            "is_manual": True,
            "recorded_by": recorded_by,
            "notes": notes,
            "created_at": payment_data["created_at"],
            "updated_at": payment_data["updated_at"],
            "verified_at": payment_data["verified_at"],
            "message": f"Manual payment of ₦{amount} recorded successfully"
        }


# Singleton instance
payment_management_service = PaymentManagementService()
