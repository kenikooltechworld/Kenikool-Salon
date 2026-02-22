"""
Natural Language Understanding Handler
Extracts intent and entities from user commands in multiple languages
"""

import logging
import json
from typing import Dict, Any, Optional
from ..clients.kimi_client import KimiClient
from ..models.voice_models import Intent, NLUResult, ConversationContext

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user intent from natural language"""
    
    def __init__(self, kimi_client: KimiClient):
        """
        Initialize intent classifier
        
        Args:
            kimi_client: Kimi-K2 client for NLU
        """
        self.kimi_client = kimi_client
        logger.info("Intent Classifier initialized")
    
    async def classify(
        self,
        text: str,
        language: str,
        context: Optional[ConversationContext] = None
    ) -> Dict[str, Any]:
        """
        Classify user intent from text
        
        Args:
            text: User input text
            language: Language code
            context: Conversation context
            
        Returns:
            dict with intent, confidence, and metadata
        """
        try:
            # Build classification prompt
            prompt = self._build_classification_prompt(text, language, context)
            
            # Get classification from Kimi
            response = await self.kimi_client.generate(
                prompt=prompt,
                max_tokens=200,
                temperature=0.3  # Low temperature for deterministic classification
            )
            
            # Parse JSON response
            result = json.loads(response)
            
            intent_str = result.get('intent', 'unknown')
            confidence = result.get('confidence', 0.0)
            
            # Convert string to Intent enum
            try:
                intent = Intent(intent_str)
            except ValueError:
                logger.warning(f"Unknown intent: {intent_str}")
                intent = Intent.UNKNOWN
            
            logger.info(f"Classified intent: {intent.value} (confidence: {confidence:.2f})")
            
            return {
                'intent': intent,
                'confidence': confidence,
                'requires_clarification': result.get('requires_clarification', False),
                'clarification_question': result.get('clarification_question')
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse intent classification response: {e}")
            return {
                'intent': Intent.UNKNOWN,
                'confidence': 0.0,
                'requires_clarification': True,
                'clarification_question': "I didn't understand that. Could you rephrase?"
            }
        except Exception as e:
            logger.error(f"Intent classification failed: {e}")
            return {
                'intent': Intent.UNKNOWN,
                'confidence': 0.0,
                'requires_clarification': False,
                'clarification_question': None
            }
    
    def _build_classification_prompt(
        self,
        text: str,
        language: str,
        context: Optional[ConversationContext] = None
    ) -> str:
        """Build prompt for intent classification"""
        
        context_str = ""
        if context and context.history:
            last_turn = context.history[-1]
            context_str = f"\nPrevious Intent: {last_turn.intent.value}\nPrevious Entities: {last_turn.entities}"
        
        prompt = f"""You are an AI assistant for a salon management system. Classify the user's intent.

Language: {language}
User Command: {text}{context_str}

Available Intents:
- book_appointment: Book a new appointment
- cancel_appointment: Cancel an existing appointment
- reschedule_appointment: Change appointment time
- show_appointments: Display appointments
- add_client: Add new client
- show_client_info: Show client details
- find_inactive_clients: Find clients who haven't visited recently
- show_revenue: Display revenue information
- show_analytics: Show business analytics
- check_inventory: Check product inventory
- update_inventory: Update stock levels
- show_staff_schedule: Display staff schedules
- check_availability: Check staff availability
- mark_attendance: Mark staff attendance
- show_performance: Show staff performance
- help: Request help
- unknown: Cannot determine intent

Respond ONLY with valid JSON:
{{
  "intent": "intent_name",
  "confidence": 0.0-1.0,
  "requires_clarification": true/false,
  "clarification_question": "question if needed or null"
}}
"""
        
        return prompt


class EntityExtractor:
    """Extracts entities from user commands"""
    
    def __init__(self, kimi_client: KimiClient):
        """
        Initialize entity extractor
        
        Args:
            kimi_client: Kimi-K2 client for NLU
        """
        self.kimi_client = kimi_client
        logger.info("Entity Extractor initialized")
    
    async def extract(
        self,
        text: str,
        intent: Intent,
        language: str,
        context: Optional[ConversationContext] = None
    ) -> Dict[str, Any]:
        """
        Extract entities from text based on intent
        
        Args:
            text: User input text
            intent: Classified intent
            language: Language code
            context: Conversation context
            
        Returns:
            dict of extracted entities
        """
        try:
            # Build extraction prompt
            prompt = self._build_extraction_prompt(text, intent, language, context)
            
            # Get entities from Kimi
            response = await self.kimi_client.generate(
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse JSON response
            entities = json.loads(response)
            
            # Resolve references from context
            if context:
                entities = self._resolve_references(entities, context)
            
            logger.info(f"Extracted entities: {entities}")
            
            return entities
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse entity extraction response: {e}")
            return {}
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return {}
    
    def _build_extraction_prompt(
        self,
        text: str,
        intent: Intent,
        language: str,
        context: Optional[ConversationContext] = None
    ) -> str:
        """Build prompt for entity extraction"""
        
        # Get required entities for this intent
        required_entities = self._get_required_entities(intent)
        
        context_str = ""
        if context and context.last_entities:
            context_str = f"\nPrevious Entities: {context.last_entities}"
        
        prompt = f"""Extract entities from the user's command for a salon management system.

