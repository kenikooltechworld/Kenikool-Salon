"""
Tests for Location Analytics Service
Tests the calculation of location performance metrics
"""

import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.location_analytics_service import LocationAnalyticsService


class TestLocationAnalyticsService:
    """Test suite for LocationAnalyticsService"""

    @pytest.fixture
    def mock_db(self):
        """Create a mock database"""
        return Mock()

    @pytest.fixture
    def sample_location_id(self):
        """Sample location ID"""
        return str(ObjectId())

    @pytest.fixture
    def sample_tenant_id(self):
        """Sample tenant ID"""
        return "test_tenant_123"

    @pytest.fixture
    def sample_dates(self):
        """Sample date range"""
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_get_location_metrics_success(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test successful retrieval of location metrics"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock location
        mock_db.locations.find_one.return_value = {
            "_id": ObjectId(sample_location_id),
            "tenant_id": sample_tenant_id,
            "name": "Main Location",
            "capacity": 10
        }

        # Mock aggregation results
        mock_db.bookings.aggregate.return_value = [
            {
                "_id": None,
                "total_revenue": 5000.0
            }
        ]

        # Mock count results
        mock_db.bookings.count_documents.side_effect = [30, 25]  # total, completed

        # Mock top services
        mock_db.bookings.aggregate.side_effect = [
            [{"_id": None, "total_revenue": 5000.0}],  # revenue
            [
                {
                    "_id": "service_1",
                    "service_name": "Haircut",
                    "count": 15,
                    "total_revenue": 2250.0,
                    "average_price": 150.0
                }
            ]  # top services
        ]

        # Mock staff performance
        mock_db.bookings.aggregate.side_effect = [
            [{"_id": None, "total_revenue": 5000.0}],  # revenue
            [
                {
                    "_id": "service_1",
                    "service_name": "Haircut",
                    "count": 15,
                    "total_revenue": 2250.0,
                    "average_price": 150.0
                }
            ],  # top services
            [
                {
                    "_id": "stylist_1",
                    "stylist_name": "John Doe",
                    "bookings": 15,
                    "total_revenue": 2250.0,
                    "average_rating": 4.8,
                    "average_booking_value": 150.0
                }
            ]  # staff performance
        ]

        # Call the method
        result = LocationAnalyticsService.get_location_metrics(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        # Verify result structure
        assert "location_id" in result
        assert "location_name" in result
        assert "period" in result
        assert "revenue" in result
        assert "bookings" in result
        assert "occupancy" in result
        assert "top_services" in result
        assert "staff_performance" in result

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_get_location_metrics_not_found(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test error when location not found"""
        mock_get_db.return_value = mock_db
        mock_db.locations.find_one.return_value = None

        start_date, end_date = sample_dates

        with pytest.raises(ValueError, match="Location not found"):
            LocationAnalyticsService.get_location_metrics(
                location_id=sample_location_id,
                tenant_id=sample_tenant_id,
                start_date=start_date,
                end_date=end_date
            )

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_calculate_revenue(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test revenue calculation"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock aggregation result
        mock_db.bookings.aggregate.return_value = [
            {
                "_id": None,
                "total_revenue": 5000.0
            }
        ]

        result = LocationAnalyticsService.calculate_revenue(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert result == 5000.0

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_calculate_revenue_no_bookings(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test revenue calculation with no bookings"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock empty aggregation result
        mock_db.bookings.aggregate.return_value = []

        result = LocationAnalyticsService.calculate_revenue(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert result == 0.0

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_count_bookings(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test booking count"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        mock_db.bookings.count_documents.return_value = 30

        result = LocationAnalyticsService.count_bookings(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert result == 30

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_count_completed_bookings(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test completed booking count"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        mock_db.bookings.count_documents.return_value = 25

        result = LocationAnalyticsService.count_completed_bookings(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert result == 25

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_calculate_occupancy(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test occupancy rate calculation"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock location with capacity
        mock_db.locations.find_one.return_value = {
            "_id": ObjectId(sample_location_id),
            "capacity": 10
        }

        # Mock completed bookings count
        mock_db.bookings.count_documents.return_value = 25

        result = LocationAnalyticsService.calculate_occupancy(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        # 25 bookings / (10 capacity * 31 days) = 8.06%
        assert 0 <= result <= 100

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_calculate_occupancy_no_capacity(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test occupancy calculation with no capacity"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock location without capacity
        mock_db.locations.find_one.return_value = {
            "_id": ObjectId(sample_location_id),
            "capacity": 0
        }

        result = LocationAnalyticsService.calculate_occupancy(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert result == 0.0

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_get_top_services(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test top services retrieval"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock aggregation result
        mock_db.bookings.aggregate.return_value = [
            {
                "_id": "service_1",
                "service_name": "Haircut",
                "count": 15,
                "total_revenue": 2250.0,
                "average_price": 150.0
            },
            {
                "_id": "service_2",
                "service_name": "Color",
                "count": 10,
                "total_revenue": 1500.0,
                "average_price": 150.0
            }
        ]

        result = LocationAnalyticsService.get_top_services(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert len(result) == 2
        assert result[0]["service_name"] == "Haircut"
        assert result[0]["bookings"] == 15

    @patch('app.services.location_analytics_service.Database.get_db')
    def test_get_staff_performance(self, mock_get_db, mock_db, sample_location_id, sample_tenant_id, sample_dates):
        """Test staff performance retrieval"""
        mock_get_db.return_value = mock_db
        start_date, end_date = sample_dates

        # Mock aggregation result
        mock_db.bookings.aggregate.return_value = [
            {
                "_id": "stylist_1",
                "stylist_name": "John Doe",
                "bookings": 15,
                "total_revenue": 2250.0,
                "average_rating": 4.8,
                "average_booking_value": 150.0
            },
            {
                "_id": "stylist_2",
                "stylist_name": "Jane Smith",
                "bookings": 10,
                "total_revenue": 1500.0,
                "average_rating": 4.5,
                "average_booking_value": 150.0
            }
        ]

        result = LocationAnalyticsService.get_staff_performance(
            location_id=sample_location_id,
            tenant_id=sample_tenant_id,
            start_date=start_date,
            end_date=end_date
        )

        assert len(result) == 2
        assert result[0]["stylist_name"] == "John Doe"
        assert result[0]["bookings"] == 15
        assert result[0]["average_rating"] == 4.8
