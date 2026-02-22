"""
Recurring Booking Service

Handles creation and management of recurring bookings.
"""

from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from enum import Enum

from app.database import get_database
from app.schemas.booking import RecurringBookingCreate
from app.services.conflict_detection_service import conflict_detection_service


class RecurrenceFrequency(str, Enum):
    """Recurrence frequency options"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class UpdateType(str, Enum):
    """Update type for recurring series"""
    SINGLE = "single"  # Update only this occurrence
    FUTURE = "future"  # Update this and future occurrences
    ALL = "all"  # Update all occurrences


class RecurringBookingService:
    """Service for managing recurring bookings"""
    
    def __init__(self):
        self._db = None
        self._templates_collection = None
        self._bookings_collection = None
    
    @property
    def db(self):
        if self._db is None:
            self._db = get_database()
        return self._db
    
    @property
    def templates_collection(self):
        if self._templates_collection is None:
            self._templates_collection = self.db.recurring_booking_templates
        return self._templates_collection
    
    @property
    def bookings_collection(self):
        if self._bookings_collection is None:
            self._bookings_collection = self.db.bookings
        return self._bookings_collection
    
    async def create_recurring_booking(
        self,
        booking_data: RecurringBookingCreate,
        client_id: str,
        salon_id: str,
        skip_conflicts: bool = False
    ) -> Dict[str, Any]:
        """
        Create a recurring booking series
        
        Args:
            booking_data: Recurring booking creation data
            client_id: ID of the client
            salon_id: ID of the salon
            skip_conflicts: If True, skip conflicting occurrences; if False, fail on conflict
            
        Returns:
            Dictionary with template_id, created_count, skipped_count, and conflicts
        """
        # Create template
        template_dict = {
            "client_id": client_id,
            "salon_id": salon_id,
            "stylist_id": booking_data.stylist_id,
            "service_id": booking_data.service_id,
            "start_date": booking_data.start_date,
            "frequency": booking_data.frequency,
            "end_date": booking_data.end_date,
            "occurrence_count": booking_data.occurrence_count,
            "notes": booking_data.notes,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.templates_collection.insert_one(template_dict)
        template_id = str(result.inserted_id)
        
        # Generate occurrences
        occurrences = self._generate_occurrences(
            start_date=booking_data.start_date,
            frequency=booking_data.frequency,
            end_date=booking_data.end_date,
            occurrence_count=booking_data.occurrence_count
        )
        
        created_bookings = []
        skipped_bookings = []
        conflicts = []
        
        # Get service duration for conflict checking
        service = await self.db.services.find_one({"_id": ObjectId(booking_data.service_id)})
        service_duration = service.get("duration", 60) if service else 60
        
        for occurrence_date in occurrences:
            # Check for conflicts
            has_conflict = await conflict_detection_service.check_conflicts(
                stylist_id=booking_data.stylist_id,
                booking_date=occurrence_date,
                duration=service_duration,
                salon_id=salon_id
            )
            
            if has_conflict:
                conflicts.append({
                    "date": occurrence_date,
                    "reason": "Stylist has conflicting booking"
                })
                
                if skip_conflicts:
                    skipped_bookings.append(occurrence_date)
                    continue
                else:
                    # Rollback: delete template and created bookings
                    await self.templates_collection.delete_one({"_id": ObjectId(template_id)})
                    if created_bookings:
                        await self.bookings_collection.delete_many({
                            "_id": {"$in": [ObjectId(bid) for bid in created_bookings]}
                        })
                    raise ValueError(f"Conflict detected on {occurrence_date}. Use skip_conflicts=True to skip conflicting dates.")
            
            # Create booking
            booking_dict = {
                "client_id": client_id,
                "salon_id": salon_id,
                "stylist_id": booking_data.stylist_id,
                "service_id": booking_data.service_id,
                "booking_date": occurrence_date,
                "status": "confirmed",
                "notes": booking_data.notes,
                "recurring_template_id": template_id,
                "created_at": datetime.utcnow()
            }
            
            booking_result = await self.bookings_collection.insert_one(booking_dict)
            created_bookings.append(str(booking_result.inserted_id))
        
        return {
            "template_id": template_id,
            "created_count": len(created_bookings),
            "skipped_count": len(skipped_bookings),
            "conflicts": conflicts,
            "booking_ids": created_bookings
        }
    
    def _generate_occurrences(
        self,
        start_date: datetime,
        frequency: RecurrenceFrequency,
        end_date: Optional[datetime] = None,
        occurrence_count: Optional[int] = None
    ) -> List[datetime]:
        """
        Generate occurrence dates based on frequency
        
        Args:
            start_date: Starting date
            frequency: Recurrence frequency
            end_date: End date (optional)
            occurrence_count: Number of occurrences (optional)
            
        Returns:
            List of occurrence dates
        """
        occurrences = [start_date]
        current_date = start_date
        
        # Determine stopping condition
        max_occurrences = occurrence_count if occurrence_count else 52  # Default to 1 year of weekly bookings
        
        for i in range(1, max_occurrences):
            if frequency == RecurrenceFrequency.DAILY:
                current_date = current_date + timedelta(days=1)
            elif frequency == RecurrenceFrequency.WEEKLY:
                current_date = current_date + timedelta(weeks=1)
            elif frequency == RecurrenceFrequency.MONTHLY:
                # Add one month (approximate)
                current_date = current_date + timedelta(days=30)
            
            # Check if we've exceeded end_date
            if end_date and current_date > end_date:
                break
            
            occurrences.append(current_date)
        
        return occurrences
    
    async def update_recurring_series(
        self,
        template_id: str,
        update_type: UpdateType,
        booking_id: Optional[str] = None,
        update_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Update recurring booking series
        
        Args:
            template_id: ID of the recurring template
            update_type: Type of update (single, future, all)
            booking_id: ID of the specific booking (required for single/future)
            update_data: Data to update
            
        Returns:
            Dictionary with updated_count
        """
        if not update_data:
            update_data = {}
        
        update_data["updated_at"] = datetime.utcnow()
        
        if update_type == UpdateType.SINGLE:
            if not booking_id:
                raise ValueError("booking_id required for single update")
            
            result = await self.bookings_collection.update_one(
                {"_id": ObjectId(booking_id)},
                {"$set": update_data}
            )
            return {"updated_count": result.modified_count}
        
        elif update_type == UpdateType.FUTURE:
            if not booking_id:
                raise ValueError("booking_id required for future update")
            
            # Get the booking date
            booking = await self.bookings_collection.find_one({"_id": ObjectId(booking_id)})
            if not booking:
                raise ValueError(f"Booking {booking_id} not found")
            
            # Update this and future bookings
            result = await self.bookings_collection.update_many(
                {
                    "recurring_template_id": template_id,
                    "booking_date": {"$gte": booking["booking_date"]}
                },
                {"$set": update_data}
            )
            return {"updated_count": result.modified_count}
        
        elif update_type == UpdateType.ALL:
            # Update template
            await self.templates_collection.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": update_data}
            )
            
            # Update all bookings
            result = await self.bookings_collection.update_many(
                {"recurring_template_id": template_id},
                {"$set": update_data}
            )
            return {"updated_count": result.modified_count}
        
        else:
            raise ValueError(f"Invalid update_type: {update_type}")
    
    async def delete_recurring_series(
        self,
        template_id: str,
        update_type: UpdateType,
        booking_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Delete recurring booking series
        
        Args:
            template_id: ID of the recurring template
            update_type: Type of deletion (single, future, all)
            booking_id: ID of the specific booking (required for single/future)
            
        Returns:
            Dictionary with deleted_count
        """
        if update_type == UpdateType.SINGLE:
            if not booking_id:
                raise ValueError("booking_id required for single deletion")
            
            result = await self.bookings_collection.delete_one({"_id": ObjectId(booking_id)})
            return {"deleted_count": result.deleted_count}
        
        elif update_type == UpdateType.FUTURE:
            if not booking_id:
                raise ValueError("booking_id required for future deletion")
            
            # Get the booking date
            booking = await self.bookings_collection.find_one({"_id": ObjectId(booking_id)})
            if not booking:
                raise ValueError(f"Booking {booking_id} not found")
            
            # Delete this and future bookings
            result = await self.bookings_collection.delete_many(
                {
                    "recurring_template_id": template_id,
                    "booking_date": {"$gte": booking["booking_date"]}
                }
            )
            
            # Deactivate template if no more bookings
            remaining = await self.bookings_collection.count_documents(
                {"recurring_template_id": template_id}
            )
            if remaining == 0:
                await self.templates_collection.update_one(
                    {"_id": ObjectId(template_id)},
                    {"$set": {"is_active": False}}
                )
            
            return {"deleted_count": result.deleted_count}
        
        elif update_type == UpdateType.ALL:
            # Delete all bookings
            result = await self.bookings_collection.delete_many(
                {"recurring_template_id": template_id}
            )
            
            # Delete template
            await self.templates_collection.delete_one({"_id": ObjectId(template_id)})
            
            return {"deleted_count": result.deleted_count}
        
        else:
            raise ValueError(f"Invalid update_type: {update_type}")
    
    async def get_template(self, template_id: str) -> Optional[Dict[str, Any]]:
        """Get recurring booking template by ID"""
        template = await self.templates_collection.find_one({"_id": ObjectId(template_id)})
        if template:
            template["_id"] = str(template["_id"])
        return template
    
    async def get_templates_for_client(
        self,
        client_id: str,
        salon_id: str,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all recurring booking templates for a client"""
        query = {"client_id": client_id, "salon_id": salon_id}
        if active_only:
            query["is_active"] = True
        
        cursor = self.templates_collection.find(query).sort("created_at", -1)
        templates = await cursor.to_list(length=100)
        
        for template in templates:
            template["_id"] = str(template["_id"])
        
        return templates


# Singleton instance
recurring_booking_service = RecurringBookingService()
