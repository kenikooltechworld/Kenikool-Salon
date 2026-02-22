from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from bson import ObjectId
from pymongo import DESCENDING
from app.database import db


class LeaderboardService:
    """Service for managing staff leaderboards and gamification."""

    @staticmethod
    async def get_leaderboard(
        salon_id: str,
        category: str = "revenue",
        period: str = "month",
        limit: int = 50,
    ) -> List[Dict[str, Any]]:
        """Get leaderboard rankings for a category and period."""
        # Calculate date range
        now = datetime.utcnow()
        if period == "week":
            start_date = now - timedelta(days=7)
        elif period == "month":
            start_date = now - timedelta(days=30)
        elif period == "quarter":
            start_date = now - timedelta(days=90)
        elif period == "year":
            start_date = now - timedelta(days=365)
        else:
            start_date = now - timedelta(days=30)

        leaderboard = []

        if category == "revenue":
            # Get revenue from bookings
            pipeline = [
                {
                    "$match": {
                        "salon_id": ObjectId(salon_id),
                        "created_at": {"$gte": start_date},
                    }
                },
                {
                    "$group": {
                        "_id": "$staff_id",
                        "total_revenue": {"$sum": "$total_price"},
                        "booking_count": {"$sum": 1},
                    }
                },
                {"$sort": {"total_revenue": DESCENDING}},
                {"$limit": limit},
            ]
            results = await db.bookings.aggregate(pipeline).to_list(None)
            for idx, result in enumerate(results):
                staff = await db.stylists.find_one({"_id": result["_id"]})
                leaderboard.append({
                    "rank": idx + 1,
                    "staff_id": str(result["_id"]),
                    "staff_name": staff.get("name", "Unknown") if staff else "Unknown",
                    "value": result["total_revenue"],
                    "bookings": result["booking_count"],
                })

        elif category == "bookings":
            # Get booking count
            pipeline = [
                {
                    "$match": {
                        "salon_id": ObjectId(salon_id),
                        "created_at": {"$gte": start_date},
                    }
                },
                {
                    "$group": {
                        "_id": "$staff_id",
                        "booking_count": {"$sum": 1},
                        "total_revenue": {"$sum": "$total_price"},
                    }
                },
                {"$sort": {"booking_count": DESCENDING}},
                {"$limit": limit},
            ]
            results = await db.bookings.aggregate(pipeline).to_list(None)
            for idx, result in enumerate(results):
                staff = await db.stylists.find_one({"_id": result["_id"]})
                leaderboard.append({
                    "rank": idx + 1,
                    "staff_id": str(result["_id"]),
                    "staff_name": staff.get("name", "Unknown") if staff else "Unknown",
                    "value": result["booking_count"],
                    "revenue": result["total_revenue"],
                })

        elif category == "ratings":
            # Get average rating
            pipeline = [
                {
                    "$match": {
                        "salon_id": ObjectId(salon_id),
                        "created_at": {"$gte": start_date},
                    }
                },
                {
                    "$group": {
                        "_id": "$staff_id",
                        "avg_rating": {"$avg": "$rating"},
                        "review_count": {"$sum": 1},
                    }
                },
                {"$sort": {"avg_rating": DESCENDING}},
                {"$limit": limit},
            ]
            results = await db.reviews.aggregate(pipeline).to_list(None)
            for idx, result in enumerate(results):
                staff = await db.stylists.find_one({"_id": result["_id"]})
                leaderboard.append({
                    "rank": idx + 1,
                    "staff_id": str(result["_id"]),
                    "staff_name": staff.get("name", "Unknown") if staff else "Unknown",
                    "value": round(result["avg_rating"], 2),
                    "reviews": result["review_count"],
                })

        elif category == "rebookings":
            # Get rebooking rate
            pipeline = [
                {
                    "$match": {
                        "salon_id": ObjectId(salon_id),
                        "created_at": {"$gte": start_date},
                    }
                },
                {
                    "$group": {
                        "_id": "$staff_id",
                        "total_bookings": {"$sum": 1},
                        "rebookings": {
                            "$sum": {
                                "$cond": [{"$eq": ["$is_rebooking", True]}, 1, 0]
                            }
                        },
                    }
                },
                {
                    "$project": {
                        "rebooking_rate": {
                            "$cond": [
                                {"$eq": ["$total_bookings", 0]},
                                0,
                                {
                                    "$multiply": [
                                        {"$divide": ["$rebookings", "$total_bookings"]},
                                        100,
                                    ]
                                },
                            ]
                        },
                        "rebookings": 1,
                        "total_bookings": 1,
                    }
                },
                {"$sort": {"rebooking_rate": DESCENDING}},
                {"$limit": limit},
            ]
            results = await db.bookings.aggregate(pipeline).to_list(None)
            for idx, result in enumerate(results):
                staff = await db.stylists.find_one({"_id": result["_id"]})
                leaderboard.append({
                    "rank": idx + 1,
                    "staff_id": str(result["_id"]),
                    "staff_name": staff.get("name", "Unknown") if staff else "Unknown",
                    "value": round(result["rebooking_rate"], 2),
                    "rebookings": result["rebookings"],
                    "total_bookings": result["total_bookings"],
                })

        return leaderboard

    @staticmethod
    async def create_achievement(
        staff_id: str,
        achievement_type: str,
        title: str,
        description: str,
        icon_url: Optional[str] = None,
        salon_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an achievement record."""
        achievement = {
            "staff_id": ObjectId(staff_id),
            "achievement_type": achievement_type,
            "title": title,
            "description": description,
            "icon_url": icon_url,
            "salon_id": ObjectId(salon_id) if salon_id else None,
            "earned_at": datetime.utcnow(),
            "created_at": datetime.utcnow(),
        }
        result = await db.achievements.insert_one(achievement)
        achievement["_id"] = result.inserted_id
        return achievement

    @staticmethod
    async def get_staff_achievements(
        staff_id: str,
        salon_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get all achievements for a staff member."""
        query = {"staff_id": ObjectId(staff_id)}
        if salon_id:
            query["salon_id"] = ObjectId(salon_id)

        achievements = await db.achievements.find(query).sort(
            "earned_at", DESCENDING
        ).to_list(None)
        return achievements

    @staticmethod
    async def check_and_award_achievements(
        staff_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Check and award achievements based on staff performance."""
        awarded = []

        # Get staff stats
        staff = await db.stylists.find_one({"_id": ObjectId(staff_id)})
        if not staff:
            return awarded

        # Check for existing achievements
        existing = await db.achievements.find(
            {"staff_id": ObjectId(staff_id)}
        ).to_list(None)
        existing_types = {a["achievement_type"] for a in existing}

        # Check booking milestones
        booking_count = await db.bookings.count_documents(
            {"staff_id": ObjectId(staff_id)}
        )

        milestones = [
            (10, "10_bookings", "10 Bookings", "Completed 10 bookings"),
            (50, "50_bookings", "50 Bookings", "Completed 50 bookings"),
            (100, "100_bookings", "100 Bookings", "Completed 100 bookings"),
            (250, "250_bookings", "250 Bookings", "Completed 250 bookings"),
            (500, "500_bookings", "500 Bookings", "Completed 500 bookings"),
        ]

        for threshold, achievement_type, title, description in milestones:
            if (
                booking_count >= threshold
                and achievement_type not in existing_types
            ):
                achievement = await LeaderboardService.create_achievement(
                    staff_id=staff_id,
                    achievement_type=achievement_type,
                    title=title,
                    description=description,
                    salon_id=salon_id,
                )
                awarded.append(achievement)

        # Check rating achievements
        avg_rating = await db.reviews.aggregate(
            [
                {"$match": {"staff_id": ObjectId(staff_id)}},
                {"$group": {"_id": None, "avg_rating": {"$avg": "$rating"}}},
            ]
        ).to_list(None)

        if avg_rating:
            rating = avg_rating[0]["avg_rating"]
            if rating >= 5.0 and "perfect_rating" not in existing_types:
                achievement = await LeaderboardService.create_achievement(
                    staff_id=staff_id,
                    achievement_type="perfect_rating",
                    title="Perfect Rating",
                    description="Achieved a 5-star average rating",
                    salon_id=salon_id,
                )
                awarded.append(achievement)
            elif rating >= 4.8 and "excellent_rating" not in existing_types:
                achievement = await LeaderboardService.create_achievement(
                    staff_id=staff_id,
                    achievement_type="excellent_rating",
                    title="Excellent Rating",
                    description="Achieved a 4.8+ star average rating",
                    salon_id=salon_id,
                )
                awarded.append(achievement)

        return awarded

    @staticmethod
    async def create_challenge(
        salon_id: str,
        title: str,
        description: str,
        challenge_type: str,
        target_value: float,
        reward_points: int,
        start_date: datetime,
        end_date: datetime,
        created_by: str,
    ) -> Dict[str, Any]:
        """Create a custom challenge."""
        challenge = {
            "salon_id": ObjectId(salon_id),
            "title": title,
            "description": description,
            "challenge_type": challenge_type,
            "target_value": target_value,
            "reward_points": reward_points,
            "start_date": start_date,
            "end_date": end_date,
            "created_by": ObjectId(created_by),
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
        }
        result = await db.challenges.insert_one(challenge)
        challenge["_id"] = result.inserted_id
        return challenge

    @staticmethod
    async def get_active_challenges(salon_id: str) -> List[Dict[str, Any]]:
        """Get all active challenges for a salon."""
        now = datetime.utcnow()
        challenges = await db.challenges.find(
            {
                "salon_id": ObjectId(salon_id),
                "is_active": True,
                "start_date": {"$lte": now},
                "end_date": {"$gte": now},
            }
        ).sort("end_date", 1).to_list(None)
        return challenges

    @staticmethod
    async def track_challenge_progress(
        challenge_id: str,
        staff_id: str,
        current_value: float,
    ) -> Dict[str, Any]:
        """Track progress on a challenge."""
        progress = {
            "challenge_id": ObjectId(challenge_id),
            "staff_id": ObjectId(staff_id),
            "current_value": current_value,
            "updated_at": datetime.utcnow(),
        }

        result = await db.challenge_progress.update_one(
            {
                "challenge_id": ObjectId(challenge_id),
                "staff_id": ObjectId(staff_id),
            },
            {"$set": progress},
            upsert=True,
        )

        return await db.challenge_progress.find_one(
            {
                "challenge_id": ObjectId(challenge_id),
                "staff_id": ObjectId(staff_id),
            }
        )

    @staticmethod
    async def get_challenge_progress(
        challenge_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get progress for all staff on a challenge."""
        challenge = await db.challenges.find_one(
            {"_id": ObjectId(challenge_id), "salon_id": ObjectId(salon_id)}
        )

        if not challenge:
            return []

        progress_list = await db.challenge_progress.find(
            {"challenge_id": ObjectId(challenge_id)}
        ).sort("current_value", DESCENDING).to_list(None)

        results = []
        for idx, progress in enumerate(progress_list):
            staff = await db.stylists.find_one({"_id": progress["staff_id"]})
            completion_percent = (
                (progress["current_value"] / challenge["target_value"]) * 100
                if challenge["target_value"] > 0
                else 0
            )
            results.append({
                "rank": idx + 1,
                "staff_id": str(progress["staff_id"]),
                "staff_name": staff.get("name", "Unknown") if staff else "Unknown",
                "current_value": progress["current_value"],
                "target_value": challenge["target_value"],
                "completion_percent": min(completion_percent, 100),
                "completed": progress["current_value"] >= challenge["target_value"],
            })

        return results

    @staticmethod
    async def get_leaderboard_settings(salon_id: str) -> Dict[str, Any]:
        """Get leaderboard settings for a salon."""
        settings = await db.salon_settings.find_one(
            {"salon_id": ObjectId(salon_id)}
        )

        if not settings:
            return {
                "leaderboard_enabled": True,
                "show_revenue": True,
                "show_bookings": True,
                "show_ratings": True,
                "show_rebookings": True,
            }

        return settings.get("leaderboard_settings", {})

    @staticmethod
    async def update_leaderboard_settings(
        salon_id: str,
        settings: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Update leaderboard settings for a salon."""
        result = await db.salon_settings.update_one(
            {"salon_id": ObjectId(salon_id)},
            {"$set": {"leaderboard_settings": settings}},
            upsert=True,
        )

        return await db.salon_settings.find_one(
            {"salon_id": ObjectId(salon_id)}
        )
