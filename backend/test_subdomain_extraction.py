#!/usr/bin/env python
"""Test subdomain extraction logic."""

def extract_subdomain(hostname: str) -> str:
    """Extract subdomain from hostname."""
    parts = hostname.split(".")
    
    if len(parts) < 2:
        return ""
    
    if len(parts) == 2:
        if parts[1] == "localhost":
            return parts[0]
        return ""
    
    return parts[0]

# Test cases
test_cases = [
    ("kenzola-salon.localhost:3000", "kenzola-salon"),
    ("kenzola-salon.localhost", "kenzola-salon"),
    ("localhost:3000", ""),
    ("localhost", ""),
    ("kenzola-salon.kenikool.com", "kenzola-salon"),
    ("api.kenikool.com", "api"),
    ("kenikool.com", ""),
]

print("Testing subdomain extraction:")
for hostname, expected in test_cases:
    hostname_without_port = hostname.split(":")[0]
    result = extract_subdomain(hostname_without_port)
    status = "✓" if result == expected else "✗"
    print(f"{status} {hostname:40} -> {result:20} (expected: {expected})")
