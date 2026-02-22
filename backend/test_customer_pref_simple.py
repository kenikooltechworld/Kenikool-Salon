"""Simple test for customer preference model without server startup."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Set up minimal environment
os.environ['MONGODB_URL'] = 'mongodb://localhost:27017'
os.environ['MONGODB_DB'] = 'Kenikol_Salon'

from bson import ObjectId
from app.models.customer_preference import CustomerPreference

def test_model_creation():
    """Test creating a customer preference model."""
    print("Testing CustomerPreference model creation...")
    
    tenant_id = ObjectId()
    customer_id = ObjectId()
    
    # Create preference
    pref = CustomerPreference(
        tenant_id=tenant_id,
        customer_id=customer_id,
    )
    
    # Check defaults
    assert pref.preferred_staff_ids == []
    assert pref.preferred_service_ids == []
    assert pref.communication_methods == ["email"]
    assert pref.language == "en"
    assert pref.notes is None
    
    print("✓ Model creation test passed!")
    print(f"  - Tenant ID: {tenant_id}")
    print(f"  - Customer ID: {customer_id}")
    print(f"  - Default communication methods: {pref.communication_methods}")
    print(f"  - Default language: {pref.language}")

if __name__ == "__main__":
    test_model_creation()
