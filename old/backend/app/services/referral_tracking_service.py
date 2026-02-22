from datetime import datetime
from typing import List, Optional, Dict, Any
from bson import ObjectId
from app.database import db


class ReferralTrackingService:
    """Service for tracking staff referrals and referral bonuses."""

    @staticmethod
    async def record_client_referral(
        client_id: str,
        referring_staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Record a client referral from a staff member."""
        referral = {
            "client_id": ObjectId(client_id),
            "referring_staff_id": ObjectId(referring_staff_id),
            "referred_at": datetime.utcnow(),
        }

        result = await db.clients.update_one(
            {
                "_id": ObjectId(client_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"referral_source": referral}},
        )

        if result.matched_count == 0:
            raise ValueError("Client not found")

        # Track referral for staff
        await db.stylists.update_one(
            {
                "_id": ObjectId(referring_staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$push": {
                    "client_referrals": {
                        "client_id": ObjectId(client_id),
                        "referred_at": datetime.utcnow(),
                    }
                }
            },
        )

        return referral

    @staticmethod
    async def record_staff_referral(
        referred_staff_id: str,
        referring_staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Record a staff member referral."""
        referral = {
            "referred_staff_id": ObjectId(referred_staff_id),
            "referring_staff_id": ObjectId(referring_staff_id),
            "referred_at": datetime.utcnow(),
        }

        result = await db.stylists.update_one(
            {
                "_id": ObjectId(referred_staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"$set": {"staff_referral_source": referral}},
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        # Track referral for referring staff
        await db.stylists.update_one(
            {
                "_id": ObjectId(referring_staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$push": {
                    "staff_referrals": {
                        "referred_staff_id": ObjectId(referred_staff_id),
                        "referred_at": datetime.utcnow(),
                    }
                }
            },
        )

        return referral

    @staticmethod
    async def get_staff_referrals(
        staff_id: str,
        salon_id: str,
    ) -> Dict[str, Any]:
        """Get all referrals made by a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "client_referrals": 1,
                "staff_referrals": 1,
            },
        )

        if not staff:
            raise ValueError("Staff member not found")

        client_referrals = staff.get("client_referrals", [])
        staff_referrals = staff.get("staff_referrals", [])

        return {
            "staff_id": staff_id,
            "client_referrals": client_referrals,
            "client_referral_count": len(client_referrals),
            "staff_referrals": staff_referrals,
            "staff_referral_count": len(staff_referrals),
        }

    @staticmethod
    async def calculate_referral_revenue(
        staff_id: str,
        salon_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Calculate revenue from referred clients."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"client_referrals": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        client_referrals = staff.get("client_referrals", [])
        referred_client_ids = [ref["client_id"] for ref in client_referrals]

        # Get bookings from referred clients
        match_query = {
            "salon_id": ObjectId(salon_id),
            "client_id": {"$in": referred_client_ids},
            "status": "completed",
        }

        if start_date and end_date:
            match_query["date"] = {
                "$gte": start_date.date(),
                "$lte": end_date.date(),
            }

        bookings = await db.bookings.find(match_query).to_list(None)

        total_revenue = sum(b.get("total_price", 0) for b in bookings)
        booking_count = len(bookings)

        return {
            "staff_id": staff_id,
            "referred_clients": len(referred_client_ids),
            "bookings_from_referrals": booking_count,
            "revenue_from_referrals": total_revenue,
            "average_booking_value": (
                total_revenue / booking_count if booking_count > 0 else 0
            ),
        }

    @staticmethod
    async def get_referral_leaderboard(
        salon_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """Get referral leaderboard."""
        staff_list = await db.stylists.find(
            {"salon_id": ObjectId(salon_id)},
            {"_id": 1, "name": 1, "client_referrals": 1},
        ).to_list(None)

        leaderboard = []

        for staff in staff_list:
            referrals = await ReferralTrackingService.calculate_referral_revenue(
                str(staff["_id"]), salon_id, start_date, end_date
            )

            leaderboard.append(
                {
                    "staff_id": str(staff["_id"]),
                    "staff_name": staff.get("name"),
                    "referral_count": referrals["referred_clients"],
                    "revenue": referrals["revenue_from_referrals"],
                    "bookings": referrals["bookings_from_referrals"],
                }
            )

        # Sort by revenue
        leaderboard.sort(key=lambda x: x["revenue"], reverse=True)
        return leaderboard[:limit]

    @staticmethod
    async def add_referral_bonus(
        staff_id: str,
        salon_id: str,
        bonus_amount: float,
        reason: str,
    ) -> Dict[str, Any]:
        """Add referral bonus to staff member."""
        bonus = {
            "amount": bonus_amount,
            "reason": reason,
            "added_at": datetime.utcnow(),
        }

        result = await db.stylists.update_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {
                "$push": {"referral_bonuses": bonus},
            },
        )

        if result.matched_count == 0:
            raise ValueError("Staff member not found")

        return bonus

    @staticmethod
    async def get_referral_bonuses(
        staff_id: str,
        salon_id: str,
    ) -> List[Dict[str, Any]]:
        """Get all referral bonuses for a staff member."""
        staff = await db.stylists.find_one(
            {
                "_id": ObjectId(staff_id),
                "salon_id": ObjectId(salon_id),
            },
            {"referral_bonuses": 1},
        )

        if not staff:
            raise ValueError("Staff member not found")

        bonuses = staff.get("referral_bonuses", [])
        total_bonuses = sum(b.get("amount", 0) for b in bonuses)

        return {
            "staff_id": staff_id,
            "bonuses": bonuses,
            "total_bonuses": total_bonuses,
            "bonus_count": len(bonuses),
        }

    @staticmethod
    async def get_referral_report(
        salon_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """Get comprehensive referral report."""
        staff_list = await db.stylists.find(
            {"salon_id": ObjectId(salon_id)},
            {"_id": 1, "name": 1, "client_referrals": 1},
        ).to_list(None)

        total_referrals = 0
        total_revenue = 0
        total_bonuses = 0
        staff_details = []

        for staff in staff_list:
            referrals = await ReferralTrackingService.calculate_referral_revenue(
                str(staff["_id"]), salon_id, start_date, end_date
            )
            bonuses = await ReferralTrackingService.get_referral_bonuses(
                str(staff["_id"]), salon_id
            )

            total_referrals += referrals["referred_clients"]
            total_revenue += referrals["revenue_from_referrals"]
            total_bonuses += bonuses["total_bonuses"]

            if referrals["referred_clients"] > 0:
                staff_details.append(
                    {
                        "staff_id": str(staff["_id"]),
                        "staff_name": staff.get("name"),
                        "referral_count": referrals["referred_clients"],
                        "revenue": referrals["revenue_from_referrals"],
                        "bonuses": bonuses["total_bonuses"],
                    }
                )

        return {
            "period": {
                "start": start_date.date() if start_date else None,
                "end": end_date.date() if end_date else None,
            },
            "total_referrals": total_referrals,
            "total_revenue": total_revenue,
            "total_bonuses": total_bonuses,
            "staff_count": len(staff_details),
            "staff_details": sorted(
                staff_details, key=lambda x: x["revenue"], reverse=True
            ),
        }
