"""
Voice Assistant Data Models
Pydantic models for voice command processing
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum


class Intent(str, Enum):
    """Available intents for voice commands"""
    BOOK_APPOINTMENT = "book_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    RESCHEDULE_APPOINTMENT = "reschedule_appointment"
    SHOW_APPOINTMENTS = "show_appointments"
    ADD_CLIENT = "add_client"
    SHOW_CLIENT_INFO = "show_client_info"
    FIND_INACTIVE_CLIENTS = "find_inactive_clients"
    SHOW_REVENUE = "show_revenue"
    SHOW_ANALYTICS = "show_analytics"
    CHECK_INVENTORY = "check_inventory"
    UPDATE_INVENTORY = "update_inventory"
    SHOW_STAFF_SCHEDULE = "show_staff_schedule"
    CHECK_AVAILABILITY = "check_availability"
    MARK_ATTENDANCE = "mark_attendance"
    SHOW_PERFORMANCE = "show_performance"
    QUICK_BOOK = "quick_book"
    DAILY_SUMMARY = "daily_summary"
    EMERGENCY_CANCEL = "emergency_cancel"
    CHECK_IN = "check_in"
    END_OF_DAY = "end_of_day"
    # AI Suggestion Commands
    SHOW_SUGGESTIONS = "show_suggestions"
    SHOW_INSIGHTS = "show_insights"
    PREDICT_BOOKINGS = "predict_bookings"
    PREDICT_CHURN = "predict_churn"
    PREDICT_REORDER = "predict_reorder"
    HELP = "help"
    UNKNOWN = "unknown"


class VoiceCommand(BaseModel):
    """Voice command input"""
    audio_data: bytes
    user_id: str
    session_id: str
    preferred_language: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class TranscriptionResult(BaseModel):
    """Result from speech-to-text"""
    text: str
    confidence: float
    language: Optional[str] = None
    duration: float = 0.0


class LanguageDetectionResult(BaseModel):
    """Result from language detection"""
    language: str  # ISO 639-1 code
    confidence: float
    alternatives: List[Tuple[str, float]] = []


class NLUResult(BaseModel):
    """Result from natural language understanding"""
    intent: Intent
    entities: Dict[str, Any]
    confidence: float
    requires_clarification: bool = False
    clarification_question: Optional[str] = None


class ActionResult(BaseModel):
    """Result from action execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None


class VoiceResponse(BaseModel):
    """Complete voice assistant response"""
    transcript: str
    detected_language: str
    intent: Intent
    response_text: str
    audio_url: Optional[str] = None
    action_result: ActionResult
    requires_followup: bool = False


class ConversationTurn(BaseModel):
    """Single turn in conversation"""
    user_input: str
    intent: Intent
    entities: Dict[str, Any]
    response: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationContext(BaseModel):
    """Conversation context for session"""
    session_id: str
    user_id: str
    language: str
    history: List[ConversationTurn] = []
    last_intent: Optional[Intent] = None
    last_entities: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
