"""
Priority Calculator Service - Calculates priority scores for waitlist entries
"""
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

from app.database import Database
from bson import ObjectId

logger = logging.getLogger(__name__)


class PriorityCalculatorService:
    """Service for calculating priority scores for waitlist entries"""
    
    # Priority calculation constants
    BASE_SCORE = 100
    MAX_WAIT_TIME_BONUS = 30  # +1 point per day, max 30 points
    PREFERRED_DATE_MATCH_BONUS = 20  # +20 points if within 7 days
    PREFERRED_DATE_PENALTY = -10  # -10 points if date has passed
    LOYALTY_BONUS_PER_BOOKING = 5  # +5 points per previous booking
    MAX_LOYALTY_BONUS = 15  # Max 3 bookings worth of bonus
    PREFERRED_DATE_WINDOW_DAYS = 7  # Days to consider as "preferred date match"
    
    @staticmethod
    def calculate_priority(entry: Dict) -> float:
        """
        Calculate priority score for a waitlist entry.
        
        Priority algorithm:
        - Base score: 100
        - Wait time bonus: +1 point per day waiting (max 30 points)
        - Preferred date match: +20 points if within 7 days
        - Preferred date penalty: -10 points if date has passed
        - Loyalty bonus: +5 points per previous booking (max 15 points)
        
        Args:
            entry: Waitlist entry dict with client_id, created_at, preferred_date
            
        Returns:
            float: Priority score
        """
        score = PriorityCalculatorService.BASE_SCORE
        
        # Add wait time score
        wait_time_score = PriorityCalculatorService._calculate_wait_time_score(
            entry.get("created_at")
        )
        score += wait_time_score
        
        # Add date preference score
        date_preference_score = PriorityCalculatorService._calculate_date_preference_score(
            entry.get("preferred_date")
        )
        score += date_preference_score
        
        # Add loyalty score
        loyalty_score = PriorityCalculatorService._calculate_loyalty_score(
            entry.get("client_id") or entry.get("client_email")
        )
        score += loyalty_score
        
        return score
    
    @staticmethod
    def _calculate_wait_time_score(created_at: Optional[datetime]) -> float:
        """
        Calculate score based on how long the entry has been waiting.
        
        +1 point per day waiting, max 30 points.
        
        Args:
            created_at: Datetime when entry was created
            
        Returns:
            float: Wait time score (0 to 30)
        """
        if not created_at:
            return 0.0
        
        # Handle both datetime objects and strings
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                return 0.0
        
        # Calculate days waiting
        now = datetime.utcnow()
        days_waiting = (now - created_at).days
        
        # Cap at max bonus
        wait_score = min(days_waiting, PriorityCalculatorService.MAX_WAIT_TIME_BONUS)
        
        return float(wait_score)
    
    @staticmethod
    def _calculate_date_preference_score(preferred_date: Optional[str]) -> float:
        """
        Calculate score based on preferred date proximity.
        
        +20 points if preferred date is within 7 days from now.
        -10 points if preferred date has passed.
        0 points otherwise.
        
        Args:
            preferred_date: Preferred date string (ISO format or similar)
            
        Returns:
            float: Date preference score (-10, 0, or 20)
        """
        if not preferred_date:
            return 0.0
        
        try:
            # Parse preferred date
            if isinstance(preferred_date, str):
                # Try ISO format first
                try:
                    pref_date = datetime.fromisoformat(preferred_date.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # Try simple date format
                    pref_date = datetime.strptime(preferred_date, '%Y-%m-%d')
            else:
                pref_date = preferred_date
            
            # Get current date (at midnight for comparison)
            now = datetime.utcnow()
            today = now.replace(hour=0, minute=0, second=0, microsecond=0)
            pref_date_normalized = pref_date.replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Calculate days until preferred date
            days_until = (pref_date_normalized - today).days
            
            # If date has passed
            if days_until < 0:
                return float(PriorityCalculatorService.PREFERRED_DATE_PENALTY)
            
            # If date is within preferred window (0 to 7 days)
            if 0 <= days_until <= PriorityCalculatorService.PREFERRED_DATE_WINDOW_DAYS:
                return float(PriorityCalculatorService.PREFERRED_DATE_MATCH_BONUS)
            
            # Date is too far in the future
            return 0.0
            
        except (ValueError, AttributeError, TypeError):
            return 0.0
    
    @staticmethod
    def _calculate_loyalty_score(client_identifier: Optional[str]) -> float:
        """
        Calculate score based on client's booking history.
        
        +5 points per previous booking (max 15 points for 3+ bookings).
        
        Args:
            client_identifier: Client ID or email to look up booking history
            
        Returns:
            float: Loyalty score (0 to 15)
        """
        if not client_identifier:
            return 0.0
        
        try:
            db = Database.get_db()
            
            # Count completed bookings for this client
            # Try to match by client_id first, then by email
            query = {}
            
            # Check if it looks like an ObjectId
            if len(client_identifier) == 24:
                try:
                    query = {
                        "$or": [
                            {"client_id": ObjectId(client_identifier)},
                            {"client_email": client_identifier}
                        ]
                    }
                except Exception:
                    query = {"client_email": client_identifier}
            else:
                query = {"client_email": client_identifier}
            
            # Count completed bookings
            booking_count = db.bookings.count_documents(
                {
                    **query,
                    "status": {"$in": ["completed", "confirmed"]}
                }
            )
            
            # Calculate loyalty bonus: +5 per booking, max 15
            loyalty_score = min(
                booking_count * PriorityCalculatorService.LOYALTY_BONUS_PER_BOOKING,
                PriorityCalculatorService.MAX_LOYALTY_BONUS
            )
            
            return float(loyalty_score)
            
        except Exception as e:
            logger.warning(f"Error calculating loyalty score: {e}")
            return 0.0


# Singleton instance
priority_calculator_service = PriorityCalculatorService()
