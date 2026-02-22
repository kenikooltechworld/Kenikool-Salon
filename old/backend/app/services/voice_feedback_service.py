"""
Voice Feedback Service

Provides voice-based feedback collection and transcription for salon bookings.

Requirements: 16.1, 16.2
"""

import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional

from pymongo.database import Database

logger = logging.getLogger(__name__)


class VoiceFeedbackService:
    """Service for collecting and managing voice-based feedback"""

    def __init__(self, db: Database):
        """
        Initialize VoiceFeedbackService

        Args:
            db: MongoDB database connection
        """
        self.db = db
        self.feedback_collection = db["voice_feedback"]
        self.bookings_collection = db["bookings"]

    async def collect_voice_feedback(
        self,
        booking_id: str,
        customer_id: str,
        audio_url: str,
        audio_duration_seconds: float,
    ) -> Dict[str, Any]:
        """
        Collect voice feedback for a booking

        Args:
            booking_id: Booking ID
            customer_id: Customer ID
            audio_url: URL to audio file
            audio_duration_seconds: Duration of audio in seconds

        Returns:
            Feedback record

        Requirement 16.1: Collect voice-based feedback after bookings
        """
        try:
            feedback_doc = {
                "booking_id": booking_id,
                "customer_id": customer_id,
                "audio_url": audio_url,
                "audio_duration_seconds": audio_duration_seconds,
                "transcription": None,
                "transcription_status": "pending",
                "sentiment": None,
                "rating": None,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }

            result = await self.feedback_collection.insert_one(feedback_doc)
            feedback_doc["_id"] = result.inserted_id

            logger.info(f"Created voice feedback record for booking {booking_id}")

            # Trigger transcription asynchronously
            asyncio.create_task(
                self._transcribe_audio(str(result.inserted_id), audio_url)
            )

            return feedback_doc

        except Exception as e:
            logger.error(f"Failed to collect voice feedback: {e}")
            raise

    async def _transcribe_audio(
        self,
        feedback_id: str,
        audio_url: str,
    ) -> None:
        """
        Transcribe audio to text

        Args:
            feedback_id: Feedback record ID
            audio_url: URL to audio file

        Requirement 16.2: Transcribe voice feedback to text
        """
        try:
            logger.info(f"Starting transcription for feedback {feedback_id}")

            # Simulate transcription (in production, would use speech-to-text API)
            transcription = await self._call_transcription_api(audio_url)

            if transcription:
                # Analyze sentiment
                sentiment = await self._analyze_sentiment(transcription)

                # Extract rating if mentioned
                rating = self._extract_rating_from_text(transcription)

                # Update feedback record
                from bson import ObjectId

                await self.feedback_collection.update_one(
                    {"_id": ObjectId(feedback_id)},
                    {
                        "$set": {
                            "transcription": transcription,
                            "transcription_status": "completed",
                            "sentiment": sentiment,
                            "rating": rating,
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )

                logger.info(f"Transcription completed for feedback {feedback_id}")

                # Update booking with feedback
                feedback_record = await self.feedback_collection.find_one(
                    {"_id": ObjectId(feedback_id)}
                )
                if feedback_record:
                    await self.bookings_collection.update_one(
                        {"_id": ObjectId(feedback_record["booking_id"])},
                        {
                            "$set": {
                                "voice_feedback_id": feedback_id,
                                "feedback_sentiment": sentiment,
                                "feedback_rating": rating,
                            }
                        },
                    )

            else:
                # Mark as failed
                from bson import ObjectId

                await self.feedback_collection.update_one(
                    {"_id": ObjectId(feedback_id)},
                    {
                        "$set": {
                            "transcription_status": "failed",
                            "updated_at": datetime.utcnow(),
                        }
                    },
                )

        except Exception as e:
            logger.error(f"Failed to transcribe audio for feedback {feedback_id}: {e}")

    async def _call_transcription_api(self, audio_url: str) -> Optional[str]:
        """
        Call speech-to-text API to transcribe audio

        Args:
            audio_url: URL to audio file

        Returns:
            Transcribed text or None if failed
        """
        try:
            # In production, would call Google Cloud Speech-to-Text, AWS Transcribe, etc.
            # For now, return a simulated transcription
            logger.debug(f"Transcribing audio from {audio_url}")

            # Simulate API call
            await asyncio.sleep(0.5)

            return "The salon experience was excellent. The staff was very friendly and professional. I would definitely recommend this salon to my friends."

        except Exception as e:
            logger.error(f"Failed to call transcription API: {e}")
            return None

    async def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of transcribed text

        Args:
            text: Transcribed text

        Returns:
            Sentiment (positive, negative, neutral)
        """
        try:
            # In production, would use sentiment analysis API
            # For now, use simple keyword matching
            positive_keywords = [
                "excellent",
                "great",
                "good",
                "amazing",
                "wonderful",
                "friendly",
                "professional",
                "recommend",
            ]
            negative_keywords = [
                "bad",
                "poor",
                "terrible",
                "awful",
                "rude",
                "unprofessional",
                "disappointed",
            ]

            text_lower = text.lower()

            positive_count = sum(1 for word in positive_keywords if word in text_lower)
            negative_count = sum(1 for word in negative_keywords if word in text_lower)

            if positive_count > negative_count:
                return "positive"
            elif negative_count > positive_count:
                return "negative"
            else:
                return "neutral"

        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {e}")
            return "neutral"

    def _extract_rating_from_text(self, text: str) -> Optional[int]:
        """
        Extract rating from transcribed text

        Args:
            text: Transcribed text

        Returns:
            Rating (1-5) or None if not found
        """
        try:
            import re

            # Look for patterns like "5 stars", "5 out of 5", "rate it 5"
            patterns = [
                r"(\d)\s*(?:stars?|out of 5|\/5)",
                r"rate[d]?\s*(?:it\s+)?(\d)",
                r"(\d)\s*(?:\/|out of)\s*5",
            ]

            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    rating = int(match.group(1))
                    if 1 <= rating <= 5:
                        return rating

            return None

        except Exception as e:
            logger.error(f"Failed to extract rating: {e}")
            return None

    async def get_feedback(self, feedback_id: str) -> Optional[Dict[str, Any]]:
        """
        Get voice feedback record

        Args:
            feedback_id: Feedback ID

        Returns:
            Feedback record or None
        """
        try:
            from bson import ObjectId

            feedback = await self.feedback_collection.find_one(
                {"_id": ObjectId(feedback_id)}
            )
            return feedback

        except Exception as e:
            logger.error(f"Failed to get feedback: {e}")
            return None

    async def get_booking_feedback(self, booking_id: str) -> Optional[Dict[str, Any]]:
        """
        Get voice feedback for a booking

        Args:
            booking_id: Booking ID

        Returns:
            Feedback record or None
        """
        try:
            feedback = await self.feedback_collection.find_one(
                {"booking_id": booking_id}
            )
            return feedback

        except Exception as e:
            logger.error(f"Failed to get booking feedback: {e}")
            return None

    async def get_customer_feedback(
        self,
        customer_id: str,
        limit: int = 10,
    ) -> list[Dict[str, Any]]:
        """
        Get all voice feedback for a customer

        Args:
            customer_id: Customer ID
            limit: Maximum number of records

        Returns:
            List of feedback records
        """
        try:
            feedback_list = list(
                await self.feedback_collection.find(
                    {"customer_id": customer_id}
                )
                .sort("created_at", -1)
                .limit(limit)
                .to_list(length=limit)
            )
            return feedback_list

        except Exception as e:
            logger.error(f"Failed to get customer feedback: {e}")
            return []

    async def get_salon_feedback_summary(
        self,
        salon_id: str,
    ) -> Dict[str, Any]:
        """
        Get summary of voice feedback for a salon

        Args:
            salon_id: Salon ID

        Returns:
            Feedback summary with statistics
        """
        try:
            # Get all bookings for salon
            bookings = list(
                await self.bookings_collection.find(
                    {"salon_id": salon_id}
                ).to_list(length=None)
            )

            booking_ids = [str(b["_id"]) for b in bookings]

            # Get all feedback for these bookings
            feedback_list = list(
                await self.feedback_collection.find(
                    {"booking_id": {"$in": booking_ids}}
                ).to_list(length=None)
            )

            # Calculate statistics
            total_feedback = len(feedback_list)
            completed_feedback = sum(
                1 for f in feedback_list if f.get("transcription_status") == "completed"
            )
            positive_feedback = sum(
                1 for f in feedback_list if f.get("sentiment") == "positive"
            )
            negative_feedback = sum(
                1 for f in feedback_list if f.get("sentiment") == "negative"
            )
            average_rating = (
                sum(f.get("rating", 0) for f in feedback_list if f.get("rating"))
                / total_feedback
                if total_feedback > 0
                else 0
            )

            return {
                "salon_id": salon_id,
                "total_feedback": total_feedback,
                "completed_feedback": completed_feedback,
                "positive_feedback": positive_feedback,
                "negative_feedback": negative_feedback,
                "average_rating": round(average_rating, 1),
                "sentiment_distribution": {
                    "positive": positive_feedback,
                    "negative": negative_feedback,
                    "neutral": total_feedback - positive_feedback - negative_feedback,
                },
            }

        except Exception as e:
            logger.error(f"Failed to get salon feedback summary: {e}")
            raise
