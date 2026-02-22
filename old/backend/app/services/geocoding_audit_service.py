"""
Geocoding audit service for logging coordinate differences between Mapbox and Nominatim.

This service tracks when Mapbox geocoding produces different results than Nominatim,
providing audit trail for location data quality and migration tracking.

Requirements:
    - 8.5: Log coordinate differences when Mapbox differs from Nominatim
"""

import logging
from typing import Dict, Any, Optional, Tuple
from datetime import datetime
from pymongo.database import Database
from bson import ObjectId

logger = logging.getLogger(__name__)


class GeocodingAuditService:
    """Service for auditing geocoding results and coordinate differences"""

    def __init__(self, db: Database):
        """
        Initialize geocoding audit service.

        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.audit_collection = db["geocoding_audit_log"]
        
        # Create index for efficient querying
        try:
            self.audit_collection.create_index("location_id")
            self.audit_collection.create_index("created_at")
            self.audit_collection.create_index("difference_km")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")

    async def log_coordinate_difference(
        self,
        location_id: str,
        address: str,
        old_coordinates: Tuple[float, float],
        new_coordinates: Tuple[float, float],
        old_source: str = "nominatim",
        new_source: str = "mapbox",
        old_formatted_address: Optional[str] = None,
        new_formatted_address: Optional[str] = None,
        old_confidence: Optional[float] = None,
        new_confidence: Optional[float] = None,
    ) -> str:
        """
        Log a coordinate difference between two geocoding sources.

        Args:
            location_id: Location ID
            address: Address that was geocoded
            old_coordinates: Tuple of (latitude, longitude) from old source
            new_coordinates: Tuple of (latitude, longitude) from new source
            old_source: Source of old coordinates (default: nominatim)
            new_source: Source of new coordinates (default: mapbox)
            old_formatted_address: Formatted address from old source
            new_formatted_address: Formatted address from new source
            old_confidence: Confidence score from old source
            new_confidence: Confidence score from new source

        Returns:
            Audit log entry ID

        Requirement 8.5: Log coordinate differences for audit
        """
        from app.utils.distance import calculate_haversine_distance

        try:
            # Calculate distance between old and new coordinates
            difference_km = calculate_haversine_distance(old_coordinates, new_coordinates)
            
            # Create audit log entry
            audit_entry = {
                "location_id": location_id,
                "address": address,
                "old_coordinates": {
                    "latitude": old_coordinates[0],
                    "longitude": old_coordinates[1],
                },
                "new_coordinates": {
                    "latitude": new_coordinates[0],
                    "longitude": new_coordinates[1],
                },
                "difference_km": difference_km,
                "old_source": old_source,
                "new_source": new_source,
                "old_formatted_address": old_formatted_address,
                "new_formatted_address": new_formatted_address,
                "old_confidence": old_confidence,
                "new_confidence": new_confidence,
                "created_at": datetime.utcnow(),
            }
            
            # Insert into audit collection
            result = self.audit_collection.insert_one(audit_entry)
            
            # Log the difference
            logger.info(
                f"Geocoding difference logged for location {location_id}: "
                f"Address: {address}, "
                f"Old: ({old_coordinates[0]}, {old_coordinates[1]}) [{old_source}], "
                f"New: ({new_coordinates[0]}, {new_coordinates[1]}) [{new_source}], "
                f"Difference: {difference_km:.2f} km"
            )
            
            # Log warning if difference is significant (>1 km)
            if difference_km > 1.0:
                logger.warning(
                    f"Significant coordinate difference for location {location_id}: "
                    f"{difference_km:.2f} km between {old_source} and {new_source}"
                )
            
            return str(result.inserted_id)
        
        except Exception as e:
            logger.error(f"Error logging coordinate difference for location {location_id}: {e}")
            raise

    async def get_audit_log(
        self,
        location_id: Optional[str] = None,
        min_difference_km: float = 0.0,
        limit: int = 100,
        skip: int = 0,
    ) -> Dict[str, Any]:
        """
        Get audit log entries with optional filtering.

        Args:
            location_id: Optional location ID to filter by
            min_difference_km: Minimum difference in kilometers to include
            limit: Maximum number of results
            skip: Number of results to skip

        Returns:
            Dictionary with audit log entries and metadata
        """
        try:
            # Build query
            query = {}
            if location_id:
                query["location_id"] = location_id
            if min_difference_km > 0:
                query["difference_km"] = {"$gte": min_difference_km}
            
            # Get total count
            total = self.audit_collection.count_documents(query)
            
            # Get entries
            entries = list(
                self.audit_collection.find(query)
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
            )
            
            # Convert ObjectId to string for JSON serialization
            for entry in entries:
                entry["_id"] = str(entry["_id"])
            
            return {
                "entries": entries,
                "total": total,
                "limit": limit,
                "skip": skip,
            }
        
        except Exception as e:
            logger.error(f"Error retrieving audit log: {e}")
            raise

    async def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about geocoding differences.

        Returns:
            Dictionary with statistics
        """
        try:
            # Get total entries
            total_entries = self.audit_collection.count_documents({})
            
            # Get average difference
            pipeline = [
                {
                    "$group": {
                        "_id": None,
                        "avg_difference": {"$avg": "$difference_km"},
                        "max_difference": {"$max": "$difference_km"},
                        "min_difference": {"$min": "$difference_km"},
                    }
                }
            ]
            
            stats_result = list(self.audit_collection.aggregate(pipeline))
            
            if stats_result:
                stats = stats_result[0]
            else:
                stats = {
                    "avg_difference": 0.0,
                    "max_difference": 0.0,
                    "min_difference": 0.0,
                }
            
            # Get entries with significant differences (>1 km)
            significant_count = self.audit_collection.count_documents({
                "difference_km": {"$gt": 1.0}
            })
            
            return {
                "total_entries": total_entries,
                "average_difference_km": round(stats.get("avg_difference", 0.0), 2),
                "max_difference_km": round(stats.get("max_difference", 0.0), 2),
                "min_difference_km": round(stats.get("min_difference", 0.0), 2),
                "significant_differences_count": significant_count,
                "significant_differences_percentage": (
                    round((significant_count / total_entries * 100), 2) if total_entries > 0 else 0
                ),
            }
        
        except Exception as e:
            logger.error(f"Error calculating statistics: {e}")
            raise

    async def export_audit_log(
        self,
        location_id: Optional[str] = None,
        min_difference_km: float = 0.0,
    ) -> list:
        """
        Export audit log entries for analysis.

        Args:
            location_id: Optional location ID to filter by
            min_difference_km: Minimum difference in kilometers to include

        Returns:
            List of audit log entries
        """
        try:
            # Build query
            query = {}
            if location_id:
                query["location_id"] = location_id
            if min_difference_km > 0:
                query["difference_km"] = {"$gte": min_difference_km}
            
            # Get all entries
            entries = list(
                self.audit_collection.find(query)
                .sort("created_at", -1)
            )
            
            # Convert ObjectId to string for JSON serialization
            for entry in entries:
                entry["_id"] = str(entry["_id"])
            
            logger.info(f"Exported {len(entries)} audit log entries")
            return entries
        
        except Exception as e:
            logger.error(f"Error exporting audit log: {e}")
            raise

    async def clear_old_entries(self, days: int = 90) -> int:
        """
        Clear audit log entries older than specified days.

        Args:
            days: Number of days to keep (default 90)

        Returns:
            Number of entries deleted
        """
        try:
            from datetime import timedelta
            
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            result = self.audit_collection.delete_many({
                "created_at": {"$lt": cutoff_date}
            })
            
            logger.info(f"Deleted {result.deleted_count} old audit log entries")
            return result.deleted_count
        
        except Exception as e:
            logger.error(f"Error clearing old entries: {e}")
            raise
