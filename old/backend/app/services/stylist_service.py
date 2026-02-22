"""
Stylist service - Business logic layer
"""
from bson import ObjectId
from datetime import datetime
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, ForbiddenException, BadRequestException

logger = logging.getLogger(__name__)


class StylistService:
    """Stylist service for handling stylist business logic"""
    
    @staticmethod
    async def get_stylists(
        tenant_id: str,
        is_active: Optional[bool] = None
    ) -> List[Dict]:
        """
        Get list of stylists for tenant with optional filtering
        
        Returns:
            List of stylist dicts
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        if is_active is not None:
            query["is_active"] = is_active
        
        stylists = list(db.stylists.find(query))
        
        return [StylistService._format_stylist_response(s) for s in stylists]
    
    @staticmethod
    async def get_by_location(tenant_id: str, location_id: str) -> List[Dict]:
        """
        Get stylists assigned to a specific location
        
        Returns:
            List of stylist dicts assigned to the location
        """
        db = Database.get_db()
        
        stylists = list(db.stylists.find({
            "tenant_id": tenant_id,
            "assigned_locations": location_id
        }))
        
        return [StylistService._format_stylist_response(s) for s in stylists]
    
    @staticmethod
    async def get_stylist(stylist_id: str, tenant_id: str) -> Dict:
        """
        Get single stylist by ID
        
        Returns:
            Dict with stylist data
        """
        db = Database.get_db()
        
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def create_stylist(
        tenant_id: str,
        name: str,
        phone: str,
        email: Optional[str] = None,
        bio: Optional[str] = None,
        photo: Optional[str] = None,
        specialties: List[str] = [],
        commission_type: Optional[str] = None,
        commission_value: Optional[float] = None,
        schedule: Optional[Dict] = None,
        assigned_locations: Optional[List[str]] = None,
        location_availability: Optional[Dict] = None
    ) -> Dict:
        """
        Create a new stylist
        
        Returns:
            Dict with created stylist data
        """
        db = Database.get_db()
        
        stylist_data = {
            "tenant_id": tenant_id,
            "name": name,
            "email": email,
            "phone": phone,
            "bio": bio,
            "photo_url": photo,
            "is_active": True,
            "specialties": specialties,
            "commission_type": commission_type,
            "commission_value": commission_value,
            "assigned_locations": assigned_locations or [],
            "location_availability": location_availability or {},
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Add schedule if provided
        if schedule:
            stylist_data["schedule"] = schedule
        
        result = db.stylists.insert_one(stylist_data)
        stylist_id = str(result.inserted_id)
        
        logger.info(f"Stylist created: {stylist_id} for tenant: {tenant_id}")
        
        # Fetch created stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def update_stylist(
        stylist_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        bio: Optional[str] = None,
        photo: Optional[str] = None,
        is_active: Optional[bool] = None,
        specialties: Optional[List[str]] = None,
        commission_type: Optional[str] = None,
        commission_value: Optional[float] = None,
        schedule: Optional[Dict] = None,
        assigned_locations: Optional[List[str]] = None,
        location_availability: Optional[Dict] = None
    ) -> Dict:
        """
        Update a stylist
        
        Returns:
            Dict with updated stylist data
        """
        db = Database.get_db()
        
        # Check stylist exists and belongs to tenant
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        if name is not None:
            update_data["name"] = name
        if email is not None:
            update_data["email"] = email
        if phone is not None:
            update_data["phone"] = phone
        if bio is not None:
            update_data["bio"] = bio
        if photo is not None:
            update_data["photo_url"] = photo
        if is_active is not None:
            update_data["is_active"] = is_active
        if specialties is not None:
            update_data["specialties"] = specialties
        if commission_type is not None:
            update_data["commission_type"] = commission_type
        if commission_value is not None:
            update_data["commission_value"] = commission_value
        if schedule is not None:
            update_data["schedule"] = schedule
        if assigned_locations is not None:
            update_data["assigned_locations"] = assigned_locations
        if location_availability is not None:
            update_data["location_availability"] = location_availability
        
        # Update stylist
        db.stylists.update_one(
            {"_id": ObjectId(stylist_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Stylist updated: {stylist_id}")
        
        # Fetch updated stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def delete_stylist(stylist_id: str, tenant_id: str) -> bool:
        """
        Delete a stylist (hard delete - completely removes from database)
        
        Returns:
            True if successful
        """
        db = Database.get_db()
        
        # Check stylist exists and belongs to tenant
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        # Hard delete - completely remove the document
        result = db.stylists.delete_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        logger.info(f"Stylist deleted (hard): {stylist_id}, deleted_count: {result.deleted_count}")
        return result.deleted_count > 0
    
    @staticmethod
    async def get_stylist_performance(stylist_id: str, tenant_id: str) -> Dict:
        """
        Get stylist performance metrics
        
        Returns comprehensive performance data including revenue, commissions,
        completed services, ratings, and rebooking rates.
        """
        db = Database.get_db()
        
        # Verify stylist exists
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Get completed bookings for this stylist
        completed_bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "status": "completed"
        }))
        
        # Calculate total revenue
        total_revenue = sum(b.get("service_price", 0.0) for b in completed_bookings)
        
        # Calculate total commission
        commission_type = stylist.get("commission_type", "percentage")
        commission_value = stylist.get("commission_value", 0)
        
        if commission_type == "percentage":
            total_commission = total_revenue * (commission_value / 100)
        elif commission_type == "fixed":
            total_commission = len(completed_bookings) * commission_value
        else:
            total_commission = 0.0
        
        # Count completed services
        completed_services = len(completed_bookings)
        
        # Get reviews for this stylist
        reviews = list(db.reviews.find({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id
        }))
        
        total_reviews = len(reviews)
        average_rating = sum(r.get("rating", 0) for r in reviews) / total_reviews if total_reviews > 0 else 0.0
        
        # Calculate rebooking rate (clients who booked more than once)
        client_booking_counts = {}
        for booking in completed_bookings:
            client_id = booking.get("client_id")
            if client_id:
                client_booking_counts[client_id] = client_booking_counts.get(client_id, 0) + 1
        
        repeat_clients = sum(1 for count in client_booking_counts.values() if count > 1)
        unique_clients = len(client_booking_counts)
        rebooking_rate = (repeat_clients / unique_clients * 100) if unique_clients > 0 else 0.0
        
        # Calculate on-time completion rate (assume completed bookings are on-time for now)
        on_time_completion_rate = 100.0 if completed_services > 0 else 0.0
        
        # Get top services
        service_counts = {}
        for booking in completed_bookings:
            service_id = booking.get("service_id")
            service_name = booking.get("service_name", "Unknown")
            if service_id:
                if service_id not in service_counts:
                    service_counts[service_id] = {"id": service_id, "name": service_name, "count": 0}
                service_counts[service_id]["count"] += 1
        
        top_services = sorted(service_counts.values(), key=lambda x: x["count"], reverse=True)[:5]
        
        # Get recent bookings (last 10)
        recent_bookings = sorted(completed_bookings, key=lambda x: x.get("booking_date", datetime.min), reverse=True)[:10]
        recent_bookings_formatted = [
            {
                "id": str(b["_id"]),
                "client_name": b.get("client_name", "Unknown"),
                "service_name": b.get("service_name", "Unknown"),
                "booking_date": b.get("booking_date").isoformat() if b.get("booking_date") else None
            }
            for b in recent_bookings
        ]
        
        return {
            "total_revenue": round(total_revenue, 2),
            "total_commission": round(total_commission, 2),
            "completed_services": completed_services,
            "average_rating": round(average_rating, 2),
            "total_reviews": total_reviews,
            "rebooking_rate": round(rebooking_rate, 2),
            "on_time_completion_rate": round(on_time_completion_rate, 2),
            "top_services": top_services,
            "recent_bookings": recent_bookings_formatted
        }
    
    @staticmethod
    async def get_stylist_commissions(
        stylist_id: str,
        tenant_id: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """
        Get stylist commission records for a date range
        
        Returns detailed commission breakdown by booking.
        """
        db = Database.get_db()
        
        # Verify stylist exists
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Parse dates - handle both YYYY-MM-DD and ISO formats
        try:
            # Try parsing as YYYY-MM-DD first
            if 'T' not in start_date:
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            else:
                start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
            
            if 'T' not in end_date:
                end_dt = datetime.strptime(end_date, '%Y-%m-%d')
                # Set to end of day for date-only format
                end_dt = end_dt.replace(hour=23, minute=59, second=59)
            else:
                end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        except ValueError:
            raise BadRequestException("Invalid date format. Use ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS)")
        
        # Get completed bookings in date range
        bookings = list(db.bookings.find({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "status": "completed",
            "booking_date": {
                "$gte": start_dt,
                "$lte": end_dt
            }
        }).sort("booking_date", -1))
        
        # Calculate commission for each booking
        commission_type = stylist.get("commission_type", "percentage")
        commission_value = stylist.get("commission_value", 0)
        
        commissions = []
        for booking in bookings:
            service_price = booking.get("service_price", 0.0)
            
            if commission_type == "percentage":
                commission_amount = service_price * (commission_value / 100)
            elif commission_type == "fixed":
                commission_amount = commission_value
            else:
                commission_amount = 0.0
            
            commissions.append({
                "id": str(booking["_id"]),
                "booking_id": str(booking["_id"]),
                "booking_date": booking.get("booking_date").isoformat() if booking.get("booking_date") else None,
                "client_name": booking.get("client_name", "Unknown"),
                "service_name": booking.get("service_name", "Unknown"),
                "service_price": round(service_price, 2),
                "commission_amount": round(commission_amount, 2),
                "commission_type": commission_type
            })
        
        return commissions
    
    @staticmethod
    async def get_stylist_attendance(
        stylist_id: str,
        tenant_id: str,
        month: str
    ) -> List[Dict]:
        """
        Get stylist attendance records for a month
        
        Returns clock-in/clock-out records and hours worked.
        """
        db = Database.get_db()
        
        # Verify stylist exists
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Parse month (format: YYYY-MM)
        try:
            year, month_num = month.split("-")
            year = int(year)
            month_num = int(month_num)
            
            # Create date range for the month
            from calendar import monthrange
            _, last_day = monthrange(year, month_num)
            
            start_date = datetime(year, month_num, 1)
            end_date = datetime(year, month_num, last_day, 23, 59, 59)
        except (ValueError, AttributeError):
            raise BadRequestException("Invalid month format. Use YYYY-MM format")
        
        # Check if attendance collection exists
        if "attendance" not in db.list_collection_names():
            return []
        
        # Get attendance records for the month (sorted by date descending - newest first)
        attendance_records = list(db.attendance.find({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "date": {
                "$gte": start_date,
                "$lte": end_date
            }
        }).sort([("date", -1)]))
        
        # Format attendance records
        formatted_records = []
        for record in attendance_records:
            clock_in = record.get("clock_in_time")
            clock_out = record.get("clock_out_time")
            
            # Calculate hours worked
            hours_worked = 0.0
            if clock_in and clock_out:
                time_diff = clock_out - clock_in
                total_seconds = time_diff.total_seconds()
                
                # Ensure we don't return negative values - if clock_out is before clock_in, set to 0
                if total_seconds < 0:
                    logger.warning(
                        f"Negative time difference detected for attendance {record['_id']}: "
                        f"clock_in={clock_in}, clock_out={clock_out}. Setting hours_worked to 0."
                    )
                    hours_worked = 0.0
                else:
                    hours_worked = round(total_seconds / 3600, 2)
            
            formatted_records.append({
                "id": str(record["_id"]),
                "date": record.get("date").isoformat() if record.get("date") else None,
                "clock_in_time": clock_in.isoformat() if clock_in else None,
                "clock_out_time": clock_out.isoformat() if clock_out else None,
                "hours_worked": round(hours_worked, 2),
                "status": record.get("status", "present")
            })
        
        return formatted_records
    
    @staticmethod
    async def clock_in(stylist_id: str, tenant_id: str) -> Dict:
        """
        Clock in a stylist
        
        Creates an attendance record with clock-in time (in local timezone).
        """
        from datetime import datetime as dt
        db = Database.get_db()
        
        # Verify stylist exists and belongs to tenant
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Use local time (browser's timezone)
        now = dt.now()
        today = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Check if already clocked in today
        existing_attendance = db.attendance.find_one({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "date": today,
            "clock_out_time": None
        })
        
        if existing_attendance:
            # Already clocked in, return existing record
            return {
                "id": str(existing_attendance["_id"]),
                "stylist_id": stylist_id,
                "date": existing_attendance["date"].isoformat(),
                "clock_in_time": existing_attendance["clock_in_time"].isoformat(),
                "clock_out_time": None,
                "status": "clocked_in",
                "message": "Already clocked in"
            }
        
        # Create new attendance record
        attendance_data = {
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "date": today,
            "clock_in_time": now,
            "clock_out_time": None,
            "hours_worked": 0.0,
            "status": "clocked_in",
            "created_at": now
        }
        
        result = db.attendance.insert_one(attendance_data)
        attendance_id = str(result.inserted_id)
        
        return {
            "id": attendance_id,
            "stylist_id": stylist_id,
            "date": today.isoformat(),
            "clock_in_time": now.isoformat(),
            "clock_out_time": None,
            "hours_worked": 0.0,
            "status": "clocked_in"
        }
    
    @staticmethod
    async def clock_out(stylist_id: str, tenant_id: str, attendance_id: str) -> Dict:
        """
        Clock out a stylist
        
        Updates attendance record with clock-out time and calculates hours worked (using local time).
        """
        from datetime import datetime as dt
        db = Database.get_db()
        
        # Verify stylist exists and belongs to tenant
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Find attendance record
        attendance = db.attendance.find_one({
            "_id": ObjectId(attendance_id),
            "tenant_id": tenant_id,
            "stylist_id": stylist_id
        })
        
        if not attendance:
            raise NotFoundException("Attendance record not found")
        
        # Check if already clocked out
        if attendance.get("clock_out_time"):
            return {
                "id": str(attendance["_id"]),
                "stylist_id": stylist_id,
                "date": attendance["date"].isoformat(),
                "clock_in_time": attendance["clock_in_time"].isoformat(),
                "clock_out_time": attendance["clock_out_time"].isoformat(),
                "hours_worked": attendance.get("hours_worked", 0),
                "status": attendance.get("status", "present"),
                "message": "Already clocked out"
            }
        
        # Update with clock-out time (using local time)
        now = dt.now()
        clock_in_time = attendance["clock_in_time"]
        
        # Calculate hours worked
        time_diff = now - clock_in_time
        hours_worked = round(time_diff.total_seconds() / 3600, 2)
        
        db.attendance.update_one(
            {"_id": ObjectId(attendance_id)},
            {
                "$set": {
                    "clock_out_time": now,
                    "hours_worked": hours_worked,
                    "status": "clocked_out",
                    "updated_at": now
                }
            }
        )
        
        return {
            "id": attendance_id,
            "stylist_id": stylist_id,
            "date": attendance["date"].isoformat(),
            "clock_in_time": clock_in_time.isoformat(),
            "clock_out_time": now.isoformat(),
            "hours_worked": hours_worked,
            "status": "clocked_out"
        }
    
    @staticmethod
    async def get_current_hours_worked(stylist_id: str, tenant_id: str) -> float:
        """
        Get current hours worked for today (if clocked in)
        
        Returns hours worked since clock-in, calculated in real-time (using local time).
        """
        from datetime import datetime as dt
        db = Database.get_db()
        
        # Verify stylist exists
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Get today's attendance record (using local time)
        now = dt.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        attendance = db.attendance.find_one({
            "tenant_id": tenant_id,
            "stylist_id": stylist_id,
            "date": {
                "$gte": today_start,
                "$lte": today_end
            },
            "clock_out_time": None
        })
        
        if not attendance:
            return 0.0
        
        # Calculate hours worked from clock-in to now
        clock_in_time = attendance["clock_in_time"]
        time_diff = now - clock_in_time
        
        # Ensure we don't return negative values
        if time_diff.total_seconds() < 0:
            return 0.0
        
        hours_worked = round(time_diff.total_seconds() / 3600, 2)
        
        return hours_worked
    
    @staticmethod
    async def assign_services(stylist_id: str, tenant_id: str, service_ids: List[str]) -> Dict:
        """
        Assign services to a stylist
        
        Updates the stylist's assigned services list.
        """
        db = Database.get_db()
        
        # Verify stylist exists and belongs to tenant
        stylist = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if not stylist:
            raise NotFoundException("Stylist not found")
        
        # Update stylist with assigned services
        db.stylists.update_one(
            {"_id": ObjectId(stylist_id)},
            {
                "$set": {
                    "assigned_services": service_ids,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Assigned {len(service_ids)} services to stylist {stylist_id}")
        
        # Fetch updated stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def assign_to_location(
        stylist_id: str,
        tenant_id: str,
        location_id: str,
        availability: Optional[Dict] = None
    ) -> Dict:
        """
        Assign a stylist to a location
        
        Returns:
            Dict with updated stylist data
        """
        db = Database.get_db()
        
        # Check stylist exists and belongs to tenant
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        # Add location to assigned_locations if not already there
        assigned_locations = stylist_doc.get("assigned_locations", [])
        if location_id not in assigned_locations:
            assigned_locations.append(location_id)
        
        # Update location_availability if provided
        location_availability = stylist_doc.get("location_availability", {})
        if availability:
            location_availability[location_id] = availability
        
        # Update stylist
        db.stylists.update_one(
            {"_id": ObjectId(stylist_id)},
            {
                "$set": {
                    "assigned_locations": assigned_locations,
                    "location_availability": location_availability,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Stylist {stylist_id} assigned to location {location_id}")
        
        # Fetch updated stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def remove_from_location(
        stylist_id: str,
        tenant_id: str,
        location_id: str
    ) -> Dict:
        """
        Remove a stylist from a location
        
        Returns:
            Dict with updated stylist data
        """
        db = Database.get_db()
        
        # Check stylist exists and belongs to tenant
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        # Remove location from assigned_locations
        assigned_locations = stylist_doc.get("assigned_locations", [])
        if location_id in assigned_locations:
            assigned_locations.remove(location_id)
        
        # Remove from location_availability
        location_availability = stylist_doc.get("location_availability", {})
        if location_id in location_availability:
            del location_availability[location_id]
        
        # Update stylist
        db.stylists.update_one(
            {"_id": ObjectId(stylist_id)},
            {
                "$set": {
                    "assigned_locations": assigned_locations,
                    "location_availability": location_availability,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Stylist {stylist_id} removed from location {location_id}")
        
        # Fetch updated stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def update_location_availability(
        stylist_id: str,
        tenant_id: str,
        location_id: str,
        availability: Dict
    ) -> Dict:
        """
        Update a stylist's availability at a specific location
        
        Returns:
            Dict with updated stylist data
        """
        db = Database.get_db()
        
        # Check stylist exists and belongs to tenant
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        # Check stylist is assigned to location
        assigned_locations = stylist_doc.get("assigned_locations", [])
        if location_id not in assigned_locations:
            raise NotFoundException("Stylist not assigned to this location")
        
        # Update location_availability
        location_availability = stylist_doc.get("location_availability", {})
        location_availability[location_id] = availability
        
        # Update stylist
        db.stylists.update_one(
            {"_id": ObjectId(stylist_id)},
            {
                "$set": {
                    "location_availability": location_availability,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        logger.info(f"Updated availability for stylist {stylist_id} at location {location_id}")
        
        # Fetch updated stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    async def upload_stylist_photo(stylist_id: str, tenant_id: str, file_bytes: bytes) -> Dict:
        """
        Upload stylist photo to Cloudinary
        
        Returns:
            Dict with updated stylist data
        """
        from app.services.cloudinary_service import upload_image
        
        db = Database.get_db()
        
        # Check stylist exists and belongs to tenant
        stylist_doc = db.stylists.find_one({
            "_id": ObjectId(stylist_id),
            "tenant_id": tenant_id
        })
        
        if stylist_doc is None:
            raise NotFoundException("Stylist not found")
        
        # Upload to Cloudinary
        photo_url = await upload_image(
            file_bytes,
            folder=f"salons/{tenant_id}/stylists",
            public_id=f"stylist_{stylist_id}"
        )
        
        # Update stylist
        db.stylists.update_one(
            {"_id": ObjectId(stylist_id)},
            {"$set": {"photo_url": photo_url, "updated_at": datetime.utcnow()}}
        )
        
        logger.info(f"Photo uploaded for stylist: {stylist_id}")
        
        # Fetch updated stylist
        stylist_doc = db.stylists.find_one({"_id": ObjectId(stylist_id)})
        return StylistService._format_stylist_response(stylist_doc)
    
    @staticmethod
    def _format_stylist_response(stylist_doc: Dict) -> Dict:
        """Format stylist document for response"""
        db = Database.get_db()
        schedule = None
        if stylist_doc.get("schedule"):
            sched = stylist_doc["schedule"]
            working_hours = sched.get("working_hours", [])
            
            # Ensure working_hours have proper format with string day names
            formatted_hours = []
            day_names = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
            
            for wh in working_hours:
                # Handle both old format (day as int) and new format (day as string)
                day = wh.get("day")
                if isinstance(day, int):
                    # Convert integer day (0-6) to day name
                    day = day_names[day] if 0 <= day < 7 else "monday"
                elif not isinstance(day, str):
                    # Skip invalid entries
                    continue
                
                formatted_hours.append({
                    "day": day,
                    "start_time": wh.get("start_time", "09:00"),
                    "end_time": wh.get("end_time", "17:00"),
                    "is_working": wh.get("is_working", True)
                })
            
            schedule = {
                "working_hours": formatted_hours,
                "break_start": sched.get("break_start"),
                "break_end": sched.get("break_end")
            }
        
        # Populate location names from location IDs
        assigned_locations = stylist_doc.get("assigned_locations", [])
        location_names = {}
        
        for loc_id in assigned_locations:
            try:
                # Handle both string IDs and ObjectId instances
                if isinstance(loc_id, str):
                    location = db.locations.find_one({"_id": ObjectId(loc_id)})
                else:
                    location = db.locations.find_one({"_id": loc_id})
                
                if location:
                    location_names[str(loc_id)] = location.get("name", str(loc_id))
                else:
                    location_names[str(loc_id)] = str(loc_id)
            except Exception as e:
                location_names[str(loc_id)] = str(loc_id)
        
        return {
            "id": str(stylist_doc["_id"]),
            "tenant_id": stylist_doc["tenant_id"],
            "name": stylist_doc["name"],
            "email": stylist_doc.get("email"),
            "phone": stylist_doc["phone"],
            "bio": stylist_doc.get("bio"),
            "photo_url": stylist_doc.get("photo_url"),
            "is_active": stylist_doc.get("is_active", True),
            "specialties": stylist_doc.get("specialties", []),
            "commission_type": stylist_doc.get("commission_type"),
            "commission_value": stylist_doc.get("commission_value"),
            "assigned_services": stylist_doc.get("assigned_services", []),
            "assigned_locations": assigned_locations,
            "location_names": location_names,
            "location_availability": stylist_doc.get("location_availability", {}),
            "schedule": schedule,
            "created_at": stylist_doc.get("created_at", datetime.utcnow()),
            "updated_at": stylist_doc.get("updated_at", datetime.utcnow())
        }


# Singleton instance
stylist_service = StylistService()
