"""
Date/Time Helper Functions
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import pytz


def get_current_utc() -> datetime:
    """Get current UTC datetime"""
    return datetime.utcnow()


def convert_to_timezone(dt: datetime, tz_name: str) -> datetime:
    """
    Convert datetime to specific timezone
    
    Args:
        dt: Datetime object (assumed UTC if naive)
        tz_name: Timezone name (e.g., 'Africa/Lagos', 'America/New_York')
        
    Returns:
        Datetime in specified timezone
    """
    if dt.tzinfo is None:
        dt = pytz.utc.localize(dt)
    
    target_tz = pytz.timezone(tz_name)
    return dt.astimezone(target_tz)


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime to string
    
    Args:
        dt: Datetime object
        format_str: Format string (default: YYYY-MM-DD HH:MM:SS)
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def format_date(dt: datetime, format_str: str = "%Y-%m-%d") -> str:
    """
    Format date to string
    
    Args:
        dt: Datetime object
        format_str: Format string (default: YYYY-MM-DD)
        
    Returns:
        Formatted date string
    """
    return dt.strftime(format_str)


def format_time(dt: datetime, format_str: str = "%H:%M:%S") -> str:
    """
    Format time to string
    
    Args:
        dt: Datetime object
        format_str: Format string (default: HH:MM:SS)
        
    Returns:
        Formatted time string
    """
    return dt.strftime(format_str)


def parse_datetime(date_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse datetime from string
    
    Args:
        date_str: Date string
        format_str: Format string (default: YYYY-MM-DD HH:MM:SS)
        
    Returns:
        Datetime object
    """
    return datetime.strptime(date_str, format_str)


def parse_date(date_str: str, format_str: str = "%Y-%m-%d") -> datetime:
    """
    Parse date from string
    
    Args:
        date_str: Date string
        format_str: Format string (default: YYYY-MM-DD)
        
    Returns:
        Datetime object
    """
    return datetime.strptime(date_str, format_str)


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to datetime"""
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """Add hours to datetime"""
    return dt + timedelta(hours=hours)


def add_minutes(dt: datetime, minutes: int) -> datetime:
    """Add minutes to datetime"""
    return dt + timedelta(minutes=minutes)


def get_start_of_day(dt: datetime) -> datetime:
    """Get start of day (00:00:00)"""
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def get_end_of_day(dt: datetime) -> datetime:
    """Get end of day (23:59:59)"""
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_start_of_month(dt: datetime) -> datetime:
    """Get start of month"""
    return dt.replace(day=1, hour=0, minute=0, second=0, microsecond=0)


def get_end_of_month(dt: datetime) -> datetime:
    """Get end of month"""
    next_month = dt.replace(day=28) + timedelta(days=4)
    last_day = next_month - timedelta(days=next_month.day)
    return last_day.replace(hour=23, minute=59, second=59, microsecond=999999)


def get_days_between(start: datetime, end: datetime) -> int:
    """Get number of days between two dates"""
    return (end - start).days


def get_hours_between(start: datetime, end: datetime) -> float:
    """Get number of hours between two datetimes"""
    return (end - start).total_seconds() / 3600


def is_past(dt: datetime) -> bool:
    """Check if datetime is in the past"""
    return dt < datetime.utcnow()


def is_future(dt: datetime) -> bool:
    """Check if datetime is in the future"""
    return dt > datetime.utcnow()


def is_today(dt: datetime) -> bool:
    """Check if datetime is today"""
    today = datetime.utcnow().date()
    return dt.date() == today


def get_relative_time(dt: datetime) -> str:
    """
    Get relative time string (e.g., '2 hours ago', 'in 3 days')
    
    Args:
        dt: Datetime object
        
    Returns:
        Relative time string
    """
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.total_seconds() < 0:
        # Future
        diff = dt - now
        if diff.days > 0:
            return f"in {diff.days} day{'s' if diff.days > 1 else ''}"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"in {hours} hour{'s' if hours > 1 else ''}"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"in {minutes} minute{'s' if minutes > 1 else ''}"
        else:
            return "in a few seconds"
    else:
        # Past
        if diff.days > 0:
            return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
        elif diff.seconds >= 3600:
            hours = diff.seconds // 3600
            return f"{hours} hour{'s' if hours > 1 else ''} ago"
        elif diff.seconds >= 60:
            minutes = diff.seconds // 60
            return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
        else:
            return "just now"
