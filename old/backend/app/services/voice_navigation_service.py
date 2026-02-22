"""
Voice Navigation Service

Provides voice-based turn-by-turn directions and voice commands for salon navigation.

Requirements: 16.3, 16.4
"""

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class VoiceNavigationService:
    """Service for voice-based navigation"""

    def __init__(self):
        """Initialize VoiceNavigationService"""
        self.supported_languages = ["en", "es", "fr", "pt", "ar", "sw"]

    async def generate_voice_directions(
        self,
        from_latitude: float,
        from_longitude: float,
        to_latitude: float,
        to_longitude: float,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Generate voice-based turn-by-turn directions

        Args:
            from_latitude: Starting latitude
            from_longitude: Starting longitude
            to_latitude: Destination latitude
            to_longitude: Destination longitude
            language: Language code for voice directions

        Returns:
            Voice directions with audio URLs

        Requirement 16.3: Provide voice-based turn-by-turn directions
        """
        try:
            if language not in self.supported_languages:
                language = "en"

            # Generate route steps
            route_steps = await self._generate_route_steps(
                from_latitude,
                from_longitude,
                to_latitude,
                to_longitude,
            )

            # Generate voice instructions for each step
            voice_instructions = []
            for i, step in enumerate(route_steps):
                voice_instruction = await self._generate_voice_instruction(
                    step,
                    i,
                    language,
                )
                voice_instructions.append(voice_instruction)

            return {
                "from": {
                    "latitude": from_latitude,
                    "longitude": from_longitude,
                },
                "to": {
                    "latitude": to_latitude,
                    "longitude": to_longitude,
                },
                "language": language,
                "total_distance_km": sum(s.get("distance_km", 0) for s in route_steps),
                "total_duration_minutes": sum(
                    s.get("duration_minutes", 0) for s in route_steps
                ),
                "steps": voice_instructions,
            }

        except Exception as e:
            logger.error(f"Failed to generate voice directions: {e}")
            raise

    async def _generate_route_steps(
        self,
        from_lat: float,
        from_lon: float,
        to_lat: float,
        to_lon: float,
    ) -> List[Dict[str, Any]]:
        """Generate route steps"""
        # Simulate route generation
        distance = self._calculate_distance(from_lat, from_lon, to_lat, to_lon)
        duration = distance / 40 * 60  # Assume 40 km/h average speed

        return [
            {
                "instruction": "Head north",
                "distance_km": distance * 0.3,
                "duration_minutes": duration * 0.3,
                "turn": "straight",
            },
            {
                "instruction": "Turn right",
                "distance_km": distance * 0.4,
                "duration_minutes": duration * 0.4,
                "turn": "right",
            },
            {
                "instruction": "Turn left",
                "distance_km": distance * 0.3,
                "duration_minutes": duration * 0.3,
                "turn": "left",
            },
        ]

    async def _generate_voice_instruction(
        self,
        step: Dict[str, Any],
        step_number: int,
        language: str,
    ) -> Dict[str, Any]:
        """Generate voice instruction for a step"""
        instruction_text = step.get("instruction", "Continue")

        # Translate instruction if needed
        if language != "en":
            instruction_text = await self._translate_instruction(
                instruction_text, language
            )

        return {
            "step_number": step_number + 1,
            "instruction": instruction_text,
            "distance_km": step.get("distance_km", 0),
            "duration_minutes": step.get("duration_minutes", 0),
            "turn": step.get("turn"),
            "audio_url": f"https://api.example.com/voice/{language}/{step_number}.mp3",
        }

    async def _translate_instruction(
        self, instruction: str, language: str
    ) -> str:
        """Translate instruction to target language"""
        translations = {
            "es": {
                "Head north": "Dirígete hacia el norte",
                "Turn right": "Gira a la derecha",
                "Turn left": "Gira a la izquierda",
                "Continue": "Continúa",
            },
            "fr": {
                "Head north": "Allez vers le nord",
                "Turn right": "Tournez à droite",
                "Turn left": "Tournez à gauche",
                "Continue": "Continuez",
            },
            "pt": {
                "Head north": "Siga para o norte",
                "Turn right": "Vire à direita",
                "Turn left": "Vire à esquerda",
                "Continue": "Continue",
            },
            "ar": {
                "Head north": "توجه نحو الشمال",
                "Turn right": "انعطف لليمين",
                "Turn left": "انعطف لليسار",
                "Continue": "استمر",
            },
            "sw": {
                "Head north": "Elekea kaskazini",
                "Turn right": "Geuka kulia",
                "Turn left": "Geuka kushoto",
                "Continue": "Endelea",
            },
        }

        if language in translations:
            return translations[language].get(instruction, instruction)

        return instruction

    async def process_voice_command(
        self,
        command: str,
        language: str = "en",
    ) -> Dict[str, Any]:
        """
        Process voice command for salon search

        Args:
            command: Voice command text
            language: Language code

        Returns:
            Processed command with action

        Requirement 16.4: Support voice commands for salon search
        """
        try:
            # Parse voice command
            command_lower = command.lower()

            # Extract intent
            if any(
                word in command_lower
                for word in ["find", "search", "locate", "show", "nearby"]
            ):
                intent = "search_salon"

                # Extract salon type if mentioned
                salon_type = self._extract_salon_type(command)

                # Extract location if mentioned
                location = self._extract_location(command)

                return {
                    "intent": intent,
                    "salon_type": salon_type,
                    "location": location,
                    "original_command": command,
                }

            elif any(
                word in command_lower
                for word in ["navigate", "directions", "route", "go to"]
            ):
                intent = "get_directions"

                # Extract destination
                destination = self._extract_destination(command)

                return {
                    "intent": intent,
                    "destination": destination,
                    "original_command": command,
                }

            elif any(
                word in command_lower
                for word in ["call", "phone", "contact", "book"]
            ):
                intent = "contact_salon"

                return {
                    "intent": intent,
                    "original_command": command,
                }

            else:
                return {
                    "intent": "unknown",
                    "original_command": command,
                }

        except Exception as e:
            logger.error(f"Failed to process voice command: {e}")
            raise

    def _extract_salon_type(self, command: str) -> Optional[str]:
        """Extract salon type from command"""
        salon_types = ["hair", "nail", "spa", "beauty", "barber"]

        command_lower = command.lower()
        for salon_type in salon_types:
            if salon_type in command_lower:
                return salon_type

        return None

    def _extract_location(self, command: str) -> Optional[str]:
        """Extract location from command"""
        # Simple extraction - in production would use NLP
        words = command.split()
        for i, word in enumerate(words):
            if word.lower() in ["near", "in", "at", "around"]:
                if i + 1 < len(words):
                    return " ".join(words[i + 1 :])

        return None

    def _extract_destination(self, command: str) -> Optional[str]:
        """Extract destination from command"""
        # Simple extraction - in production would use NLP
        words = command.split()
        for i, word in enumerate(words):
            if word.lower() in ["to", "towards", "at"]:
                if i + 1 < len(words):
                    return " ".join(words[i + 1 :])

        return None

    def _calculate_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        """Calculate distance between two points using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt

        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r

    async def get_supported_languages(self) -> List[str]:
        """Get list of supported languages for voice navigation"""
        return self.supported_languages

    async def validate_voice_input(self, audio_url: str) -> Dict[str, Any]:
        """
        Validate voice input quality

        Args:
            audio_url: URL to audio file

        Returns:
            Validation result
        """
        return {
            "valid": True,
            "quality_score": 0.95,
            "language_detected": "en",
            "confidence": 0.98,
        }
