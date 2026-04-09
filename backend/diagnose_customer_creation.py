"""
Diagnostic script to test customer creation flow.
"""

import sys
import logging
from bson import ObjectId
from app.db import connect_db
from app.models.customer import Customer
from app.models.tenant import Tenant

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def diagnose_customer_creation(tenant_id_str: str, email: str):
    """Test customer creation flow."""
    connect_db()
    
    tenant_id = ObjectId(tenant_id_str)
    
    # Check if tenant exists
    tenant = Tenant.objects(id=tenant_id).first()
    if not tenant:
        logger.error(f"Tenant {tenant_id} not found")
        return
    
    logger.info(f"Tenant: {tenant.name} ({tenant.subdomain})")
    
    # Check if customer exists
    existing = Customer.objects(email=email, tenant_id=tenant_id).first()
    if existing:
        logger.info(f"Customer already exists: {existing.id}")
        logger.info(f"  Name: {existing.first_name} {existing.last_name}")
        logger.info(f"  Email: {existing.email}")
        logger.info(f"  Phone: {existing.phone}")
        logger.info(f"  Status: {existing.status}")
        logger.info(f"  Created: {existing.created_at}")
        
        # Delete for testing
        response = input(f"\nDelete this customer? (yes/no): ")
        if response.lower() == "yes":
            existing.delete()
            logger.info("Customer deleted")
    else:
        logger.info(f"No customer found with email: {email}")
    
    # Try to create customer
    logger.info("\nAttempting to create customer...")
    try:
        new_customer = Customer(
            tenant_id=tenant_id,
            first_name="Test",
            last_name="Customer",
            email=email,
            phone="+234 801 234 5678",
            communication_preference="email",
            status="active",
            is_guest=False,
        )
        new_customer.save()
        logger.info(f"✓ Customer created successfully: {new_customer.id}")
        
        # Verify it was saved
        verify = Customer.objects(id=new_customer.id).first()
        if verify:
            logger.info("✓ Customer verified in database")
        else:
            logger.error("✗ Customer not found after save")
            
    except Exception as e:
        logger.error(f"✗ Failed to create customer: {str(e)}")
        logger.exception(e)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python diagnose_customer_creation.py <tenant_id> <email>")
        sys.exit(1)
    
    diagnose_customer_creation(sys.argv[1], sys.argv[2])
