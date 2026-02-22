"""
Migration: Add booking location indexes for Phase 6 - Location-Based Booking

This migration creates indexes to optimize location-based booking queries:
- Index on location_id for filtering bookings by location
- Compound index on location_id + start_time for availability checks
- Compound index on staff_id + location_id + start_time for double-booking checks
"""

from pymongo import ASCENDING, DESCENDING
from app.database import Database


def migrate():
    """Create booking location indexes"""
    db = Database.get_db()
    bookings_collection = db["bookings"]
    
    print("Creating booking location indexes...")
    
    # Index 1: location_id for filtering
    print("  - Creating index on location_id...")
    bookings_collection.create_index(
        [("location_id", ASCENDING)],
        name="idx_booking_location_id"
    )
    
    # Index 2: location_id + booking_date for availability checks
    print("  - Creating compound index on location_id + booking_date...")
    bookings_collection.create_index(
        [("location_id", ASCENDING), ("booking_date", DESCENDING)],
        name="idx_booking_location_date"
    )
    
    # Index 3: staff_id + location_id + booking_date for double-booking checks
    print("  - Creating compound index on stylist_id + location_id + booking_date...")
    bookings_collection.create_index(
        [
            ("stylist_id", ASCENDING),
            ("location_id", ASCENDING),
            ("booking_date", DESCENDING)
        ],
        name="idx_booking_staff_location_date"
    )
    
    # Index 4: tenant_id + location_id for multi-tenant queries
    print("  - Creating compound index on tenant_id + location_id...")
    bookings_collection.create_index(
        [("tenant_id", ASCENDING), ("location_id", ASCENDING)],
        name="idx_booking_tenant_location"
    )
    
    print("✓ Booking location indexes created successfully")


def rollback():
    """Remove booking location indexes"""
    db = Database.get_db()
    bookings_collection = db["bookings"]
    
    print("Removing booking location indexes...")
    
    indexes_to_remove = [
        "idx_booking_location_id",
        "idx_booking_location_date",
        "idx_booking_staff_location_date",
        "idx_booking_tenant_location"
    ]
    
    for index_name in indexes_to_remove:
        try:
            bookings_collection.drop_index(index_name)
            print(f"  - Removed index: {index_name}")
        except Exception as e:
            print(f"  - Index {index_name} not found or error: {e}")
    
    print("✓ Booking location indexes removed")


if __name__ == "__main__":
    migrate()
