"""
Tests for review analytics service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import MagicMock
from app.services.review_analytics_service import ReviewAnalyticsService


@pytest.fixture
def mock_db():
    """Create mock database"""
    db = MagicMock()
    db.reviews = MagicMock()
    return db


@pytest.fixture
def analytics_service(mock_db):
    """Create analytics service instance"""
    return ReviewAnalyticsService(mock_db)


@pytest.mark.asyncio
async def test_get_rating_trend(analytics_service, mock_db):
    """Test rating trend calculation"""
    tenant_id = "test_tenant"
    now = datetime.utcnow()
    start_date = now - timedelta(days=15)
    end_date = now + timedelta(days=1)
    
    mock_db.reviews.aggregate.return_value = [
        {
            "_id": (now - timedelta(days=10)).strftime("%Y-%m-%d"),
            "average_rating": 5.0,
            "total_reviews": 1
        }
    ]
    
    trend = await analytics_service.get_rating_trend(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    assert isinstance(trend, list)
    assert len(trend) == 1
    assert trend[0]["average_rating"] == 5.0


@pytest.mark.asyncio
async def test_get_service_ratings(analytics_service, mock_db):
    """Test service ratings aggregation"""
    tenant_id = "test_tenant"
    now = datetime.utcnow()
    start_date = now - timedelta(days=15)
    end_date = now + timedelta(days=1)
    
    mock_db.reviews.aggregate.return_value = [
        {
            "_id": "service_1",
            "service_name": "Haircut",
            "average_rating": 4.5,
            "total_reviews": 2
        }
    ]
    
    service_ratings = await analytics_service.get_service_ratings(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    assert isinstance(service_ratings, list)
    assert len(service_ratings) == 1
    assert service_ratings[0]["service_name"] == "Haircut"


@pytest.mark.asyncio
async def test_get_response_rate(analytics_service, mock_db):
    """Test response rate calculation"""
    tenant_id = "test_tenant"
    now = datetime.utcnow()
    start_date = now - timedelta(days=15)
    end_date = now + timedelta(days=1)
    
    mock_db.reviews.count_documents.side_effect = [4, 2]
    
    response_rate = await analytics_service.get_response_rate(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    assert response_rate["responded_count"] == 2
    assert response_rate["total_reviews"] == 4
    assert response_rate["response_rate"] == 50.0


@pytest.mark.asyncio
async def test_get_overall_metrics(analytics_service, mock_db):
    """Test overall metrics calculation"""
    tenant_id = "test_tenant"
    now = datetime.utcnow()
    start_date = now - timedelta(days=15)
    end_date = now + timedelta(days=1)
    
    mock_db.reviews.aggregate.return_value = [
        {
            "_id": None,
            "average_rating": 4.25,
            "total_reviews": 4,
            "rating_1": 0,
            "rating_2": 1,
            "rating_3": 1,
            "rating_4": 1,
            "rating_5": 2
        }
    ]
    
    mock_db.reviews.count_documents.return_value = 2
    
    metrics = await analytics_service.get_overall_metrics(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    assert metrics["average_rating"] == 4.25
    assert metrics["total_reviews"] == 4
    assert metrics["rating_distribution"]["5"] == 2


@pytest.mark.asyncio
async def test_get_complete_analytics(analytics_service, mock_db):
    """Test complete analytics dashboard data"""
    tenant_id = "test_tenant"
    now = datetime.utcnow()
    start_date = now - timedelta(days=15)
    end_date = now + timedelta(days=1)
    
    mock_db.reviews.aggregate.return_value = []
    mock_db.reviews.count_documents.return_value = 0
    
    analytics = await analytics_service.get_complete_analytics(
        tenant_id=tenant_id,
        start_date=start_date,
        end_date=end_date
    )
    
    assert "period" in analytics
    assert "filters" in analytics
    assert "overall_metrics" in analytics
    assert "rating_trend" in analytics
