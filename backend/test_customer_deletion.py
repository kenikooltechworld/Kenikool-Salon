"""Test script for customer cascading deletion."""

import sys
import os
from bson import ObjectId

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import connect_db
from app.services.customer_deletion_service import CustomerDeletionService


def test_customer_deletion():
    """Test customer deletion with cascading deletes."""
    # Connect to database
    connect_db()
    
    # Test with a sample tenant and customer ID
    # Replace these with actual IDs from your database
    tenant_id = ObjectId("000000000000000000000001")  # Replace with real tenant ID
    customer_id = ObjectId("000000000000000000000001")  # Replace with real customer ID
    
    print(f"Testing customer deletion for customer_id: {customer_id}")
    print(f"Tenant ID: {tenant_id}")
    print("-" * 60)
    
    try:
        deletion_stats = CustomerDeletionService.delete_customer_and_related_data(
            tenant_id=tenant_id,
            customer_id=customer_id
        )
        
        print("\nDeletion completed successfully!")
        print(f"Customer: {deletion_stats['customer_name']}")
        print(f"\nDeleted records by collection:")
        for collection, count in deletion_stats["deleted_records"].items():
            if count > 0:
                print(f"  - {collection}: {count}")
        print(f"\nTotal related records deleted: {deletion_stats['total_related_records_deleted']}")
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("Customer Cascading Deletion Test")
    print("=" * 60)
    print("\nNOTE: This is a test script. Update tenant_id and customer_id")
    print("with real values before running.\n")
    
    # Uncomment to run the test
    # test_customer_deletion()
    
    print("Test script ready. Uncomment the test_customer_deletion() call to run.")
