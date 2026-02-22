"""Quick test for customer preference implementation."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from bson import ObjectId
from app.models.customer_preference import CustomerPreference

def test_customer_preference_model():
    """Test basic customer preference model functionality."""
    print("Testing CustomerPreference model...")
    
    tenant_id = ObjectId()
    customer_id = ObjectId()
    staff_id = ObjectId()
    service_id = ObjectId()
    
    # Test 1: Create with defaults
    print("  Test 1: Create with defaults...")
    pref = CustomerPreference(
        tenant_id=tenant_id,
        customer_id=customer_id,
    )
    pref.save()
    
    assert pref.id is not None
    assert pref.customer_id == customer_id
    assert pref.preferred_staff_ids == []
    assert pref.communication_methods == ["email"]
    assert pref.language == "en"
    print("    ✓ Passed")
    
    # Test 2: Update preferences
    print("  Test 2: Update preferences...")
    pref.preferred_staff_ids = [staff_id]
    pref.preferred_service_ids = [service_id]
    pref.communication_methods = ["email", "sms"]
    pref.language = "fr"
    pref.save()
    
    updated = CustomerPreference.objects(id=pref.id).first()
    assert updated.preferred_staff_ids == [staff_id]
    assert updated.language == "fr"
    print("    ✓ Passed")
    
    # Test 3: Query by customer
    print("  Test 3: Query by customer...")
    found = CustomerPreference.objects(
        customer_id=customer_id,
        tenant_id=tenant_id
    ).first()
    assert found is not None
    assert found.id == pref.id
    print("    ✓ Passed")
    
    # Cleanup
    pref.delete()
    
    print("✓ All tests passed!")

if __name__ == "__main__":
    test_customer_preference_model()
