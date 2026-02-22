"""
Commission Management Service - Handles tiered commissions and payouts
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

from app.database import Database
from app.api.exceptions import NotFoundException, BadRequestException

logger = logging.getLogger(__name__)


class CommissionManagementService:
    """Service for managing staff commissions"""

    @staticmethod
    def get_staff_commissions(
        tenant_id: str,
        staff_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        status: Optional[str] = None
    ) -> List[Dict]:
        """Get commission history for a staff member"""
        db = Database.get_db()
        
        query = {
            "tenant_id": tenant_id,
            "staff_id": staff_id
        }
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["pay_period_start"] = date_query
        
        if status:
            query["payout_status"] = status
        
        commissions = list(db.commission_history.find(query).sort("created_at", -1))
        return commissions

    @staticmethod
    def get_commission_summary(
        tenant_id: str,
        staff_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """Get commission summary for a staff member"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Get all commissions in period
        commissions = list(db.commission_history.find({
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }))
        
        # Calculate totals
        total_commission = sum(c.get("commission_amount", 0) for c in commissions)
        pending_commission = sum(
            c.get("commission_amount", 0) 
            for c in commissions 
            if c.get("payout_status") == "pending"
        )
        paid_commission = sum(
            c.get("commission_amount", 0) 
            for c in commissions 
            if c.get("payout_status") == "paid"
        )
        
        # Get by source type
        by_source = {}
        for commission in commissions:
            source_type = commission.get("source_type", "unknown")
            if source_type not in by_source:
                by_source[source_type] = 0
            by_source[source_type] += commission.get("commission_amount", 0)
        
        return {
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
            "period_start": start_date,
            "period_end": end_date,
            "total_commission": total_commission,
            "pending_commission": pending_commission,
            "paid_commission": paid_commission,
            "disputed_commission": total_commission - pending_commission - paid_commission,
            "commission_count": len(commissions),
            "by_source": by_source
        }

    @staticmethod
    def record_commission(
        tenant_id: str,
        staff_id: str,
        source_type: str,
        source_id: str,
        source_reference: str,
        base_amount: float,
        commission_rate: float,
        pay_period_start: datetime,
        pay_period_end: datetime,
        tier_applied: Optional[int] = None,
        adjustment_amount: Optional[float] = None,
        adjustment_reason: Optional[str] = None
    ) -> Dict:
        """Record a commission entry"""
        db = Database.get_db()
        
        # Get staff
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Calculate commission
        commission_amount = base_amount * (commission_rate / 100)
        if adjustment_amount:
            commission_amount += adjustment_amount
        
        commission = {
            "tenant_id": tenant_id,
            "staff_id": staff_id,
            "staff_name": staff.get("name"),
            "source_type": source_type,
            "source_id": source_id,
            "source_reference": source_reference,
            "base_amount": base_amount,
            "commission_rate": commission_rate,
            "commission_amount": commission_amount,
            "tier_applied": tier_applied,
            "payout_status": "pending",
            "payout_date": None,
            "payout_method": None,
            "adjustment_amount": adjustment_amount,
            "adjustment_reason": adjustment_reason,
            "pay_period_start": pay_period_start,
            "pay_period_end": pay_period_end,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.commission_history.insert_one(commission)
        commission["_id"] = result.inserted_id
        return commission

    @staticmethod
    def adjust_commission(
        tenant_id: str,
        commission_id: str,
        adjustment_amount: float,
        adjustment_reason: str
    ) -> Dict:
        """Adjust a commission amount"""
        db = Database.get_db()
        
        commission = db.commission_history.find_one({
            "_id": ObjectId(commission_id),
            "tenant_id": tenant_id
        })
        
        if not commission:
            raise NotFoundException("Commission not found")
        
        # Update commission amount
        new_amount = commission.get("commission_amount", 0) + adjustment_amount
        
        db.commission_history.update_one(
            {"_id": ObjectId(commission_id)},
            {
                "$set": {
                    "commission_amount": new_amount,
                    "adjustment_amount": adjustment_amount,
                    "adjustment_reason": adjustment_reason,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return db.commission_history.find_one({"_id": ObjectId(commission_id)})

    @staticmethod
    def process_commission_payout(
        tenant_id: str,
        commission_id: str,
        payout_method: str,
        notes: Optional[str] = None
    ) -> Dict:
        """Process a commission payout"""
        db = Database.get_db()
        
        commission = db.commission_history.find_one({
            "_id": ObjectId(commission_id),
            "tenant_id": tenant_id
        })
        
        if not commission:
            raise NotFoundException("Commission not found")
        
        if commission.get("payout_status") != "pending":
            raise BadRequestException("Only pending commissions can be paid")
        
        db.commission_history.update_one(
            {"_id": ObjectId(commission_id)},
            {
                "$set": {
                    "payout_status": "paid",
                    "payout_date": datetime.utcnow(),
                    "payout_method": payout_method,
                    "notes": notes,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return db.commission_history.find_one({"_id": ObjectId(commission_id)})

    @staticmethod
    def dispute_commission(
        tenant_id: str,
        commission_id: str,
        dispute_reason: str
    ) -> Dict:
        """Mark a commission as disputed"""
        db = Database.get_db()
        
        commission = db.commission_history.find_one({
            "_id": ObjectId(commission_id),
            "tenant_id": tenant_id
        })
        
        if not commission:
            raise NotFoundException("Commission not found")
        
        db.commission_history.update_one(
            {"_id": ObjectId(commission_id)},
            {
                "$set": {
                    "payout_status": "disputed",
                    "dispute_reason": dispute_reason,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return db.commission_history.find_one({"_id": ObjectId(commission_id)})

    @staticmethod
    def get_commission_tiers(
        tenant_id: str,
        staff_id: str
    ) -> List[Dict]:
        """Get commission tiers for a staff member"""
        db = Database.get_db()
        
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        tiers = staff.get("commission_tiers", [])
        return tiers

    @staticmethod
    def set_commission_tiers(
        tenant_id: str,
        staff_id: str,
        tiers: List[Dict]
    ) -> Dict:
        """Set commission tiers for a staff member"""
        db = Database.get_db()
        
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        # Validate tiers
        for tier in tiers:
            if "min_revenue" not in tier or "commission_rate" not in tier:
                raise BadRequestException("Each tier must have min_revenue and commission_rate")
        
        # Sort tiers by min_revenue
        sorted_tiers = sorted(tiers, key=lambda x: x["min_revenue"])
        
        db.stylists.update_one(
            {"_id": ObjectId(staff_id)},
            {
                "$set": {
                    "commission_tiers": sorted_tiers,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        
        return db.stylists.find_one({"_id": ObjectId(staff_id)})

    @staticmethod
    def calculate_tiered_commission(
        tenant_id: str,
        staff_id: str,
        revenue: float
    ) -> Dict:
        """Calculate commission based on tiered rates"""
        db = Database.get_db()
        
        staff = db.stylists.find_one({
            "_id": ObjectId(staff_id),
            "tenant_id": tenant_id
        })
        
        if not staff:
            raise NotFoundException("Staff member not found")
        
        tiers = staff.get("commission_tiers", [])
        
        if not tiers:
            # Use default commission rate
            default_rate = staff.get("commission_rate", 0)
            return {
                "revenue": revenue,
                "commission_rate": default_rate,
                "commission_amount": revenue * (default_rate / 100),
                "tier_applied": None
            }
        
        # Find applicable tier
        applicable_tier = None
        for i, tier in enumerate(sorted(tiers, key=lambda x: x["min_revenue"], reverse=True)):
            if revenue >= tier.get("min_revenue", 0):
                applicable_tier = tier
                tier_index = i
                break
        
        if not applicable_tier:
            applicable_tier = tiers[0]
            tier_index = 0
        
        commission_rate = applicable_tier.get("commission_rate", 0)
        commission_amount = revenue * (commission_rate / 100)
        
        return {
            "revenue": revenue,
            "commission_rate": commission_rate,
            "commission_amount": commission_amount,
            "tier_applied": tier_index,
            "tier_details": applicable_tier
        }

    @staticmethod
    def get_commission_report(
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        staff_id: Optional[str] = None
    ) -> Dict:
        """Generate commission report"""
        db = Database.get_db()
        
        # Default date range
        if not end_date:
            end_date = datetime.utcnow()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        query = {
            "tenant_id": tenant_id,
            "created_at": {"$gte": start_date, "$lte": end_date}
        }
        
        if staff_id:
            query["staff_id"] = staff_id
        
        commissions = list(db.commission_history.find(query))
        
        # Calculate totals
        total_commission = sum(c.get("commission_amount", 0) for c in commissions)
        pending = sum(
            c.get("commission_amount", 0) 
            for c in commissions 
            if c.get("payout_status") == "pending"
        )
        paid = sum(
            c.get("commission_amount", 0) 
            for c in commissions 
            if c.get("payout_status") == "paid"
        )
        disputed = sum(
            c.get("commission_amount", 0) 
            for c in commissions 
            if c.get("payout_status") == "disputed"
        )
        
        # Group by staff
        by_staff = {}
        for commission in commissions:
            staff_id_key = commission.get("staff_id")
            if staff_id_key not in by_staff:
                by_staff[staff_id_key] = {
                    "staff_name": commission.get("staff_name"),
                    "total": 0,
                    "pending": 0,
                    "paid": 0,
                    "disputed": 0,
                    "count": 0
                }
            
            by_staff[staff_id_key]["total"] += commission.get("commission_amount", 0)
            by_staff[staff_id_key]["count"] += 1
            
            status = commission.get("payout_status")
            if status == "pending":
                by_staff[staff_id_key]["pending"] += commission.get("commission_amount", 0)
            elif status == "paid":
                by_staff[staff_id_key]["paid"] += commission.get("commission_amount", 0)
            elif status == "disputed":
                by_staff[staff_id_key]["disputed"] += commission.get("commission_amount", 0)
        
        return {
            "period_start": start_date,
            "period_end": end_date,
            "total_commission": total_commission,
            "pending_commission": pending,
            "paid_commission": paid,
            "disputed_commission": disputed,
            "commission_count": len(commissions),
            "by_staff": by_staff
        }


# Singleton instance
commission_management_service = CommissionManagementService()
