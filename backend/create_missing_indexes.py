"""
Create missing MongoDB indexes for performance optimization.
This script adds indexes to collections that are missing them.
"""

import os
import sys
from pymongo import MongoClient, ASCENDING, DESCENDING
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017/salon_db")

def create_missing_indexes():
    """Create all missing indexes for better query performance."""
    client = MongoClient(MONGODB_URL)
    db = client.get_default_database()
    
    print("Creating missing indexes...")
    
    # Appointments collection
    print("Creating indexes for appointments...")
    db.appointments.create_index([("tenant_id", ASCENDING)])
    db.appointments.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.appointments.create_index([("tenant_id", ASCENDING), ("start_time", DESCENDING)])
    db.appointments.create_index([("tenant_id", ASCENDING), ("customer_id", ASCENDING)])
    db.appointments.create_index([("tenant_id", ASCENDING), ("staff_id", ASCENDING)])
    db.appointments.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    
    # Transactions collection
    print("Creating indexes for transactions...")
    db.transactions.create_index([("tenant_id", ASCENDING)])
    db.transactions.create_index([("tenant_id", ASCENDING), ("payment_status", ASCENDING)])
    db.transactions.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    db.transactions.create_index([("tenant_id", ASCENDING), ("customer_id", ASCENDING)])
    
    # Receipts collection
    print("Creating indexes for receipts...")
    db.receipts.create_index([("tenant_id", ASCENDING)])
    db.receipts.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    db.receipts.create_index([("tenant_id", ASCENDING), ("customer_id", ASCENDING)])
    db.receipts.create_index([("tenant_id", ASCENDING), ("transaction_id", ASCENDING)])
    
    # Inventory collection
    print("Creating indexes for inventory...")
    db.inventory.create_index([("tenant_id", ASCENDING)])
    db.inventory.create_index([("tenant_id", ASCENDING), ("is_active", ASCENDING)])
    db.inventory.create_index([("tenant_id", ASCENDING), ("category", ASCENDING)])
    db.inventory.create_index([("tenant_id", ASCENDING), ("quantity", ASCENDING)])
    
    # Inventory transactions collection
    print("Creating indexes for inventory_transactions...")
    db.inventory_transactions.create_index([("tenant_id", ASCENDING)])
    db.inventory_transactions.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    db.inventory_transactions.create_index([("tenant_id", ASCENDING), ("transaction_type", ASCENDING)])
    
    # Service commissions collection
    print("Creating indexes for service_commissions...")
    db.service_commissions.create_index([("tenant_id", ASCENDING)])
    db.service_commissions.create_index([("tenant_id", ASCENDING), ("staff_id", ASCENDING)])
    db.service_commissions.create_index([("tenant_id", ASCENDING), ("earned_date", DESCENDING)])
    db.service_commissions.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    
    # Refunds collection
    print("Creating indexes for refunds...")
    db.refunds.create_index([("tenant_id", ASCENDING)])
    db.refunds.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.refunds.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    
    # Payments collection
    print("Creating indexes for payments...")
    db.payments.create_index([("tenant_id", ASCENDING)])
    db.payments.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.payments.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    
    # Invoices collection
    print("Creating indexes for invoices...")
    db.invoices.create_index([("tenant_id", ASCENDING)])
    db.invoices.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.invoices.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    db.invoices.create_index([("tenant_id", ASCENDING), ("customer_id", ASCENDING)])
    
    # Services collection
    print("Creating indexes for services...")
    db.services.create_index([("tenant_id", ASCENDING)])
    db.services.create_index([("tenant_id", ASCENDING), ("is_active", ASCENDING)])
    db.services.create_index([("tenant_id", ASCENDING), ("category_id", ASCENDING)])
    
    # Staff collection
    print("Creating indexes for staff...")
    db.staff.create_index([("tenant_id", ASCENDING)])
    db.staff.create_index([("tenant_id", ASCENDING), ("is_active", ASCENDING)])
    db.staff.create_index([("tenant_id", ASCENDING), ("user_id", ASCENDING)])
    
    # Customers collection
    print("Creating indexes for customers...")
    db.customers.create_index([("tenant_id", ASCENDING)])
    db.customers.create_index([("tenant_id", ASCENDING), ("email", ASCENDING)])
    db.customers.create_index([("tenant_id", ASCENDING), ("phone", ASCENDING)])
    
    # Queue entries (waiting room)
    print("Creating indexes for queue_entries...")
    db.queue_entries.create_index([("tenant_id", ASCENDING)])
    db.queue_entries.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.queue_entries.create_index([("tenant_id", ASCENDING), ("check_in_time", DESCENDING)])
    
    # Notifications collection
    print("Creating indexes for notifications...")
    db.notifications.create_index([("tenant_id", ASCENDING)])
    db.notifications.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.notifications.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    
    # Memberships collection
    print("Creating indexes for memberships...")
    db.memberships.create_index([("tenant_id", ASCENDING)])
    db.memberships.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.memberships.create_index([("tenant_id", ASCENDING), ("tier_id", ASCENDING)])
    
    # Service packages collection
    print("Creating indexes for service_packages...")
    db.service_packages.create_index([("tenant_id", ASCENDING)])
    db.service_packages.create_index([("tenant_id", ASCENDING), ("is_active", ASCENDING)])
    
    # Stock alerts collection
    print("Creating indexes for stock_alerts...")
    db.stock_alerts.create_index([("tenant_id", ASCENDING)])
    db.stock_alerts.create_index([("tenant_id", ASCENDING), ("is_resolved", ASCENDING)])
    db.stock_alerts.create_index([("tenant_id", ASCENDING), ("created_at", DESCENDING)])
    
    # Time slots collection
    print("Creating indexes for time_slots...")
    db.time_slots.create_index([("tenant_id", ASCENDING)])
    db.time_slots.create_index([("tenant_id", ASCENDING), ("status", ASCENDING)])
    db.time_slots.create_index([("tenant_id", ASCENDING), ("start_time", ASCENDING)])
    
    print("\n✅ All missing indexes created successfully!")
    print("\nTo verify indexes, run:")
    print("  db.collection_name.getIndexes()")
    
    client.close()

if __name__ == "__main__":
    try:
        create_missing_indexes()
    except Exception as e:
        print(f"❌ Error creating indexes: {e}")
        sys.exit(1)
