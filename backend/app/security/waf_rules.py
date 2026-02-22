"""Web Application Firewall (WAF) rules for OWASP Top 10 protection."""

import re
import logging
from typing import Any, Dict, List
from urllib.parse import unquote

logger = logging.getLogger(__name__)


class WAFRules:
    """OWASP Top 10 WAF rules implementation."""

    # SQL Injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\bUNION\b.*\bSELECT\b)",
        r"(\bSELECT\b.*\bFROM\b)",
        r"(\bINSERT\b.*\bINTO\b)",
        r"(\bUPDATE\b.*\bSET\b)",
        r"(\bDELETE\b.*\bFROM\b)",
        r"(\bDROP\b.*\b(TABLE|DATABASE)\b)",
        r"(\bEXEC\b|\bEXECUTE\b)",
        r"(--|#|\/\*|\*\/)",  # SQL comments
        r"(\bOR\b.*=.*)",
        r"(\bAND\b.*=.*)",
    ]

    # NoSQL Injection patterns
    NOSQL_INJECTION_PATTERNS = [
        r"\$where",
        r"\$regex",
        r"\$ne",
        r"\$gt",
        r"\$lt",
        r"\$gte",
        r"\$lte",
        r"\$in",
        r"\$nin",
        r"\$or",
        r"\$and",
        r"\$not",
        r"\$nor",
        r"\$exists",
        r"\$type",
        r"\$mod",
        r"\$text",
        r"\$where",
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"<iframe[^>]*>",
        r"<object[^>]*>",
        r"<embed[^>]*>",
        r"<img[^>]*on\w+",
        r"<svg[^>]*on\w+",
    ]

    # Command Injection patterns
    COMMAND_INJECTION_PATTERNS = [
        r"[;&|`$(){}[\]<>]",  # Shell metacharacters
        r"\$\(",  # Command substitution
        r"`.*`",  # Backtick command substitution
    ]

    # Path Traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",
        r"\.\.",
        r"%2e%2e",
        r"\.\.\\",
    ]

    # XXE patterns
    XXE_PATTERNS = [
        r"<!DOCTYPE[^>]*\[",
        r"<!ENTITY",
        r"SYSTEM",
        r"PUBLIC",
    ]

    @staticmethod
    def check_sql_injection(value: str) -> bool:
        """Check for SQL injection attempts."""
        if not isinstance(value, str):
            return False

        value_upper = value.upper()
        for pattern in WAFRules.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                logger.warning(f"SQL injection attempt detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_nosql_injection(value: Any) -> bool:
        """Check for NoSQL injection attempts."""
        if isinstance(value, dict):
            for key in value.keys():
                if key.startswith("$"):
                    logger.warning(f"NoSQL injection attempt detected: {key}")
                    return True
            for v in value.values():
                if WAFRules.check_nosql_injection(v):
                    return True
            return False

        if isinstance(value, list):
            for item in value:
                if WAFRules.check_nosql_injection(item):
                    return True
            return False

        if isinstance(value, str):
            value_lower = value.lower()
            for pattern in WAFRules.NOSQL_INJECTION_PATTERNS:
                if re.search(pattern, value_lower):
                    logger.warning(f"NoSQL injection attempt detected: {value[:50]}")
                    return True
        return False

    @staticmethod
    def check_xss(value: str) -> bool:
        """Check for XSS attempts."""
        if not isinstance(value, str):
            return False

        value_lower = value.lower()
        for pattern in WAFRules.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(f"XSS attempt detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_command_injection(value: str) -> bool:
        """Check for command injection attempts."""
        if not isinstance(value, str):
            return False

        for pattern in WAFRules.COMMAND_INJECTION_PATTERNS:
            if re.search(pattern, value):
                logger.warning(f"Command injection attempt detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_path_traversal(value: str) -> bool:
        """Check for path traversal attempts."""
        if not isinstance(value, str):
            return False

        # Decode URL-encoded values
        decoded = unquote(value)
        for pattern in WAFRules.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, decoded, re.IGNORECASE):
                logger.warning(f"Path traversal attempt detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_xxe(value: str) -> bool:
        """Check for XXE (XML External Entity) attempts."""
        if not isinstance(value, str):
            return False

        value_upper = value.upper()
        for pattern in WAFRules.XXE_PATTERNS:
            if re.search(pattern, value_upper):
                logger.warning(f"XXE attempt detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def check_deserialization(value: str) -> bool:
        """Check for insecure deserialization attempts."""
        if not isinstance(value, str):
            return False

        # Check for pickle, pickle2, and other dangerous serialization formats
        dangerous_patterns = [
            r"pickle",
            r"__reduce__",
            r"__getstate__",
            r"__setstate__",
        ]

        value_lower = value.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, value_lower):
                logger.warning(f"Deserialization attempt detected: {value[:50]}")
                return True
        return False

    @staticmethod
    def validate_all(data: Dict[str, Any]) -> List[str]:
        """Validate data against all WAF rules."""
        violations = []

        for key, value in data.items():
            if isinstance(value, str):
                if WAFRules.check_sql_injection(value):
                    violations.append(f"SQL injection detected in field: {key}")
                if WAFRules.check_nosql_injection(value):
                    violations.append(f"NoSQL injection detected in field: {key}")
                if WAFRules.check_xss(value):
                    violations.append(f"XSS detected in field: {key}")
                if WAFRules.check_command_injection(value):
                    violations.append(f"Command injection detected in field: {key}")
                if WAFRules.check_path_traversal(value):
                    violations.append(f"Path traversal detected in field: {key}")
                if WAFRules.check_xxe(value):
                    violations.append(f"XXE detected in field: {key}")
                if WAFRules.check_deserialization(value):
                    violations.append(f"Deserialization attack detected in field: {key}")
            elif isinstance(value, dict):
                nested_violations = WAFRules.validate_all(value)
                violations.extend(nested_violations)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        nested_violations = WAFRules.validate_all(item)
                        violations.extend(nested_violations)

        return violations
