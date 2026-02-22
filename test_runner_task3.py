#!/usr/bin/env python
"""Run Task 3 tests."""

import subprocess
import sys
import os

os.chdir("backend")

# Run all Task 3 related tests
test_files = [
    "tests/unit/test_authentication.py",
    "tests/unit/test_authentication_properties.py",
    "tests/unit/test_rbac.py",
    "tests/unit/test_rbac_properties.py",
    "tests/unit/test_mfa.py",
    "tests/unit/test_mfa_real_data.py",
    "tests/unit/test_session_management.py",
    "tests/unit/test_session_properties.py",
]

for test_file in test_files:
    print(f"\n{'='*80}")
    print(f"Running {test_file}")
    print('='*80)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
        capture_output=False,
        text=True,
    )
    if result.returncode != 0:
        print(f"FAILED: {test_file}")
    else:
        print(f"PASSED: {test_file}")
