from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import DESCENDING
from app.database import db
import asyncio


class StaffReviewService:
    """Service for managing staff performance reviews and feedback."""

    @staticmethod
    async def create_review(
        staff_id: str,
        reviewer_id: str,
        salon_id: str,
        review_date: datetime,
        review_period_start: datetime,
        review_period_end: datetime,
        ratings: Dict[str, int],
        strengths: str,
        areas_for_improvement: str,
        goals: List[Dict[str, Any]],
        follow_up_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Create a performance review."""
        review = {
            "staff_id": ObjectId(staff_id),
            "reviewer_id": ObjectId(reviewer_id),
            "salon_id": ObjectId(salon_id),
            "review_date": review_date,
            "review_period_start": review_period_start,
            "review_period_end": review_period_end,
            "ratings": ratings,
            "strengths": strengths,
            "areas_for_improvement": areas_for_improvement,
            "goals": goals,
            "staff_self_review": None,
            "follow_up_date": follow_up_date,
            "status": "completed",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.performance_reviews.insert_one(review)
        review["_id"] = result.inserted_id
        return review

    @staticmethod
    async def get_staff_reviews(
        staff_id: str,
        salon_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all reviews for a staff member."""
        reviews = await db.performance_reviews.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        ).sort("review_date", DESCENDING).skip(skip).limit(limit).to_list(None)
        return reviews

    @staticmethod
    async def get_review(
        review_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get a specific review."""
        review = await db.performance_reviews.find_one(
            {
                "_id": ObjectId(review_id),
                "salon_id": ObjectId(salon_id),
            }
        )
        return review

    @staticmethod
    async def add_self_review(
        review_id: str,
        self_review_text: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Add staff self-review comments."""
        review = await db.performance_reviews.find_one_and_update(
            {
                "_id": ObjectId(review_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "staff_self_review": self_review_text,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return review

    @staticmethod
    async def schedule_review(
        staff_id: str,
        salon_id: str,
        scheduled_date: datetime,
        reviewer_id: str,
    ) -> Dict[str, Any]:
        """Schedule a performance review."""
        scheduled_review = {
            "staff_id": ObjectId(staff_id),
            "salon_id": ObjectId(salon_id),
            "scheduled_date": scheduled_date,
            "reviewer_id": ObjectId(reviewer_id),
            "status": "scheduled",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.scheduled_reviews.insert_one(scheduled_review)
        scheduled_review["_id"] = result.inserted_id
        return scheduled_review

    @staticmethod
    async def get_scheduled_reviews(
        salon_id: str,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get all scheduled reviews for a salon."""
        now = datetime.utcnow()
        reviews = await db.scheduled_reviews.find(
            {
                "salon_id": ObjectId(salon_id),
                "status": "scheduled",
                "scheduled_date": {"$gte": now},
            }
        ).sort("scheduled_date", 1).skip(skip).limit(limit).to_list(None)
        return reviews

    @staticmethod
    async def get_overdue_reviews(salon_id: str) -> List[Dict[str, Any]]:
        """Get overdue reviews."""
        now = datetime.utcnow()
        reviews = await db.scheduled_reviews.find(
            {
                "salon_id": ObjectId(salon_id),
                "status": "scheduled",
                "scheduled_date": {"$lt": now},
            }
        ).sort("scheduled_date", 1).to_list(None)
        return reviews

    @staticmethod
    async def complete_scheduled_review(
        scheduled_review_id: str,
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Mark a scheduled review as completed."""
        review = await db.scheduled_reviews.find_one_and_update(
            {
                "_id": ObjectId(scheduled_review_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "status": "completed",
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return review

    @staticmethod
    async def get_review_trends(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get review trends over time."""
        reviews = await db.performance_reviews.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        ).sort("review_date", 1).to_list(None)

        if not reviews:
            return {
                "total_reviews": 0,
                "average_ratings": {},
                "trends": [],
            }

        # Calculate average ratings over time
        trends = []
        rating_keys = set()

        for review in reviews:
            rating_keys.update(review.get("ratings", {}).keys())
            trends.append({
                "date": review["review_date"],
                "ratings": review.get("ratings", {}),
            })

        # Calculate overall averages
        average_ratings = {}
        for key in rating_keys:
            values = [
                r["ratings"].get(key, 0)
                for r in reviews
                if key in r.get("ratings", {})
            ]
            if values:
                average_ratings[key] = sum(values) / len(values)

        return {
            "total_reviews": len(reviews),
            "average_ratings": average_ratings,
            "trends": trends,
        }

    @staticmethod
    async def get_review_reports(
        salon_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Generate review reports for a period."""
        reviews = await db.performance_reviews.find(
            {
                "salon_id": ObjectId(salon_id),
                "review_date": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }
        ).to_list(None)

        # Group by staff
        staff_reviews = {}
        for review in reviews:
            staff_id = str(review["staff_id"])
            if staff_id not in staff_reviews:
                staff_reviews[staff_id] = []
            staff_reviews[staff_id].append(review)

        # Calculate statistics
        report = {
            "period_start": start_date,
            "period_end": end_date,
            "total_reviews": len(reviews),
            "staff_reviewed": len(staff_reviews),
            "average_ratings": {},
            "staff_details": {},
        }

        # Calculate overall averages
        all_ratings = {}
        for review in reviews:
            for key, value in review.get("ratings", {}).items():
                if key not in all_ratings:
                    all_ratings[key] = []
                all_ratings[key].append(value)

        for key, values in all_ratings.items():
            report["average_ratings"][key] = sum(values) / len(values)

        # Get staff details
        for staff_id, staff_reviews_list in staff_reviews.items():
            staff = await db.stylists.find_one({"_id": ObjectId(staff_id)})
            staff_name = staff.get("name", "Unknown") if staff else "Unknown"

            staff_avg_ratings = {}
            for review in staff_reviews_list:
                for key, value in review.get("ratings", {}).items():
                    if key not in staff_avg_ratings:
                        staff_avg_ratings[key] = []
                    staff_avg_ratings[key].append(value)

            for key in staff_avg_ratings:
                staff_avg_ratings[key] = (
                    sum(staff_avg_ratings[key]) / len(staff_avg_ratings[key])
                )

            report["staff_details"][staff_id] = {
                "staff_name": staff_name,
                "review_count": len(staff_reviews_list),
                "average_ratings": staff_avg_ratings,
            }

        return report

    @staticmethod
    async def update_review_goals(
        review_id: str,
        goals: List[Dict[str, Any]],
        salon_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Update goals for a review."""
        review = await db.performance_reviews.find_one_and_update(
            {
                "_id": ObjectId(review_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$set": {
                    "goals": goals,
                    "updated_at": datetime.utcnow(),
                }
            },
            return_document=True,
        )
        return review

    @staticmethod
    async def get_pending_reviews(
        salon_id: str,
        reviewer_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get pending reviews for a salon or reviewer."""
        query = {
            "salon_id": ObjectId(salon_id),
            "status": "scheduled",
        }
        if reviewer_id:
            query["reviewer_id"] = ObjectId(reviewer_id)

        reviews = await db.scheduled_reviews.find(query).sort(
            "scheduled_date", 1
        ).to_list(None)
        return reviews

    @staticmethod
    async def create_review_template(
        salon_id: str,
        template_name: str,
        criteria: List[Dict[str, Any]],
        created_by: str,
    ) -> Dict[str, Any]:
        """Create a customizable review template."""
        template = {
            "salon_id": ObjectId(salon_id),
            "template_name": template_name,
            "criteria": criteria,
            "created_by": ObjectId(created_by),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.review_templates.insert_one(template)
        template["_id"] = result.inserted_id
        return template

    @staticmethod
    async def get_review_templates(salon_id: str) -> List[Dict[str, Any]]:
        """Get all review templates for a salon."""
        templates = await db.review_templates.find(
            {
                "salon_id": ObjectId(salon_id),
                "is_active": True,
            }
        ).to_list(None)
        return templates

    @staticmethod
    async def send_review_reminder(
        scheduled_review_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Send reminder notification for scheduled review."""
        review = await db.scheduled_reviews.find_one(
            {
                "_id": ObjectId(scheduled_review_id),
                "salon_id": ObjectId(salon_id),
            }
        )

        if not review:
            raise ValueError("Scheduled review not found")

        # Create notification
        notification = {
            "salon_id": ObjectId(salon_id),
            "recipient_id": review["reviewer_id"],
            "type": "review_reminder",
            "title": "Performance Review Reminder",
            "message": f"You have a scheduled performance review",
            "related_id": ObjectId(scheduled_review_id),
            "is_read": False,
            "created_at": datetime.utcnow(),
        }
        await db.notifications.insert_one(notification)

        # Mark reminder as sent
        await db.scheduled_reviews.update_one(
            {"_id": ObjectId(scheduled_review_id)},
            {"$set": {"reminder_sent": True, "reminder_sent_at": datetime.utcnow()}},
        )

        return review

    @staticmethod
    async def send_review_reminders_batch(salon_id: str) -> int:
        """Send reminders for reviews due in next 3 days."""
        now = datetime.utcnow()
        three_days_later = now + timedelta(days=3)

        reviews = await db.scheduled_reviews.find(
            {
                "salon_id": ObjectId(salon_id),
                "status": "scheduled",
                "scheduled_date": {"$gte": now, "$lte": three_days_later},
                "reminder_sent": {"$ne": True},
            }
        ).to_list(None)

        count = 0
        for review in reviews:
            try:
                await StaffReviewService.send_review_reminder(
                    str(review["_id"]), salon_id
                )
                count += 1
            except Exception as e:
                print(f"Failed to send reminder: {e}")

        return count

    @staticmethod
    async def get_review_criteria_options(salon_id: str) -> Dict[str, Any]:
        """Get available review criteria for a salon."""
        # Default criteria
        default_criteria = {
            "punctuality": {"label": "Punctuality", "description": "Arrives on time and meets deadlines"},
            "quality": {"label": "Quality of Work", "description": "Quality of services provided"},
            "teamwork": {"label": "Teamwork", "description": "Collaboration with team members"},
            "communication": {"label": "Communication", "description": "Clarity and effectiveness of communication"},
            "reliability": {"label": "Reliability", "description": "Dependability and consistency"},
            "customer_service": {"label": "Customer Service", "description": "Client satisfaction and care"},
            "initiative": {"label": "Initiative", "description": "Takes on responsibilities proactively"},
            "professionalism": {"label": "Professionalism", "description": "Maintains professional standards"},
        }

        # Check if salon has custom criteria
        salon_settings = await db.salon_settings.find_one(
            {"salon_id": ObjectId(salon_id)}
        )

        if salon_settings and "review_criteria" in salon_settings:
            return salon_settings["review_criteria"]

        return default_criteria

    @staticmethod
    async def update_review_criteria(
        salon_id: str,
        criteria: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update review criteria for a salon."""
        result = await db.salon_settings.update_one(
            {"salon_id": ObjectId(salon_id)},
            {"$set": {"review_criteria": criteria}},
            upsert=True,
        )
        return criteria

    @staticmethod
    async def get_review_improvement_tracking(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Track improvement goals across reviews."""
        reviews = await db.performance_reviews.find(
            {
                "staff_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            }
        ).sort("review_date", 1).to_list(None)

        if not reviews:
            return {"total_reviews": 0, "goals_tracking": []}

        # Track goals across reviews
        goals_tracking = []
        for review in reviews:
            for goal in review.get("goals", []):
                goals_tracking.append({
                    "goal": goal.get("goal"),
                    "target_date": goal.get("target_date"),
                    "status": goal.get("status", "pending"),
                    "review_date": review["review_date"],
                })

        return {
            "total_reviews": len(reviews),
            "goals_tracking": goals_tracking,
            "latest_review": reviews[-1] if reviews else None,
        }
