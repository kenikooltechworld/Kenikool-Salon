#!/usr/bin/env python
"""Manual test script for registration service - NO DATABASE REQUIRED."""

from app.services.registration_service import RegistrationService
from app.config import Settings

settings = Settings()
service = RegistrationService(settings)

print("=" * 80)
print("REGISTRATION SERVICE TESTS - REAL DATA (NO DATABASE)")
print("=" * 80)

passed = 0
failed = 0

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
if is_valid:
    print(f"✓ PASS")
    passed += 1
else:
    print(f"✗ FAIL: {error}")
    failed += 1

# Test 2: Invalid email
print("\n[TEST 2] Invalid email format")
data['email'] = 'invalid-email'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "Invalid email format" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject invalid email")
    failed += 1

# Test 3: Weak password (too short)
print("\n[TEST 3] Weak password (too short)")
data['email'] = 'john@example.com'
data['password'] = 'weak'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "8 characters" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject weak password")
    failed += 1

# Test 4: Password missing uppercase
print("\n[TEST 4] Password missing uppercase")
data['password'] = 'securepass123!'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "uppercase" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject password without uppercase")
    failed += 1

# Test 5: Password missing lowercase
print("\n[TEST 5] Password missing lowercase")
data['password'] = 'SECUREPASS123!'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "lowercase" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject password without lowercase")
    failed += 1

# Test 6: Password missing digit
print("\n[TEST 6] Password missing digit")
data['password'] = 'SecurePass!'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "digit" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject password without digit")
    failed += 1

# Test 7: Password missing special character
print("\n[TEST 7] Password missing special character")
data['password'] = 'SecurePass123'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "special character" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject password without special char")
    failed += 1

# Test 8: Valid strong password
print("\n[TEST 8] Valid strong password")
data['password'] = 'SecurePass123!'
is_valid, error = service.validate_registration_data(data)
if is_valid:
    print(f"✓ PASS")
    passed += 1
else:
    print(f"✗ FAIL: {error}")
    failed += 1

# Test 9: Invalid phone (too short)
print("\n[TEST 9] Invalid phone (too short)")
data['phone'] = '123'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "Invalid phone format" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject invalid phone")
    failed += 1

# Test 10: Valid phone formats
print("\n[TEST 10] Valid phone formats")
valid_phones = ['+234 123 456 7890', '+2341234567890', '2341234567890', '+27 10 123 4567', '+256 701 234567']
all_valid = True
for phone in valid_phones:
    data['phone'] = phone
    is_valid, error = service.validate_registration_data(data)
    if is_valid:
        print(f"  ✓ {phone}")
    else:
        print(f"  ✗ {phone}: {error}")
        all_valid = False
if all_valid:
    passed += 1
else:
    failed += 1

# Test 11: Short salon name
print("\n[TEST 11] Short salon name")
data['phone'] = '+234 123 456 7890'
data['salon_name'] = 'AB'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "3-255 characters" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject short salon name")
    failed += 1

# Test 12: Short owner name
print("\n[TEST 12] Short owner name")
data['salon_name'] = 'Acme Salon'
data['owner_name'] = 'J'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "2-100 characters" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject short owner name")
    failed += 1

# Test 13: Short address
print("\n[TEST 13] Short address")
data['owner_name'] = 'John Doe'
data['address'] = '123'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "5-500 characters" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject short address")
    failed += 1

# Test 14: Invalid referral code
print("\n[TEST 14] Invalid referral code")
data['address'] = '123 Main St, Lagos'
data['referral_code'] = 'REF@123'
is_valid, error = service.validate_registration_data(data)
if not is_valid and "alphanumeric" in error:
    print(f"✓ PASS - Correctly rejected: {error}")
    passed += 1
else:
    print(f"✗ FAIL: Should reject invalid referral code")
    failed += 1

