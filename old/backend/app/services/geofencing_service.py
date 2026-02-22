"""
Geofencing service for nearby salon alerts using Mapbox Geofencing API.

This service manages geofences around salon locations and triggers notifications
when customers enter or exit geofenced areas.

Requirements:
    - 11.1: Define circular zones around salon locations
    - 11.2: Trigger notifications on zone entry
    - 11.3: Log exit events for analytics
    - 11.4: Update geofence boundaries when salon location changes
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from pymongo.database import Database
from bson import ObjectId

logger = logging.getLogger(__name__)


class GeofenceZone:
    """Represents a geofence zone around a salon"""

    def __init__(
        self,
        salon_id: str,
        latitude: float,
        longitude: float,
        radius_meters: int = 500,
        name: Optional[str] = None
    ):
        """
        Initialize a geofence zone.

        Args:
            salon_id: Salon ID
            latitude: Center latitude
            longitude: Center longitude
            radius_meters: Radius in meters (default 500m)
            name: Optional zone name
        """
        self.salon_id = salon_id
        self.latitude = latitude
        self.longitude = longitude
        self.radius_meters = radius_meters
        self.name = name or f"Salon {salon_id}"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "salon_id": self.salon_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "radius_meters": self.radius_meters,
            "name": self.name,
        }


class GeofencingService:
    """Service for managing geofences and nearby salon alerts"""

    # Default geofence radius in meters
    DEFAULT_RADIUS_METERS = 500

    def __init__(self, db: Database):
        """
        Initialize geofencing service.

        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.geofences_collection = db["geofences"]
        self.geofence_events_collection = db["geofence_events"]
        
        # Create indexes for efficient querying
        try:
            self.geofences_collection.create_index("salon_id")
            self.geofences_collection.create_index("customer_id")
            self.geofence_events_collection.create_index("customer_id")
            self.geofence_events_collection.create_index("salon_id")
            self.geofence_events_collection.create_index("event_type")
            self.geofence_events_collection.create_index("created_at")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")

    async def create_geofence(
        self,
        customer_id: str,
        salon_id: str,
        latitude: float,
        longitude: float,
        radius_meters: int = DEFAULT_RADIUS_METERS,
        enabled: bool = True
    ) -> str:
        """
        Create a geofence for a customer around a salon.

        Args:
            customer_id: Customer ID
            salon_id: Salon ID
            latitude: Salon latitude
            longitude: Salon longitude
            radius_meters: Geofence radius in meters
            enabled: Whether geofence is enabled

        Returns:
            Geofence ID

        Requirement 11.1: Define circular zones around salon locations
        """
        try:
            geofence_doc = {
                "customer_id": customer_id,
                "salon_id": salon_id,
                "latitude": latitude,
                "longitude": longitude,
                "radius_meters": radius_meters,
                "enabled": enabled,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            result = self.geofences_collection.insert_one(geofence_doc)
            
            logger.info(
                f"Created geofence {result.inserted_id} for customer {customer_id} "
                f"around salon {salon_id} with radius {radius_meters}m"
            )
            
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Error creating geofence: {e}")
            raise

    async def update_geofence(
        self,
        geofence_id: str,
        latitude: Optional[float] = None,
        longitude: Optional[float] = None,
        radius_meters: Optional[int] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a geofence.

        Args:
            geofence_id: Geofence ID
            latitude: New latitude
            longitude: New longitude
            radius_meters: New radius in meters
            enabled: New enabled status

        Returns:
            Updated geofence document

        Requirement 11.4: Update geofence boundaries when salon location changes
        """
        try:
            update_doc = {"updated_at": datetime.utcnow()}
            
            if latitude is not None:
                update_doc["latitude"] = latitude
            if longitude is not None:
                update_doc["longitude"] = longitude
            if radius_meters is not None:
                update_doc["radius_meters"] = radius_meters
            if enabled is not None:
                update_doc["enabled"] = enabled
            
            result = self.geofences_collection.find_one_and_update(
                {"_id": ObjectId(geofence_id)},
                {"$set": update_doc},
                return_document=True
            )
            
            if result:
                logger.info(f"Updated geofence {geofence_id}")
            else:
                logger.warning(f"Geofence {geofence_id} not found")
            
            return result
        
        except Exception as e:
            logger.error(f"Error updating geofence {geofence_id}: {e}")
            raise

    async def delete_geofence(self, geofence_id: str) -> None:
        """
        Delete a geofence.

        Args:
            geofence_id: Geofence ID
        """
        try:
            result = self.geofences_collection.delete_one({"_id": ObjectId(geofence_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted geofence {geofence_id}")
            else:
                logger.warning(f"Geofence {geofence_id} not found")
        
        except Exception as e:
            logger.error(f"Error deleting geofence {geofence_id}: {e}")
            raise

    async def log_geofence_entry(
        self,
        customer_id: str,
        salon_id: str,
        geofence_id: str,
        latitude: float,
        longitude: float
    ) -> str:
        """
        Log a geofence entry event.

        Args:
            customer_id: Customer ID
            salon_id: Salon ID
            geofence_id: Geofence ID
            latitude: Customer latitude at entry
            longitude: Customer longitude at entry

        Returns:
            Event ID

        Requirement 11.2: Trigger notifications on zone entry
        """
        try:
            event_doc = {
                "customer_id": customer_id,
                "salon_id": salon_id,
                "geofence_id": geofence_id,
                "event_type": "entry",
                "latitude": latitude,
                "longitude": longitude,
                "created_at": datetime.utcnow(),
            }
            
            result = self.geofence_events_collection.insert_one(event_doc)
            
            logger.info(
                f"Logged geofence entry for customer {customer_id} "
                f"at salon {salon_id}"
            )
            
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Error logging geofence entry: {e}")
            raise

    async def log_geofence_exit(
        self,
        customer_id: str,
        salon_id: str,
        geofence_id: str,
        latitude: float,
        longitude: float,
        duration_seconds: Optional[int] = None
    ) -> str:
        """
        Log a geofence exit event.

        Args:
            customer_id: Customer ID
            salon_id: Salon ID
            geofence_id: Geofence ID
            latitude: Customer latitude at exit
            longitude: Customer longitude at exit
            duration_seconds: Time spent in geofence

        Returns:
            Event ID

        Requirement 11.3: Log exit events for analytics
        """
        try:
            event_doc = {
                "customer_id": customer_id,
                "salon_id": salon_id,
                "geofence_id": geofence_id,
                "event_type": "exit",
                "latitude": latitude,
                "longitude": longitude,
                "duration_seconds": duration_seconds,
                "created_at": datetime.utcnow(),
            }
            
            result = self.geofence_events_collection.insert_one(event_doc)
            
            logger.info(
                f"Logged geofence exit for customer {customer_id} "
                f"at salon {salon_id} (duration: {duration_seconds}s)"
            )
            
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Error logging geofence exit: {e}")
            raise

    async def get_customer_geofences(self, customer_id: str) -> List[Dict[str, Any]]:
        """
        Get all geofences for a customer.

        Args:
            customer_id: Customer ID

        Returns:
            List of geofence documents
        """
        try:
            geofences = list(
                self.geofences_collection.find({"customer_id": customer_id})
            )
            
            # Convert ObjectId to string
            for geofence in geofences:
                geofence["_id"] = str(geofence["_id"])
            
            return geofences
        
        except Exception as e:
            logger.error(f"Error getting geofences for customer {customer_id}: {e}")
            raise

    async def get_salon_geofences(self, salon_id: str) -> List[Dict[str, Any]]:
        """
        Get all geofences for a salon.

        Args:
            salon_id: Salon ID

        Returns:
            List of geofence documents
        """
        try:
            geofences = list(
                self.geofences_collection.find({"salon_id": salon_id})
            )
            
            # Convert ObjectId to string
            for geofence in geofences:
                geofence["_id"] = str(geofence["_id"])
            
            return geofences
        
        except Exception as e:
            logger.error(f"Error getting geofences for salon {salon_id}: {e}")
            raise

    async def get_geofence_events(
        self,
        customer_id: Optional[str] = None,
        salon_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
        skip: int = 0
    ) -> Dict[str, Any]:
        """
        Get geofence events with optional filtering.

        Args:
            customer_id: Optional customer ID to filter by
            salon_id: Optional salon ID to filter by
            event_type: Optional event type to filter by (entry/exit)
            limit: Maximum number of results
            skip: Number of results to skip

        Returns:
            Dictionary with events and metadata
        """
        try:
            # Build query
            query = {}
            if customer_id:
                query["customer_id"] = customer_id
            if salon_id:
                query["salon_id"] = salon_id
            if event_type:
                query["event_type"] = event_type
            
            # Get total count
            total = self.geofence_events_collection.count_documents(query)
            
            # Get events
            events = list(
                self.geofence_events_collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert ObjectId to string
            for event in events:
                event["_id"] = str(event["_id"])
            
            return {
                "events": events,
                "total": total,
                "limit": limit,
                "skip": skip,
            }
        
        except Exception as e:
            logger.error(f"Error getting geofence events: {e}")
            raise

    async def get_geofence_analytics(
        self,
        salon_id: Optional[str] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get geofence analytics.

        Args:
            salon_id: Optional salon ID to filter by
            days: Number of days to analyze

        Returns:
            Dictionary with analytics data
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Build query
            query = {"created_at": {"$gte": cutoff_date}}
            if salon_id:
                query["salon_id"] = salon_id
            
            # Get total events
            total_events = self.geofence_events_collection.count_documents(query)
            
            # Get entry events
            entry_events = self.geofence_events_collection.count_documents({
                **query,
                "event_type": "entry"
            })
            
            # Get exit events
            exit_events = self.geofence_events_collection.count_documents({
                **query,
                "event_type": "exit"
            })
            
            # Get unique customers
            unique_customers = len(
                self.geofence_events_collection.distinct("customer_id", query)
            )
            
            # Get average duration
            pipeline = [
                {"$match": {**query, "event_type": "exit", "duration_seconds": {"$exists": True}}},
                {
                    "$group": {
                        "_id": None,
                        "avg_duration": {"$avg": "$duration_seconds"},
                        "max_duration": {"$max": "$duration_seconds"},
                        "min_duration": {"$min": "$duration_seconds"},
                    }
                }
            ]
            
            duration_result = list(self.geofence_events_collection.aggregate(pipeline))
            
            if duration_result:
                duration_stats = duration_result[0]
            else:
                duration_stats = {
                    "avg_duration": 0,
                    "max_duration": 0,
                    "min_duration": 0,
                }
            
            return {
                "total_events": total_events,
                "entry_events": entry_events,
                "exit_events": exit_events,
                "unique_customers": unique_customers,
                "average_duration_seconds": round(duration_stats.get("avg_duration", 0), 2),
                "max_duration_seconds": duration_stats.get("max_duration", 0),
                "min_duration_seconds": duration_stats.get("min_duration", 0),
                "period_days": days,
            }
        
        except Exception as e:
            logger.error(f"Error getting geofence analytics: {e}")
            raise

    async def update_salon_geofences(
        self,
        salon_id: str,
        new_latitude: float,
        new_longitude: float
    ) -> int:
        """
        Update all geofences for a salon when its location changes.

        Args:
            salon_id: Salon ID
            new_latitude: New salon latitude
            new_longitude: New salon longitude

        Returns:
            Number of geofences updated

        Requirement 11.4: Update geofence boundaries when salon location changes
        """
        try:
            result = self.geofences_collection.update_many(
                {"salon_id": salon_id},
                {
                    "$set": {
                        "latitude": new_latitude,
                        "longitude": new_longitude,
                        "updated_at": datetime.utcnow(),
                    }
                }
            )
            
            logger.info(
                f"Updated {result.modified_count} geofences for salon {salon_id} "
                f"to new location ({new_latitude}, {new_longitude})"
            )
            
            return result.modified_count
        
        except Exception as e:
            logger.error(f"Error updating geofences for salon {salon_id}: {e}")
            raise
