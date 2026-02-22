"""
Package Booking Integration Service - Handles package credit reservation and redemption for bookings
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class PackageBookingIntegrationService:
    """Service for integrating package credits with booking system"""

    @staticmethod
    def check_available_credits(
        client_id: str,
        service_id: str,
        tenant_id: str
    ) -> List[Dict]:
        """
        Check if client has available package credits for a service
        
        Requirements: 14.1, 14.2
        
        Args:
            client_id: Client ID
            service_id: Service ID
            tenant_id: Tenant ID
            
        Returns:
            List of available service credits for the service
        """
        db = Database.get_db()
        
        # Find active packages for client
        packages = list(db.package_purchases.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
            "status": "active",
            "expiration_date": {"$gt": datetime.utcnow()}
        }))
        
        if not packages:
            return []
        
        # Get service credits for these packages
        package_ids = [p["_id"] for p in packages]
        credits = list(db.service_credits.find({
            "purchase_id": {"$in": package_ids},
            "service_id": service_id,
            "remaining_quantity": {"$gt": 0},
            "status": {"$in": ["available", "reserved"]}
        }))
        
        return [PackageBookingIntegrationService._format_credit(c) for c in credits]

    @staticmethod
    def reserve_credit(
        credit_id: str,
        booking_id: str,
        tenant_id: str
    ) -> Dict:
        """
        Reserve a service credit for a booking
        
        Requirements: 14.3
        
        Args:
            credit_id: Service credit ID
            booking_id: Booking ID
            tenant_id: Tenant ID
            
        Returns:
            Updated credit record
        """
        db = Database.get_db()
        
        # Get the credit
        credit = db.service_credits.find_one({
            "_id": ObjectId(credit_id),
            "tenant_id": tenant_id
        })
        
        if not credit:
            raise NotFoundException("Service credit not found")
        
        if credit["remaining_quantity"] <= 0:
            raise BadRequestException("No remaining credits for this service")
        
        # Create reservation
        reservation = {
            "_id": ObjectId(),
            "credit_id": ObjectId(credit_id),
            "booking_id": booking_id,
            "reserved_at": datetime.utcnow(),
            "expires_at": datetime.utcnow() + __import__('datetime').timedelta(hours=24),
            "status": "active"
        }
        
        db.credit_reservations.insert_one(reservation)
        
        # Update credit status to reserved if not already
        if credit["status"] == "available":
            db.service_credits.update_one(
                {"_id": ObjectId(credit_id)},
                {"$set": {"status": "reserved"}}
            )
            credit["status"] = "reserved"
        
        return PackageBookingIntegrationService._format_credit(credit)

    @staticmethod
    def release_credit(
        credit_id: str,
        booking_id: str,
        tenant_id: str
    ) -> Dict:
        """
        Release a reserved credit back to available status
        
        Requirements: 14.5
        
        Args:
            credit_id: Service credit ID
            booking_id: Booking ID
            tenant_id: Tenant ID
            
        Returns:
            Updated credit record
        """
        db = Database.get_db()
        
        # Get the credit
        credit = db.service_credits.find_one({
            "_id": ObjectId(credit_id),
            "tenant_id": tenant_id
        })
        
        if not credit:
            raise NotFoundException("Service credit not found")
        
        # Find and remove the reservation
        reservation = db.credit_reservations.find_one({
            "credit_id": ObjectId(credit_id),
            "booking_id": booking_id,
            "status": "active"
        })
        
        if reservation:
            db.credit_reservations.update_one(
                {"_id": reservation["_id"]},
                {"$set": {"status": "released"}}
            )
        
        # Check if there are any other active reservations
        active_reservations = db.credit_reservations.find_one({
            "credit_id": ObjectId(credit_id),
            "status": "active"
        })
        
        # If no active reservations, set status back to available
        if not active_reservations:
            db.service_credits.update_one(
                {"_id": ObjectId(credit_id)},
                {"$set": {"status": "available"}}
            )
            credit["status"] = "available"
        
        return PackageBookingIntegrationService._format_credit(credit)

    @staticmethod
    def redeem_credit_for_booking(
        credit_id: str,
        booking_id: str,
        tenant_id: str,
        staff_id: str
    ) -> Dict:
        """
        Redeem a service credit for a completed booking
        
        Requirements: 14.4
        
        Args:
            credit_id: Service credit ID
            booking_id: Booking ID
            tenant_id: Tenant ID
            staff_id: Staff member ID who processed the redemption
            
        Returns:
            Redemption transaction record
        """
        db = Database.get_db()
        
        # Get the credit
        credit = db.service_credits.find_one({
            "_id": ObjectId(credit_id),
            "tenant_id": tenant_id
        })
        
        if not credit:
            raise NotFoundException("Service credit not found")
        
        if credit["remaining_quantity"] <= 0:
            raise BadRequestException("No remaining credits for this service")
        
        # Get the booking to verify it exists
        booking = db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id
        })
        
        if not booking:
            raise NotFoundException("Booking not found")
        
        # Decrement the credit
        db.service_credits.update_one(
            {"_id": ObjectId(credit_id)},
            {
                "$inc": {"remaining_quantity": -1},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        
        # Mark reservation as redeemed
        db.credit_reservations.update_one(
            {
                "credit_id": ObjectId(credit_id),
                "booking_id": booking_id,
                "status": "active"
            },
            {"$set": {"status": "redeemed"}}
        )
        
        # Create redemption transaction
        redemption = {
            "_id": ObjectId(),
            "purchase_id": credit["purchase_id"],
            "credit_id": ObjectId(credit_id),
            "service_id": credit["service_id"],
            "client_id": booking["client_id"],
            "booking_id": booking_id,
            "redeemed_by_staff_id": staff_id,
            "redemption_date": datetime.utcnow(),
            "service_value": credit["service_price"],
            "tenant_id": tenant_id,
            "created_at": datetime.utcnow()
        }
        
        db.redemption_transactions.insert_one(redemption)
        
        # Update credit status if all credits are redeemed
        updated_credit = db.service_credits.find_one({"_id": ObjectId(credit_id)})
        if updated_credit["remaining_quantity"] == 0:
            db.service_credits.update_one(
                {"_id": ObjectId(credit_id)},
                {"$set": {"status": "redeemed"}}
            )
        
        return {
            "_id": str(redemption["_id"]),
            "purchase_id": str(redemption["purchase_id"]),
            "credit_id": str(redemption["credit_id"]),
            "service_id": redemption["service_id"],
            "client_id": redemption["client_id"],
            "booking_id": booking_id,
            "redeemed_by_staff_id": staff_id,
            "redemption_date": redemption["redemption_date"].isoformat(),
            "service_value": redemption["service_value"]
        }

    @staticmethod
    def get_booking_package_info(
        booking_id: str,
        tenant_id: str
    ) -> Optional[Dict]:
        """
        Get package information for a booking if it was paid via package credits
        
        Requirements: 14.6
        
        Args:
            booking_id: Booking ID
            tenant_id: Tenant ID
            
        Returns:
            Package info dict or None if not paid via package
        """
        db = Database.get_db()
        
        # Find redemption transaction for this booking
        redemption = db.redemption_transactions.find_one({
            "booking_id": booking_id,
            "tenant_id": tenant_id
        })
        
        if not redemption:
            return None
        
        # Get the package purchase
        package = db.package_purchases.find_one({
            "_id": redemption["purchase_id"]
        })
        
        if not package:
            return None
        
        # Get the package definition
        package_def = db.package_definitions.find_one({
            "_id": package["package_definition_id"]
        })
        
        if not package_def:
            return None
        
        # Get remaining credits for this service
        credit = db.service_credits.find_one({
            "_id": redemption["credit_id"]
        })
        
        return {
            "package_id": str(package["_id"]),
            "package_name": package_def.get("name"),
            "service_id": redemption["service_id"],
            "service_value": redemption["service_value"],
            "remaining_credits": credit["remaining_quantity"] if credit else 0,
            "redemption_date": redemption["redemption_date"].isoformat()
        }

    @staticmethod
    def _format_credit(credit: Dict) -> Dict:
        """Format credit document for API response"""
        return {
            "_id": str(credit["_id"]),
            "purchase_id": str(credit["purchase_id"]),
            "service_id": credit["service_id"],
            "service_name": credit.get("service_name"),
            "service_price": credit.get("service_price"),
            "initial_quantity": credit["initial_quantity"],
            "remaining_quantity": credit["remaining_quantity"],
            "reserved_quantity": credit.get("reserved_quantity", 0),
            "status": credit["status"]
        }
