"""Script to delete all users and their related data from the database."""

import sys
import os
from datetime import datetime
from bson import ObjectId

# Add backend to path
sys.path.insert(0, '/app/backend')

# Initialize database connection
from app.db import init_db
init_db()

from app.models.user import User
from app.models.customer import Customer
from app.models.staff import Staff
from app.models.tenant import Tenant
from app.models.appointment import Appointment
from app.models.invoice import Invoice
from app.models.payment import Payment
from app.models.transaction import Transaction
from app.models.subscription import Subscription
from app.models.audit_log import AuditLog


def delete_all_users():
    """Delete all users and their related data."""
    print("\n" + "="*60)
    print("DELETE ALL USERS AND RELATED DATA")
    print("="*60 + "\n")
    
    try:
        # Get all users
        all_users = User.objects()
        user_count = all_users.count()
        
        if user_count == 0:
            print("✓ No users found in database")
            return True
        
        print(f"Found {user_count} users to delete\n")
        
        # Collect all tenant IDs from users
        tenant_ids = set()
        for user in all_users:
            if hasattr(user, 'tenant_id') and user.tenant_id:
                tenant_ids.add(user.tenant_id)
        
        print(f"Found {len(tenant_ids)} tenants associated with users\n")
        
        # Delete data for each tenant
        for tenant_id in tenant_ids:
            print(f"Deleting data for tenant: {tenant_id}")
            
            # Delete customers
            customers = Customer.objects(tenant_id=tenant_id)
            customer_count = customers.count()
            customers.delete()
            print(f"  ✓ Deleted {customer_count} customers")
            
            # Delete staff
            staff = Staff.objects(tenant_id=tenant_id)
            staff_count = staff.count()
            staff.delete()
            print(f"  ✓ Deleted {staff_count} staff members")
            
            # Delete appointments
            appointments = Appointment.objects(tenant_id=tenant_id)
            appointment_count = appointments.count()
            appointments.delete()
            print(f"  ✓ Deleted {appointment_count} appointments")
            
            # Delete invoices
            invoices = Invoice.objects(tenant_id=tenant_id)
            invoice_count = invoices.count()
            invoices.delete()
            print(f"  ✓ Deleted {invoice_count} invoices")
            
            # Delete payments
            payments = Payment.objects(tenant_id=tenant_id)
            payment_count = payments.count()
            payments.delete()
            print(f"  ✓ Deleted {payment_count} payments")
            
            # Delete transactions
            transactions = Transaction.objects(tenant_id=tenant_id)
            transaction_count = transactions.count()
            transactions.delete()
            print(f"  ✓ Deleted {transaction_count} transactions")
            
            # Delete subscriptions
            subscriptions = Subscription.objects(tenant_id=tenant_id)
            subscription_count = subscriptions.count()
            subscriptions.delete()
            print(f"  ✓ Deleted {subscription_count} subscriptions")
            
            # Delete audit logs
            audit_logs = AuditLog.objects(tenant_id=tenant_id)
            audit_log_count = audit_logs.count()
            audit_logs.delete()
            print(f"  ✓ Deleted {audit_log_count} audit logs")
            
            # Delete tenant
            try:
                tenant = Tenant.objects(id=tenant_id).first()
                if tenant:
                    tenant.delete()
                    print(f"  ✓ Deleted tenant")
            except Exception as e:
                print(f"  ⚠ Could not delete tenant: {e}")
            
            print()
        
        # Delete all users
        print(f"Deleting {user_count} users...")
        User.objects().delete()
        print(f"✓ Deleted {user_count} users\n")
        
        # Verify deletion
        remaining_users = User.objects().count()
        if remaining_users == 0:
            print("="*60)
            print("✓ ALL USERS AND RELATED DATA SUCCESSFULLY DELETED")
            print("="*60 + "\n")
            return True
        else:
            print(f"⚠ Warning: {remaining_users} users still remain in database")
            return False
            
    except Exception as e:
        print(f"✗ Error during deletion: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("\n⚠️  WARNING: This will delete ALL users and their related data!")
    print("This action cannot be undone.\n")
    
    # Check for command-line argument
    if len(sys.argv) > 1 and sys.argv[1] == "--confirm":
        confirm = "DELETE ALL"
    else:
        confirm = input("Type 'DELETE ALL' to confirm: ").strip()
    
    if confirm == "DELETE ALL":
        success = delete_all_users()
        sys.exit(0 if success else 1)
    else:
        print("✓ Deletion cancelled")
        sys.exit(0)
