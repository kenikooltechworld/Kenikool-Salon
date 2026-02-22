"""
Kimi-K2 Client for Natural Language Understanding
Communicates with Kimi-K2 Docker container for intent recognition and reasoning
"""

import logging
from typing import Optional, List, Dict, Any
from .base_client import BaseDockerClient

logger = logging.getLogger(__name__)


class KimiClient(BaseDockerClient):
    """Client for Kimi-K2 NLU Docker container"""
    
    async def generate(
        self,
        prompt: str,
        max_tokens: int = 500,
        temperature: float = 0.7,
        top_p: float = 0.9,
        stop: Optional[List[str]] = None
    ) -> str:
        """
        Generate text using Kimi-K2 model
        
        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            stop: Stop sequences
            
        Returns:
            Generated text
            
        Raises:
            httpx.HTTPError: If generation fails
        """
        try:
            payload = {
                'prompt': prompt,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'top_p': top_p,
                'stream': False
            }
            
            if stop:
                payload['stop'] = stop
            
            response = await self._post(
                '/v1/completions',
                json_data=payload
            )
            
            result = response.json()
            generated_text = result['choices'][0]['text'].strip()
            
            logger.info(f"Generated {len(generated_text)} chars from {len(prompt)} char prompt")
            
            return generated_text
            
        except Exception as e:
            logger.error(f"Kimi generation failed: {e}")
            raise
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 500,
        temperature: float = 0.7
    ) -> str:
        """
        Chat completion using Kimi-K2
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            
        Returns:
            Assistant's response
        """
        try:
            payload = {
                'messages': messages,
                'max_tokens': max_tokens,
                'temperature': temperature,
                'stream': False
            }
            
            response = await self._post(
                '/v1/chat/completions',
                json_data=payload
            )
            
            result = response.json()
            response_text = result['choices'][0]['message']['content'].strip()
            
            logger.info(f"Chat response: {len(response_text)} chars")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Kimi chat failed: {e}")
            raise
    
    async def extract_intent(
        self,
        text: str,
        language: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Extract intent and entities from text
        
        Args:
            text: User input text
            language: Language code
            context: Optional conversation context
            
        Returns:
            dict with intent, entities, and confidence
        """
        try:
            # Build prompt for intent extraction
            prompt = self._build_intent_prompt(text, language, context)
            
            # Generate response
            response = await self.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3  # Lower temperature for more deterministic output
            )
            
            # Parse response (expecting JSON format)
            import json
            result = json.loads(response)
            
            return {
                'intent': result.get('intent', 'unknown'),
                'entities': result.get('entities', {}),
                'confidence': result.get('confidence', 0.0),
                'requires_clarification': result.get('requires_clarification', False),
                'clarification_question': result.get('clarification_question')
            }
            
        except Exception as e:
            logger.error(f"Intent extraction failed: {e}")
            raise
    
    def _build_intent_prompt(
        self,
        text: str,
        language: str,
        context: Optional[str] = None
    ) -> str:
        """Build prompt for intent extraction"""
        
        prompt = f"""You are an AI assistant for a salon management system. Extract the intent and entities from the user's command.

Language: {language}
User Command: {text}
"""
        
        if context:
            prompt += f"\nConversation Context: {context}\n"
        
        prompt += """
Available Intents:
- book_appointment: Book a new appointment
- cancel_appointment: Cancel an existing appointment
- reschedule_appointment: Change appointment time
- show_appointments: Display appointments
- add_client: Add new client
- show_client_info: Show client details
- show_revenue: Display revenue information
- show_analytics: Show business analytics
- check_inventory: Check product inventory
- update_inventory: Update stock levels
- show_staff_schedule: Display staff schedules
- mark_attendance: Mark staff attendance
- help: Request help
- unknown: Cannot determine intent

Entities to extract (if present):
- client_name: Client's name
- service: Service type
- stylist: Stylist name
- date: Appointment date
- time: Appointment time
- product: Product name
- quantity: Quantity/amount
- time_period: Time period (today, week, month)

Respond ONLY with valid JSON in this format:
{
  "intent": "intent_name",
  "entities": {"entity_name": "value"},
  "confidence": 0.0-1.0,
  "requires_clarification": true/false,
  "clarification_question": "question if clarification needed"
}
"""
        
        return prompt
