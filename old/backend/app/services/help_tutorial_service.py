import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class HelpTutorialService:
    """Provides help and tutorial system for voice assistant"""

    def __init__(self):
        """Initialize help/tutorial service"""
        self.commands_by_language = self._initialize_commands()
        self.tutorials = self._initialize_tutorials()

    def _initialize_commands(self) -> Dict[str, List[Dict]]:
        """Initialize command help for all languages"""
        return {
            "en": [
                {
                    "command": "book appointment",
                    "description": "Schedule a new appointment",
                    "example": "Book an appointment for Sarah for haircut tomorrow at 2 PM",
                    "category": "booking"
                },
                {
                    "command": "cancel appointment",
                    "description": "Cancel an existing appointment",
                    "example": "Cancel John's appointment",
                    "category": "booking"
                },
                {
                    "command": "show appointments",
                    "description": "View today's appointments",
                    "example": "Show me today's appointments",
                    "category": "booking"
                },
                {
                    "command": "add client",
                    "description": "Add a new client",
                    "example": "Add new client named Maria",
                    "category": "client"
                },
                {
                    "command": "show client info",
                    "description": "View client details",
                    "example": "Show me Sarah's information",
                    "category": "client"
                },
                {
                    "command": "show revenue",
                    "description": "View revenue information",
                    "example": "How much revenue today",
                    "category": "financial"
                },
                {
                    "command": "show analytics",
                    "description": "View salon analytics",
                    "example": "Show me analytics",
                    "category": "financial"
                },
                {
                    "command": "check inventory",
                    "description": "Check stock levels",
                    "example": "Check inventory",
                    "category": "inventory"
                },
                {
                    "command": "show staff schedule",
                    "description": "View staff schedule",
                    "example": "Show staff schedule",
                    "category": "staff"
                },
                {
                    "command": "mark attendance",
                    "description": "Mark staff attendance",
                    "example": "Mark Sarah as present",
                    "category": "staff"
                }
            ],
            "yo": [
                {
                    "command": "ṣe àpointment",
                    "description": "Ṣe àpointment tuntun",
                    "example": "Ṣe àpointment fun Sarah",
                    "category": "booking"
                }
            ],
            "ig": [
                {
                    "command": "mee appointment",
                    "description": "Mee appointment ọhụrụ",
                    "example": "Mee appointment maka Sarah",
                    "category": "booking"
                }
            ],
            "ha": [
                {
                    "command": "yi appointment",
                    "description": "Yi appointment sabon",
                    "example": "Yi appointment don Sarah",
                    "category": "booking"
                }
            ],
            "pcm": [
                {
                    "command": "book appointment",
                    "description": "Book new appointment",
                    "example": "Book appointment for Sarah",
                    "category": "booking"
                }
            ]
        }

    def _initialize_tutorials(self) -> Dict[str, Dict]:
        """Initialize tutorials for new users"""
        return {
            "getting_started": {
                "title": "Getting Started with Voice Assistant",
                "steps": [
                    "Click the microphone button to start recording",
                    "Speak your command clearly",
                    "Wait for the assistant to process",
                    "Listen to the response or read the transcript",
                    "Click stop to end recording"
                ],
                "duration_minutes": 5
            },
            "booking_tutorial": {
                "title": "How to Book Appointments",
                "steps": [
                    "Say 'book appointment'",
                    "Provide client name",
                    "Specify service type",
                    "Choose date and time",
                    "Confirm the booking"
                ],
                "duration_minutes": 3
            },
            "shortcuts_tutorial": {
                "title": "Using Voice Shortcuts",
                "steps": [
                    "Say 'quick book' for fast bookings",
                    "Say 'daily summary' for reports",
                    "Say 'emergency cancel' to cancel quickly",
                    "Say 'check in' for client arrival",
                    "Say 'end of day' for closing reports"
                ],
                "duration_minutes": 4
            },
            "multilingual_tutorial": {
                "title": "Using Multiple Languages",
                "steps": [
                    "Select language from dropdown",
                    "Speak in your preferred language",
                    "Assistant responds in same language",
                    "Switch languages anytime",
                    "Supported: English, Yoruba, Igbo, Hausa, Pidgin"
                ],
                "duration_minutes": 3
            }
        }

    def get_help_for_command(self, command: str, language: str = "en") -> Optional[Dict]:
        """Get help for specific command"""
        commands = self.commands_by_language.get(language, [])
        for cmd in commands:
            if cmd["command"].lower() == command.lower():
                return cmd
        return None

    def get_all_commands(self, language: str = "en") -> List[Dict]:
        """Get all commands for language"""
        return self.commands_by_language.get(language, [])

    def get_commands_by_category(self, category: str, language: str = "en") -> List[Dict]:
        """Get commands by category"""
        commands = self.commands_by_language.get(language, [])
        return [cmd for cmd in commands if cmd.get("category") == category]

    def get_tutorial(self, tutorial_name: str) -> Optional[Dict]:
        """Get tutorial content"""
        return self.tutorials.get(tutorial_name)

    def get_all_tutorials(self) -> List[Dict]:
        """Get all available tutorials"""
        return [
            {
                "name": name,
                "title": tutorial["title"],
                "duration_minutes": tutorial["duration_minutes"]
            }
            for name, tutorial in self.tutorials.items()
        ]

    def get_contextual_help(self, context: str, language: str = "en") -> str:
        """Get contextual help based on current context"""
        help_messages = {
            "booking": "Try saying 'book appointment' to schedule a new appointment",
            "client": "Try saying 'add client' to add a new client",
            "financial": "Try saying 'show revenue' to see financial information",
            "inventory": "Try saying 'check inventory' to view stock levels",
            "staff": "Try saying 'show staff schedule' to view staff information"
        }
        return help_messages.get(context, "Say 'help' to see available commands")

    def get_command_suggestions(self, partial_command: str, language: str = "en") -> List[str]:
        """Get command suggestions based on partial input"""
        commands = self.commands_by_language.get(language, [])
        partial_lower = partial_command.lower()
        suggestions = [
            cmd["command"] for cmd in commands
            if partial_lower in cmd["command"].lower()
        ]
        return suggestions[:5]  # Return top 5 suggestions

    def record_help_access(self, user_id: str, help_type: str, topic: str):
        """Record help access for analytics"""
        logger.info(f"Help accessed - User: {user_id}, Type: {help_type}, Topic: {topic}")
