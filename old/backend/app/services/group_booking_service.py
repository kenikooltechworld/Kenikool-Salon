"""
Group booking service for managing group bookings
"""
from datetime import datetime
from typing import Optional, List, Dict
from pymongo.database import Database as PyMongoDatabase
from bson import ObjectId


class GroupBookingService:
    """Service for managing group bookings"""
    
    def __init__(self, db: PyMongoDatabase):
        self.db = db
        self.group_bookings = db.group_bookings
        self.bookings = db.bookings
        self.clients = db.clients
        self.services = db.services
        self.stylists = db.stylists
    
    def calculate_group_discount(self, group_size: int, total_price: float) -> Dict:
        """Calculate group discount based on size"""
        discount_percentage = 0
        
        # Discount tiers
        if group_size >= 10:
            discount_percentage = 20
        elif group_size >= 7:
            discount_percentage = 15
        elif group_size >= 5:
            discount_percentage = 10
        elif group_size >= 3:
            discount_percentage = 5
        
        discount_amount = total_price * (discount_percentage / 100)
        final_price = total_price - discount_amount
        
        return {
            "discount_percentage": discount_percentage,
            "discount_amount": discount_amount,
            "final_price": final_price
        }
    
    async def validate_group_booking(
        self,
        tenant_id: str,
        members: List[Dict],
        booking_date: datetime
    ) -> Dict:
        """Validate group booking availability"""
        errors = []
        
        # Check each member's availability
        for i, member in enumerate(members):
            # Validate service exists
            service = await self.services.find_one({
                "_id": ObjectId(member["service_id"]),
                "tenant_id": tenant_id,
                "is_active": True
            })
            
            if not service:
                errors.append(f"Member {i+1}: Service not found or inactive")
                continue
            
            # Validate stylist exists and is available
            stylist = await self.stylists.find_one({
                "_id": ObjectId(member["stylist_id"]),
                "tenant_id": tenant_id,
                "is_available": True
            })
            
            if not stylist:
                errors.append(f"Member {i+1}: Stylist not found or unavailable")
                continue
            
            # Check for conflicts
            conflict = await self.bookings.find_one({
                "tenant_id": tenant_id,
                "stylist_id": member["stylist_id"],
                "booking_date": booking_date,
                "status": {"$in": ["pending", "confirmed"]}
            })
            
            if conflict:
                errors.append(f"Member {i+1}: Stylist {stylist['name']} is already booked at this time")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    async def create_individual_bookings(
        self,
        tenant_id: str,
        group_booking_id: str,
        members: List[Dict],
        booking_date: datetime
    ) -> List[str]:
        """Create individual bookings for each group member"""
        booking_ids = []
        
        for member in members:
            # Get full details
            client = await self.clients.find_one({"_id": ObjectId(member["client_id"])})
            service = await self.services.find_one({"_id": ObjectId(member["service_id"])})
            stylist = await self.stylists.find_one({"_id": ObjectId(member["stylist_id"])})
            
            if not all([client, service, stylist]):
                continue
            
            # Create individual booking
            booking_data = {
                "tenant_id": tenant_id,
                "client_id": member["client_id"],
                "client_name": client["name"],
                "client_phone": client["phone"],
                "service_id": member["service_id"],
                "service_name": service["name"],
                "service_price": service["price"],
                "stylist_id": member["stylist_id"],
                "stylist_name": stylist["name"],
                "booking_date": booking_date,
                "duration_minutes": service["duration_minutes"],
                "status": "pending",
                "notes": f"Part of group booking: {group_booking_id}",
                "group_booking_id": group_booking_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = await self.bookings.insert_one(booking_data)
            booking_ids.append(str(result.inserted_id))
        
        return booking_ids
    
    async def update_group_booking_status(
        self,
        tenant_id: str,
        group_booking_id: str,
        status: str
    ) -> bool:
        """Update group booking status and all member bookings"""
        # Update group booking
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == "confirmed":
            update_data["confirmed_at"] = datetime.utcnow()
        elif status == "completed":
            update_data["completed_at"] = datetime.utcnow()
        elif status == "cancelled":
            update_data["cancelled_at"] = datetime.utcnow()
        
        result = await self.group_bookings.update_one(
            {"_id": ObjectId(group_booking_id), "tenant_id": tenant_id},
            {"$set": update_data}
        )
        
        if result.modified_count == 0:
            return False
        
        # Update all member bookings
        await self.bookings.update_many(
            {"group_booking_id": group_booking_id, "tenant_id": tenant_id},
            {"$set": {"status": status, "updated_at": datetime.utcnow()}}
        )
        
        return True
    
    async def get_group_booking_summary(
        self,
        tenant_id: str,
        group_booking_id: str
    ) -> Dict:
        """Get detailed summary of group booking"""
        group_booking = await self.group_bookings.find_one({
            "_id": ObjectId(group_booking_id),
            "tenant_id": tenant_id
        })
        
        if not group_booking:
            return None
        
        # Get all member bookings
        member_bookings = await self.bookings.find({
            "group_booking_id": group_booking_id,
            "tenant_id": tenant_id
        }).to_list(length=None)
        
        # Calculate status summary
        status_counts = {}
        for booking in member_bookings:
            status = booking["status"]
            status_counts[status] = status_counts.get(status, 0) + 1
        
        return {
            "group_booking": group_booking,
            "member_bookings": member_bookings,
            "status_summary": status_counts,
            "total_members": len(member_bookings)
        }
    
    async def cancel_group_booking(
        self,
        tenant_id: str,
        group_booking_id: str,
        reason: Optional[str] = None
    ) -> Dict:
        """Cancel a group booking and all member bookings"""
        # Update group booking
        result = await self.update_group_booking_status(
            tenant_id=tenant_id,
            group_booking_id=group_booking_id,
            status="cancelled"
        )
        
        if not result:
            return {"success": False, "error": "Group booking not found"}
        
        # Add cancellation reason if provided
        if reason:
            await self.group_bookings.update_one(
                {"_id": ObjectId(group_booking_id)},
                {"$set": {"cancellation_reason": reason}}
            )
        
        return {
            "success": True,
            "message": "Group booking cancelled successfully"
        }
