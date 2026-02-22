from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
from app.database import Database
from app.services.priority_calculator_service import PriorityCalculatorService
import uuid
import re


class WaitlistService:
    
    @staticmethod
    def add_to_waitlist(
        tenant_id: str,
        client_name: str,
        client_email: str,
        client_phone: str,
        service_id: str,
        preferred_date: Optional[str] = None,
        location_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict:
        """Add client to waitlist"""
        db = Database.get_db()
        
        # Check if already on waitlist
        existing = db.waitlist.find_one({
            "tenant_id": tenant_id,
            "client_email": client_email,
            "service_id": ObjectId(service_id),
            "status": "waiting"
        })
        
        if existing:
            raise ValueError("Already on waitlist for this service")
        
        # Generate unique access token
        access_token = str(uuid.uuid4())
        
        waitlist_entry = {
            "tenant_id": tenant_id,
            "client_name": client_name,
            "client_email": client_email,
            "client_phone": client_phone,
            "service_id": ObjectId(service_id),
            "preferred_date": preferred_date,
            "location_id": location_id,
            "notes": notes,
            "status": "waiting",
            "priority_score": 0.0,
            "access_token": access_token,
            "position": db.waitlist.count_documents({
                "tenant_id": tenant_id,
                "service_id": ObjectId(service_id),
                "status": "waiting"
            }) + 1,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.waitlist.insert_one(waitlist_entry)
        waitlist_entry["_id"] = str(result.inserted_id)
        
        return waitlist_entry
    
    @staticmethod
    def get_waitlist_entries(
        tenant_id: str,
        status: Optional[str] = None,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        location_id: Optional[str] = None,
        search_query: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        sort_by: str = "priority",
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, any]:
        """
        Get waitlist entries with advanced filtering and pagination.
        
        Args:
            tenant_id: Tenant ID for isolation
            status: Filter by status (waiting, notified, booked, cancelled, expired)
            service_id: Filter by service ID
            stylist_id: Filter by stylist ID
            location_id: Filter by location ID
            search_query: Search by client name or phone (case-insensitive partial match)
            date_from: Filter entries created from this date
            date_to: Filter entries created until this date
            sort_by: Sort by 'priority', 'created_at', or 'updated_at'
            limit: Number of entries to return (pagination)
            offset: Number of entries to skip (pagination)
            
        Returns:
            Dict with 'entries' list and 'total' count
        """
        db = Database.get_db()
        
        # Build query
        query = {"tenant_id": tenant_id}
        
        # Status filter
        if status:
            query["status"] = status
        
        # Service filter
        if service_id:
            try:
                query["service_id"] = ObjectId(service_id)
            except Exception:
                query["service_id"] = service_id
        
        # Stylist filter
        if stylist_id:
            query["stylist_id"] = stylist_id
        
        # Location filter
        if location_id:
            query["location_id"] = location_id
        
        # Search filter (client name or phone)
        if search_query:
            # Case-insensitive partial match for name or phone
            search_pattern = re.compile(search_query, re.IGNORECASE)
            query["$or"] = [
                {"client_name": {"$regex": search_pattern}},
                {"client_phone": {"$regex": search_pattern}}
            ]
        
        # Date range filter
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            if date_query:
                query["created_at"] = date_query
        
        # Get total count before pagination
        total = db.waitlist.count_documents(query)
        
        # Determine sort order
        sort_field = "created_at"
        sort_order = -1  # Descending (newest first)
        
        if sort_by == "priority":
            sort_field = "priority_score"
            sort_order = -1  # Highest priority first
        elif sort_by == "created_at":
            sort_field = "created_at"
            sort_order = -1  # Newest first
        elif sort_by == "updated_at":
            sort_field = "updated_at"
            sort_order = -1  # Most recently updated first
        
        # Execute query with sorting and pagination
        entries = list(
            db.waitlist.find(query)
            .sort(sort_field, sort_order)
            .skip(offset)
            .limit(limit)
        )
        
        # Compute priority scores for each entry
        for entry in entries:
            entry["priority_score"] = PriorityCalculatorService.calculate_priority(entry)
            # Convert ObjectId to string for JSON serialization
            if "_id" in entry:
                entry["_id"] = str(entry["_id"])
            if "service_id" in entry and isinstance(entry["service_id"], ObjectId):
                entry["service_id"] = str(entry["service_id"])
        
        return {
            "entries": entries,
            "total": total,
            "limit": limit,
            "offset": offset
        }
    
    @staticmethod
    def get_waitlist(tenant_id: str, service_id: Optional[str] = None) -> List[Dict]:
        """Get waitlist (legacy method for backward compatibility)"""
        db = Database.get_db()
        
        query = {
            "tenant_id": tenant_id,
            "status": "waiting"
        }
        
        if service_id:
            query["service_id"] = ObjectId(service_id)
        
        waitlist = list(db.waitlist.find(query).sort("position", 1))
        
        return waitlist
    
    @staticmethod
    def get_entry_by_token(token: str) -> Optional[Dict]:
        """
        Get waitlist entry by access token (for client self-service).
        
        Args:
            token: Access token
            
        Returns:
            Waitlist entry or None if not found
        """
        db = Database.get_db()
        entry = db.waitlist.find_one({"access_token": token})
        
        if entry:
            entry["_id"] = str(entry["_id"])
            if "service_id" in entry and isinstance(entry["service_id"], ObjectId):
                entry["service_id"] = str(entry["service_id"])
        
        return entry
    
    @staticmethod
    def update_client_info(
        token: str,
        client_name: Optional[str] = None,
        client_phone: Optional[str] = None,
        client_email: Optional[str] = None
    ) -> Optional[Dict]:
        """
        Update client information via access token.
        
        Args:
            token: Access token
            client_name: New client name
            client_phone: New client phone
            client_email: New client email
            
        Returns:
            Updated entry or None if not found
        """
        db = Database.get_db()
        
        # Find entry by token
        entry = db.waitlist.find_one({"access_token": token})
        if not entry:
            return None
        
        # Check if entry is already booked or cancelled
        if entry["status"] in ["booked", "cancelled", "expired"]:
            raise ValueError(f"Cannot update entry with status: {entry['status']}")
        
        # Build update dict
        update_dict = {"updated_at": datetime.utcnow()}
        if client_name:
            update_dict["client_name"] = client_name
        if client_phone:
            update_dict["client_phone"] = client_phone
        if client_email:
            update_dict["client_email"] = client_email
        
        # Update entry
        result = db.waitlist.find_one_and_update(
            {"access_token": token},
            {"$set": update_dict},
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            if "service_id" in result and isinstance(result["service_id"], ObjectId):
                result["service_id"] = str(result["service_id"])
        
        return result
    
    @staticmethod
    def cancel_by_token(token: str) -> Optional[Dict]:
        """
        Cancel waitlist entry via access token.
        
        Args:
            token: Access token
            
        Returns:
            Updated entry or None if not found
        """
        db = Database.get_db()
        
        # Find entry by token
        entry = db.waitlist.find_one({"access_token": token})
        if not entry:
            return None
        
        # Check if entry is already booked or cancelled
        if entry["status"] in ["booked", "cancelled", "expired"]:
            raise ValueError(f"Cannot cancel entry with status: {entry['status']}")
        
        # Update status to cancelled
        result = db.waitlist.find_one_and_update(
            {"access_token": token},
            {
                "$set": {
                    "status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            },
            return_document=True
        )
        
        if result:
            result["_id"] = str(result["_id"])
            if "service_id" in result and isinstance(result["service_id"], ObjectId):
                result["service_id"] = str(result["service_id"])
        
        return result
    
    @staticmethod
    def notify_from_waitlist(tenant_id: str, service_id: str) -> Dict:
        """Notify next person on waitlist"""
        db = Database.get_db()
        
        # Get first person on waitlist
        entry = db.waitlist.find_one({
            "tenant_id": tenant_id,
            "service_id": ObjectId(service_id),
            "status": "waiting"
        }, sort=[("position", 1)])
        
        if not entry:
            return {"status": "no_one_to_notify"}
        
        # Update status
        db.waitlist.update_one(
            {"_id": entry["_id"]},
            {
                "$set": {
                    "status": "notified",
                    "notified_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        # Send notification
        try:
            from app.tasks.reminder_tasks import send_waitlist_notification
            send_waitlist_notification.delay(str(entry["_id"]))
        except Exception as e:
            pass
        
        return {
            "status": "notified",
            "client_email": entry.get("client_email"),
            "client_name": entry.get("client_name")
        }
    
    @staticmethod
    def remove_from_waitlist(tenant_id: str, waitlist_id: str) -> bool:
        """Remove from waitlist"""
        db = Database.get_db()
        
        result = db.waitlist.update_one(
            {
                "_id": ObjectId(waitlist_id),
                "tenant_id": tenant_id
            },
            {
                "$set": {
                    "status": "cancelled",
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def get_waitlist_stats(tenant_id: str) -> Dict:
        """Get waitlist statistics"""
        db = Database.get_db()
        
        total_waiting = db.waitlist.count_documents({
            "tenant_id": tenant_id,
            "status": "waiting"
        })
        
        total_notified = db.waitlist.count_documents({
            "tenant_id": tenant_id,
            "status": "notified"
        })
        
        # Get services with most waitlist entries
        pipeline = [
            {
                "$match": {
                    "tenant_id": tenant_id,
                    "status": "waiting"
                }
            },
            {
                "$group": {
                    "_id": "$service_id",
                    "count": {"$sum": 1}
                }
            },
            {
                "$sort": {"count": -1}
            },
            {
                "$limit": 10
            }
        ]
        
        top_services = list(db.waitlist.aggregate(pipeline))
        
        return {
            "total_waiting": total_waiting,
            "total_notified": total_notified,
            "top_services": top_services
        }
    
    @staticmethod
    def bulk_update_status(
        waitlist_ids: List[str],
        tenant_id: str,
        status: str
    ) -> Dict[str, any]:
        """
        Bulk update status for multiple waitlist entries.
        
        Args:
            waitlist_ids: List of waitlist entry IDs to update
            tenant_id: Tenant ID for isolation
            status: Target status (waiting, notified, booked, cancelled, expired)
            
        Returns:
            Dict with success_count, failure_count, and failures list
            
        Requirements: 9.1, 9.4, 9.5
        """
        db = Database.get_db()
        
        # Validate status
        valid_statuses = ["waiting", "notified", "booked", "cancelled", "expired"]
        if status not in valid_statuses:
            raise ValueError(f"Invalid status: {status}. Must be one of {valid_statuses}")
        
        success_count = 0
        failure_count = 0
        failures = []
        
        # Process each entry independently
        for waitlist_id in waitlist_ids:
            try:
                # Validate ObjectId format
                try:
                    obj_id = ObjectId(waitlist_id)
                except Exception:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Invalid waitlist ID format"
                    })
                    failure_count += 1
                    continue
                
                # Update entry
                result = db.waitlist.update_one(
                    {
                        "_id": obj_id,
                        "tenant_id": tenant_id
                    },
                    {
                        "$set": {
                            "status": status,
                            "updated_at": datetime.utcnow(),
                            # Record notification timestamp if transitioning to notified
                            **({"notified_at": datetime.utcnow()} if status == "notified" else {})
                        }
                    }
                )
                
                if result.matched_count == 0:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Entry not found or does not belong to tenant"
                    })
                    failure_count += 1
                elif result.modified_count > 0:
                    success_count += 1
                else:
                    # Entry exists but was not modified (already had this status)
                    success_count += 1
                    
            except Exception as e:
                failures.append({
                    "id": waitlist_id,
                    "error": str(e)
                })
                failure_count += 1
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "failures": failures
        }
    
    @staticmethod
    def bulk_delete(
        waitlist_ids: List[str],
        tenant_id: str
    ) -> Dict[str, any]:
        """
        Bulk delete multiple waitlist entries.
        
        Args:
            waitlist_ids: List of waitlist entry IDs to delete
            tenant_id: Tenant ID for isolation
            
        Returns:
            Dict with success_count, failure_count, and failures list
            
        Requirements: 9.2, 9.4, 9.5
        """
        db = Database.get_db()
        
        success_count = 0
        failure_count = 0
        failures = []
        
        # Process each entry independently
        for waitlist_id in waitlist_ids:
            try:
                # Validate ObjectId format
                try:
                    obj_id = ObjectId(waitlist_id)
                except Exception:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Invalid waitlist ID format"
                    })
                    failure_count += 1
                    continue
                
                # Delete entry
                result = db.waitlist.delete_one(
                    {
                        "_id": obj_id,
                        "tenant_id": tenant_id
                    }
                )
                
                if result.deleted_count > 0:
                    success_count += 1
                else:
                    failures.append({
                        "id": waitlist_id,
                        "error": "Entry not found or does not belong to tenant"
                    })
                    failure_count += 1
                    
            except Exception as e:
                failures.append({
                    "id": waitlist_id,
                    "error": str(e)
                })
                failure_count += 1
        
        return {
            "success_count": success_count,
            "failure_count": failure_count,
            "failures": failures
        }


# Singleton instance
waitlist_service = WaitlistService()
