"""
Unit tests for dashboard API endpoints
"""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId

from app.main import app
from app.database import get_database


class TestDashboardMetricsEndpoint:
    """Test /api/dashboard/metrics endpoint"""
    
    def test_get_metrics_success(self, client, auth_headers, test_db, test_tenant):
        """Test successful metrics retrieval"""
        # Create some test data
        tenant_id = test_tenant["id"]
        
        # Create test bookings
        test_db.bookings.insert_many([
            {
                "tenant_id": tenant_id,
                "status": "completed",
                "service_price": 500,
                "completed_at": datetime.now(),
                "booking_date": datetime.now(),
                "created_at": datetime.now()
            }
            for _ in range(5)
        ])
        
        # Create test clients
        test_db.clients.insert_many([
            {
                "tenant_id": tenant_id,
                "name": f"Client {i}",
                "created_at": datetime.now()
            }
            for i in range(10)
        ])
        
        response = client.get(
            "/api/dashboard/metrics?period=week",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total_revenue" in data
        assert "revenue_trend" in data
        assert "total_bookings" in data
        assert "booking_trend" in data
        assert "total_clients" in data
        assert "client_trend" in data
        assert "new_clients" in data
        assert "retention_rate" in data
        assert "returning_client_percentage" in data
        assert data["period"] == "week"
    
    def test_get_metrics_invalid_period(self, client, auth_headers):
        """Test metrics with invalid period parameter"""
        response = client.get(
            "/api/dashboard/metrics?period=invalid",
            headers=auth_headers
        )
        
        assert response.status_code == 422  # Validation error
    
    def test_get_metrics_unauthorized(self, client):
        """Test metrics without authentication"""
        response = client.get("/api/dashboard/metrics")
        
        assert response.status_code == 401
    
    def test_get_metrics_with_no_data(self, client, auth_headers, test_db):
        """Test metrics when no data exists"""
        response = client.get(
            "/api/dashboard/metrics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Should return zero values with null trends
        assert data["total_revenue"] == 0.0
        assert data["total_bookings"] == 0
        assert data["total_clients"] == 0


class TestRevenueChartEndpoint:
    """Test /api/dashboard/revenue-chart endpoint"""
    
    def test_get_revenue_chart_daily(self, client, auth_headers, test_db, test_tenant):
        """Test revenue chart with daily period"""
        tenant_id = test_tenant["id"]
        
        # Create test bookings with different dates
        test_db.bookings.insert_many([
            {
                "tenant_id": tenant_id,
                "status": "completed",
                "service_price": 1000,
                "completed_at": datetime(2026, 1, 1, 10, 0, 0),
                "booking_date": datetime(2026, 1, 1),
                "created_at": datetime(2026, 1, 1)
            },
            {
                "tenant_id": tenant_id,
                "status": "completed",
                "service_price": 1500,
                "completed_at": datetime(2026, 1, 2, 10, 0, 0),
                "booking_date": datetime(2026, 1, 2),
                "created_at": datetime(2026, 1, 2)
            }
        ])
        
        response = client.get(
            "/api/dashboard/revenue-chart?period=daily",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["period"] == "daily"
        assert "data" in data
        assert isinstance(data["data"], list)
    
    def test_get_revenue_chart_empty_data(self, client, auth_headers):
        """Test revenue chart with no data"""
        response = client.get(
            "/api/dashboard/revenue-chart",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["data"]) == 0


class TestTopServicesEndpoint:
    """Test /api/dashboard/top-services endpoint"""
    
    def test_get_top_services_success(self, client, auth_headers, test_db, test_tenant):
        """Test successful top services retrieval"""
        tenant_id = test_tenant["id"]
        
        # Create test services
        service1 = test_db.services.insert_one({
            "tenant_id": tenant_id,
            "name": "Haircut",
            "price": 500
        })
        
        service2 = test_db.services.insert_one({
            "tenant_id": tenant_id,
            "name": "Coloring",
            "price": 1000
        })
        
        # Create bookings for services
        test_db.bookings.insert_many([
            {
                "tenant_id": tenant_id,
                "service_id": str(service1.inserted_id),
                "status": "completed",
                "service_price": 500
            }
            for _ in range(10)
        ])
        
        test_db.bookings.insert_many([
            {
                "tenant_id": tenant_id,
                "service_id": str(service2.inserted_id),
                "status": "completed",
                "service_price": 1000
            }
            for _ in range(5)
        ])
        
        response = client.get(
            "/api/dashboard/top-services",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "services" in data
        assert len(data["services"]) > 0
        # First service should have more bookings
        assert data["services"][0]["booking_count"] >= data["services"][1]["booking_count"]
    
    def test_get_top_services_no_data(self, client, auth_headers):
        """Test top services with no bookings"""
        response = client.get(
            "/api/dashboard/top-services",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["services"]) == 0


class TestActivityFeedEndpoint:
    """Test /api/dashboard/activity-feed endpoint"""
    
    def test_get_activity_feed_success(self, client, auth_headers, test_db, test_tenant):
        """Test successful activity feed retrieval"""
        tenant_id = test_tenant["id"]
        
        # Create test client
        client_doc = test_db.clients.insert_one({
            "tenant_id": tenant_id,
            "name": "Jane Smith"
        })
        
        # Create test booking
        test_db.bookings.insert_one({
            "tenant_id": tenant_id,
            "client_id": str(client_doc.inserted_id),
            "status": "confirmed",
            "created_at": datetime.now()
        })
        
        response = client.get(
            "/api/dashboard/activity-feed",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "activities" in data
        assert isinstance(data["activities"], list)


class TestAlertsEndpoint:
    """Test /api/dashboard/alerts endpoint"""
    
    def test_get_alerts_low_inventory(self, client, auth_headers, test_db, test_tenant):
        """Test alerts for low inventory"""
        tenant_id = test_tenant["id"]
        
        # Create low inventory item
        test_db.inventory.insert_one({
            "tenant_id": tenant_id,
            "name": "Shampoo",
            "quantity": 3
        })
        
        response = client.get(
            "/api/dashboard/alerts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "alerts" in data
        assert len(data["alerts"]) > 0
        assert data["alerts"][0]["type"] == "inventory"
    
    def test_get_alerts_no_alerts(self, client, auth_headers):
        """Test when there are no alerts"""
        response = client.get(
            "/api/dashboard/alerts",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["alerts"]) == 0


class TestUpcomingEventsEndpoint:
    """Test /api/dashboard/upcoming-events endpoint"""
    
    def test_get_upcoming_events_success(self, client, auth_headers, test_db, test_tenant):
        """Test successful upcoming events retrieval"""
        tenant_id = test_tenant["id"]
        
        # Create future bookings
        tomorrow = datetime.now() + timedelta(days=1)
        test_db.bookings.insert_many([
            {
                "tenant_id": tenant_id,
                "booking_date": tomorrow,
                "status": "confirmed"
            }
            for _ in range(5)
        ])
        
        response = client.get(
            "/api/dashboard/upcoming-events",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "events" in data
        assert isinstance(data["events"], list)


class TestQuickStatsEndpoint:
    """Test /api/dashboard/quick-stats endpoint"""
    
    def test_get_quick_stats_success(self, client, auth_headers, test_db, test_tenant):
        """Test successful quick stats retrieval"""
        tenant_id = test_tenant["id"]
        
        # Create some test bookings
        test_db.bookings.insert_many([
            {
                "tenant_id": tenant_id,
                "status": "completed",
                "service_price": 500,
                "booking_date": datetime.now(),
                "created_at": datetime.now()
            }
            for _ in range(10)
        ])
        
        response = client.get(
            "/api/dashboard/quick-stats",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "avg_booking_value" in data
        assert "cancellation_rate" in data
        assert "no_show_rate" in data
        assert "online_booking_percentage" in data
        assert "gift_card_sales" in data
        assert "loyalty_points_redeemed" in data


class TestErrorHandling:
    """Test error handling across endpoints"""
    
    def test_unauthorized_access(self, client):
        """Test that endpoints require authentication"""
        endpoints = [
            "/api/dashboard/metrics",
            "/api/dashboard/revenue-chart",
            "/api/dashboard/top-services",
            "/api/dashboard/activity-feed",
            "/api/dashboard/alerts",
            "/api/dashboard/upcoming-events",
            "/api/dashboard/quick-stats"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 401


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
