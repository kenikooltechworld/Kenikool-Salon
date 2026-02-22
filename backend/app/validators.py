"""Input validators for security and data integrity."""

import re
from typing import Any
from pydantic import field_validator, BaseModel
from email_validator import validate_email, EmailNotValidError


class EmailValidator(BaseModel):
    """Email validation."""

    email: str

    @field_validator("email")
    @classmethod
    def validate_email_format(cls, v: str) -> str:
        """Validate email format."""
        try:
            valid = validate_email(v)
            return valid.email
        except EmailNotValidError as e:
            raise ValueError(f"Invalid email: {str(e)}")


class PasswordValidator(BaseModel):
    """Password validation."""

    password: str

    @field_validator("password")
    @classmethod
    def validate_password_strength(cls, v: str) -> str:
        """Validate password meets security requirements."""
        if len(v) < 12:
            raise ValueError("Password must be at least 12 characters long")

        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*()_+\-=\[\]{};:'\",.<>?/\\|`~]", v):
            raise ValueError("Password must contain at least one special character")

        return v


class PhoneValidator(BaseModel):
    """Phone number validation."""

    phone: str

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        """Validate phone number format."""
        # Remove common formatting characters
        cleaned = re.sub(r"[\s\-\(\)\.]+", "", v)

        # Check if it's a valid phone number (7-15 digits)
        if not re.match(r"^\+?1?\d{7,15}$", cleaned):
            raise ValueError("Invalid phone number format")

        return cleaned


class NameValidator(BaseModel):
    """Name validation."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate name format."""
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")

        if len(v) > 100:
            raise ValueError("Name must not exceed 100 characters")

        # Allow letters, spaces, hyphens, and apostrophes
        if not re.match(r"^[a-zA-Z\s\-']+$", v):
            raise ValueError("Name contains invalid characters")

        return v.strip()


def sanitize_string(value: str, max_length: int = 255) -> str:
    """Sanitize string input."""
    if not isinstance(value, str):
        raise ValueError("Input must be a string")

    # Remove null bytes
    value = value.replace("\x00", "")

    # Limit length
    if len(value) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length}")

    return value.strip()


def validate_file_upload(
    filename: str, allowed_extensions: set, max_size: int = 10 * 1024 * 1024
) -> bool:
    """Validate file upload."""
    # Check filename length
    if len(filename) > 255:
        raise ValueError("Filename too long")

    # Check file extension
    if "." not in filename:
        raise ValueError("File must have an extension")

    ext = filename.rsplit(".", 1)[1].lower()
    if ext not in allowed_extensions:
        raise ValueError(f"File type not allowed. Allowed: {allowed_extensions}")

    # Check for path traversal attempts
    if ".." in filename or "/" in filename or "\\" in filename:
        raise ValueError("Invalid filename")

    return True


def prevent_nosql_injection(value: Any) -> Any:
    """Prevent NoSQL injection attacks."""
    if isinstance(value, dict):
        # Check for MongoDB operators
        for key in value.keys():
            if key.startswith("$"):
                raise ValueError(f"Invalid field name: {key}")
        return {k: prevent_nosql_injection(v) for k, v in value.items()}

    if isinstance(value, list):
        return [prevent_nosql_injection(item) for item in value]

    if isinstance(value, str):
        # Check for common NoSQL injection patterns
        dangerous_patterns = [
            r"\$where",
            r"\$regex",
            r"\$ne",
            r"\$gt",
            r"\$lt",
            r"\$or",
            r"\$and",
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potentially malicious input detected")

    return value


def prevent_xss(value: str) -> str:
    """Prevent XSS attacks by escaping HTML."""
    if not isinstance(value, str):
        return value

    # HTML entity encoding
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;",
    }

    for char, entity in replacements.items():
        value = value.replace(char, entity)

    return value
