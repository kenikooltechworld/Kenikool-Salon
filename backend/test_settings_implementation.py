"""Quick test script for tenant settings implementation."""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.services.tenant_settings_service import TenantSettingsService
from app.schemas.tenant_settings import TenantSettingsSchema, BusinessHours
from datetime import datetime

def test_settings_schema():
    """Test that the settings schema validates correctly."""
    print("Testing TenantSettingsSchema validation...")
    
    # Test with valid data
    settings_data = {
        "salon_name": "Test Salon",
        "email": "test@salon.com",
        "phone": "+234801234567",
        "address": "123 Main St",
        "tax_rate": 7.5,
        "currency": "NGN",
        "timezone": "Africa/Lagos",
        "language": "en",
        "business_hours": {
            "monday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
            "tuesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
            "wednesday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
            "thursday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
            "friday": {"open_time": "09:00", "close_time": "18:00", "is_closed": False},
            "saturday": {"open_time": "10:00", "close_time": "16:00", "is_closed": False},
            "sunday": {"open_time": "00:00", "close_time": "00:00", "is_closed": True},
        },
        "notification_email": True,
        "notification_sms": False,
        "notification_push": False,
        "logo_url": None,
        "primary_color": "#FF6B6B",
        "secondary_color": "#FFFFFF",
        "appointment_reminder_hours": 24,
        "allow_online_booking": True,
        "require_customer_approval": False,
        "auto_confirm_bookings": True,
    }
    
    try:
        schema = TenantSettingsSchema(**settings_data)
        print("✅ Schema validation passed")
        print(f"   - Salon Name: {schema.salon_name}")
        print(f"   - Currency: {schema.currency}")
        print(f"   - Timezone: {schema.timezone}")
        print(f"   - Tax Rate: {schema.tax_rate}%")
        return True
    except Exception as e:
        print(f"❌ Schema validation failed: {e}")
        return False

def test_settings_service():
    """Test the settings service methods."""
    print("\nTesting TenantSettingsService...")
    
    # Test get_settings with non-existent tenant
    result = TenantSettingsService.get_settings("nonexistent_tenant_id")
    if result is None:
        print("✅ get_settings returns None for non-existent tenant")
    else:
        print("❌ get_settings should return None for non-existent tenant")
        return False
    
    return True

def test_business_hours():
    """Test business hours validation."""
    print("\nTesting BusinessHours validation...")
    
    try:
        hours = BusinessHours(open_time="09:00", close_time="18:00", is_closed=False)
        print("✅ BusinessHours validation passed")
        print(f"   - Open: {hours.open_time}")
        print(f"   - Close: {hours.close_time}")
        print(f"   - Closed: {hours.is_closed}")
        return True
    except Exception as e:
        print(f"❌ BusinessHours validation failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Tenant Settings Implementation Tests")
    print("=" * 60)
    
    results = []
    results.append(("Schema Validation", test_settings_schema()))
    results.append(("Service Methods", test_settings_service()))
    results.append(("Business Hours", test_business_hours()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
