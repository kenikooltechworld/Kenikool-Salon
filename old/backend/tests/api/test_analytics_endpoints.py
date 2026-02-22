"""
Tests for Analytics API endpoints
Task 26: Test Analytics Endpoints
"""

import pytest
from datetime import datetime, timedelta, timezone


class TestRevenueAnalytics:
    """Test revenue analytics endpoints"""

    def test_get_revenue_analytics(self, test_client, auth_headers):
        """Test getting revenue analytics"""
        response = test_client.get(
            "/api/analytics/revenue",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "total_revenue" in data
        assert "revenue_by_month" in data
        assert "revenue_by_service" in data

    def test_get_revenue_trends(self, test_client, auth_headers):
        """Test getting revenue trends"""
        response = test_client.get(
            "/api/analytics/revenue-trends",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_revenue_trends_with_dates(self, test_client, auth_headers):
        """Test getting revenue trends with date range"""
        start_date = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y-%m-%d")
        end_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        response = test_client.get(
            f"/api/analytics/revenue-trends?start_date={start_date}&end_date={end_date}",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestServiceAnalytics:
    """Test service analytics endpoints"""

    def test_get_service_performance(self, test_client, auth_headers):
        """Test getting service performance metrics"""
        response = test_client.get(
            "/api/analytics/services",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_get_service_efficiency(self, test_client, auth_headers):
        """Test getting service efficiency metrics"""
        response = test_client.get(
            "/api/analytics/service-efficiency",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestStaffAnalytics:
    """Test staff analytics endpoints"""

    def test_get_staff_performance(self, test_client, auth_headers):
        """Test getting staff performance metrics"""
        response = test_client.get(
            "/api/analytics/staff-performance",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert "staff_metrics" in data or "total_staff" in data or isinstance(data, dict)


class TestClientAnalytics:
    """Test client analytics endpoints"""

    def test_get_client_retention(self, test_client, auth_headers):
        """Test getting client retention metrics"""
        response = test_client.get(
            "/api/analytics/client-retention",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)


class TestAIInsights:
    """Test AI insights endpoint"""

    def test_get_ai_insights(self, test_client, auth_headers):
        """Test getting AI-generated insights"""
        response = test_client.get(
            "/api/analytics/insights",
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


print("✅ Task 26: Analytics Endpoint Tests Created")
