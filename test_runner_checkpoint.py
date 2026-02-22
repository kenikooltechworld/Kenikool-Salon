#!/usr/bin/env python
"""Run tests for Task 4.1 checkpoint."""

import subprocess
import sys
import os

# Change to the root directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 80)
print("TASK 4.1: CORE INFRASTRUCTURE CHECKPOINT")
print("=" * 80)
print()

# Run unit tests
print("1. Running unit tests...")
print("-" * 80)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests/unit/", "-v", "--tb=short"],
    capture_output=False,
    text=True,
)

if result.returncode != 0:
    print("\n❌ Unit tests failed!")
    sys.exit(1)

print("\n✅ Unit tests passed!")
print()

# Run integration tests
print("2. Running integration tests...")
print("-" * 80)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests/integration/", "-v", "--tb=short"],
    capture_output=False,
    text=True,
)

if result.returncode != 0:
    print("\n❌ Integration tests failed!")
    sys.exit(1)

print("\n✅ Integration tests passed!")
print()

# Run coverage check
print("3. Checking test coverage...")
print("-" * 80)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "backend/tests/", "--cov=app", "--cov-report=term-missing"],
    capture_output=False,
    text=True,
)

print()
print("=" * 80)
print("CHECKPOINT VALIDATION COMPLETE")
print("=" * 80)
