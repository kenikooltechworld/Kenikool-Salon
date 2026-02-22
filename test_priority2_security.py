#!/usr/bin/env python
"""Test runner for Priority 2 Security implementation."""

import sys
import subprocess

def run_tests():
    """Run all Priority 2 security tests."""
    test_files = [
        "backend/tests/security/test_waf_rules.py",
        "backend/tests/security/test_enumeration_prevention.py",
        "backend/tests/security/test_dependency_scanning.py",
    ]
    
    for test_file in test_files:
        print(f"\n{'='*80}")
        print(f"Running: {test_file}")
        print('='*80)
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            cwd="backend"
        )
        if result.returncode != 0:
            print(f"FAILED: {test_file}")
            return False
    
    return True

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