# Test 15: Valid referral code
print("\n[TEST 15] Valid referral code")
data['referral_code'] = 'REF123'
is_valid, error = service.validate_registration_data(data)
if is_valid:
    print(f"✓ PASS")
    passed += 1
else:
    print(f"✗ FAIL: {error}")
    failed += 1

# Test 16: Verification code generation
print("\n[TEST 16] Verification code generation (10 codes)")
codes = set()
all_valid = True
for i in range(10):
    code = service.generate_verification_code()
    codes.add(code)
    is_numeric = code.isdigit()
    is_6_digits = len(code) == 6
    if is_numeric and is_6_digits:
        print(f"  ✓ Code {i+1}: {code}")
    else:
        print(f"  ✗ Code {i+1}: {code} (numeric: {is_numeric}, length: {len(code)})")
        all_valid = False
print(f"  Uniqueness: {len(codes)}/10 unique codes")
if all_valid and len(codes) >= 9:
    passed += 1
else:
    failed += 1

# Test 17: Password hashing
print("\n[TEST 17] Password hashing")
password = 'SecurePass123!'
hash1 = service.hash_password(password)
hash2 = service.hash_password(password)
if hash1 != password and hash2 != password and hash1 != hash2 and len(hash1) > 20:
    print(f"  ✓ Original: {password}")
    print(f"  ✓ Hash 1:   {hash1[:50]}...")
    print(f"  ✓ Hash 2:   {hash2[:50]}...")
    print(f"  ✓ Hashes are different (due to salt)")
    print(f"  ✓ Hash length: {len(hash1)} characters")
    passed += 1
else:
    print(f"  ✗ Password hashing failed")
    failed += 1

# Test 18: Email validation
print("\n[TEST 18] Email validation")
test_emails = [
    ('john@example.com', True),
    ('invalid-email', False),
    ('john@', False),
    ('john@example', False),
    ('test.user+tag@example.co.uk', True),
]
all_valid = True
for email, should_be_valid in test_emails:
    is_valid = service._is_valid_email(email)
    if is_valid == should_be_valid:
        print(f"  ✓ {email}: {is_valid}")
    else:
        print(f"  ✗ {email}: {is_valid} (expected: {should_be_valid})")
        all_valid = False
if all_valid:
    passed += 1
else:
    failed += 1

# Test 19: Phone validation
print("\n[TEST 19] Phone validation")
test_phones = [
    ('+234 123 456 7890', True),
    ('+2341234567890', True),
    ('2341234567890', True),
    ('+27 10 123 4567', True),
    ('+256 701 234567', True),
    ('123', False),
    ('+1234', False),
]
all_valid = True
for phone, should_be_valid in test_phones:
    is_valid = service._is_valid_phone(phone)
    if is_valid == should_be_valid:
        print(f"  ✓ {phone}: {is_valid}")
    else:
        print(f"  ✗ {phone}: {is_valid} (expected: {should_be_valid})")
        all_valid = False
if all_valid:
    passed += 1
else:
    failed += 1

# Test 20: Password strength
print("\n[TEST 20] Password strength validation")
test_passwords = [
    ('SecurePass123!', True),
    ('weak', False),
    ('Pass1!', False),
    ('securepass123!', False),
    ('SECUREPASS123!', False),
    ('SecurePass!', False),
    ('SecurePass123', False),
    ('Pass1!ab', True),
]
all_valid = True
for password, should_be_strong in test_passwords:
    is_strong, error = service._is_strong_password(password)
    if is_strong == should_be_strong:
        status = "Strong" if is_strong else f"Weak - {error}"
        print(f"  ✓ '{password}': {status}")
    else:
        print(f"  ✗ '{password}': {is_strong} (expected: {should_be_strong})")
        all_valid = False
if all_valid:
    passed += 1
else:
    failed += 1

print("\n" + "=" * 80)
print(f"RESULTS: {passed} PASSED, {failed} FAILED")
print("=" * 80)
