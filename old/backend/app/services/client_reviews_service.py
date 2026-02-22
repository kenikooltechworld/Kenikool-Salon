"""
Client Reviews Integration Service

Handles review integration with client profiles:
- Link reviews to clients
- Calculate average rating per client
- Track review submission rate
- Request reviews from clients
- Flag negative reviews

Requirements: REQ-CM-014
"""
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from bson import ObjectId

from app.database import Database
from app.services.communication_service import CommunicationService

logger = logging.getLogger(__name__)


class ClientReviewsService:
    """Service for integrating reviews with client profiles"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    def get_client_reviews(
        self,
        tenant_id: str,
        client_id: str,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get all reviews submitted by a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of reviews with pagination info
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })

        if not client:
            raise ValueError("Client not found")

        # Get total count
        total_count = db.reviews.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id
        })

        # Get reviews
        reviews = list(
            db.reviews.find({
                "client_id": client_id,
                "tenant_id": tenant_id
            })
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )

        # Convert ObjectId to string
        for review in reviews:
            review["id"] = str(review.pop("_id"))

        return {
            "reviews": reviews,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count
        }

    def get_client_average_rating(
        self,
        tenant_id: str,
        client_id: str
    ) -> Dict[str, Any]:
        """
        Get average rating given by a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            
        Returns:
            Average rating and review count
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        reviews = list(db.reviews.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
            "is_approved": True
        }))

        if not reviews:
            return {
                "average_rating": 0,
                "review_count": 0,
                "rating_distribution": {}
            }

        # Calculate average
        total_rating = sum(r.get("rating", 0) for r in reviews)
        average_rating = total_rating / len(reviews)

        # Calculate distribution
        distribution = {}
        for i in range(1, 6):
            count = len([r for r in reviews if r.get("rating") == i])
            distribution[i] = count

        return {
            "average_rating": round(average_rating, 2),
            "review_count": len(reviews),
            "rating_distribution": distribution
        }

    def get_client_review_submission_rate(
        self,
        tenant_id: str,
        client_id: str
    ) -> Dict[str, Any]:
        """
        Get review submission rate for a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            
        Returns:
            Review submission rate and metrics
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        # Get client
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })

        if not client:
            raise ValueError("Client not found")

        # Get total visits
        total_visits = client.get("total_visits", 0)

        if total_visits == 0:
            return {
                "submission_rate": 0,
                "total_visits": 0,
                "total_reviews": 0
            }

        # Get total reviews
        total_reviews = db.reviews.count_documents({
            "client_id": client_id,
            "tenant_id": tenant_id
        })

        # Calculate rate
        submission_rate = (total_reviews / total_visits * 100) if total_visits > 0 else 0

        return {
            "submission_rate": round(submission_rate, 2),
            "total_visits": total_visits,
            "total_reviews": total_reviews
        }

    def request_review(
        self,
        tenant_id: str,
        client_id: str,
        booking_id: str,
        channel: str = "sms",
        custom_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Request a review from a client
        
        Args:
            tenant_id: Tenant ID
            client_id: Client ID
            booking_id: Booking ID to review
            channel: Communication channel (sms, email, whatsapp)
            custom_message: Custom message to send
            
        Returns:
            Review request details
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        # Get client
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })

        if not client:
            raise ValueError("Client not found")

        # Get booking
        booking = db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "client_id": client_id
        })

        if not booking:
            raise ValueError("Booking not found")

        # Determine recipient
        if channel == "email":
            if not client.get("email"):
                raise ValueError("Client has no email address")
            recipient = client["email"]
        else:
            recipient = client.get("phone")
            if not recipient:
                raise ValueError("Client has no phone number")

        # Create default message
        if not custom_message:
            if channel == "email":
                custom_message = f"Hi {client.get('name')}, we'd love to hear about your recent visit! Please share your feedback."
            else:
                custom_message = f"Hi {client.get('name')}, please rate your recent visit with us!"

        # Log communication
        communication = CommunicationService.log_communication(
            client_id=client_id,
            tenant_id=tenant_id,
            channel=channel,
            message_type="review_request",
            content=custom_message,
            recipient=recipient,
            direction="outbound",
            booking_id=booking_id
        )

        # Send message
        try:
            if channel == "sms":
                from app.services.termii_service import send_sms
                success = send_sms(recipient, custom_message)
            elif channel == "whatsapp":
                from app.services.termii_service import send_whatsapp
                success = send_whatsapp(recipient, custom_message)
            elif channel == "email":
                from app.services.email_service import email_service
                success = email_service.send_email(
                    to=recipient,
                    subject="Share Your Feedback",
                    html=f"<p>{custom_message}</p>",
                    text=custom_message
                )
            else:
                success = False

            # Update communication status
            CommunicationService.update_communication_status(
                communication_id=str(communication["_id"]),
                status="sent" if success else "failed"
            )

            # Create review request record
            review_request = {
                "client_id": client_id,
                "tenant_id": tenant_id,
                "booking_id": booking_id,
                "channel": channel,
                "status": "sent" if success else "failed",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }

            result = db.review_requests.insert_one(review_request)
            review_request["id"] = str(result.inserted_id)

            return review_request

        except Exception as e:
            logger.error(f"Error sending review request: {e}")
            CommunicationService.update_communication_status(
                communication_id=str(communication["_id"]),
                status="failed",
                error_message=str(e)
            )
            raise

    def flag_negative_review(
        self,
        tenant_id: str,
        review_id: str,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Flag a negative review for follow-up
        
        Args:
            tenant_id: Tenant ID
            review_id: Review ID
            reason: Reason for flagging
            
        Returns:
            Flagged review
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        # Get review
        review = db.reviews.find_one({
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id
        })

        if not review:
            raise ValueError("Review not found")

        # Flag review
        db.reviews.update_one(
            {"_id": ObjectId(review_id)},
            {
                "$set": {
                    "flagged": True,
                    "flag_reason": reason,
                    "flagged_at": datetime.now(),
                    "updated_at": datetime.now()
                }
            }
        )

        # Create follow-up task
        follow_up = {
            "client_id": review.get("client_id"),
            "tenant_id": tenant_id,
            "review_id": review_id,
            "task_type": "negative_review_followup",
            "status": "pending",
            "reason": reason,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }

        result = db.follow_up_tasks.insert_one(follow_up)
        follow_up["id"] = str(result.inserted_id)

        # Get updated review
        updated_review = db.reviews.find_one({"_id": ObjectId(review_id)})
        if updated_review:
            updated_review["id"] = str(updated_review.pop("_id"))

        return updated_review

    def respond_to_review(
        self,
        tenant_id: str,
        review_id: str,
        response_text: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a response to a review
        
        Args:
            tenant_id: Tenant ID
            review_id: Review ID
            response_text: Response text
            user_id: User responding
            
        Returns:
            Updated review with response
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        # Get review
        review = db.reviews.find_one({
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id
        })

        if not review:
            raise ValueError("Review not found")

        # Add response
        response = {
            "text": response_text,
            "user_id": user_id,
            "created_at": datetime.now()
        }

        db.reviews.update_one(
            {"_id": ObjectId(review_id)},
            {
                "$set": {
                    "response": response,
                    "updated_at": datetime.now()
                }
            }
        )

        # Get updated review
        updated_review = db.reviews.find_one({"_id": ObjectId(review_id)})
        if updated_review:
            updated_review["id"] = str(updated_review.pop("_id"))

        return updated_review

    def get_negative_reviews(
        self,
        tenant_id: str,
        rating_threshold: int = 3,
        offset: int = 0,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get negative reviews (below threshold) for follow-up
        
        Args:
            tenant_id: Tenant ID
            rating_threshold: Rating threshold (reviews below this are negative)
            offset: Pagination offset
            limit: Pagination limit
            
        Returns:
            List of negative reviews
            
        Requirements: REQ-CM-014
        """
        db = ClientReviewsService._get_db()
        # Get total count
        total_count = db.reviews.count_documents({
            "tenant_id": tenant_id,
            "rating": {"$lt": rating_threshold},
            "flagged": {"$ne": True}
        })

        # Get reviews
        reviews = list(
            db.reviews.find({
                "tenant_id": tenant_id,
                "rating": {"$lt": rating_threshold},
                "flagged": {"$ne": True}
            })
            .sort("created_at", -1)
            .skip(offset)
            .limit(limit)
        )

        # Convert ObjectId to string
        for review in reviews:
            review["id"] = str(review.pop("_id"))

        return {
            "reviews": reviews,
            "total_count": total_count,
            "has_more": (offset + limit) < total_count
        }


# Create singleton instance
client_reviews_service = ClientReviewsService()
