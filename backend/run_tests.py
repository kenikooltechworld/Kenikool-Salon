#!/usr/bin/env python
"""Run tests and report results."""

import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/unit/", "-v", "--tb=short"],
    cwd="backend",
    capture_output=True,
    text=True,
)

print(result.stdout)
print(result.stderr)
sys.exit(result.returncode)
