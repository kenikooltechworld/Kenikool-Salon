"""
Enhanced payment management service
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class PaymentService:
    """Service for enhanced payment management"""
    
    @staticmethod
    def create_payment(
        tenant_id: str,
        amount: float,
        payment_date: str,
        payment_method: str,
        invoice_id: Optional[str] = None,
        bill_id: Optional[str] = None,
        reference_number: Optional[str] = None,
        notes: Optional[str] = None,
        bank_account: Optional[str] = None,
        check_number: Optional[str] = None
    ) -> Dict:
        """
        Create an enhanced payment record
        
        Returns:
            Dict with created payment data
        """
        db = Database.get_db()
        
        if not invoice_id and not bill_id:
            raise BadRequestException("Either invoice_id or bill_id must be provided")
        
        if invoice_id and bill_id:
            raise BadRequestException("Cannot specify both invoice_id and bill_id")
        
        # Validate invoice or bill exists and get details
        target_doc = None
        target_type = None
        
        if invoice_id:
            target_doc = db.invoices.find_one({
                "_id": ObjectId(invoice_id),
                "tenant_id": tenant_id
            })
            if not target_doc:
                raise NotFoundException("Invoice not found")
            target_type = "invoice"
            
            # Validate payment amount
            amount_due = target_doc.get("amount_due", 0)
            if amount > amount_due:
                raise BadRequestException(f"Payment amount (₦{amount}) exceeds amount due (₦{amount_due})")
        
        elif bill_id:
            target_doc = db.bills.find_one({
                "_id": ObjectId(bill_id),
                "tenant_id": tenant_id
            })
            if not target_doc:
                raise NotFoundException("Bill not found")
            target_type = "bill"
            
            # Validate payment amount
            amount_due = target_doc.get("amount_due", 0)
            if amount > amount_due:
                raise BadRequestException(f"Payment amount (₦{amount}) exceeds amount due (₦{amount_due})")
        
        # Create payment record
        payment_data = {
            "tenant_id": tenant_id,
            "invoice_id": invoice_id,
            "bill_id": bill_id,
            "amount": amount,
            "payment_date": payment_date,
            "payment_method": payment_method,
            "reference_number": reference_number,
            "notes": notes,
            "bank_account": bank_account,
            "check_number": check_number,
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.enhanced_payments.insert_one(payment_data)
        payment_id = str(result.inserted_id)
        
        # Update invoice or bill amounts
        new_amount_paid = target_doc.get("amount_paid", 0) + amount
        new_amount_due = target_doc.get("total", 0) - new_amount_paid
        
        # Update status
        new_status = target_doc.get("status")
        if new_amount_due <= 0:
            new_status = "paid"
        elif new_amount_paid > 0 and target_doc.get("status") == "draft":
            new_status = "pending" if target_type == "bill" else "sent"
        
        collection = db.invoices if target_type == "invoice" else db.bills
        collection.update_one(
            {"_id": ObjectId(invoice_id or bill_id)},
            {
                "$set": {
                    "amount_paid": new_amount_paid,
                    "amount_due": new_amount_due,
                    "status": new_status,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Enhanced payment created: {payment_id} for {target_type}: {invoice_id or bill_id}")
        
        payment_doc = db.enhanced_payments.find_one({"_id": ObjectId(payment_id)})
        return PaymentService._format_payment_response(payment_doc)
    
    @staticmethod
    def get_payments(
        tenant_id: str,
        invoice_id: Optional[str] = None,
        bill_id: Optional[str] = None,
        payment_method: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """
        Get payments for tenant
        
        Returns:
            List of payment dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if invoice_id:
            query["invoice_id"] = invoice_id
        if bill_id:
            query["bill_id"] = bill_id
        if payment_method:
            query["payment_method"] = payment_method
        if status:
            query["status"] = status
        
        payments = list(db.enhanced_payments.find(query).sort("payment_date", -1))
        
        return [PaymentService._format_payment_response(p) for p in payments]
    
    @staticmethod
    def get_payment(tenant_id: str, payment_id: str) -> Dict:
        """
        Get a single payment by ID
        
        Returns:
            Dict with payment data
        """
        db = Database.get_db()
        
        payment = db.enhanced_payments.find_one({
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        return PaymentService._format_payment_response(payment)
    
    @staticmethod
    def create_refund(
        tenant_id: str,
        payment_id: str,
        amount: float,
        reason: str,
        refund_date: str,
        refund_method: Optional[str] = None
    ) -> Dict:
        """
        Create a refund for a payment
        
        Returns:
            Dict with refund data
        """
        db = Database.get_db()
        
        # Get original payment
        payment = db.enhanced_payments.find_one({
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        if payment.get("status") == "refunded":
            raise BadRequestException("Payment has already been refunded")
        
        # Check if refund amount is valid
        original_amount = payment.get("amount", 0)
        existing_refunds = list(db.refunds.find({
            "payment_id": payment_id,
            "status": "completed"
        }))
        
        total_refunded = sum(r.get("amount", 0) for r in existing_refunds)
        available_for_refund = original_amount - total_refunded
        
        if amount > available_for_refund:
            raise BadRequestException(f"Refund amount (₦{amount}) exceeds available amount (₦{available_for_refund})")
        
        # Create refund record
        refund_data = {
            "tenant_id": tenant_id,
            "payment_id": payment_id,
            "invoice_id": payment.get("invoice_id"),
            "bill_id": payment.get("bill_id"),
            "amount": amount,
            "reason": reason,
            "refund_date": refund_date,
            "refund_method": refund_method or payment.get("payment_method"),
            "status": "completed",
            "created_at": datetime.utcnow()
        }
        
        result = db.refunds.insert_one(refund_data)
        refund_id = str(result.inserted_id)
        
        # Update payment status if fully refunded
        if amount == available_for_refund:
            db.enhanced_payments.update_one(
                {"_id": ObjectId(payment_id)},
                {
                    "$set": {
                        "status": "refunded",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
        
        # Update invoice or bill amounts
        invoice_id = payment.get("invoice_id")
        bill_id = payment.get("bill_id")
        
        if invoice_id or bill_id:
            target_id = invoice_id or bill_id
            collection = db.invoices if invoice_id else db.bills
            
            target_doc = collection.find_one({"_id": ObjectId(target_id)})
            if target_doc:
                new_amount_paid = target_doc.get("amount_paid", 0) - amount
                new_amount_due = target_doc.get("total", 0) - new_amount_paid
                
                # Update status if needed
                new_status = target_doc.get("status")
                if new_amount_due > 0 and target_doc.get("status") == "paid":
                    new_status = "sent" if invoice_id else "approved"
                
                collection.update_one(
                    {"_id": ObjectId(target_id)},
                    {
                        "$set": {
                            "amount_paid": new_amount_paid,
                            "amount_due": new_amount_due,
                            "status": new_status,
                            "updated_at": datetime.utcnow()
                        }
                    }
                )
        
        logger.info(f"Refund created: {refund_id} for payment: {payment_id}")
        
        refund_doc = db.refunds.find_one({"_id": ObjectId(refund_id)})
        return PaymentService._format_refund_response(refund_doc)
    
    @staticmethod
    def get_refunds(
        tenant_id: str,
        payment_id: Optional[str] = None,
        invoice_id: Optional[str] = None,
        bill_id: Optional[str] = None
    ) -> List[Dict]:
        """
        Get refunds for tenant
        
        Returns:
            List of refund dicts
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        
        if payment_id:
            query["payment_id"] = payment_id
        if invoice_id:
            query["invoice_id"] = invoice_id
        if bill_id:
            query["bill_id"] = bill_id
        
        refunds = list(db.refunds.find(query).sort("refund_date", -1))
        
        return [PaymentService._format_refund_response(r) for r in refunds]
    
    @staticmethod
    def get_payment_history(
        tenant_id: str,
        invoice_id: Optional[str] = None,
        bill_id: Optional[str] = None
    ) -> Dict:
        """
        Get complete payment history for an invoice or bill
        
        Returns:
            Dict with payment history
        """
        db = Database.get_db()
        
        query = {"tenant_id": tenant_id}
        if invoice_id:
            query["invoice_id"] = invoice_id
        if bill_id:
            query["bill_id"] = bill_id
        
        # Get payments
        payments = list(db.enhanced_payments.find(query).sort("payment_date", 1))
        
        # Get refunds
        refunds = list(db.refunds.find(query).sort("refund_date", 1))
        
        # Calculate totals
        total_paid = sum(p.get("amount", 0) for p in payments if p.get("status") != "cancelled")
        total_refunded = sum(r.get("amount", 0) for r in refunds if r.get("status") == "completed")
        net_paid = total_paid - total_refunded
        
        return {
            "payments": [PaymentService._format_payment_response(p) for p in payments],
            "refunds": [PaymentService._format_refund_response(r) for r in refunds],
            "summary": {
                "total_paid": total_paid,
                "total_refunded": total_refunded,
                "net_paid": net_paid,
                "payment_count": len(payments),
                "refund_count": len(refunds)
            }
        }
    
    @staticmethod
    def _format_payment_response(payment_doc: Dict) -> Dict:
        """Format payment document for response"""
        return {
            "id": str(payment_doc["_id"]),
            "tenant_id": payment_doc["tenant_id"],
            "invoice_id": payment_doc.get("invoice_id"),
            "bill_id": payment_doc.get("bill_id"),
            "amount": payment_doc["amount"],
            "payment_date": payment_doc["payment_date"],
            "payment_method": payment_doc["payment_method"],
            "reference_number": payment_doc.get("reference_number"),
            "notes": payment_doc.get("notes"),
            "bank_account": payment_doc.get("bank_account"),
            "check_number": payment_doc.get("check_number"),
            "status": payment_doc.get("status", "completed"),
            "created_at": payment_doc["created_at"],
            "updated_at": payment_doc["updated_at"]
        }
    
    @staticmethod
    def _format_refund_response(refund_doc: Dict) -> Dict:
        """Format refund document for response"""
        return {
            "id": str(refund_doc["_id"]),
            "tenant_id": refund_doc["tenant_id"],
            "payment_id": refund_doc["payment_id"],
            "invoice_id": refund_doc.get("invoice_id"),
            "bill_id": refund_doc.get("bill_id"),
            "amount": refund_doc["amount"],
            "reason": refund_doc["reason"],
            "refund_date": refund_doc["refund_date"],
            "refund_method": refund_doc["refund_method"],
            "status": refund_doc.get("status", "completed"),
            "created_at": refund_doc["created_at"]
        }


# Singleton instance
payment_service = PaymentService()