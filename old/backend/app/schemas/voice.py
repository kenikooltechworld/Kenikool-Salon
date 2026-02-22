from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class Intent(str, Enum):
    """Supported voice command intents"""
    BOOK_APPOINTMENT = "book_appointment"
    CANCEL_APPOINTMENT = "cancel_appointment"
    RESCHEDULE_APPOINTMENT = "reschedule_appointment"
    SHOW_APPOINTMENTS = "show_appointments"
    ADD_CLIENT = "add_client"
    SHOW_CLIENT_INFO = "show_client_info"
    SHOW_REVENUE = "show_revenue"
    SHOW_ANALYTICS = "show_analytics"
    CHECK_INVENTORY = "check_inventory"
    UPDATE_INVENTORY = "update_inventory"
    SHOW_STAFF_SCHEDULE = "show_staff_schedule"
    MARK_ATTENDANCE = "mark_attendance"
    HELP = "help"
    UNKNOWN = "unknown"


class TranscriptionResult(BaseModel):
    """Result of speech-to-text conversion"""
    text: str
    confidence: float
    language: Optional[str] = None
    duration: float


class LanguageDetectionResult(BaseModel):
    """Result of language detection"""
    language: str
    confidence: float
    alternatives: List[tuple] = []


class NLUResult(BaseModel):
    """Result of natural language understanding"""
    intent: Intent
    entities: Dict[str, Any] = {}
    confidence: float
    requires_clarification: bool = False
    clarification_question: Optional[str] = None


class ActionResult(BaseModel):
    """Result of action execution"""
    success: bool
    data: Optional[Dict[str, Any]] = None
    message: str
    error: Optional[str] = None


class VoiceResponse(BaseModel):
    """Complete voice command response"""
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
    entities: Dict[str, Any] = {}
    response: str
    timestamp: datetime


class ConversationContext(BaseModel):
    """Conversation session context"""
    session_id: str
    user_id: str
    language: str
    history: List[ConversationTurn] = []
    last_intent: Optional[Intent] = None
    last_entities: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime


class VoiceCommandRequest(BaseModel):
    """Request to process voice command"""
    audio_data: bytes
    user_id: str
    session_id: str
    preferred_language: Optional[str] = None


class SuggestionType(str, Enum):
    """Types of AI suggestions"""
    BOOKING_TIME = "booking_time"
    STYLIST_ASSIGNMENT = "stylist_assignment"
    INVENTORY_REORDER = "inventory_reorder"
    CLIENT_RETENTION = "client_retention"
    UPSELL_SERVICE = "upsell_service"
    STAFFING_OPTIMIZATION = "staffing_optimization"


class Suggestion(BaseModel):
    """AI-generated suggestion"""
    id: str
    type: SuggestionType
    title: str
    description: str
    confidence: float
    reasoning: str
    action_data: Dict[str, Any] = {}
    created_at: datetime
    expires_at: Optional[datetime] = None
    was_accepted: Optional[bool] = None
    user_feedback: Optional[str] = None


class InsightType(str, Enum):
    """Types of business insights"""
    PERFORMANCE = "performance"
    OPPORTUNITY = "opportunity"
    RISK = "risk"
    TREND = "trend"


class Insight(BaseModel):
    """Business intelligence insight"""
    id: str
    type: InsightType
    title: str
    description: str
    impact_level: str
    data_points: Dict[str, Any] = {}
    recommendations: List[str] = []
    created_at: datetime


class AlertType(str, Enum):
    """Types of proactive alerts"""
    INVENTORY_SHORTAGE = "inventory_shortage"
    CLIENT_CHURN_RISK = "client_churn_risk"
    UNDERUTILIZED_SLOTS = "underutilized_slots"
    PERFORMANCE_DECLINE = "performance_decline"
    OPPORTUNITY_DETECTED = "opportunity_detected"


class Alert(BaseModel):
    """Proactive alert"""
    id: str
    type: AlertType
    severity: str
    title: str
    message: str
    action_required: bool
    suggested_actions: List[str] = []
    data: Dict[str, Any] = {}
    created_at: datetime
    acknowledged: bool = False
