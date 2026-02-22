"""
Service Zone Service

Manages service zones and restricted areas for salons.

Requirements: 12.1, 12.2, 12.3, 12.4, 12.5
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo.database import Database
from bson import ObjectId

logger = logging.getLogger(__name__)


class ServiceZoneService:
    """Service for managing service zones and restricted areas"""

    def __init__(self, db: Database):
        """
        Initialize service zone service.

        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.zones_collection = db["service_zones"]
        
        # Create indexes for efficient querying
        try:
            self.zones_collection.create_index("salon_id")
            self.zones_collection.create_index("type")
            self.zones_collection.create_index("enabled")
        except Exception as e:
            logger.warning(f"Could not create indexes: {e}")

    async def create_service_zone(
        self,
        salon_id: str,
        name: str,
        zone_type: str,
        coordinates: List[List[float]],
        enabled: bool = True
    ) -> Dict[str, Any]:
        """
        Create a service zone for a salon.

        Args:
            salon_id: Salon ID
            name: Zone name
            zone_type: "service" or "restricted"
            coordinates: GeoJSON polygon coordinates
            enabled: Whether zone is enabled

        Returns:
            Created zone document

        Requirement 12.1: Allow salon owners to define custom service zones
        """
        try:
            zone_doc = {
                "salon_id": salon_id,
                "name": name,
                "type": zone_type,
                "coordinates": coordinates,
                "enabled": enabled,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            
            result = self.zones_collection.insert_one(zone_doc)
            zone_doc["_id"] = str(result.inserted_id)
            
            logger.info(
                f"Created {zone_type} zone '{name}' for salon {salon_id}"
            )
            
            return zone_doc
        
        except Exception as e:
            logger.error(f"Error creating service zone: {e}")
            raise

    async def update_service_zone(
        self,
        zone_id: str,
        name: Optional[str] = None,
        coordinates: Optional[List[List[float]]] = None,
        enabled: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        Update a service zone.

        Args:
            zone_id: Zone ID
            name: New name
            coordinates: New coordinates
            enabled: New enabled status

        Returns:
            Updated zone document
        """
        try:
            update_doc = {"updated_at": datetime.utcnow()}
            
            if name is not None:
                update_doc["name"] = name
            if coordinates is not None:
                update_doc["coordinates"] = coordinates
            if enabled is not None:
                update_doc["enabled"] = enabled
            
            result = self.zones_collection.find_one_and_update(
                {"_id": ObjectId(zone_id)},
                {"$set": update_doc},
                return_document=True
            )
            
            if result:
                result["_id"] = str(result["_id"])
                logger.info(f"Updated service zone {zone_id}")
            else:
                logger.warning(f"Service zone {zone_id} not found")
            
            return result
        
        except Exception as e:
            logger.error(f"Error updating service zone {zone_id}: {e}")
            raise

    async def delete_service_zone(self, zone_id: str) -> None:
        """
        Delete a service zone.

        Args:
            zone_id: Zone ID
        """
        try:
            result = self.zones_collection.delete_one({"_id": ObjectId(zone_id)})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted service zone {zone_id}")
            else:
                logger.warning(f"Service zone {zone_id} not found")
        
        except Exception as e:
            logger.error(f"Error deleting service zone {zone_id}: {e}")
            raise

    async def get_salon_service_zones(self, salon_id: str) -> List[Dict[str, Any]]:
        """
        Get all service zones for a salon.

        Args:
            salon_id: Salon ID

        Returns:
            List of zone documents
        """
        try:
            zones = list(
                self.zones_collection.find({"salon_id": salon_id})
            )
            
            # Convert ObjectId to string
            for zone in zones:
                zone["_id"] = str(zone["_id"])
            
            return zones
        
        except Exception as e:
            logger.error(f"Error getting zones for salon {salon_id}: {e}")
            raise

    async def get_service_zone(self, zone_id: str) -> Dict[str, Any]:
        """
        Get a single service zone.

        Args:
            zone_id: Zone ID

        Returns:
            Zone document
        """
        try:
            zone = self.zones_collection.find_one({"_id": ObjectId(zone_id)})
            
            if zone:
                zone["_id"] = str(zone["_id"])
            
            return zone
        
        except Exception as e:
            logger.error(f"Error getting service zone {zone_id}: {e}")
            raise

    async def validate_location(
        self,
        salon_id: str,
        latitude: float,
        longitude: float
    ) -> Dict[str, Any]:
        """
        Validate if a location is within service zones.

        Args:
            salon_id: Salon ID
            latitude: Location latitude
            longitude: Location longitude

        Returns:
            Validation result

        Requirement 12.2: Display message when service is unavailable in restricted zone
        """
        try:
            zones = await self.get_salon_service_zones(salon_id)
            
            inside_service_zone = False
            inside_restricted_zone = False
            
            for zone in zones:
                if not zone.get("enabled"):
                    continue
                
                # Check if point is inside polygon
                if self._point_in_polygon(latitude, longitude, zone["coordinates"]):
                    if zone["type"] == "service":
                        inside_service_zone = True
                    elif zone["type"] == "restricted":
                        inside_restricted_zone = True
            
            return {
                "valid": not inside_restricted_zone,
                "inside_service_zone": inside_service_zone,
                "inside_restricted_zone": inside_restricted_zone,
                "message": (
                    "Service unavailable in this area"
                    if inside_restricted_zone
                    else "Service available"
                ),
            }
        
        except Exception as e:
            logger.error(f"Error validating location: {e}")
            raise

    async def get_service_zone_stats(self, salon_id: str) -> Dict[str, Any]:
        """
        Get service zone statistics.

        Args:
            salon_id: Salon ID

        Returns:
            Statistics dictionary
        """
        try:
            zones = await self.get_salon_service_zones(salon_id)
            
            service_zones = [z for z in zones if z["type"] == "service"]
            restricted_zones = [z for z in zones if z["type"] == "restricted"]
            
            # Calculate total area (simplified - just count zones)
            total_area_km2 = len(zones) * 0.5  # Placeholder calculation
            
            return {
                "total_zones": len(zones),
                "service_zones": len(service_zones),
                "restricted_zones": len(restricted_zones),
                "total_area_km2": round(total_area_km2, 2),
            }
        
        except Exception as e:
            logger.error(f"Error getting service zone stats: {e}")
            raise

    @staticmethod
    def _point_in_polygon(
        latitude: float,
        longitude: float,
        polygon: List[List[float]]
    ) -> bool:
        """
        Check if a point is inside a polygon using ray casting algorithm.

        Args:
            latitude: Point latitude
            longitude: Point longitude
            polygon: List of [lon, lat] coordinates

        Returns:
            True if point is inside polygon
        """
        x, y = longitude, latitude
        n = len(polygon)
        inside = False

        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y

        return inside
