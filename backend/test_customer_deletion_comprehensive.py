"""Comprehensive test script for customer deletion and recreation."""

import sys
import os
from bson import ObjectId
from datetime import datetime

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import connect_db
from app.models.customer import Customer
from app.services.customer_deletion_service import CustomerDeletionService


def test_customer_deletion_and_recreation(tenant_id_str: str, customer_email: str):
    """
    Test customer deletion and recreation with the same email.
    
    Args:
        tenant_id_str: Tenant ID as string
        customer_email: Email of the customer to test with
    """
    # Connect to database
    connect_db()
    
    tenant_id = ObjectId(tenant_id_str)
    
    print("=" * 80)
    print("CUSTOMER DELETION AND RECREATION TEST")
    print("=" * 80)
    print(f"Tenant ID: {tenant_id}")
    print(f"Customer Email: {customer_email}")
    print("-" * 80)
    
    # Step 1: Find the customer
    print("\n[STEP 1] Finding customer...")
    customer = Customer.objects(email=customer_email, tenant_id=tenant_id).first()
    
    if not customer:
        print(f"❌ No customer found with email: {customer_email}")
        print("Creating a test customer first...")
        
        # Create test customer
        test_customer = Customer(
            tenant_id=tenant_id,
            first_name="Test",
            last_name="Customer",
            email=customer_email,
            phone="+234 800 000 0000",
            status="active",
            is_guest=False
        )
        test_customer.save()
        customer = test_customer
        print(f"✅ Created test customer: {customer.id}")
    else:
        print(f"✅ Found customer: {customer.id}")
        print(f"   Name: {customer.first_name} {customer.last_name}")
        print(f"   Email: {customer.email}")
        print(f"   Phone: {customer.phone}")
    
    customer_id = customer.id
    customer_name = f"{customer.first_name} {customer.last_name}"
    
    # Step 2: Check related records before deletion
    print("\n[STEP 2] Checking related records before deletion...")
    from app.models.appointment import Appointment
    from app.models.invoice import Invoice
    from app.models.payment import Payment
    from app.models.notification import Notification
    
    appointments_count = Appointment.objects(tenant_id=tenant_id, customer_id=customer_id).count()
    invoices_count = Invoice.objects(tenant_id=tenant_id, customer_id=customer_id).count()
    payments_count = Payment.objects(tenant_id=tenant_id, customer_id=customer_id).count()
    notifications_count = Notification.objects(tenant_id=tenant_id, recipient_id=str(customer_id), recipient_type="customer").count()
    
    print(f"   Appointments: {appointments_count}")
    print(f"   Invoices: {invoices_count}")
    print(f"   Payments: {payments_count}")
    print(f"   Notifications: {notifications_count}")
    
    # Step 3: Delete the customer
    print("\n[STEP 3] Deleting customer and all related data...")
    try:
        deletion_stats = CustomerDeletionService.delete_customer_and_related_data(
            tenant_id=tenant_id,
            customer_id=customer_id
        )
        
        print(f"✅ Deletion completed successfully!")
        print(f"\nDeleted records:")
        for collection, count in deletion_stats["deleted_records"].items():
            if count > 0:
                print(f"   - {collection}: {count}")
        print(f"\n   Total related records deleted: {deletion_stats['total_related_records_deleted']}")
        
    except Exception as e:
        print(f"❌ Deletion failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 4: Verify customer is deleted
    print("\n[STEP 4] Verifying customer is deleted...")
    verify_customer = Customer.objects(id=customer_id, tenant_id=tenant_id).first()
    
    if verify_customer:
        print(f"❌ FAILED: Customer {customer_id} still exists!")
        print(f"   Name: {verify_customer.first_name} {verify_customer.last_name}")
        print(f"   Email: {verify_customer.email}")
        return
    else:
        print(f"✅ Customer {customer_id} successfully deleted")
    
    # Step 5: Check if email is available
    print("\n[STEP 5] Checking if email is available for reuse...")
    email_check = Customer.objects(email=customer_email, tenant_id=tenant_id).first()
    
    if email_check:
        print(f"❌ FAILED: Email {customer_email} is still in use!")
        print(f"   Customer ID: {email_check.id}")
        print(f"   Name: {email_check.first_name} {email_check.last_name}")
        return
    else:
        print(f"✅ Email {customer_email} is available")
    
    # Step 6: Try to recreate customer with same email
    print("\n[STEP 6] Attempting to recreate customer with same email...")
    try:
        new_customer = Customer(
            tenant_id=tenant_id,
            first_name="Recreated",
            last_name="Customer",
            email=customer_email,
            phone="+234 800 000 0001",
            status="active",
            is_guest=False
        )
        new_customer.save()
        
        print(f"✅ Successfully created new customer with same email!")
        print(f"   New Customer ID: {new_customer.id}")
        print(f"   Name: {new_customer.first_name} {new_customer.last_name}")
        print(f"   Email: {new_customer.email}")
        
        # Clean up - delete the test customer
        print("\n[CLEANUP] Deleting test customer...")
        new_customer.delete()
        print("✅ Cleanup complete")
        
    except Exception as e:
        print(f"❌ FAILED to recreate customer: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 80)
    print("TEST COMPLETED SUCCESSFULLY!")
    print("=" * 80)


def main():
    """Main function."""
    print("\nCustomer Deletion and Recreation Test")
    print("This script tests the complete customer deletion flow\n")
    
    # Get inputs
    if len(sys.argv) < 3:
        print("Usage: python test_customer_deletion_comprehensive.py <tenant_id> <customer_email>")
        print("\nExample:")
        print("  python test_customer_deletion_comprehensive.py 507f1f77bcf86cd799439011 test@example.com")
        sys.exit(1)
    
    tenant_id = sys.argv[1]
    customer_email = sys.argv[2]
    
    test_customer_deletion_and_recreation(tenant_id, customer_email)


if __name__ == "__main__":
    main()
