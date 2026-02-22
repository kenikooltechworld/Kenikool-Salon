"""
A/B Testing Service for campaigns
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from bson import ObjectId
from pymongo import ASCENDING
from app.database import Database
import random


class ABTestService:
    """Service for managing A/B tests"""

    @staticmethod
    def _get_db():
        """Get database instance"""
        return Database.get_db()

    def __init__(self):
        self.collection = ABTestService._get_db().ab_tests
        self._ensure_indexes()

    def _ensure_indexes(self):
        """Create necessary indexes"""
        self.collection.create_index([("tenant_id", ASCENDING)])
        self.collection.create_index([("campaign_id", ASCENDING)])
        self.collection.create_index([("status", ASCENDING)])
        self.collection.create_index([("created_at", ASCENDING)])

    async def create_ab_test(
        self,
        campaign_id: str,
        tenant_id: str,
        name: str,
        variants: List[Dict[str, Any]],
        traffic_split: Dict[str, float],
        created_by: str = "system"
    ) -> Dict[str, Any]:
        """Create a new A/B test"""
        # Validate traffic split sums to 100
        total_split = sum(traffic_split.values())
        if abs(total_split - 100.0) > 0.01:
            raise ValueError(f"Traffic split must sum to 100%, got {total_split}%")
        
        ab_test = {
            "campaign_id": campaign_id,
            "tenant_id": tenant_id,
            "name": name,
            "status": "draft",
            "variants": variants,
            "traffic_split": traffic_split,
            "winner_variant_id": None,
            "started_at": None,
            "completed_at": None,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await self.collection.insert_one(ab_test)
        ab_test["_id"] = result.inserted_id
        return ab_test

    async def get_ab_test(self, test_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get an A/B test by ID"""
        try:
            test = await self.collection.find_one({
                "_id": ObjectId(test_id),
                "tenant_id": tenant_id
            })
            return test
        except:
            return None

    async def get_ab_test_by_campaign(self, campaign_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get A/B test for a campaign"""
        test = await self.collection.find_one({
            "campaign_id": campaign_id,
            "tenant_id": tenant_id
        })
        return test

    async def start_ab_test(self, test_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Start an A/B test"""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(test_id), "tenant_id": tenant_id, "status": "draft"},
                {
                    "$set": {
                        "status": "running",
                        "started_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            return result
        except:
            return None

    async def stop_ab_test(self, test_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Stop an A/B test"""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(test_id), "tenant_id": tenant_id, "status": "running"},
                {
                    "$set": {
                        "status": "completed",
                        "completed_at": datetime.utcnow(),
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            return result
        except:
            return None

    async def select_winner(
        self,
        test_id: str,
        tenant_id: str,
        winner_variant_id: str
    ) -> Optional[Dict[str, Any]]:
        """Select winning variant"""
        try:
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(test_id), "tenant_id": tenant_id},
                {
                    "$set": {
                        "winner_variant_id": winner_variant_id,
                        "updated_at": datetime.utcnow()
                    }
                },
                return_document=True
            )
            return result
        except:
            return None

    async def update_ab_test(
        self,
        test_id: str,
        tenant_id: str,
        **kwargs
    ) -> Optional[Dict[str, Any]]:
        """Update an A/B test"""
        try:
            kwargs["updated_at"] = datetime.utcnow()
            result = await self.collection.find_one_and_update(
                {"_id": ObjectId(test_id), "tenant_id": tenant_id},
                {"$set": kwargs},
                return_document=True
            )
            return result
        except:
            return None

    def assign_variant(self, traffic_split: Dict[str, float]) -> str:
        """Randomly assign a variant based on traffic split"""
        rand = random.uniform(0, 100)
        cumulative = 0
        
        for variant_id, percentage in traffic_split.items():
            cumulative += percentage
            if rand <= cumulative:
                return variant_id
        
        # Fallback to first variant
        return list(traffic_split.keys())[0]

    async def get_variant_performance(
        self,
        test_id: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """Get performance metrics for all variants"""
        test = await self.get_ab_test(test_id, tenant_id)
        if not test:
            return {}
        
        # Get campaign sends for this test
        sends_collection = db.campaign_sends
        variant_stats = {}
        
        for variant in test.get("variants", []):
            variant_id = variant.get("id")
            
            # Aggregate stats for this variant
            pipeline = [
                {
                    "$match": {
                        "ab_test_id": test_id,
                        "variant_id": variant_id
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total": {"$sum": 1},
                        "delivered": {
                            "$sum": {"$cond": [{"$eq": ["$status", "delivered"]}, 1, 0]}
                        },
                        "opened": {
                            "$sum": {"$cond": [{"$ne": ["$opened_at", None]}, 1, 0]}
                        },
                        "clicked": {
                            "$sum": {"$cond": [{"$ne": ["$clicked_at", None]}, 1, 0]}
                        },
                        "conversions": {
                            "$sum": {"$cond": [{"$gt": ["$revenue_attributed", 0]}, 1, 0]}
                        },
                        "revenue": {"$sum": "$revenue_attributed"}
                    }
                }
            ]
            
            result = await sends_collection.aggregate(pipeline).to_list(1)
            if result:
                stats = result[0]
                variant_stats[variant_id] = {
                    "total": stats.get("total", 0),
                    "delivered": stats.get("delivered", 0),
                    "opened": stats.get("opened", 0),
                    "clicked": stats.get("clicked", 0),
                    "conversions": stats.get("conversions", 0),
                    "revenue": stats.get("revenue", 0),
                    "open_rate": (stats.get("opened", 0) / stats.get("total", 1)) * 100 if stats.get("total", 0) > 0 else 0,
                    "click_rate": (stats.get("clicked", 0) / stats.get("total", 1)) * 100 if stats.get("total", 0) > 0 else 0,
                    "conversion_rate": (stats.get("conversions", 0) / stats.get("total", 1)) * 100 if stats.get("total", 0) > 0 else 0
                }
            else:
                variant_stats[variant_id] = {
                    "total": 0,
                    "delivered": 0,
                    "opened": 0,
                    "clicked": 0,
                    "conversions": 0,
                    "revenue": 0,
                    "open_rate": 0,
                    "click_rate": 0,
                    "conversion_rate": 0
                }
        
        return variant_stats

    async def determine_winner(self, test_id: str, tenant_id: str) -> Optional[str]:
        """Determine winning variant based on conversion rate"""
        performance = await self.get_variant_performance(test_id, tenant_id)
        
        if not performance:
            return None
        
        # Find variant with highest conversion rate
        winner = max(
            performance.items(),
            key=lambda x: x[1].get("conversion_rate", 0)
        )
        
        return winner[0]


# Lazy-loaded singleton instance
_ab_test_service = None

def get_ab_test_service():
    """Get or create the AB test service"""
    global _ab_test_service
    if _ab_test_service is None:
        _ab_test_service = ABTestService()
    return _ab_test_service

# For backward compatibility
class _LazyABTestService:
    def __getattr__(self, name):
        return getattr(get_ab_test_service(), name)

ab_test_service = _LazyABTestService()

