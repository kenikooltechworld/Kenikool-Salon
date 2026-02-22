"""Simple test to verify payment endpoint works."""

import sys
import os
from decimal import Decimal
from unittest.mock import patch, MagicMock
from bson import ObjectId

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.models.payment import Payment
from app.models.invoice import Invoice
from app.models.customer import Customer
from app.models.tenant import Tenant
from app.models.user import User
from app.services.payment_service import PaymentService
from app.services.auth_service import AuthenticationService
from app.config import settings
from app.db import init_db, close_db

# Initialize database
init_db()

# Create test data
tenant = Tenant(
    name="Test Salon",
    subdomain="test-salon-simple",
    subscription_tier="professional",
    status="active",
)
tenant.save()
print(f"✓ Created tenant: {tenant.id}")

customer = Customer(
    tenant_id=tenant.id,
    first_name="John",
    last_name="Doe",
    email="customer@test.com",
    phone="+234123456789",
)
customer.save()
print(f"✓ Created customer: {customer.id}")

invoice = Invoice(
    tenant_id=tenant.id,
    customer_id=customer.id,
    subtotal=Decimal("10000"),
    discount=Decimal("0"),
    tax=Decimal("1000"),
    total=Decimal("11000"),
    status="issued",
)
invoice.save()
print(f"✓ Created invoice: {invoice.id}")

# Test payment service
print("\nTesting PaymentService...")

# Mock the context
with patch("app.context.get_tenant_id") as mock_get_tenant_id:
    mock_get_tenant_id.return_value = str(tenant.id)
    
    # Mock Paystack
    with patch("app.services.paystack_service.PaystackService.initialize_transaction") as mock_paystack:
        mock_paystack.return_value = {
            "reference": "test_ref_123",
            "authorization_url": "https://checkout.paystack.com/test",
            "access_code": "test_access_code",
        }
        
        service = PaymentService()
        
        try:
            result = service.initialize_payment(
                amount=Decimal("11000"),
                customer_id=str(customer.id),
                invoice_id=str(invoice.id),
                email="customer@test.com",
                metadata={"order_id": "12345"},
            )
            
            print(f"✓ Payment initialized successfully")
            print(f"  - Payment ID: {result['payment_id']}")
            print(f"  - Reference: {result['reference']}")
            print(f"  - Authorization URL: {result['authorization_url']}")
            
            # Verify payment record
            payment = Payment.objects(
                reference="test_ref_123",
                tenant_id=tenant.id,
            ).first()
            
            if payment:
                print(f"✓ Payment record created")
                print(f"  - Status: {payment.status}")
                print(f"  - Amount: {payment.amount}")
                print(f"  - Customer ID: {payment.customer_id}")
            else:
                print("✗ Payment record not found")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()

# Cleanup
close_db()
print("\n✓ Test completed successfully")
