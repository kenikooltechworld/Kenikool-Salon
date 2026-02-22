"""
Tests for waitlist analytics service
Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.services.waitlist_analytics_service import WaitlistAnalyticsService
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-analytics"


class TestWaitlistAnalyticsService:
    """Test waitlist analytics service functionality"""
    
    def test_stats_calculation_with_no_entries(self, db, tenant_id):
        """Test stats calculation with no entries"""
        # Ensure no entries exist
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Get stats
        stats = WaitlistAnalyticsService.get_waitlist_stats(tenant_id)
        
        # Verify
        assert stats["total_entries"] == 0
        assert stats["by_status"] == {}
        assert stats["average_wait_time_days"] == 0
    
    def test_stats_calculation_with_entries_in_all_statuses(self, db, tenant_id):
        """Test stats calculation with entries in all statuses"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create entries with different statuses
        now = datetime.utcnow()
        entries = [
            {
                "tenant_id": tenant_id,
                "client_name": "Client 1",
                "status": "waiting",
                "created_at": now,
                "updated_at": now
            },
            {
                "tenant_id": tenant_id,
                "client_name": "Client 2",
                "status": "notified",
                "created_at": now - timedelta(days=2),
                "notified_at": now,
                "updated_at": now
            },
            {
                "tenant_id": tenant_id,
                "client_name": "Client 3",
                "status": "booked",
                "created_at": now - timedelta(days=5),
                "booked_at": now,
                "updated_at": now
            },
            {
                "tenant_id": tenant_id,
                "client_name": "Client 4",
                "status": "expired",
                "created_at": now - timedelta(days=31),
                "updated_at": now,
            }
        ]
        
        for entry in entries:
            db.waitlist.insert_one(entry)
        
        # Get stats
        stats = WaitlistAnalyticsService.get_waitlist_stats(tenant_id)
        
        # Verify
        assert stats["total_entries"] == 4
        assert stats["by_status"]["waiting"] == 1
        assert stats["by_status"]["notified"] == 1
        assert stats["by_status"]["booked"] == 1
        assert stats["by_status"]["expired"] == 1
        assert stats["average_wait_time_days"] > 0
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_conversion_rate_calculation(self, db, tenant_id):
        """Test conversion rate calculation"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create entries
        now = datetime.utcnow()
        entries = [
            {"tenant_id": tenant_id, "status": "booked", "created_at": now},
            {"tenant_id": tenant_id, "status": "booked", "created_at": now},
            {"tenant_id": tenant_id, "status": "notified", "created_at": now},
            {"tenant_id": tenant_id, "status": "waiting", "created_at": now},
            {"tenant_id": tenant_id, "status": "expired", "created_at": now},
        ]
        
        for entry in entries:
            db.waitlist.insert_one(entry)
        
        # Get conversion metrics
        metrics = WaitlistAnalyticsService.get_conversion_metrics(tenant_id)
        
        # Verify
        assert metrics["total_entries"] == 5
        assert metrics["booked"] == 2
        assert metrics["notified"] == 1
        assert metrics["waiting"] == 1
        assert metrics["expired"] == 1
        assert metrics["conversion_rate_percent"] == 40.0  # 2/5 = 40%
        assert metrics["notification_rate_percent"] == 20.0  # 1/5 = 20%
        assert metrics["expiration_rate_percent"] == 20.0  # 1/5 = 20%
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_service_demand_ranking(self, db, tenant_id):
        """Test service demand ranking"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create entries for different services
        service_id_1 = ObjectId()
        service_id_2 = ObjectId()
        service_id_3 = ObjectId()
        
        entries = [
            {"tenant_id": tenant_id, "service_id": service_id_1, "service_name": "Haircut", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "service_id": service_id_1, "service_name": "Haircut", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "service_id": service_id_1, "service_name": "Haircut", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "service_id": service_id_2, "service_name": "Color", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "service_id": service_id_2, "service_name": "Color", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "service_id": service_id_3, "service_name": "Styling", "created_at": datetime.utcnow()},
        ]
        
        for entry in entries:
            db.waitlist.insert_one(entry)
        
        # Get service demand
        demand = WaitlistAnalyticsService.get_service_demand(tenant_id, limit=10)
        
        # Verify
        assert len(demand) == 3
        assert demand[0]["service_name"] == "Haircut"
        assert demand[0]["count"] == 3
        assert demand[1]["service_name"] == "Color"
        assert demand[1]["count"] == 2
        assert demand[2]["service_name"] == "Styling"
        assert demand[2]["count"] == 1
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_stylist_demand_ranking(self, db, tenant_id):
        """Test stylist demand ranking"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create entries for different stylists
        stylist_id_1 = ObjectId()
        stylist_id_2 = ObjectId()
        
        entries = [
            {"tenant_id": tenant_id, "stylist_id": stylist_id_1, "stylist_name": "Alice", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "stylist_id": stylist_id_1, "stylist_name": "Alice", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "stylist_id": stylist_id_2, "stylist_name": "Bob", "created_at": datetime.utcnow()},
            {"tenant_id": tenant_id, "stylist_id": "any", "stylist_name": "Any Stylist", "created_at": datetime.utcnow()},
        ]
        
        for entry in entries:
            db.waitlist.insert_one(entry)
        
        # Get stylist demand
        demand = WaitlistAnalyticsService.get_stylist_demand(tenant_id, limit=10)
        
        # Verify
        assert len(demand) == 3
        assert demand[0]["stylist_name"] == "Alice"
        assert demand[0]["count"] == 2
        assert demand[1]["stylist_name"] == "Bob"
        assert demand[1]["count"] == 1
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_date_range_filtering(self, db, tenant_id):
        """Test date range filtering"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create entries with different dates
        now = datetime.utcnow()
        old_date = now - timedelta(days=60)
        recent_date = now - timedelta(days=5)
        
        entries = [
            {"tenant_id": tenant_id, "status": "waiting", "created_at": old_date},
            {"tenant_id": tenant_id, "status": "waiting", "created_at": old_date},
            {"tenant_id": tenant_id, "status": "booked", "created_at": recent_date},
            {"tenant_id": tenant_id, "status": "booked", "created_at": recent_date},
        ]
        
        for entry in entries:
            db.waitlist.insert_one(entry)
        
        # Get stats with date range (last 30 days)
        date_from = now - timedelta(days=30)
        stats = WaitlistAnalyticsService.get_waitlist_stats(tenant_id, date_from=date_from)
        
        # Verify - should only include recent entries
        assert stats["total_entries"] == 2
        assert stats["by_status"]["booked"] == 2
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_service_demand_limit(self, db, tenant_id):
        """Test service demand limit parameter"""
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
        
        # Create entries for 15 different services
        for i in range(15):
            service_id = ObjectId()
            for j in range(15 - i):  # Decreasing counts
                db.waitlist.insert_one({
                    "tenant_id": tenant_id,
                    "service_id": service_id,
                    "service_name": f"Service {i}",
                    "created_at": datetime.utcnow()
                })
        
        # Get top 5 services
        demand = WaitlistAnalyticsService.get_service_demand(tenant_id, limit=5)
        
        # Verify
        assert len(demand) == 5
        assert demand[0]["count"] >= demand[1]["count"]
        assert demand[1]["count"] >= demand[2]["count"]
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": tenant_id})
    
    def test_tenant_isolation(self, db):
        """Test tenant isolation in analytics"""
        tenant_1 = "tenant-1"
        tenant_2 = "tenant-2"
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": {"$in": [tenant_1, tenant_2]}})
        
        # Create entries for different tenants
        now = datetime.utcnow()
        entries_1 = [
            {"tenant_id": tenant_1, "status": "waiting", "created_at": now},
            {"tenant_id": tenant_1, "status": "booked", "created_at": now},
        ]
        entries_2 = [
            {"tenant_id": tenant_2, "status": "waiting", "created_at": now},
            {"tenant_id": tenant_2, "status": "waiting", "created_at": now},
            {"tenant_id": tenant_2, "status": "waiting", "created_at": now},
        ]
        
        for entry in entries_1 + entries_2:
            db.waitlist.insert_one(entry)
        
        # Get stats for each tenant
        stats_1 = WaitlistAnalyticsService.get_waitlist_stats(tenant_1)
        stats_2 = WaitlistAnalyticsService.get_waitlist_stats(tenant_2)
        
        # Verify isolation
        assert stats_1["total_entries"] == 2
        assert stats_1["by_status"]["waiting"] == 1
        assert stats_1["by_status"]["booked"] == 1
        
        assert stats_2["total_entries"] == 3
        assert stats_2["by_status"]["waiting"] == 3
        
        # Clean up
        db.waitlist.delete_many({"tenant_id": {"$in": [tenant_1, tenant_2]}})
