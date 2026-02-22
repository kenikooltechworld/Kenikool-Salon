#!/usr/bin/env python
"""Manual test script for registration service with real data."""

from app.services.registration_service import RegistrationService
from app.config import Settings

settings = Settings()
service = RegistrationService(settings)

print("=" * 70)
print("REGISTRATION SERVICE TESTS - REAL DATA")
print("=" * 70)

# Test 1: Valid registration data
print("\n[TEST 1] Valid registration data")
data = {
    'salon_name': 'Acme Salon',
    'owner_name': 'John Doe',
    'email': 'john@example.com',
    'phone': '+234 123 456 7890',
    'password': 'SecurePass123!',
    'address': '123 Main St, Lagos',
}
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS" if is_valid else f"✗ FAIL: {error}")

# Test 2: Invalid email
print("\n[TEST 2] Invalid email format")
data['email'] = 'invalid-email'
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS - Correctly rejected" if not is_valid else f"✗ FAIL: Should reject invalid email")
print(f"  Error: {error}")

# Test 3: Weak password (too short)
print("\n[TEST 3] Weak password (too short)")
data['email'] = 'john@example.com'
data['password'] = 'weak'
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS - Correctly rejected" if not is_valid else f"✗ FAIL: Should reject weak password")
print(f"  Error: {error}")

# Test 4: Password missing uppercase
print("\n[TEST 4] Password missing uppercase")
data['password'] = 'securepass123!'
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS - Correctly rejected" if not is_valid else f"✗ FAIL: Should reject password without uppercase")
print(f"  Error: {error}")

# Test 5: Password missing special character
print("\n[TEST 5] Password missing special character")
data['password'] = 'SecurePass123'
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS - Correctly rejected" if not is_valid else f"✗ FAIL: Should reject password without special char")
print(f"  Error: {error}")

# Test 6: Valid strong password
print("\n[TEST 6] Valid strong password")
data['password'] = 'SecurePass123!'
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS" if is_valid else f"✗ FAIL: {error}")

# Test 7: Invalid phone
print("\n[TEST 7] Invalid phone format")
data['phone'] = '123'
is_valid, error = service.validate_registration_data(data)
print(f"✓ PASS - Correctly rejected" if not is_valid else f"✗ FAIL: Should reject invalid phone")
print(f"  Error: {error}")

# Test 8: Valid phone formats
print("\n[TEST 8] Valid phone formats")
valid_phones = ['+234 123 456 7890', '+2341234567890', '2341234567890']
for phone in valid_phones:
    data['phone'] = phone
    is_valid, error = service.validate_registration_data(data)
    status = "✓" if is_valid else "✗"
    print(f"  {status} {phone}")

# Test 9: Subdomain generation
print("\n[TEST 9] Subdomain generation")
test_names = [
    ('Acme Salon', 'acme-salon'),
    ('Acme\'s Salon & Spa', 'acmes-salon-spa'),
    ('The Best Hair Salon', 'the-best-hair-salon'),
]
for name, expected in test_names:
    subdomain = service.generate_subdomain(name)
    status = "✓" if subdomain == expected else "✗"
    print(f"  {status} '{name}' -> '{subdomain}' (expected: '{expected}')")

# Test 10: Verification code generation
print("\n[TEST 10] Verification code generation")
codes = set()
for i in range(10):
    code = service.generate_verification_code()
    codes.add(code)
    is_numeric = code.isdigit()
    is_6_digits = len(code) == 6
    status = "✓" if (is_numeric and is_6_digits) else "✗"
    print(f"  {status} Code {i+1}: {code} (numeric: {is_numeric}, length: {len(code)})")
print(f"  Uniqueness: {len(codes)}/10 unique codes")

# Test 11: Password hashing
print("\n[TEST 11] Password hashing")
password = 'SecurePass123!'
hash1 = service.hash_password(password)
hash2 = service.hash_password(password)
print(f"  Original: {password}")
print(f"  Hash 1:   {hash1[:50]}...")
print(f"  Hash 2:   {hash2[:50]}...")
print(f"  ✓ Hashes are different (due to salt): {hash1 != hash2}")
print(f"  ✓ Hash length: {len(hash1)} characters")

# Test 12: Email validation
print("\n[TEST 12] Email validation")
test_emails = [
    ('john@example.com', True),
    ('invalid-email', False),
    ('john@', False),
    ('john@example', False),
    ('test.user+tag@example.co.uk', True),
]
for email, should_be_valid in test_emails:
    is_valid = service._is_valid_email(email)
    status = "✓" if is_valid == should_be_valid else "✗"
    print(f"  {status} {email}: {is_valid} (expected: {should_be_valid})")

# Test 13: Phone validation
print("\n[TEST 13] Phone validation")
test_phones = [
    ('+234 123 456 7890', True),
    ('+2341234567890', True),
    ('2341234567890', True),
    ('123', False),
    ('+234 123 456 7890 123', False),
]
for phone, should_be_valid in test_phones:
    is_valid = service._is_valid_phone(phone)
    status = "✓" if is_valid == should_be_valid else "✗"
    print(f"  {status} {phone}: {is_valid} (expected: {should_be_valid})")

# Test 14: Password strength
print("\n[TEST 14] Password strength validation")
test_passwords = [
    ('SecurePass123!', True, None),
    ('weak', False, '12 characters'),
    ('securepass123!', False, 'uppercase'),
    ('SECUREPASS123!', False, 'lowercase'),
    ('SecurePass!', False, 'digit'),
    ('SecurePass123', False, 'special character'),
]
for password, should_be_strong, error_keyword in test_passwords:
    is_strong, error = service._is_strong_password(password)
    if should_be_strong:
        status = "✓" if is_strong else "✗"
        print(f"  {status} '{password}': Strong")
    else:
        status = "✓" if (not is_strong and error_keyword in error) else "✗"
        print(f"  {status} '{password}': Weak - {error}")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETED")
print("=" * 70)
