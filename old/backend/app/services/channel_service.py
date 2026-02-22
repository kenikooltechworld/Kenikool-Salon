from typing import Dict, Any, Optional
import re


class ChannelService:
    """Service for handling multi-channel message validation and formatting"""

    # Channel-specific character limits
    CHANNEL_LIMITS = {
        "sms": 160,
        "whatsapp": 4096,
        "email": None  # No limit for email
    }

    # Channel-specific formatting rules
    CHANNEL_RULES = {
        "sms": {
            "max_length": 160,
            "supports_links": False,
            "supports_formatting": False
        },
        "whatsapp": {
            "max_length": 4096,
            "supports_links": True,
            "supports_formatting": True
        },
        "email": {
            "max_length": None,
            "supports_links": True,
            "supports_formatting": True
        }
    }

    # Channel-specific costs (per message)
    CHANNEL_COSTS = {
        "sms": 0.05,
        "whatsapp": 0.08,
        "email": 0.01
    }

    @staticmethod
    def validate_message(channel: str, content: str) -> Dict[str, Any]:
        """Validate message for a specific channel"""
        if channel not in ChannelService.CHANNEL_LIMITS:
            return {
                "valid": False,
                "error": f"Unknown channel: {channel}"
            }

        max_length = ChannelService.CHANNEL_LIMITS[channel]
        
        if max_length and len(content) > max_length:
            return {
                "valid": False,
                "error": f"Message exceeds {channel} character limit of {max_length}",
                "character_count": len(content),
                "limit": max_length
            }

        return {
            "valid": True,
            "character_count": len(content),
            "limit": max_length
        }

    @staticmethod
    def format_message(channel: str, content: str) -> str:
        """Format message according to channel rules"""
        if channel == "sms":
            # Remove extra whitespace and newlines for SMS
            content = " ".join(content.split())
            # Truncate if necessary
            if len(content) > 160:
                content = content[:157] + "..."
        
        elif channel == "whatsapp":
            # WhatsApp supports formatting, keep as is
            pass
        
        elif channel == "email":
            # Email can have any format
            pass

        return content

    @staticmethod
    def calculate_cost(channel: str, recipient_count: int) -> float:
        """Calculate cost for sending to recipients on a channel"""
        if channel not in ChannelService.CHANNEL_COSTS:
            return 0.0
        
        return ChannelService.CHANNEL_COSTS[channel] * recipient_count

    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email address"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number (basic validation)"""
        # Remove common formatting characters
        cleaned = re.sub(r'[\s\-\(\)\.+]', '', phone)
        # Check if it's all digits and reasonable length
        return cleaned.isdigit() and 10 <= len(cleaned) <= 15

    @staticmethod
    def get_channel_info(channel: str) -> Optional[Dict[str, Any]]:
        """Get information about a channel"""
        if channel not in ChannelService.CHANNEL_RULES:
            return None

        return {
            "channel": channel,
            "rules": ChannelService.CHANNEL_RULES[channel],
            "cost_per_message": ChannelService.CHANNEL_COSTS[channel],
            "character_limit": ChannelService.CHANNEL_LIMITS[channel]
        }

    @staticmethod
    def validate_channels(channels: list) -> Dict[str, Any]:
        """Validate a list of channels"""
        valid_channels = []
        invalid_channels = []

        for channel in channels:
            if channel in ChannelService.CHANNEL_LIMITS:
                valid_channels.append(channel)
            else:
                invalid_channels.append(channel)

        return {
            "valid": len(invalid_channels) == 0,
            "valid_channels": valid_channels,
            "invalid_channels": invalid_channels
        }

    @staticmethod
    def estimate_total_cost(channels: list, recipient_count: int) -> Dict[str, Any]:
        """Estimate total cost for a multi-channel campaign"""
        channel_costs = {}
        total_cost = 0.0

        for channel in channels:
            cost = ChannelService.calculate_cost(channel, recipient_count)
            channel_costs[channel] = cost
            total_cost += cost

        return {
            "total_cost": total_cost,
            "channel_costs": channel_costs,
            "recipient_count": recipient_count
        }

    @staticmethod
    def get_supported_channels() -> list:
        """Get list of supported channels"""
        return list(ChannelService.CHANNEL_LIMITS.keys())
