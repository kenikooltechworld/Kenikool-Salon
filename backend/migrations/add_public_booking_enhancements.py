"""
Database migration for public booking enhancements.

This migration adds:
1. New fields to PublicBooking model (payment_option, payment_status, etc.)
2. New PublicBookingNotificationPreference collection
3. Indexes for performance optimization
"""

from datetime import datetime
from pymongo import ASCENDING, DESCENDING
from bson import ObjectId


def upgrade(db):
    """
    Upgrade database schema for public booking enhancements.
    
    Changes:
    - Add payment_option, payment_status, payment_id to PublicBooking
    - Add cancellation_reason, cancelled_at to PublicBooking
    - Add rescheduled_from to PublicBooking
    - Add reminder_24h_sent, reminder_1h_sent to PublicBooking
    - Create PublicBookingNotificationPreference collection
    - Create indexes for performance
    """
    
    # 1. Add new fields to existing PublicBooking documents
    print("Adding new fields to PublicBooking collection...")
    
    db.public_bookings.update_many(
        {},
        {
            "$set": {
                "payment_option": "later",  # Default to pay later for existing bookings
                "payment_status": None,
                "payment_id": None,
                "cancellation_reason": None,
                "cancelled_at": None,
                "rescheduled_from": None,
                "reminder_24h_sent": False,
                "reminder_1h_sent": False,
            }
        }
    )
    print("✓ Added new fields to PublicBooking collection")
    
    # 2. Create PublicBookingNotificationPreference collection
    print("Creating PublicBookingNotificationPreference collection...")
    
    db.create_collection("public_booking_notification_preferences")
    print("✓ Created PublicBookingNotificationPreference collection")
    
    # 3. Create indexes for PublicBooking
    print("Creating indexes for PublicBooking...")
    
    # Index for finding bookings by tenant and date (for reminders)
    db.public_bookings.create_index(
        [("tenant_id", ASCENDING), ("booking_date", ASCENDING)],
        name="idx_tenant_booking_date"
    )
    print("✓ Created index: tenant_id + booking_date")
    
    # Index for finding bookings by status
    db.public_bookings.create_index(
        [("status", ASCENDING)],
        name="idx_status"
    )
    print("✓ Created index: status")
    
    # Index for finding bookings by customer email
    db.public_bookings.create_index(
        [("customer_email", ASCENDING)],
        name="idx_customer_email"
    )
    print("✓ Created index: customer_email")
    
    # Index for finding bookings that need reminders
    db.public_bookings.create_index(
        [("booking_date", ASCENDING), ("reminder_24h_sent", ASCENDING)],
        name="idx_booking_date_reminder_24h"
    )
    print("✓ Created index: booking_date + reminder_24h_sent")
    
    # Index for finding cancelled bookings
    db.public_bookings.create_index(
        [("status", ASCENDING), ("cancelled_at", DESCENDING)],
        name="idx_status_cancelled_at"
    )
    print("✓ Created index: status + cancelled_at")
    
    # 4. Create indexes for PublicBookingNotificationPreference
    print("Creating indexes for PublicBookingNotificationPreference...")
    
    # Index for finding preferences by booking ID
    db.public_booking_notification_preferences.create_index(
        [("booking_id", ASCENDING)],
        name="idx_booking_id",
        unique=True
    )
    print("✓ Created index: booking_id (unique)")
    
    # Index for finding preferences by customer email
    db.public_booking_notification_preferences.create_index(
        [("customer_email", ASCENDING)],
        name="idx_customer_email"
    )
    print("✓ Created index: customer_email")
    
    # 5. Create default notification preferences for existing bookings
    print("Creating default notification preferences for existing bookings...")
    
    existing_bookings = db.public_bookings.find(
        {"status": {"$in": ["confirmed", "completed"]}}
    )
    
    preferences_to_insert = []
    for booking in existing_bookings:
        preferences_to_insert.append({
            "booking_id": booking["_id"],
            "customer_email": booking.get("customer_email"),
            "customer_phone": booking.get("customer_phone"),
            "send_confirmation_email": True,
            "send_24h_reminder_email": True,
            "send_1h_reminder_email": True,
            "send_sms_reminders": False,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
        })
    
    if preferences_to_insert:
        db.public_booking_notification_preferences.insert_many(preferences_to_insert)
        print(f"✓ Created {len(preferences_to_insert)} default notification preferences")
    else:
        print("✓ No existing bookings to create preferences for")
    
    print("\n✓ Migration completed successfully!")


def downgrade(db):
    """
    Downgrade database schema (rollback).
    
    Changes:
    - Remove new fields from PublicBooking
    - Drop PublicBookingNotificationPreference collection
    - Drop new indexes
    """
    
    print("Rolling back public booking enhancements...")
    
    # 1. Remove new fields from PublicBooking
    print("Removing new fields from PublicBooking...")
    
    db.public_bookings.update_many(
        {},
        {
            "$unset": {
                "payment_option": "",
                "payment_status": "",
                "payment_id": "",
                "cancellation_reason": "",
                "cancelled_at": "",
                "rescheduled_from": "",
                "reminder_24h_sent": "",
                "reminder_1h_sent": "",
            }
        }
    )
    print("✓ Removed new fields from PublicBooking")
    
    # 2. Drop PublicBookingNotificationPreference collection
    print("Dropping PublicBookingNotificationPreference collection...")
    
    db.public_booking_notification_preferences.drop()
    print("✓ Dropped PublicBookingNotificationPreference collection")
    
    # 3. Drop indexes
    print("Dropping indexes...")
    
    try:
        db.public_bookings.drop_index("idx_tenant_booking_date")
        print("✓ Dropped index: idx_tenant_booking_date")
    except Exception as e:
        print(f"  Index idx_tenant_booking_date not found: {e}")
    
    try:
        db.public_bookings.drop_index("idx_status")
        print("✓ Dropped index: idx_status")
    except Exception as e:
        print(f"  Index idx_status not found: {e}")
    
    try:
        db.public_bookings.drop_index("idx_customer_email")
        print("✓ Dropped index: idx_customer_email")
    except Exception as e:
        print(f"  Index idx_customer_email not found: {e}")
    
    try:
        db.public_bookings.drop_index("idx_booking_date_reminder_24h")
        print("✓ Dropped index: idx_booking_date_reminder_24h")
    except Exception as e:
        print(f"  Index idx_booking_date_reminder_24h not found: {e}")
    
    try:
        db.public_bookings.drop_index("idx_status_cancelled_at")
        print("✓ Dropped index: idx_status_cancelled_at")
    except Exception as e:
        print(f"  Index idx_status_cancelled_at not found: {e}")
    
    print("\n✓ Rollback completed successfully!")


# Migration metadata
migration = {
    "name": "add_public_booking_enhancements",
    "description": "Add payment, cancellation, rescheduling, and notification fields to public bookings",
    "version": "1.0.0",
    "created_at": datetime.now(),
    "upgrade": upgrade,
    "downgrade": downgrade,
}
