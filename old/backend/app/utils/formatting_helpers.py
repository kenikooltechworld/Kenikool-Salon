"""
Formatting Helper Functions
"""
import re
from typing import Optional
from decimal import Decimal


def format_currency(
    amount: float,
    currency: str = "NGN",
    include_symbol: bool = True,
    decimal_places: int = 2
) -> str:
    """
    Format amount as currency
    
    Args:
        amount: Amount to format
        currency: Currency code (default: NGN)
        include_symbol: Include currency symbol
        decimal_places: Number of decimal places
        
    Returns:
        Formatted currency string
    """
    # Currency symbols
    symbols = {
        "NGN": "₦",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
        "JPY": "¥"
    }
    
    # Format with commas and decimal places
    formatted = f"{amount:,.{decimal_places}f}"
    
    if include_symbol:
        symbol = symbols.get(currency, currency)
        return f"{symbol}{formatted}"
    
    return formatted


def format_number(
    number: float,
    decimal_places: int = 0,
    use_commas: bool = True
) -> str:
    """
    Format number with commas and decimal places
    
    Args:
        number: Number to format
        decimal_places: Number of decimal places
        use_commas: Use comma separators
        
    Returns:
        Formatted number string
    """
    if use_commas:
        return f"{number:,.{decimal_places}f}"
    else:
        return f"{number:.{decimal_places}f}"


def format_percentage(
    value: float,
    decimal_places: int = 1,
    include_symbol: bool = True
) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value to format (0-100)
        decimal_places: Number of decimal places
        include_symbol: Include % symbol
        
    Returns:
        Formatted percentage string
    """
    formatted = f"{value:.{decimal_places}f}"
    
    if include_symbol:
        return f"{formatted}%"
    
    return formatted


def format_phone(phone: str, country_code: str = "NG") -> str:
    """
    Format phone number for display
    
    Args:
        phone: Phone number to format
        country_code: Country code (default: NG)
        
    Returns:
        Formatted phone number
    """
    # Remove all non-digit characters
    digits = re.sub(r'\D', '', phone)
    
    if country_code == "NG":
        # Nigerian format: +234 XXX XXX XXXX
        if digits.startswith("234"):
            return f"+234 {digits[3:6]} {digits[6:9]} {digits[9:]}"
        elif digits.startswith("0"):
            return f"+234 {digits[1:4]} {digits[4:7]} {digits[7:]}"
        else:
            return phone
    elif country_code == "US":
        # US format: (XXX) XXX-XXXX
        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:]}"
        elif len(digits) == 11 and digits[0] == "1":
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:]}"
        else:
            return phone
    else:
        # Generic international format
        return f"+{digits}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted file size string
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} PB"


def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "..."
) -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    """
    Convert text to URL-friendly slug
    
    Args:
        text: Text to slugify
        
    Returns:
        Slugified text
    """
    # Convert to lowercase
    text = text.lower()
    
    # Replace spaces and underscores with hyphens
    text = re.sub(r'[\s_]+', '-', text)
    
    # Remove non-alphanumeric characters except hyphens
    text = re.sub(r'[^a-z0-9\-]', '', text)
    
    # Remove multiple consecutive hyphens
    text = re.sub(r'-+', '-', text)
    
    # Remove leading and trailing hyphens
    text = text.strip('-')
    
    return text


def capitalize_words(text: str) -> str:
    """
    Capitalize first letter of each word
    
    Args:
        text: Text to capitalize
        
    Returns:
        Capitalized text
    """
    return ' '.join(word.capitalize() for word in text.split())


def format_name(first_name: str, last_name: str, format_type: str = "full") -> str:
    """
    Format person's name
    
    Args:
        first_name: First name
        last_name: Last name
        format_type: Format type (full, last_first, initials)
        
    Returns:
        Formatted name
    """
    if format_type == "full":
        return f"{first_name} {last_name}"
    elif format_type == "last_first":
        return f"{last_name}, {first_name}"
    elif format_type == "initials":
        return f"{first_name[0]}.{last_name[0]}."
    else:
        return f"{first_name} {last_name}"


def format_address(
    street: str,
    city: str,
    state: str,
    postal_code: Optional[str] = None,
    country: Optional[str] = None
) -> str:
    """
    Format address for display
    
    Args:
        street: Street address
        city: City
        state: State/Province
        postal_code: Postal code (optional)
        country: Country (optional)
        
    Returns:
        Formatted address
    """
    parts = [street, city, state]
    
    if postal_code:
        parts.append(postal_code)
    
    if country:
        parts.append(country)
    
    return ", ".join(parts)


def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        if remaining_seconds > 0:
            return f"{minutes}m {remaining_seconds}s"
        return f"{minutes}m"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        if remaining_minutes > 0:
            return f"{hours}h {remaining_minutes}m"
        return f"{hours}h"


def format_list(items: list, conjunction: str = "and") -> str:
    """
    Format list of items as comma-separated string
    
    Args:
        items: List of items
        conjunction: Conjunction word (and, or)
        
    Returns:
        Formatted list string
    """
    if not items:
        return ""
    
    if len(items) == 1:
        return str(items[0])
    
    if len(items) == 2:
        return f"{items[0]} {conjunction} {items[1]}"
    
    return f"{', '.join(str(item) for item in items[:-1])}, {conjunction} {items[-1]}"


def mask_sensitive_data(data: str, visible_chars: int = 4, mask_char: str = "*") -> str:
    """
    Mask sensitive data (e.g., credit card, phone)
    
    Args:
        data: Data to mask
        visible_chars: Number of visible characters at end
        mask_char: Character to use for masking
        
    Returns:
        Masked data
    """
    if not data or len(data) <= visible_chars:
        return data
    
    masked_length = len(data) - visible_chars
    return mask_char * masked_length + data[-visible_chars:]
