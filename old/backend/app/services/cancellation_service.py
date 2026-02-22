"""
Cancellation Service
Handles booking cancellation management
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class CancellationService:
    """Service for managing booking cancellations"""

    @staticmethod
    def record_cancellation(
        db,
        tenant_id: str,
        booking_id: str,
        reason: str,
        category: str,
        notes: Optional[str] = None
    ) -> Dict:
        """
        Record a booking cancellation
        
        Requirements: 11.1, 11.2, 11.3, 11.4, 11.5
        """
        # Verify booking exists
        booking = db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not booking:
            raise NotFoundException("Booking not found")
        
        # Create cancellation record
        cancellation_data = {
            "tenant_id": ObjectId(tenant_id),
            "booking_id": ObjectId(booking_id),
            "reason": reason,
            "category": category,
            "notes": notes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.cancellations.insert_one(cancellation_data)
        cancellation_id = str(result.inserted_id)
        
        logger.info(f"Cancellation recorded: {cancellation_id} for booking: {booking_id}")
        
        # Update booking status
        db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {
                "$set": {
                    "status": "cancelled",
                    "cancellation_id": ObjectId(cancellation_id),
                    "cancelled_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return CancellationService._format_cancellation_response(
            db.cancellations.find_one({"_id": ObjectId(cancellation_id)})
        )
    
    @staticmethod
    def get_cancellation(
        db,
        tenant_id: str,
        cancellation_id: str
    ) -> Optional[Dict]:
        """Get a specific cancellation record"""
        cancellation = db.cancellations.find_one({
            "_id": ObjectId(cancellation_id),
            "tenant_id": ObjectId(tenant_id)
        })
        if not cancellation:
            return None
        return CancellationService._format_cancellation_response(cancellation)
    
    @staticmethod
    def get_booking_cancellation(
        db,
        tenant_id: str,
        booking_id: str
    ) -> Optional[Dict]:
        """Get cancellation record for a booking"""
        cancellation = db.cancellations.find_one({
            "tenant_id": ObjectId(tenant_id),
            "booking_id": ObjectId(booking_id)
        })
        if not cancellation:
            return None
        return CancellationService._format_cancellation_response(cancellation)
    
    @staticmethod
    def get_client_cancellations(
        db,
        tenant_id: str,
        client_id: str,
        skip: int = 0,
        limit: int = 10
    ) -> Dict:
        """Get all cancellations for a client"""
        # Get all bookings for client
        bookings = list(db.bookings.find({
            "tenant_id": ObjectId(tenant_id),
            "client_id": ObjectId(client_id)
        }))
        booking_ids = [b["_id"] for b in bookings]
        
        # Get cancellations for those bookings
        cancellations = list(db.cancellations.find({
            "tenant_id": ObjectId(tenant_id),
            "booking_id": {"$in": booking_ids}
        }).skip(skip).limit(limit))
        
        total = db.cancellations.count_documents({
            "tenant_id": ObjectId(tenant_id),
            "booking_id": {"$in": booking_ids}
        })
        
        return {
            "client_id": client_id,
            "cancellations": [CancellationService._format_cancellation_response(c) for c in cancellations],
            "total": total,
            "skip": skip,
            "limit": limit
        }
    
    @staticmethod
    def get_cancellation_reasons(db, tenant_id: str) -> List[str]:
        """Get list of common cancellation reasons"""
        reasons = db.cancellation_reasons.find_one({
            "tenant_id": ObjectId(tenant_id)
        })
        if not reasons:
            return [
                "Customer requested",
                "Stylist unavailable",
                "Scheduling conflict",
                "No-show",
                "Other"
            ]
        return reasons.get("reasons", [])
    
    @staticmethod
    def get_cancellation_categories(db, tenant_id: str) -> List[str]:
        """Get list of cancellation categories"""
        return [
            "customer_initiated",
            "business_initiated",
            "no_show",
            "system_initiated"
        ]
    
    @staticmethod
    def _format_cancellation_response(cancellation_doc: Dict) -> Dict:
        """Format cancellation document for API response"""
        if not cancellation_doc:
            return None
        
        return {
            "id": str(cancellation_doc.get("_id")),
            "booking_id": str(cancellation_doc.get("booking_id")),
            "reason": cancellation_doc.get("reason"),
            "category": cancellation_doc.get("category"),
            "notes": cancellation_doc.get("notes"),
            "created_at": cancellation_doc.get("created_at"),
            "updated_at": cancellation_doc.get("updated_at")
        }
