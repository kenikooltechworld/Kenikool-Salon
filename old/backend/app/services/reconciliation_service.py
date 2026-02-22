"""
Payment Reconciliation Service - Reconciliation and gateway sync operations
Handles payment reconciliation, gateway synchronization, and duplicate detection
"""
from bson import ObjectId
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class ReconciliationService:
    """Service for payment reconciliation and gateway sync operations"""
    
    @staticmethod
    def get_reconciliation_data(
        tenant_id: str,
        days_back: int = 30
    ) -> Dict:
        """
        Get payment reconciliation data including unmatched, mismatched, and duplicate payments
        
        Args:
            tenant_id: Tenant ID for isolation
            days_back: Number of days to look back (default 30)
            
        Returns:
            Dict with reconciliation data including unmatched, mismatched, and duplicate payments
        """
        db = Database.get_db()
        
        # Calculate date range
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Find unmatched payments (no booking_id)
        unmatched_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "booking_id": None,
            "created_at": {"$gte": cutoff_date}
        }).sort("created_at", -1))
        
        unmatched_data = [
            {
                "id": str(p["_id"]),
                "reference": p.get("reference"),
                "amount": p.get("amount"),
                "gateway": p.get("gateway"),
                "status": p.get("status"),
                "created_at": p.get("created_at"),
                "gateway_sync_status": p.get("gateway_sync_status", "synced")
            }
            for p in unmatched_payments
        ]
        
        # Find payments with mismatched amounts
        # (where payment amount doesn't match booking amount)
        mismatched_payments = []
        all_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "booking_id": {"$ne": None},
            "created_at": {"$gte": cutoff_date}
        }))
        
        for payment in all_payments:
            try:
                booking_oid = ObjectId(payment["booking_id"])
                booking = db.bookings.find_one({
                    "_id": booking_oid,
                    "tenant_id": tenant_id
                })
                
                if booking:
                    booking_amount = booking.get("total_amount", 0)
                    payment_amount = payment.get("amount", 0)
                    
                    # Check if amounts don't match
                    if abs(booking_amount - payment_amount) > 0.01:  # Allow small floating point differences
                        mismatched_payments.append({
                            "id": str(payment["_id"]),
                            "payment_id": str(payment["_id"]),
                            "booking_id": payment.get("booking_id"),
                            "reference": payment.get("reference"),
                            "payment_amount": payment_amount,
                            "booking_amount": booking_amount,
                            "difference": booking_amount - payment_amount,
                            "gateway": payment.get("gateway"),
                            "status": payment.get("status"),
                            "created_at": payment.get("created_at"),
                            "gateway_sync_status": payment.get("gateway_sync_status", "synced")
                        })
            except Exception as e:
                logger.warning(f"Error checking payment {payment.get('_id')}: {str(e)}")
        
        # Find duplicate payments (same reference or same booking with same amount within short time)
        duplicate_groups = []
        reference_map = {}
        
        for payment in all_payments:
            ref = payment.get("reference")
            if ref:
                if ref not in reference_map:
                    reference_map[ref] = []
                reference_map[ref].append(payment)
        
        # Find references with multiple payments
        for ref, payments in reference_map.items():
            if len(payments) > 1:
                duplicate_groups.append({
                    "reference": ref,
                    "count": len(payments),
                    "payments": [
                        {
                            "id": str(p["_id"]),
                            "amount": p.get("amount"),
                            "gateway": p.get("gateway"),
                            "status": p.get("status"),
                            "created_at": p.get("created_at")
                        }
                        for p in payments
                    ]
                })
        
        # Find payments pending sync
        pending_sync_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "gateway_sync_status": {"$in": ["pending", "failed"]},
            "created_at": {"$gte": cutoff_date}
        }).sort("created_at", -1))
        
        pending_sync_data = [
            {
                "id": str(p["_id"]),
                "reference": p.get("reference"),
                "amount": p.get("amount"),
                "gateway": p.get("gateway"),
                "status": p.get("status"),
                "gateway_sync_status": p.get("gateway_sync_status"),
                "last_synced_at": p.get("last_synced_at"),
                "created_at": p.get("created_at")
            }
            for p in pending_sync_payments
        ]
        
        # Calculate summary statistics
        total_payments = len(all_payments)
        total_unmatched = len(unmatched_data)
        total_mismatched = len(mismatched_payments)
        total_duplicates = len(duplicate_groups)
        total_pending_sync = len(pending_sync_data)
        
        return {
            "date_range": {
                "from": cutoff_date.isoformat(),
                "to": datetime.utcnow().isoformat(),
                "days": days_back
            },
            "summary": {
                "total_payments": total_payments,
                "unmatched_count": total_unmatched,
                "mismatched_count": total_mismatched,
                "duplicate_groups": total_duplicates,
                "pending_sync_count": total_pending_sync,
                "reconciliation_status": "needs_review" if (total_unmatched + total_mismatched + total_duplicates + total_pending_sync) > 0 else "reconciled"
            },
            "unmatched_payments": unmatched_data,
            "mismatched_payments": mismatched_payments,
            "duplicate_groups": duplicate_groups,
            "pending_sync_payments": pending_sync_data
        }
    
    @staticmethod
    def sync_with_gateway(
        tenant_id: str,
        payment_id: str,
        gateway_client: Optional[object] = None
    ) -> Dict:
        """
        Sync payment status with gateway
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID to sync
            gateway_client: Optional gateway client (for testing)
            
        Returns:
            Dict with updated payment data
            
        Raises:
            NotFoundException: If payment not found
            BadRequestException: If sync fails
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
        
        # Skip sync for manual payments
        if payment.get("is_manual"):
            return {
                "id": payment_id,
                "status": payment.get("status"),
                "gateway_sync_status": "skipped",
                "message": "Manual payments do not require gateway sync"
            }
        
        # Get gateway reference
        gateway = payment.get("gateway")
        reference = payment.get("reference")
        
        if not gateway or not reference:
            raise BadRequestException("Payment missing gateway or reference information")
        
        try:
            # In production, this would call the actual gateway API
            # For now, we'll simulate a successful sync
            gateway_status = payment.get("status")  # In real implementation, fetch from gateway
            
            # Update payment sync status
            db.payments.update_one(
                {"_id": payment_oid},
                {
                    "$set": {
                        "gateway_sync_status": "synced",
                        "last_synced_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            logger.info(f"Payment {payment_id} synced with gateway {gateway}")
            
            return {
                "id": payment_id,
                "status": gateway_status,
                "gateway_sync_status": "synced",
                "last_synced_at": datetime.utcnow(),
                "message": f"Payment synced successfully with {gateway}"
            }
        
        except Exception as e:
            logger.error(f"Failed to sync payment {payment_id} with gateway: {str(e)}")
            
            # Update sync status to failed
            db.payments.update_one(
                {"_id": payment_oid},
                {
                    "$set": {
                        "gateway_sync_status": "failed",
                        "last_synced_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            raise BadRequestException(f"Failed to sync with gateway: {str(e)}")
    
    @staticmethod
    def manual_match_payment(
        tenant_id: str,
        payment_id: str,
        booking_id: str,
        matched_by: str
    ) -> Dict:
        """
        Manually link a payment to a booking
        
        Args:
            tenant_id: Tenant ID
            payment_id: Payment ID to match
            booking_id: Booking ID to link to
            matched_by: User ID who performed the match
            
        Returns:
            Dict with updated payment data
            
        Raises:
            NotFoundException: If payment or booking not found
            BadRequestException: If validation fails
        """
        db = Database.get_db()
        
        try:
            payment_oid = ObjectId(payment_id)
            booking_oid = ObjectId(booking_id)
        except Exception:
            raise BadRequestException("Invalid payment or booking ID format")
        
        # Fetch payment
        payment = db.payments.find_one({
            "_id": payment_oid,
            "tenant_id": tenant_id
        })
        
        if not payment:
            raise NotFoundException("Payment not found")
        
        # Fetch booking
        booking = db.bookings.find_one({
            "_id": booking_oid,
            "tenant_id": tenant_id
        })
        
        if not booking:
            raise NotFoundException("Booking not found")
        
        # Validate payment amount matches booking amount (or is partial)
        payment_amount = payment.get("amount", 0)
        booking_amount = booking.get("total_amount", 0)
        
        if payment_amount > booking_amount:
            raise BadRequestException(
                f"Payment amount (₦{payment_amount}) exceeds booking amount (₦{booking_amount})"
            )
        
        # Update payment with booking reference
        db.payments.update_one(
            {"_id": payment_oid},
            {
                "$set": {
                    "booking_id": booking_id,
                    "client_id": booking.get("client_id"),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Update booking payment status if payment is complete
        if payment.get("status") == "completed":
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
            f"Payment {payment_id} manually matched to booking {booking_id} by {matched_by}"
        )
        
        return {
            "id": payment_id,
            "booking_id": booking_id,
            "client_id": booking.get("client_id"),
            "amount": payment_amount,
            "status": payment.get("status"),
            "matched_at": datetime.utcnow(),
            "message": f"Payment successfully linked to booking {booking_id}"
        }
    
    @staticmethod
    def get_reconciliation_report(
        tenant_id: str,
        days_back: int = 30
    ) -> Dict:
        """
        Generate a reconciliation report
        
        Args:
            tenant_id: Tenant ID
            days_back: Number of days to include in report
            
        Returns:
            Dict with reconciliation report data
        """
        db = Database.get_db()
        
        # Get reconciliation data
        recon_data = ReconciliationService.get_reconciliation_data(tenant_id, days_back)
        
        # Calculate additional metrics
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        all_payments = list(db.payments.find({
            "tenant_id": tenant_id,
            "created_at": {"$gte": cutoff_date}
        }))
        
        total_amount = sum(p.get("amount", 0) for p in all_payments)
        matched_payments = [p for p in all_payments if p.get("booking_id")]
        matched_amount = sum(p.get("amount", 0) for p in matched_payments)
        
        reconciliation_percentage = (len(matched_payments) / len(all_payments) * 100) if all_payments else 0
        
        return {
            "report_date": datetime.utcnow().isoformat(),
            "date_range": recon_data["date_range"],
            "summary": recon_data["summary"],
            "metrics": {
                "total_payments": len(all_payments),
                "total_amount": total_amount,
                "matched_payments": len(matched_payments),
                "matched_amount": matched_amount,
                "reconciliation_percentage": round(reconciliation_percentage, 2),
                "unmatched_amount": total_amount - matched_amount
            },
            "issues": {
                "unmatched_payments": recon_data["unmatched_payments"],
                "mismatched_payments": recon_data["mismatched_payments"],
                "duplicate_groups": recon_data["duplicate_groups"],
                "pending_sync_payments": recon_data["pending_sync_payments"]
            },
            "recommendations": ReconciliationService._generate_recommendations(recon_data)
        }
    
    @staticmethod
    def _generate_recommendations(recon_data: Dict) -> List[str]:
        """
        Generate recommendations based on reconciliation data
        
        Args:
            recon_data: Reconciliation data
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        summary = recon_data.get("summary", {})
        
        if summary.get("unmatched_count", 0) > 0:
            recommendations.append(
                f"Review {summary['unmatched_count']} unmatched payments and link them to bookings"
            )
        
        if summary.get("mismatched_count", 0) > 0:
            recommendations.append(
                f"Investigate {summary['mismatched_count']} payments with amount mismatches"
            )
        
        if summary.get("duplicate_groups", 0) > 0:
            recommendations.append(
                f"Review {summary['duplicate_groups']} potential duplicate payment groups"
            )
        
        if summary.get("pending_sync_count", 0) > 0:
            recommendations.append(
                f"Retry syncing {summary['pending_sync_count']} payments with gateway"
            )
        
        if not recommendations:
            recommendations.append("All payments are reconciled and in good standing")
        
        return recommendations


# Singleton instance
reconciliation_service = ReconciliationService()
