"""
Pricing engine service - Dynamic pricing logic
"""
from bson import ObjectId
from datetime import datetime, time
from typing import Dict, List, Optional
import logging

from app.database import Database
from app.api.exceptions import NotFoundException

logger = logging.getLogger(__name__)


class PricingEngineService:
    """Service for dynamic pricing calculations"""
    
    @staticmethod
    def create_pricing_rule(
        tenant_id: str,
        name: str,
        rule_type: str,
        multiplier: float,
        service_ids: List[str] = None,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        days_of_week: List[int] = None,
        min_bookings: Optional[int] = None,
        max_bookings: Optional[int] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        enabled: bool = True,
        priority: int = 0
    ) -> Dict:
        """
        Create a new pricing rule
        
        Returns:
            Dict with created rule data
        """
        db = Database.get_db()
        
        rule_data = {
            "tenant_id": tenant_id,
            "name": name,
            "rule_type": rule_type,
            "service_ids": service_ids or [],
            "multiplier": multiplier,
            "start_time": start_time,
            "end_time": end_time,
            "days_of_week": days_of_week or [],
            "min_bookings": min_bookings,
            "max_bookings": max_bookings,
            "start_date": start_date,
            "end_date": end_date,
            "enabled": enabled,
            "priority": priority,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = db.pricing_rules.insert_one(rule_data)
        rule_id = str(result.inserted_id)
        
        logger.info(f"Pricing rule created: {rule_id} for tenant: {tenant_id}")
        
        rule_doc = db.pricing_rules.find_one({"_id": ObjectId(rule_id)})
        return PricingEngineService._format_rule_response(rule_doc)
    
    @staticmethod
    def get_pricing_rules(tenant_id: str) -> List[Dict]:
        """
        Get all pricing rules for tenant
        
        Returns:
            List of pricing rule dicts
        """
        db = Database.get_db()
        
        rules = list(db.pricing_rules.find({"tenant_id": tenant_id}).sort("priority", -1))
        
        return [PricingEngineService._format_rule_response(r) for r in rules]
    
    @staticmethod
    def update_pricing_rule(
        rule_id: str,
        tenant_id: str,
        **updates
    ) -> Dict:
        """
        Update a pricing rule
        
        Returns:
            Dict with updated rule data
        """
        db = Database.get_db()
        
        # Check rule exists and belongs to tenant
        rule_doc = db.pricing_rules.find_one({
            "_id": ObjectId(rule_id),
            "tenant_id": tenant_id
        })
        
        if rule_doc is None:
            raise NotFoundException("Pricing rule not found")
        
        # Build update data
        update_data = {"updated_at": datetime.utcnow()}
        
        for key, value in updates.items():
            if value is not None:
                update_data[key] = value
        
        # Update rule
        db.pricing_rules.update_one(
            {"_id": ObjectId(rule_id)},
            {"$set": update_data}
        )
        
        logger.info(f"Pricing rule updated: {rule_id}")
        
        rule_doc = db.pricing_rules.find_one({"_id": ObjectId(rule_id)})
        return PricingEngineService._format_rule_response(rule_doc)
    
    @staticmethod
    def delete_pricing_rule(rule_id: str, tenant_id: str) -> None:
        """Delete a pricing rule"""
        db = Database.get_db()
        
        result = db.pricing_rules.delete_one({
            "_id": ObjectId(rule_id),
            "tenant_id": tenant_id
        })
        
        if result.deleted_count == 0:
            raise NotFoundException("Pricing rule not found")
        
        logger.info(f"Pricing rule deleted: {rule_id}")
    
    @staticmethod
    def calculate_price(
        tenant_id: str,
        service_id: str,
        booking_date: str,
        booking_time: str
    ) -> Dict:
        """
        Calculate dynamic price for a service
        
        Args:
            service_id: Service ID
            booking_date: Date in YYYY-MM-DD format
            booking_time: Time in HH:MM format
        
        Returns:
            Dict with price calculation details
        """
        db = Database.get_db()
        
        # Get service base price
        service = db.services.find_one({
            "_id": ObjectId(service_id),
            "tenant_id": tenant_id
        })
        
        if not service:
            raise NotFoundException("Service not found")
        
        base_price = service.get("price", 0.0)
        
        # Parse booking date and time
        booking_dt = datetime.strptime(booking_date, "%Y-%m-%d")
        booking_tm = datetime.strptime(booking_time, "%H:%M").time()
        day_of_week = booking_dt.weekday()  # 0 = Monday, 6 = Sunday
        
        # Get all enabled rules for this tenant
        rules = list(db.pricing_rules.find({
            "tenant_id": tenant_id,
            "enabled": True
        }).sort("priority", -1))
        
        # Apply rules
        applied_rules = []
        total_multiplier = 1.0
        
        for rule in rules:
            # Check if rule applies to this service
            service_ids = rule.get("service_ids", [])
            if service_ids and service_id not in service_ids:
                continue
            
            rule_applies = False
            rule_type = rule.get("rule_type")
            
            # Time-of-day rules
            if rule_type == "time_of_day":
                start_time = rule.get("start_time")
                end_time = rule.get("end_time")
                
                if start_time and end_time:
                    start_tm = datetime.strptime(start_time, "%H:%M").time()
                    end_tm = datetime.strptime(end_time, "%H:%M").time()
                    
                    if start_tm <= booking_tm <= end_tm:
                        rule_applies = True
            
            # Day-of-week rules
            elif rule_type == "day_of_week":
                days_of_week = rule.get("days_of_week", [])
                if day_of_week in days_of_week:
                    rule_applies = True
            
            # Demand-based rules
            elif rule_type == "demand":
                # Count bookings on this date
                bookings_count = db.bookings.count_documents({
                    "tenant_id": tenant_id,
                    "booking_date": booking_dt,
                    "status": {"$in": ["confirmed", "completed"]}
                })
                
                min_bookings = rule.get("min_bookings")
                max_bookings = rule.get("max_bookings")
                
                if min_bookings is not None and max_bookings is not None:
                    if min_bookings <= bookings_count <= max_bookings:
                        rule_applies = True
                elif min_bookings is not None:
                    if bookings_count >= min_bookings:
                        rule_applies = True
                elif max_bookings is not None:
                    if bookings_count <= max_bookings:
                        rule_applies = True
            
            # Seasonal/date-based rules
            elif rule_type == "seasonal":
                start_date = rule.get("start_date")
                end_date = rule.get("end_date")
                
                if start_date and end_date:
                    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
                    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                    
                    if start_dt <= booking_dt <= end_dt:
                        rule_applies = True
            
            # Apply multiplier if rule matches
            if rule_applies:
                multiplier = rule.get("multiplier", 1.0)
                total_multiplier *= multiplier
                
                applied_rules.append({
                    "rule_id": str(rule["_id"]),
                    "name": rule.get("name"),
                    "rule_type": rule_type,
                    "multiplier": multiplier
                })
        
        # Calculate final price
        final_price = round(base_price * total_multiplier, 2)
        
        return {
            "service_id": service_id,
            "base_price": base_price,
            "final_price": final_price,
            "applied_rules": applied_rules,
            "total_multiplier": round(total_multiplier, 2)
        }
    
    @staticmethod
    def _format_rule_response(rule_doc: Dict) -> Dict:
        """Format pricing rule document for response"""
        return {
            "id": str(rule_doc["_id"]),
            "tenant_id": rule_doc["tenant_id"],
            "name": rule_doc["name"],
            "rule_type": rule_doc["rule_type"],
            "service_ids": rule_doc.get("service_ids", []),
            "multiplier": rule_doc["multiplier"],
            "start_time": rule_doc.get("start_time"),
            "end_time": rule_doc.get("end_time"),
            "days_of_week": rule_doc.get("days_of_week", []),
            "min_bookings": rule_doc.get("min_bookings"),
            "max_bookings": rule_doc.get("max_bookings"),
            "start_date": rule_doc.get("start_date"),
            "end_date": rule_doc.get("end_date"),
            "enabled": rule_doc.get("enabled", True),
            "priority": rule_doc.get("priority", 0),
            "created_at": rule_doc["created_at"],
            "updated_at": rule_doc["updated_at"]
        }


# Singleton instance
pricing_engine_service = PricingEngineService()