Language: {language}
Intent: {intent.value}
User Command: {text}{context_str}

Required Entities for {intent.value}:
{required_entities}

Common Entity Types:
- client_name: Client's full name
- client_phone: Client's phone number
- service: Service type (haircut, manicure, etc.)
- stylist: Stylist/staff name
- date: Appointment date (extract as YYYY-MM-DD if possible)
- time: Appointment time (extract as HH:MM if possible)
- product: Product name
- quantity: Quantity or amount
- time_period: Time period (today, week, month, etc.)

Special Instructions:
- If the user says "her", "him", "them", use the previous client_name from context
- If the user says "tomorrow", "next week", calculate the actual date
- If entities are missing, set them to null

Respond ONLY with valid JSON object of entities:
{{
  "entity_name": "value or null"
}}
"""
        
        return prompt
    
    def _get_required_entities(self, intent: Intent) -> str:
        """Get required entities for an intent"""
        
        entity_map = {
            Intent.BOOK_APPOINTMENT: "client_name, service, stylist (optional), date, time",
            Intent.CANCEL_APPOINTMENT: "client_name OR appointment_id",
            Intent.RESCHEDULE_APPOINTMENT: "client_name OR appointment_id, new_date (optional), new_time (optional)",
            Intent.SHOW_APPOINTMENTS: "date (optional), stylist (optional)",
            Intent.ADD_CLIENT: "client_name, client_phone",
            Intent.SHOW_CLIENT_INFO: "client_name",
            Intent.FIND_INACTIVE_CLIENTS: "time_period (optional)",
            Intent.SHOW_REVENUE: "time_period (optional)",
            Intent.SHOW_ANALYTICS: "metric_type (optional)",
            Intent.CHECK_INVENTORY: "product (optional)",
            Intent.UPDATE_INVENTORY: "product, quantity, action (add/remove/set)",
            Intent.SHOW_STAFF_SCHEDULE: "stylist (optional), date (optional)",
            Intent.CHECK_AVAILABILITY: "time, date (optional)",
            Intent.MARK_ATTENDANCE: "stylist, status (present/absent)",
            Intent.SHOW_PERFORMANCE: "stylist, time_period (optional)",
            Intent.HELP: "None",
            Intent.UNKNOWN: "None"
        }
        
        return entity_map.get(intent, "None")
    
    def _resolve_references(
        self,
        entities: Dict[str, Any],
        context: ConversationContext
    ) -> Dict[str, Any]:
        """
        Resolve pronoun references using conversation context
        
        Args:
            entities: Extracted entities
            context: Conversation context
            
        Returns:
            Entities with resolved references
        """
        if not context.last_entities:
            return entities
        
        # Resolve client_name references
        if entities.get('client_name') in ['her', 'him', 'them', 'they', 'she', 'he']:
            if 'client_name' in context.last_entities:
                entities['client_name'] = context.last_entities['client_name']
                logger.info(f"Resolved pronoun to: {entities['client_name']}")
        
        # Resolve stylist references
        if entities.get('stylist') in ['her', 'him', 'them', 'they', 'she', 'he']:
            if 'stylist' in context.last_entities:
                entities['stylist'] = context.last_entities['stylist']
                logger.info(f"Resolved stylist pronoun to: {entities['stylist']}")
        
        return entities


class NLUHandler:
    """Main NLU handler combining intent classification and entity extraction"""
    
    def __init__(self, kimi_client: KimiClient):
        """
        Initialize NLU handler
        
        Args:
            kimi_client: Kimi-K2 client for NLU
        """
        self.intent_classifier = IntentClassifier(kimi_client)
        self.entity_extractor = EntityExtractor(kimi_client)
        logger.info("NLU Handler initialized")
    
    async def understand(
        self,
        text: str,
        language: str,
        context: Optional[ConversationContext] = None
    ) -> NLUResult:
        """
        Understand user intent and extract entities
        
        Args:
            text: User input text
            language: Language code
            context: Conversation context
            
        Returns:
            NLUResult with intent, entities, and confidence
        """
        try:
            # Step 1: Classify intent
            classification = await self.intent_classifier.classify(text, language, context)
            
            intent = classification['intent']
            confidence = classification['confidence']
            requires_clarification = classification['requires_clarification']
            clarification_question = classification['clarification_question']
            
            # Step 2: Extract entities (if intent is known)
            entities = {}
            if intent != Intent.UNKNOWN and intent != Intent.HELP:
                entities = await self.entity_extractor.extract(text, intent, language, context)
            
            # Step 3: Validate required entities
            missing_entities = self._check_missing_entities(intent, entities)
            if missing_entities:
                requires_clarification = True
                clarification_question = self._generate_clarification_question(
                    intent,
                    missing_entities,
                    language
                )
            
            result = NLUResult(
                intent=intent,
                entities=entities,
                confidence=confidence,
                requires_clarification=requires_clarification,
                clarification_question=clarification_question
            )
            
            logger.info(f"NLU Result: {intent.value}, entities: {len(entities)}, confidence: {confidence:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"NLU understanding failed: {e}")
            return NLUResult(
                intent=Intent.UNKNOWN,
                entities={},
                confidence=0.0,
                requires_clarification=True,
                clarification_question="I'm having trouble understanding. Could you try again?"
            )
    
    def _check_missing_entities(self, intent: Intent, entities: Dict[str, Any]) -> list:
        """
        Check for missing required entities
        
        Args:
            intent: User intent
            entities: Extracted entities
            
        Returns:
            List of missing entity names
        """
        required_map = {
            Intent.BOOK_APPOINTMENT: ['client_name', 'service', 'date', 'time'],
            Intent.CANCEL_APPOINTMENT: ['client_name'],
            Intent.RESCHEDULE_APPOINTMENT: ['client_name'],
            Intent.ADD_CLIENT: ['client_name', 'client_phone'],
            Intent.SHOW_CLIENT_INFO: ['client_name'],
            Intent.UPDATE_INVENTORY: ['product', 'quantity'],
            Intent.MARK_ATTENDANCE: ['stylist', 'status'],
            Intent.SHOW_PERFORMANCE: ['stylist']
        }
        
        required = required_map.get(intent, [])
        missing = []
        
        for entity_name in required:
            if entity_name not in entities or entities[entity_name] is None:
                missing.append(entity_name)
        
        return missing
    
    def _generate_clarification_question(
        self,
        intent: Intent,
        missing_entities: list,
        language: str
    ) -> str:
        """
        Generate clarification question for missing entities
        
        Args:
            intent: User intent
            missing_entities: List of missing entity names
            language: Language code
            
        Returns:
            Clarification question
        """
        # English questions
        questions_en = {
            'client_name': "What is the client's name?",
            'client_phone': "What is the client's phone number?",
            'service': "What service would you like to book?",
            'stylist': "Which stylist should I assign?",
            'date': "What date would you like?",
            'time': "What time works best?",
            'product': "Which product?",
            'quantity': "How many?",
            'status': "Are they present or absent?"
        }
        
        # Yoruba questions
        questions_yo = {
            'client_name': "Kini orukọ alabara naa?",
            'client_phone': "Kini nọmba foonu alabara naa?",
            'service': "Iru iṣẹ wo ni o fẹ?",
            'stylist': "Stylist wo ni ki n yan?",
            'date': "Ọjọ wo ni o fẹ?",
            'time': "Akoko wo ni o dara?",
            'product': "Ọja wo?",
            'quantity': "Melo?",
            'status': "Ṣe o wa tabi ko si?"
        }
        
        # Igbo questions
        questions_ig = {
            'client_name': "Kedu aha onye ahịa ahụ?",
            'client_phone': "Kedu nọmba ekwentị onye ahịa ahụ?",
            'service': "Kedu ụdị ọrụ ị chọrọ?",
            'stylist': "Kedu stylist m ga-ahọpụta?",
            'date': "Kedu ụbọchị ị chọrọ?",
            'time': "Kedu oge kacha mma?",
            'product': "Kedu ngwaahịa?",
            'quantity': "Ole?",
            'status': "Ha nọ ma ọ bụ ha anọghị?"
        }
        
        # Hausa questions
        questions_ha = {
            'client_name': "Menene sunan abokin ciniki?",
            'client_phone': "Menene lambar wayar abokin ciniki?",
            'service': "Wane irin hidima kake so?",
            'stylist': "Wane stylist zan sanya?",
            'date': "Wane rana kake so?",
            'time': "Wane lokaci ya fi dacewa?",
            'product': "Wane kaya?",
            'quantity': "Nawa?",
            'status': "Suna nan ko ba su nan ba?"
        }
        
        # Pidgin questions
        questions_pcm = {
            'client_name': "Wetin be the client name?",
            'client_phone': "Wetin be the client phone number?",
            'service': "Which service you wan book?",
            'stylist': "Which stylist I go assign?",
            'date': "Which date you wan?",
            'time': "Which time dey okay for you?",
            'product': "Which product?",
            'quantity': "How many?",
            'status': "Dem dey present or absent?"
        }
        
        # Select questions based on language
        questions = {
            'en': questions_en,
            'yo': questions_yo,
            'ig': questions_ig,
            'ha': questions_ha,
            'pcm': questions_pcm
        }.get(language, questions_en)
        
        # Get first missing entity question
        if missing_entities:
            entity = missing_entities[0]
            return questions.get(entity, questions_en.get(entity, "Could you provide more details?"))
        
        return "Could you provide more details?"
