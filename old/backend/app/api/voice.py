"""
Voice API Endpoints

Provides endpoints for voice-based feedback collection, command processing, and settings management.

Requirements: 19.1, 19.2, 19.6, 19.7
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from app.api.dependencies import get_current_user, get_db
from app.services.voice_feedback_service import VoiceFeedbackService
from app.services.voice_navigation_service import VoiceNavigationService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/voice", tags=["voice"])


# Request Models
class VoiceFeedbackRequest(BaseModel):
    """Request for voice feedback collection"""

    commandId: str
    rating: int  # 1-5
    comment: Optional[str] = None
    wasHelpful: bool


class VoiceDirectionsRequest(BaseModel):
    """Request for voice directions"""

    intent: str
    context: Optional[Dict[str, Any]] = None


class VoiceCommandRequest(BaseModel):
    """Request for voice command processing"""

    text: str
    language: str = "en"


class VoiceSettingsRequest(BaseModel):
    """Request for updating voice settings"""

    enabled: Optional[bool] = None
    language: Optional[str] = None
    sensitivity: Optional[int] = None
    wakeWord: Optional[str] = None
    autoActivation: Optional[bool] = None
    dataStorage: Optional[str] = None
    privacyMode: Optional[bool] = None
    feedbackCollection: Optional[bool] = None


# Response Models
class VoiceLanguageResponse(BaseModel):
    """Voice language response"""

    code: str
    name: str
    nativeName: str
    isSupported: bool


class VoiceSettingsResponse(BaseModel):
    """Voice settings response"""

    enabled: bool
    language: str
    sensitivity: int
    wakeWord: str
    autoActivation: bool
    dataStorage: str
    privacyMode: bool
    feedbackCollection: bool


class VoiceCommandResponse(BaseModel):
    """Voice command response"""

    id: str
    text: str
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    timestamp: datetime


def get_voice_feedback_service(db=Depends(get_db)) -> VoiceFeedbackService:
    """Get VoiceFeedbackService instance"""
    return VoiceFeedbackService(db)


def get_voice_navigation_service() -> VoiceNavigationService:
    """Get VoiceNavigationService instance"""
    return VoiceNavigationService()


@router.post("/feedback/collect")
async def collect_voice_feedback(
    request: VoiceFeedbackRequest,
    current_user=Depends(get_current_user),
    voice_service: VoiceFeedbackService = Depends(get_voice_feedback_service),
) -> Dict[str, Any]:
    """
    Collect voice feedback for a booking

    Args:
        request: Voice feedback request

    Returns:
        Feedback record

    Raises:
        HTTPException: If collection fails

    Requirement 16.1: Collect voice-based feedback after bookings
    """
    try:
        customer_id = current_user.get("id")

        feedback = await voice_service.collect_voice_feedback(
            request.booking_id,
            customer_id,
            request.audio_url,
            request.audio_duration_seconds,
        )

        return {
            "message": "Voice feedback collected successfully",
            "feedback_id": str(feedback.get("_id")),
            "status": "processing",
        }

    except Exception as e:
        logger.error(f"Failed to collect voice feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to collect voice feedback",
        )


@router.get("/feedback/{feedback_id}")
async def get_voice_feedback(
    feedback_id: str,
    current_user=Depends(get_current_user),
    voice_service: VoiceFeedbackService = Depends(get_voice_feedback_service),
) -> Dict[str, Any]:
    """
    Get voice feedback record

    Args:
        feedback_id: Feedback ID

    Returns:
        Feedback record

    Raises:
        HTTPException: If not found
    """
    try:
        feedback = await voice_service.get_feedback(feedback_id)

        if not feedback:
            raise HTTPException(
                status_code=404,
                detail="Feedback not found",
            )

        return {
            "feedback_id": str(feedback.get("_id")),
            "booking_id": feedback.get("booking_id"),
            "transcription": feedback.get("transcription"),
            "transcription_status": feedback.get("transcription_status"),
            "sentiment": feedback.get("sentiment"),
            "rating": feedback.get("rating"),
            "created_at": feedback.get("created_at").isoformat()
            if feedback.get("created_at")
            else None,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get voice feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get voice feedback",
        )


@router.get("/feedback/booking/{booking_id}")
async def get_booking_voice_feedback(
    booking_id: str,
    current_user=Depends(get_current_user),
    voice_service: VoiceFeedbackService = Depends(get_voice_feedback_service),
) -> Dict[str, Any]:
    """
    Get voice feedback for a booking

    Args:
        booking_id: Booking ID

    Returns:
        Feedback record or null

    Requirement 16.2: Store feedback in database
    """
    try:
        feedback = await voice_service.get_booking_feedback(booking_id)

        if not feedback:
            return {"feedback": None}

        return {
            "feedback_id": str(feedback.get("_id")),
            "booking_id": feedback.get("booking_id"),
            "transcription": feedback.get("transcription"),
            "transcription_status": feedback.get("transcription_status"),
            "sentiment": feedback.get("sentiment"),
            "rating": feedback.get("rating"),
        }

    except Exception as e:
        logger.error(f"Failed to get booking voice feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get booking voice feedback",
        )


@router.get("/feedback/salon/{salon_id}/summary")
async def get_salon_feedback_summary(
    salon_id: str,
    current_user=Depends(get_current_user),
    voice_service: VoiceFeedbackService = Depends(get_voice_feedback_service),
) -> Dict[str, Any]:
    """
    Get summary of voice feedback for a salon

    Args:
        salon_id: Salon ID

    Returns:
        Feedback summary with statistics
    """
    try:
        summary = await voice_service.get_salon_feedback_summary(salon_id)
        return summary

    except Exception as e:
        logger.error(f"Failed to get salon feedback summary: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get salon feedback summary",
        )


@router.post("/directions")
async def get_voice_directions(
    request: VoiceDirectionsRequest,
    voice_service: VoiceNavigationService = Depends(get_voice_navigation_service),
) -> Dict[str, Any]:
    """
    Get voice-based turn-by-turn directions

    Args:
        request: Voice directions request

    Returns:
        Voice directions with audio URLs

    Raises:
        HTTPException: If generation fails

    Requirement 16.3: Provide voice-based turn-by-turn directions
    """
    try:
        directions = await voice_service.generate_voice_directions(
            request.from_latitude,
            request.from_longitude,
            request.to_latitude,
            request.to_longitude,
            request.language,
        )

        return directions

    except Exception as e:
        logger.error(f"Failed to generate voice directions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate voice directions",
        )


@router.post("/command")
async def process_voice_command(
    request: VoiceCommandRequest,
    current_user=Depends(get_current_user),
    voice_service: VoiceNavigationService = Depends(get_voice_navigation_service),
) -> Dict[str, Any]:
    """
    Process voice command for salon operations

    Args:
        request: Voice command request with text and language

    Returns:
        Processed command with action and result

    Raises:
        HTTPException: If processing fails

    Requirement 19.2: Voice command processing and responses
    """
    try:
        result = await voice_service.process_voice_command(
            request.text,
            request.language,
        )

        return {
            "id": result.get("id", ""),
            "text": request.text,
            "success": result.get("success", True),
            "message": result.get("message", "Command processed"),
            "data": result.get("data"),
            "timestamp": datetime.utcnow(),
        }

    except Exception as e:
        logger.error(f"Failed to process voice command: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process voice command",
        )


@router.get("/languages")
async def get_supported_languages(
    voice_service: VoiceNavigationService = Depends(get_voice_navigation_service),
) -> Dict[str, Any]:
    """
    Get list of supported languages for voice recognition

    Returns:
        List of supported languages with metadata

    Requirement 19.6: Support multiple languages
    """
    try:
        languages = [
            {
                "code": "en",
                "name": "English",
                "nativeName": "English",
                "isSupported": True,
            },
            {
                "code": "es",
                "name": "Spanish",
                "nativeName": "Español",
                "isSupported": True,
            },
            {
                "code": "fr",
                "name": "French",
                "nativeName": "Français",
                "isSupported": True,
            },
            {
                "code": "de",
                "name": "German",
                "nativeName": "Deutsch",
                "isSupported": True,
            },
            {
                "code": "it",
                "name": "Italian",
                "nativeName": "Italiano",
                "isSupported": True,
            },
            {
                "code": "pt",
                "name": "Portuguese",
                "nativeName": "Português",
                "isSupported": True,
            },
            {
                "code": "ja",
                "name": "Japanese",
                "nativeName": "日本語",
                "isSupported": True,
            },
            {
                "code": "zh",
                "name": "Chinese",
                "nativeName": "中文",
                "isSupported": True,
            },
        ]

        return {
            "supported_languages": languages,
            "count": len(languages),
        }

    except Exception as e:
        logger.error(f"Failed to get supported languages: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get supported languages",
        )


@router.get("/settings")
async def get_voice_settings(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, Any]:
    """
    Get current user's voice settings

    Returns:
        User's voice settings

    Requirement 19.7: Privacy controls and settings
    """
    try:
        user_id = current_user.get("id")
        
        # Get settings from database or return defaults
        settings_collection = db["voice_settings"]
        settings = await settings_collection.find_one({"user_id": user_id})
        
        if not settings:
            # Return default settings
            return {
                "enabled": True,
                "language": "en",
                "sensitivity": 50,
                "wakeWord": "Hey Salon",
                "autoActivation": False,
                "dataStorage": "standard",
                "privacyMode": False,
                "feedbackCollection": True,
            }
        
        return {
            "enabled": settings.get("enabled", True),
            "language": settings.get("language", "en"),
            "sensitivity": settings.get("sensitivity", 50),
            "wakeWord": settings.get("wakeWord", "Hey Salon"),
            "autoActivation": settings.get("autoActivation", False),
            "dataStorage": settings.get("dataStorage", "standard"),
            "privacyMode": settings.get("privacyMode", False),
            "feedbackCollection": settings.get("feedbackCollection", True),
        }

    except Exception as e:
        logger.error(f"Failed to get voice settings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get voice settings",
        )


@router.put("/settings")
async def update_voice_settings(
    request: VoiceSettingsRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, Any]:
    """
    Update user's voice settings

    Args:
        request: Voice settings to update

    Returns:
        Updated voice settings

    Requirement 19.7: Privacy controls and settings
    """
    try:
        user_id = current_user.get("id")
        settings_collection = db["voice_settings"]
        
        # Prepare update data
        update_data = {}
        if request.enabled is not None:
            update_data["enabled"] = request.enabled
        if request.language is not None:
            update_data["language"] = request.language
        if request.sensitivity is not None:
            update_data["sensitivity"] = request.sensitivity
        if request.wakeWord is not None:
            update_data["wakeWord"] = request.wakeWord
        if request.autoActivation is not None:
            update_data["autoActivation"] = request.autoActivation
        if request.dataStorage is not None:
            update_data["dataStorage"] = request.dataStorage
        if request.privacyMode is not None:
            update_data["privacyMode"] = request.privacyMode
        if request.feedbackCollection is not None:
            update_data["feedbackCollection"] = request.feedbackCollection
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update or insert settings
        result = await settings_collection.update_one(
            {"user_id": user_id},
            {"$set": update_data},
            upsert=True,
        )
        
        # Get updated settings
        settings = await settings_collection.find_one({"user_id": user_id})
        
        return {
            "enabled": settings.get("enabled", True),
            "language": settings.get("language", "en"),
            "sensitivity": settings.get("sensitivity", 50),
            "wakeWord": settings.get("wakeWord", "Hey Salon"),
            "autoActivation": settings.get("autoActivation", False),
            "dataStorage": settings.get("dataStorage", "standard"),
            "privacyMode": settings.get("privacyMode", False),
            "feedbackCollection": settings.get("feedbackCollection", True),
        }

    except Exception as e:
        logger.error(f"Failed to update voice settings: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to update voice settings",
        )


@router.post("/feedback/collect")
async def collect_voice_feedback(
    request: VoiceFeedbackRequest,
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, Any]:
    """
    Collect voice feedback for a command

    Args:
        request: Voice feedback request

    Returns:
        Feedback collection confirmation

    Requirement 19.7: Collect user feedback
    """
    try:
        user_id = current_user.get("id")
        feedback_collection = db["voice_feedback"]
        
        feedback_doc = {
            "user_id": user_id,
            "command_id": request.commandId,
            "rating": request.rating,
            "comment": request.comment,
            "was_helpful": request.wasHelpful,
            "created_at": datetime.utcnow(),
        }
        
        result = await feedback_collection.insert_one(feedback_doc)
        
        return {
            "success": True,
            "message": "Feedback collected successfully",
            "feedback_id": str(result.inserted_id),
        }

    except Exception as e:
        logger.error(f"Failed to collect voice feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to collect voice feedback",
        )


@router.get("/history")
async def get_voice_command_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> List[Dict[str, Any]]:
    """
    Get user's voice command history

    Args:
        limit: Maximum number of commands to return
        offset: Number of commands to skip

    Returns:
        List of voice commands

    Requirement 19.1: Voice recognition setup and configuration
    """
    try:
        user_id = current_user.get("id")
        history_collection = db["voice_command_history"]
        
        commands = await history_collection.find(
            {"user_id": user_id}
        ).sort("created_at", -1).skip(offset).limit(limit).to_list(limit)
        
        return [
            {
                "id": str(cmd.get("_id")),
                "text": cmd.get("text"),
                "intent": cmd.get("intent"),
                "parameters": cmd.get("parameters", {}),
                "confidence": cmd.get("confidence", 0),
                "timestamp": cmd.get("created_at").isoformat()
                if cmd.get("created_at")
                else None,
                "language": cmd.get("language", "en"),
            }
            for cmd in commands
        ]

    except Exception as e:
        logger.error(f"Failed to get voice command history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get voice command history",
        )


@router.delete("/history")
async def clear_voice_command_history(
    current_user=Depends(get_current_user),
    db=Depends(get_db),
) -> Dict[str, Any]:
    """
    Clear user's voice command history

    Returns:
        Confirmation of deletion

    Requirement 19.7: Privacy controls
    """
    try:
        user_id = current_user.get("id")
        history_collection = db["voice_command_history"]
        
        result = await history_collection.delete_many({"user_id": user_id})
        
        return {
            "success": True,
            "message": "Voice history cleared successfully",
            "deleted_count": result.deleted_count,
        }

    except Exception as e:
        logger.error(f"Failed to clear voice command history: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to clear voice command history",
        )


@router.post("/test-microphone")
async def test_microphone(
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Test microphone access and permissions

    Returns:
        Microphone test result

    Requirement 19.1: Voice recognition setup
    """
    try:
        # This endpoint is mainly for backend validation
        # Actual microphone testing happens on the frontend
        return {
            "success": True,
            "message": "Microphone test successful. Please check your browser permissions.",
        }

    except Exception as e:
        logger.error(f"Failed to test microphone: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to test microphone",
        )


@router.post("/directions")
async def get_voice_directions(
    request: VoiceDirectionsRequest,
    current_user=Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Get voice directions for a specific intent

    Args:
        request: Voice directions request with intent and context

    Returns:
        Voice directions with audio guidance

    Requirement 19.2: Voice command processing
    """
    try:
        # Generate directions based on intent
        directions_map = {
            "book_appointment": "To book an appointment, say the client name, service, staff member, and preferred time.",
            "check_schedule": "To check the schedule, say the staff member's name and the date.",
            "client_lookup": "To find a client, say their name or phone number.",
            "service_info": "To get service information, say the service name.",
            "cancel_appointment": "To cancel an appointment, say the appointment ID or client name.",
            "reschedule_appointment": "To reschedule, say the appointment ID and new date and time.",
            "get_availability": "To check availability, say the staff member name and preferred date.",
        }
        
        directions = directions_map.get(
            request.intent,
            "Please repeat your request.",
        )
        
        return {
            "directions": directions,
            "audioUrl": None,  # Audio generation would happen here
            "intent": request.intent,
            "context": request.context,
        }

    except Exception as e:
        logger.error(f"Failed to get voice directions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to get voice directions",
        )
