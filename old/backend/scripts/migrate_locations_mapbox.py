#!/usr/bin/env python3
"""
Migration script for validating and geocoding locations using Mapbox.

This script:
1. Validates all locations have valid coordinates
2. Logs locations with missing/invalid coordinates
3. Geocodes locations with address but no coordinates
4. Stores results in the database

Usage:
    python migrate_locations_mapbox.py [--dry-run] [--tenant-id TENANT_ID]

Requirements:
    - 8.3: Validate all locations have valid coordinates
    - 8.4: Geocode locations without coordinates
"""

import asyncio
import logging
import argparse
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from bson import ObjectId

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('location_migration.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class LocationMigration:
    """Handles location migration and validation"""

    def __init__(self, db_url: str, dry_run: bool = False):
        """
        Initialize migration service.

        Args:
            db_url: MongoDB connection URL
            dry_run: If True, don't make changes to database
        """
        self.dry_run = dry_run
        self.client = MongoClient(db_url)
        self.db = self.client.get_database()
        self.locations_collection = self.db["locations"]
        
        # Statistics
        self.stats = {
            "total_locations": 0,
            "valid_locations": 0,
            "missing_coordinates": 0,
            "invalid_coordinates": 0,
            "geocoded_successfully": 0,
            "geocoding_failed": 0,
            "errors": []
        }

    async def validate_coordinates(self, latitude: Any, longitude: Any) -> bool:
        """
        Validate that coordinates are within valid ranges.

        Args:
            latitude: Latitude value
            longitude: Longitude value

        Returns:
            True if coordinates are valid, False otherwise
        """
        try:
            lat = float(latitude)
            lon = float(longitude)
            
            if lat < -90 or lat > 90:
                return False
            if lon < -180 or lon > 180:
                return False
            
            return True
        except (TypeError, ValueError):
            return False

    async def geocode_address(self, address: str, country: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Geocode an address using Mapbox.

        Args:
            address: Address to geocode
            country: Optional country code

        Returns:
            Dictionary with geocoding result or None if failed
        """
        try:
            # Import here to avoid circular imports
            from app.services.mapbox_service import MapboxService
            from app.services.cache_service import CacheService
            from app.config import settings
            
            cache_service = CacheService()
            mapbox_service = MapboxService(cache_service=cache_service)
            
            result = await mapbox_service.geocode_address(address, country=country)
            return result
        except Exception as e:
            logger.error(f"Error geocoding address '{address}': {e}")
            return None

    async def run_migration(self, tenant_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the migration process.

        Args:
            tenant_id: Optional tenant ID to migrate only specific tenant

        Returns:
            Migration statistics
        """
        logger.info("Starting location migration...")
        
        # Build query
        query = {}
        if tenant_id:
            query["tenant_id"] = tenant_id
        
        # Get all locations
        locations = list(self.locations_collection.find(query))
        self.stats["total_locations"] = len(locations)
        
        logger.info(f"Found {len(locations)} locations to validate")
        
        # Process each location
        for idx, location in enumerate(locations, 1):
            location_id = location.get("_id")
            address = location.get("address")
            latitude = location.get("latitude")
            longitude = location.get("longitude")
            country = location.get("country")
            
            logger.info(f"[{idx}/{len(locations)}] Processing location {location_id}")
            
            # Check if coordinates exist
            if latitude is None or longitude is None:
                self.stats["missing_coordinates"] += 1
                logger.warning(f"Location {location_id} has missing coordinates")
                
                # Try to geocode if address exists
                if address:
                    logger.info(f"Attempting to geocode address for location {location_id}: {address}")
                    geocoding_result = await self.geocode_address(address, country=country)
                    
                    if geocoding_result:
                        self.stats["geocoded_successfully"] += 1
                        logger.info(
                            f"Successfully geocoded location {location_id}: "
                            f"({geocoding_result['latitude']}, {geocoding_result['longitude']})"
                        )
                        
                        # Update location in database
                        if not self.dry_run:
                            try:
                                update_doc = {
                                    "latitude": geocoding_result["latitude"],
                                    "longitude": geocoding_result["longitude"],
                                    "formatted_address": geocoding_result.get("formatted_address", address),
                                    "geocoding_source": "mapbox",
                                    "geocoding_confidence": geocoding_result.get("confidence", 0.0),
                                    "updated_at": datetime.utcnow(),
                                }
                                
                                self.locations_collection.update_one(
                                    {"_id": location_id},
                                    {"$set": update_doc}
                                )
                                logger.info(f"Updated location {location_id} with geocoding result")
                            except Exception as e:
                                logger.error(f"Error updating location {location_id}: {e}")
                                self.stats["errors"].append({
                                    "location_id": str(location_id),
                                    "error": f"Failed to update: {str(e)}"
                                })
                    else:
                        self.stats["geocoding_failed"] += 1
                        logger.error(f"Failed to geocode address for location {location_id}")
                        self.stats["errors"].append({
                            "location_id": str(location_id),
                            "error": "Geocoding failed"
                        })
                else:
                    logger.error(f"Location {location_id} has no address to geocode")
                    self.stats["errors"].append({
                        "location_id": str(location_id),
                        "error": "No address provided"
                    })
            
            # Validate existing coordinates
            elif not await self.validate_coordinates(latitude, longitude):
                self.stats["invalid_coordinates"] += 1
                logger.error(
                    f"Location {location_id} has invalid coordinates: "
                    f"({latitude}, {longitude})"
                )
                self.stats["errors"].append({
                    "location_id": str(location_id),
                    "error": f"Invalid coordinates: ({latitude}, {longitude})"
                })
            
            else:
                self.stats["valid_locations"] += 1
                logger.debug(f"Location {location_id} has valid coordinates")
        
        logger.info("Location migration completed")
        return self.stats

    def print_summary(self) -> None:
        """Print migration summary"""
        logger.info("=" * 60)
        logger.info("MIGRATION SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total locations: {self.stats['total_locations']}")
        logger.info(f"Valid locations: {self.stats['valid_locations']}")
        logger.info(f"Missing coordinates: {self.stats['missing_coordinates']}")
        logger.info(f"Invalid coordinates: {self.stats['invalid_coordinates']}")
        logger.info(f"Successfully geocoded: {self.stats['geocoded_successfully']}")
        logger.info(f"Geocoding failed: {self.stats['geocoding_failed']}")
        logger.info(f"Total errors: {len(self.stats['errors'])}")
        
        if self.stats["errors"]:
            logger.info("\nERRORS:")
            for error in self.stats["errors"]:
                logger.error(f"  Location {error['location_id']}: {error['error']}")
        
        logger.info("=" * 60)


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Migrate locations to Mapbox geocoding"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without making changes to database"
    )
    parser.add_argument(
        "--tenant-id",
        type=str,
        help="Migrate only specific tenant"
    )
    parser.add_argument(
        "--db-url",
        type=str,
        default="mongodb://localhost:27017/kenikool",
        help="MongoDB connection URL"
    )
    
    args = parser.parse_args()
    
    logger.info(f"Starting migration (dry_run={args.dry_run})")
    
    migration = LocationMigration(args.db_url, dry_run=args.dry_run)
    stats = await migration.run_migration(tenant_id=args.tenant_id)
    migration.print_summary()
    
    # Exit with error code if there were errors
    if stats["errors"]:
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
