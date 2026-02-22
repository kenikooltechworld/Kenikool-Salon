"""
Validation Helper Functions
"""
import re
from typing import Optional
from urllib.parse import urlparse


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str, country_code: str = "NG") -> bool:
    """
    Validate phone number format
    
    Args:
        phone: Phone number to validate
        country_code: Country code (default: NG for Nigeria)
        
    Returns:
        True if valid, False otherwise
    """
    if not phone:
        return False
    
    # Remove spaces, dashes, and parentheses
    phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    if country_code == "NG":
        # Nigerian phone numbers: +234XXXXXXXXXX or 0XXXXXXXXXX
        pattern = r'^(\+234|0)[7-9][0-1]\d{8}$'
        return bool(re.match(pattern, phone))
    else:
        # Generic international format
        pattern = r'^\+?[1-9]\d{1,14}$'
        return bool(re.match(pattern, phone))


def validate_url(url: str, require_https: bool = False) -> bool:
    """
    Validate URL format
    
    Args:
        url: URL to validate
        require_https: Require HTTPS protocol
        
    Returns:
        True if valid, False otherwise
    """
    if not url:
        return False
    
    try:
        result = urlparse(url)
        
        # Check if scheme and netloc are present
        if not all([result.scheme, result.netloc]):
            return False
        
        # Check if HTTPS is required
        if require_https and result.scheme != 'https':
            return False
        
        # Check if scheme is http or https
        if result.scheme not in ['http', 'https']:
            return False
        
        return True
    except:
        return False


def validate_password_strength(password: str) -> dict:
    """
    Validate password strength
    
    Args:
        password: Password to validate
        
    Returns:
        Dict with validation results
    """
    if not password:
        return {
            "valid": False,
            "errors": ["Password is required"]
        }
    
    errors = []
    
    # Check length
    if len(password) < 8:
        errors.append("Password must be at least 8 characters long")
    
    # Check for uppercase
    if not re.search(r'[A-Z]', password):
        errors.append("Password must contain at least one uppercase letter")
    
    # Check for lowercase
    if not re.search(r'[a-z]', password):
        errors.append("Password must contain at least one lowercase letter")
    
    # Check for digit
    if not re.search(r'\d', password):
        errors.append("Password must contain at least one digit")
    
    # Check for special character
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        errors.append("Password must contain at least one special character")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors
    }


def validate_username(username: str) -> bool:
    """
    Validate username format
    
    Args:
        username: Username to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not username:
        return False
    
    # Username: 3-20 characters, alphanumeric and underscore only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return bool(re.match(pattern, username))


def validate_slug(slug: str) -> bool:
    """
    Validate URL slug format
    
    Args:
        slug: Slug to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not slug:
        return False
    
    # Slug: lowercase letters, numbers, and hyphens only
    pattern = r'^[a-z0-9]+(?:-[a-z0-9]+)*$'
    return bool(re.match(pattern, slug))


def validate_hex_color(color: str) -> bool:
    """
    Validate hex color code format
    
    Args:
        color: Hex color code to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not color:
        return False
    
    # Hex color: #RGB or #RRGGBB
    pattern = r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$'
    return bool(re.match(pattern, color))


def validate_postal_code(postal_code: str, country_code: str = "NG") -> bool:
    """
    Validate postal code format
    
    Args:
        postal_code: Postal code to validate
        country_code: Country code (default: NG for Nigeria)
        
    Returns:
        True if valid, False otherwise
    """
    if not postal_code:
        return False
    
    if country_code == "NG":
        # Nigerian postal codes: 6 digits
        pattern = r'^\d{6}$'
        return bool(re.match(pattern, postal_code))
    elif country_code == "US":
        # US ZIP codes: 5 digits or 5+4 digits
        pattern = r'^\d{5}(-\d{4})?$'
        return bool(re.match(pattern, postal_code))
    elif country_code == "UK":
        # UK postcodes
        pattern = r'^[A-Z]{1,2}\d{1,2}[A-Z]?\s?\d[A-Z]{2}$'
        return bool(re.match(pattern, postal_code.upper()))
    else:
        # Generic: alphanumeric with optional spaces and hyphens
        pattern = r'^[A-Z0-9\s\-]{3,10}$'
        return bool(re.match(pattern, postal_code.upper()))


def sanitize_string(text: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string by removing potentially harmful characters
    
    Args:
        text: Text to sanitize
        max_length: Maximum length (optional)
        
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove script tags and content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Trim whitespace
    text = text.strip()
    
    # Truncate if max_length specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_credit_card(card_number: str) -> bool:
    """
    Validate credit card number using Luhn algorithm
    
    Args:
        card_number: Credit card number to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not card_number:
        return False
    
    # Remove spaces and dashes
    card_number = re.sub(r'[\s\-]', '', card_number)
    
    # Check if all digits
    if not card_number.isdigit():
        return False
    
    # Check length (13-19 digits)
    if len(card_number) < 13 or len(card_number) > 19:
        return False
    
    # Luhn algorithm
    def luhn_checksum(card_num):
        def digits_of(n):
            return [int(d) for d in str(n)]
        
        digits = digits_of(card_num)
        odd_digits = digits[-1::-2]
        even_digits = digits[-2::-2]
        checksum = sum(odd_digits)
        for d in even_digits:
            checksum += sum(digits_of(d * 2))
        return checksum % 10
    
    return luhn_checksum(card_number) == 0
