from typing import Dict, List, Tuple, Optional
import logging
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk import download
from app.schemas.voice import Intent

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    download('punkt', quiet=True)
    download('averaged_perceptron_tagger', quiet=True)
    download('maxent_ne_chunker', quiet=True)
    download('words', quiet=True)
    download('stopwords', quiet=True)
except Exception as e:
    logger.warning(f"NLTK download warning: {e}")

# Import pos_tag and ne_chunk after data is downloaded
try:
    from nltk.tag import pos_tag
    from nltk.chunk import ne_chunk
except ImportError as e:
    logger.error(f"Failed to import NLTK components: {e}")
    raise


class NLUHandler:
    """Natural Language Understanding using NLTK"""

    def __init__(self):
        """Initialize NLU handler"""
        self.intent_patterns = self._load_intent_patterns()
        self.stop_words = set(stopwords.words('english'))
        logger.info("NLU handler initialized successfully with NLTK")

    def _load_intent_patterns(self) -> Dict[str, List[str]]:
        """Load intent patterns for all languages"""
        return {
            Intent.BOOK_APPOINTMENT: [
                "book", "schedule", "appointment", "reserve", "make booking",
                "book me", "i want to book", "can i book", "book a slot",
                "ṣe àpointment", "mee appointment", "yi appointment"
            ],
            Intent.CANCEL_APPOINTMENT: [
                "cancel", "delete", "remove", "appointment", "booking",
                "cancel my", "i want to cancel", "please cancel",
                "fagile", "kansela", "soke"
            ],
            Intent.RESCHEDULE_APPOINTMENT: [
                "reschedule", "change", "move", "appointment", "booking",
                "reschedule my", "can i change", "move my appointment",
                "tun", "yi", "gida"
            ],
            Intent.SHOW_APPOINTMENTS: [
                "show", "list", "appointments", "bookings", "schedule",
                "what are my", "my appointments", "today's appointments",
                "upcoming appointments", "next appointment"
            ],
            Intent.ADD_CLIENT: [
                "add", "new", "client", "customer", "register",
                "add new client", "register client", "new customer"
            ],
            Intent.SHOW_CLIENT_INFO: [
                "show", "client", "history", "information", "details",
                "client history", "show client", "client details"
            ],
            Intent.SHOW_REVENUE: [
                "revenue", "earnings", "income", "sales", "money",
                "how much", "total revenue", "today's revenue", "this week"
            ],
            Intent.SHOW_ANALYTICS: [
                "analytics", "report", "statistics", "performance",
                "show analytics", "performance report", "statistics"
            ],
            Intent.CHECK_INVENTORY: [
                "inventory", "stock", "products", "supplies", "low",
                "check inventory", "what products", "stock level", "low stock"
            ],
            Intent.UPDATE_INVENTORY: [
                "add", "inventory", "stock", "update", "mark",
                "add inventory", "update stock", "mark as used"
            ],
            Intent.SHOW_STAFF_SCHEDULE: [
                "staff", "schedule", "stylist", "availability",
                "show schedule", "who's available", "staff schedule"
            ],
            Intent.MARK_ATTENDANCE: [
                "mark", "attendance", "present", "absent", "check in",
                "mark attendance", "check in", "mark present"
            ],
            Intent.HELP: [
                "help", "commands", "what can", "how to", "guide",
                "help me", "show commands", "what can i do"
            ]
        }

    async def understand(
        self,
        text: str,
        language: str = "en"
    ) -> Dict:
        """
        Extract intent and entities from text using NLTK
        
        Args:
            text: User input text
            language: Language code
            
        Returns:
            Dictionary with intent, entities, and confidence
        """
        try:
            # Tokenize and POS tag
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            
            # Extract named entities
            entities = self._extract_entities_nltk(text, pos_tags)

            # Classify intent
            intent, confidence = self._classify_intent(text)

            return {
                "intent": intent,
                "entities": entities,
                "confidence": confidence,
                "requires_clarification": confidence < 0.6,
                "clarification_question": None if confidence >= 0.6 else "Could you please rephrase that?"
            }

        except Exception as e:
            logger.error(f"NLU processing failed: {e}")
            return {
                "intent": Intent.UNKNOWN,
                "entities": {},
                "confidence": 0.0,
                "requires_clarification": True,
                "clarification_question": "I didn't understand that. Could you please rephrase?"
            }

    def _extract_entities_nltk(self, text: str, pos_tags: List[Tuple]) -> Dict:
        """
        Extract entities using NLTK POS tagging and NER
        
        Args:
            text: User input text
            pos_tags: POS tagged tokens
            
        Returns:
            Dictionary of extracted entities
        """
        entities = {}
        
        try:
            # Named Entity Recognition using NLTK
            tokens = word_tokenize(text)
            pos_tags = pos_tag(tokens)
            ne_tree = ne_chunk(pos_tags)
            
            # Extract named entities
            for subtree in ne_tree:
                if hasattr(subtree, 'label'):
                    entity_type = subtree.label()
                    entity_text = " ".join([word for word, tag in subtree.leaves()])
                    
                    if entity_type not in entities:
                        entities[entity_type] = []
                    entities[entity_type].append(entity_text)
        except Exception as e:
            logger.warning(f"NLTK NER failed: {e}")
        
        # Extract additional entities using pattern matching
        text_lower = text.lower()
        
        # Extract proper nouns (capitalized words)
        words = text.split()
        proper_nouns = [w for w in words if w[0].isupper() and len(w) > 2]
        if proper_nouns:
            if "PERSON" not in entities:
                entities["PERSON"] = []
            entities["PERSON"].extend(proper_nouns)
        
        # Extract services
        services = ["haircut", "coloring", "styling", "treatment", "massage", "perm", "relaxer", "braiding"]
        found_services = [s for s in services if s in text_lower]
        if found_services:
            entities["SERVICE"] = found_services
        
        # Extract products
        products = ["shampoo", "conditioner", "dye", "gel", "spray", "oil", "cream", "serum"]
        found_products = [p for p in products if p in text_lower]
        if found_products:
            entities["PRODUCT"] = found_products
        
        # Extract time references
        times = ["today", "tomorrow", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
                 "morning", "afternoon", "evening", "night", "next week", "this week"]
        found_times = [t for t in times if t in text_lower]
        if found_times:
            entities["TIME"] = found_times
        
        # Extract numbers (quantities, prices)
        import re
        numbers = re.findall(r'\d+', text)
        if numbers:
            entities["NUMBER"] = numbers
        
        return entities

    def _classify_intent(self, text: str) -> Tuple[Intent, float]:
        """
        Classify intent from text using pattern matching
        
        Args:
            text: User input text
            
        Returns:
            Tuple of (intent, confidence)
        """
        text_lower = text.lower()
        matches = {}

        # Check each intent pattern
        for intent, keywords in self.intent_patterns.items():
            match_count = 0
            for keyword in keywords:
                if keyword in text_lower:
                    match_count += 1

            if match_count > 0:
                # Calculate confidence based on matches
                confidence = min(match_count / len(keywords), 1.0)
                matches[intent] = confidence

        # Return best match
        if matches:
            best_intent = max(matches, key=matches.get)
            return best_intent, matches[best_intent]

        return Intent.UNKNOWN, 0.0

    async def extract_entities(
        self,
        text: str,
        intent: Intent
    ) -> Dict:
        """
        Extract specific entities for an intent
        
        Args:
            text: User input text
            intent: Detected intent
            
        Returns:
            Dictionary of extracted entities
        """
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        return self._extract_entities_nltk(text, pos_tags)

    def get_pos_tags(self, text: str) -> List[Tuple]:
        """
        Get POS tags for text
        
        Args:
            text: User input text
            
        Returns:
            List of (word, pos_tag) tuples
        """
        tokens = word_tokenize(text)
        return pos_tag(tokens)

    def get_noun_phrases(self, text: str) -> List[str]:
        """
        Extract noun phrases from text
        
        Args:
            text: User input text
            
        Returns:
            List of noun phrases
        """
        tokens = word_tokenize(text)
        pos_tags = pos_tag(tokens)
        
        noun_phrases = []
        current_phrase = []
        
        for word, tag in pos_tags:
            if tag.startswith('NN'):
                current_phrase.append(word)
            else:
                if current_phrase:
                    noun_phrases.append(" ".join(current_phrase))
                    current_phrase = []
        
        if current_phrase:
            noun_phrases.append(" ".join(current_phrase))
        
        return noun_phrases
