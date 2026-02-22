from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from app.schemas.white_label import WhiteLabelConfig, WhiteLabelConfigUpdate
from app.services.white_label_service import WhiteLabelService
from app.services.branding_version_service import BrandingVersionService


class ScheduledBrandingChange:
    """Represents a scheduled branding change"""
    
    def __init__(
        self,
        id: str,
        tenant_id: str,
        scheduled_for: datetime,
        branding_config: Dict[str, Any],
        change_type: str,  # "scheduled_change" or "ab_test"
        description: Optional[str] = None,
        created_by: Optional[str] = None,
        created_at: Optional[datetime] = None,
        is_active: bool = True,
        ab_test_id: Optional[str] = None,
        ab_test_variant: Optional[str] = None,
    ):
        self.id = id
        self.tenant_id = tenant_id
        self.scheduled_for = scheduled_for
        self.branding_config = branding_config
        self.change_type = change_type
        self.description = description
        self.created_by = created_by
        self.created_at = created_at or datetime.utcnow()
        self.is_active = is_active
        self.ab_test_id = ab_test_id
        self.ab_test_variant = ab_test_variant
        self.executed_at: Optional[datetime] = None
        self.execution_status: str = "pending"  # pending, executed, failed, cancelled


class ScheduledBrandingService:
    """Service for managing scheduled branding changes and A/B testing"""

    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.scheduled_branding_changes
        self.ab_tests_collection = db.branding_ab_tests
        self.white_label_service = WhiteLabelService(db)
        self.version_service = BrandingVersionService(db)

    async def schedule_branding_change(
        self,
        tenant_id: str,
        scheduled_for: datetime,
        branding_config: Dict[str, Any],
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Schedule a branding change for a future date"""
        
        # Validate scheduled time is in the future
        if scheduled_for <= datetime.utcnow():
            raise ValueError("Scheduled time must be in the future")

        # Create scheduled change document
        change_id = str(uuid.uuid4())
        change_doc = {
            "_id": change_id,
            "tenant_id": tenant_id,
            "scheduled_for": scheduled_for,
            "branding_config": branding_config,
            "change_type": "scheduled_change",
            "description": description,
            "created_by": created_by,
            "created_at": datetime.utcnow(),
            "is_active": True,
            "execution_status": "pending",
            "executed_at": None,
        }

        result = await self.collection.insert_one(change_doc)

        return {
            "id": change_id,
            "tenant_id": tenant_id,
            "scheduled_for": scheduled_for.isoformat(),
            "description": description,
            "status": "pending",
            "created_at": change_doc["created_at"].isoformat(),
        }

    async def get_scheduled_change(
        self, tenant_id: str, change_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get a specific scheduled change"""
        change = await self.collection.find_one(
            {"_id": change_id, "tenant_id": tenant_id}
        )
        if change:
            return self._format_scheduled_change(change)
        return None

    async def list_scheduled_changes(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Dict[str, Any]], int]:
        """List scheduled changes for a tenant"""
        query = {"tenant_id": tenant_id}
        
        if status:
            query["execution_status"] = status

        total = await self.collection.count_documents(query)

        cursor = self.collection.find(query).sort(
            "scheduled_for", 1
        ).skip(skip).limit(limit)

        changes = []
        async for doc in cursor:
            changes.append(self._format_scheduled_change(doc))

        return changes, total

    async def cancel_scheduled_change(
        self, tenant_id: str, change_id: str
    ) -> bool:
        """Cancel a scheduled change"""
        result = await self.collection.update_one(
            {"_id": change_id, "tenant_id": tenant_id, "execution_status": "pending"},
            {"$set": {"execution_status": "cancelled", "is_active": False}},
        )
        return result.modified_count > 0

    async def execute_scheduled_change(
        self, tenant_id: str, change_id: str
    ) -> bool:
        """Execute a scheduled change immediately"""
        change = await self.collection.find_one(
            {"_id": change_id, "tenant_id": tenant_id}
        )

        if not change:
            raise ValueError("Scheduled change not found")

        if change["execution_status"] != "pending":
            raise ValueError(f"Cannot execute change with status: {change['execution_status']}")

        try:
            # Get current config
            config = await self.white_label_service.get_config(tenant_id)
            if not config:
                raise ValueError("White label configuration not found")

            # Create version snapshot before applying changes
            await self.version_service.create_version(
                tenant_id=tenant_id,
                config=config,
                change_description=f"Scheduled change executed: {change.get('description', '')}",
                created_by=change.get("created_by"),
            )

            # Apply branding changes
            update_data = WhiteLabelConfigUpdate(
                branding=change["branding_config"].get("branding"),
                domain=change["branding_config"].get("domain"),
                features=change["branding_config"].get("features"),
            )

            await self.white_label_service.update_config(tenant_id, update_data)

            # Mark as executed
            await self.collection.update_one(
                {"_id": change_id},
                {
                    "$set": {
                        "execution_status": "executed",
                        "executed_at": datetime.utcnow(),
                    }
                },
            )

            return True

        except Exception as e:
            # Mark as failed
            await self.collection.update_one(
                {"_id": change_id},
                {
                    "$set": {
                        "execution_status": "failed",
                        "error": str(e),
                    }
                },
            )
            raise

    async def execute_pending_changes(self) -> List[Dict[str, Any]]:
        """Execute all pending scheduled changes that are due"""
        now = datetime.utcnow()

        # Find all pending changes that are due
        pending_changes = await self.collection.find(
            {
                "execution_status": "pending",
                "scheduled_for": {"$lte": now},
                "is_active": True,
            }
        ).to_list(None)

        executed = []
        for change in pending_changes:
            try:
                await self.execute_scheduled_change(
                    change["tenant_id"], change["_id"]
                )
                executed.append(
                    {
                        "change_id": change["_id"],
                        "tenant_id": change["tenant_id"],
                        "status": "executed",
                    }
                )
            except Exception as e:
                executed.append(
                    {
                        "change_id": change["_id"],
                        "tenant_id": change["tenant_id"],
                        "status": "failed",
                        "error": str(e),
                    }
                )

        return executed

    # A/B Testing Methods

    async def create_ab_test(
        self,
        tenant_id: str,
        test_name: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        split_percentage: float = 50.0,
        duration_days: int = 7,
        description: Optional[str] = None,
        created_by: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create an A/B test for branding configurations"""
        
        # Validate split percentage
        if not (0 < split_percentage < 100):
            raise ValueError("Split percentage must be between 0 and 100")

        # Validate duration
        if duration_days < 1:
            raise ValueError("Duration must be at least 1 day")

        test_id = str(uuid.uuid4())
        start_date = datetime.utcnow()
        end_date = start_date + timedelta(days=duration_days)

        test_doc = {
            "_id": test_id,
            "tenant_id": tenant_id,
            "test_name": test_name,
            "description": description,
            "variant_a": variant_a,
            "variant_b": variant_b,
            "split_percentage": split_percentage,
            "start_date": start_date,
            "end_date": end_date,
            "duration_days": duration_days,
            "created_by": created_by,
            "created_at": start_date,
            "status": "active",
            "results": {
                "variant_a_conversions": 0,
                "variant_a_visits": 0,
                "variant_b_conversions": 0,
                "variant_b_visits": 0,
            },
        }

        result = await self.ab_tests_collection.insert_one(test_doc)

        return {
            "test_id": test_id,
            "test_name": test_name,
            "status": "active",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "split_percentage": split_percentage,
        }

    async def get_ab_test(self, tenant_id: str, test_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific A/B test"""
        test = await self.ab_tests_collection.find_one(
            {"_id": test_id, "tenant_id": tenant_id}
        )
        if test:
            return self._format_ab_test(test)
        return None

    async def list_ab_tests(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> tuple[List[Dict[str, Any]], int]:
        """List A/B tests for a tenant"""
        query = {"tenant_id": tenant_id}
        
        if status:
            query["status"] = status

        total = await self.ab_tests_collection.count_documents(query)

        cursor = self.ab_tests_collection.find(query).sort(
            "created_at", -1
        ).skip(skip).limit(limit)

        tests = []
        async for doc in cursor:
            tests.append(self._format_ab_test(doc))

        return tests, total

    async def get_variant_for_user(
        self, tenant_id: str, test_id: str, user_id: str
    ) -> Optional[str]:
        """Determine which variant a user should see"""
        test = await self.ab_tests_collection.find_one(
            {"_id": test_id, "tenant_id": tenant_id}
        )

        if not test or test["status"] != "active":
            return None

        # Use user_id hash to consistently assign variant
        user_hash = hash(f"{user_id}_{test_id}") % 100
        
        if user_hash < test["split_percentage"]:
            return "variant_a"
        else:
            return "variant_b"

    async def track_ab_test_visit(
        self, tenant_id: str, test_id: str, variant: str
    ) -> bool:
        """Track a visit for an A/B test variant"""
        field = f"results.{variant}_visits"
        
        result = await self.ab_tests_collection.update_one(
            {"_id": test_id, "tenant_id": tenant_id},
            {"$inc": {field: 1}},
        )
        
        return result.modified_count > 0

    async def track_ab_test_conversion(
        self, tenant_id: str, test_id: str, variant: str
    ) -> bool:
        """Track a conversion for an A/B test variant"""
        field = f"results.{variant}_conversions"
        
        result = await self.ab_tests_collection.update_one(
            {"_id": test_id, "tenant_id": tenant_id},
            {"$inc": {field: 1}},
        )
        
        return result.modified_count > 0

    async def get_ab_test_results(
        self, tenant_id: str, test_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get results and statistics for an A/B test"""
        test = await self.ab_tests_collection.find_one(
            {"_id": test_id, "tenant_id": tenant_id}
        )

        if not test:
            return None

        results = test["results"]
        
        # Calculate conversion rates
        variant_a_conversion_rate = (
            results["variant_a_conversions"] / results["variant_a_visits"] * 100
            if results["variant_a_visits"] > 0
            else 0
        )
        
        variant_b_conversion_rate = (
            results["variant_b_conversions"] / results["variant_b_visits"] * 100
            if results["variant_b_visits"] > 0
            else 0
        )

        # Determine winner (simple comparison)
        winner = None
        if variant_a_conversion_rate > variant_b_conversion_rate:
            winner = "variant_a"
        elif variant_b_conversion_rate > variant_a_conversion_rate:
            winner = "variant_b"

        return {
            "test_id": test_id,
            "test_name": test["test_name"],
            "status": test["status"],
            "start_date": test["start_date"].isoformat(),
            "end_date": test["end_date"].isoformat(),
            "results": {
                "variant_a": {
                    "visits": results["variant_a_visits"],
                    "conversions": results["variant_a_conversions"],
                    "conversion_rate": round(variant_a_conversion_rate, 2),
                },
                "variant_b": {
                    "visits": results["variant_b_visits"],
                    "conversions": results["variant_b_conversions"],
                    "conversion_rate": round(variant_b_conversion_rate, 2),
                },
            },
            "winner": winner,
            "improvement": round(
                abs(variant_a_conversion_rate - variant_b_conversion_rate), 2
            ),
        }

    async def end_ab_test(
        self, tenant_id: str, test_id: str, winning_variant: Optional[str] = None
    ) -> bool:
        """End an A/B test and optionally apply the winning variant"""
        test = await self.ab_tests_collection.find_one(
            {"_id": test_id, "tenant_id": tenant_id}
        )

        if not test:
            raise ValueError("A/B test not found")

        # Update test status
        await self.ab_tests_collection.update_one(
            {"_id": test_id},
            {"$set": {"status": "completed"}},
        )

        # If winning variant specified, apply it
        if winning_variant:
            if winning_variant not in ["variant_a", "variant_b"]:
                raise ValueError("Invalid variant")

            variant_config = test[winning_variant]
            
            # Create version snapshot
            config = await self.white_label_service.get_config(tenant_id)
            if config:
                await self.version_service.create_version(
                    tenant_id=tenant_id,
                    config=config,
                    change_description=f"A/B test winner applied: {test['test_name']} - {winning_variant}",
                )

            # Apply winning variant
            update_data = WhiteLabelConfigUpdate(
                branding=variant_config.get("branding"),
                domain=variant_config.get("domain"),
                features=variant_config.get("features"),
            )

            await self.white_label_service.update_config(tenant_id, update_data)

        return True

    def _format_scheduled_change(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Format a scheduled change document for response"""
        return {
            "id": doc["_id"],
            "tenant_id": doc["tenant_id"],
            "scheduled_for": doc["scheduled_for"].isoformat(),
            "description": doc.get("description"),
            "status": doc["execution_status"],
            "created_at": doc["created_at"].isoformat(),
            "created_by": doc.get("created_by"),
            "executed_at": doc.get("executed_at").isoformat() if doc.get("executed_at") else None,
        }

    def _format_ab_test(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Format an A/B test document for response"""
        return {
            "test_id": doc["_id"],
            "test_name": doc["test_name"],
            "description": doc.get("description"),
            "status": doc["status"],
            "start_date": doc["start_date"].isoformat(),
            "end_date": doc["end_date"].isoformat(),
            "split_percentage": doc["split_percentage"],
            "created_at": doc["created_at"].isoformat(),
            "created_by": doc.get("created_by"),
        }
