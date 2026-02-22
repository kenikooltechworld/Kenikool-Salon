#!/usr/bin/env python
"""Run Phase 3 tests and generate verification report."""

import subprocess
import sys
import json
from pathlib import Path

def run_tests(test_path, test_name):
    """Run tests and return results."""
    print(f"\n{'='*70}")
    print(f"Running {test_name}...")
    print(f"{'='*70}")
    
    result = subprocess.run(
        [sys.executable, "-m", "pytest", test_path, "-v", "--tb=short", "-q"],
        cwd="backend",
        capture_output=True,
        text=True,
        timeout=60
    )
    
    return {
        "name": test_name,
        "path": test_path,
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "passed": result.returncode == 0
    }

def main():
    """Run all Phase 3 tests."""
    print("\n" + "="*70)
    print("PHASE 3 - STAFF AND CUSTOMER MANAGEMENT TEST VERIFICATION")
    print("="*70)
    
    tests = [
        # Staff Management Tests
        ("tests/unit/test_staff.py", "Staff Model Unit Tests"),
        ("tests/integration/test_staff_api.py", "Staff API Integration Tests"),
        
        # Shift Management Tests
        ("tests/unit/test_shift.py", "Shift Model Unit Tests"),
        ("tests/integration/test_shift_api.py", "Shift API Integration Tests"),
        
        # Time-Off Request Tests
        ("tests/unit/test_time_off_request.py", "Time-Off Request Unit Tests"),
        ("tests/integration/test_time_off_request_api.py", "Time-Off Request API Tests"),
        
        # Customer Management Tests
        ("tests/unit/test_customer.py", "Customer Model Unit Tests"),
        ("tests/integration/test_customer_api.py", "Customer API Integration Tests"),
        
        # Customer History Tests
        ("tests/unit/test_appointment_history.py", "Appointment History Unit Tests"),
        ("tests/integration/test_appointment_history_api.py", "Appointment History API Tests"),
        
        # Customer Preferences Tests
        ("tests/unit/test_customer_preference.py", "Customer Preference Unit Tests"),
        ("tests/integration/test_customer_preference_api.py", "Customer Preference API Tests"),
    ]
    
    results = []
    passed_count = 0
    failed_count = 0
    
    for test_path, test_name in tests:
        try:
            result = run_tests(test_path, test_name)
            results.append(result)
            
            if result["passed"]:
                passed_count += 1
                print(f"✓ {test_name}: PASSED")
            else:
                failed_count += 1
                print(f"✗ {test_name}: FAILED")
                if result["stderr"]:
                    print(f"  Error: {result['stderr'][:200]}")
        except subprocess.TimeoutExpired:
            print(f"✗ {test_name}: TIMEOUT")
            failed_count += 1
        except Exception as e:
            print(f"✗ {test_name}: ERROR - {str(e)}")
            failed_count += 1
    
    # Print summary
    print("\n" + "="*70)
    print("PHASE 3 TEST SUMMARY")
    print("="*70)
    print(f"Total Tests: {len(tests)}")
    print(f"Passed: {passed_count}")
    print(f"Failed: {failed_count}")
    print(f"Success Rate: {(passed_count/len(tests)*100):.1f}%")
    
    # Print detailed results
    print("\n" + "="*70)
    print("DETAILED RESULTS")
    print("="*70)
    
    for result in results:
        status = "✓ PASSED" if result["passed"] else "✗ FAILED"
        print(f"\n{result['name']}: {status}")
        if not result["passed"] and result["stdout"]:
            print(f"Output:\n{result['stdout'][:500]}")
    
    return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
