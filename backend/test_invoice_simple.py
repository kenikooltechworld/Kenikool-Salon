"""Simple test to verify invoice implementation."""

import sys
from decimal import Decimal
from bson import ObjectId
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, '/workspace/backend')

# Test imports
try:
    from app.models.invoice import Invoice, InvoiceLineItem
    print("✓ Invoice model imported successfully")
except Exception as e:
    print(f"✗ Failed to import Invoice model: {e}")
    sys.exit(1)

try:
    from app.schemas.invoice import (
        InvoiceCreateRequest,
        InvoiceResponse,
        InvoiceLineItemRequest,
    )
    print("✓ Invoice schemas imported successfully")
except Exception as e:
    print(f"✗ Failed to import Invoice schemas: {e}")
    sys.exit(1)

try:
    from app.services.invoice_service import InvoiceService
    print("✓ InvoiceService imported successfully")
except Exception as e:
    print(f"✗ Failed to import InvoiceService: {e}")
    sys.exit(1)

try:
    from app.routes.invoices import router
    print("✓ Invoice routes imported successfully")
except Exception as e:
    print(f"✗ Failed to import Invoice routes: {e}")
    sys.exit(1)

# Test model creation
try:
    tenant_id = ObjectId()
    customer_id = ObjectId()
    
    line_item = InvoiceLineItem(
        service_id=ObjectId(),
        service_name="Haircut",
        quantity=Decimal("1"),
        unit_price=Decimal("50.00"),
        total=Decimal("50.00"),
    )
    
    invoice = Invoice(
        tenant_id=tenant_id,
        customer_id=customer_id,
        line_items=[line_item],
        subtotal=Decimal("50.00"),
        discount=Decimal("0"),
        tax=Decimal("5.00"),
        total=Decimal("55.00"),
        status="draft",
    )
    
    print("✓ Invoice model created successfully")
except Exception as e:
    print(f"✗ Failed to create Invoice model: {e}")
    sys.exit(1)

# Test schema validation
try:
    line_item_req = InvoiceLineItemRequest(
        service_id=str(ObjectId()),
        service_name="Haircut",
        quantity=Decimal("1"),
        unit_price=Decimal("50.00"),
    )
    
    invoice_req = InvoiceCreateRequest(
        customer_id=str(customer_id),
        line_items=[line_item_req],
        discount=Decimal("0"),
        tax=Decimal("5.00"),
    )
    
    print("✓ Invoice schemas validated successfully")
except Exception as e:
    print(f"✗ Failed to validate Invoice schemas: {e}")
    sys.exit(1)

# Test service methods exist
try:
    assert hasattr(InvoiceService, 'create_invoice')
    assert hasattr(InvoiceService, 'create_invoice_from_appointment')
    assert hasattr(InvoiceService, 'get_invoice')
    assert hasattr(InvoiceService, 'list_invoices')
    assert hasattr(InvoiceService, 'update_invoice')
    assert hasattr(InvoiceService, 'mark_invoice_paid')
    assert hasattr(InvoiceService, 'cancel_invoice')
    assert hasattr(InvoiceService, 'issue_invoice')
    print("✓ InvoiceService has all required methods")
except Exception as e:
    print(f"✗ InvoiceService missing methods: {e}")
    sys.exit(1)

# Test route endpoints exist
try:
    assert hasattr(router, 'routes')
    print(f"✓ Invoice router has {len(router.routes)} endpoints")
except Exception as e:
    print(f"✗ Invoice router error: {e}")
    sys.exit(1)

print("\n✓ All invoice implementation tests passed!")
