"""
Tests for public review endpoints
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_db():
    """Mock database"""
    db = MagicMock()
    return db


@pytest.fixture
def sample_reviews():
    """Sample approved reviews"""
    return [
        {
            "_id": ObjectId(),
            "tenant_id": "tenant123",
            "booking_id": "booking1",
            "client_id": "client1",
            "client_name": "John Doe",
            "service_id": "service1",
            "service_name": "Haircut",
            "stylist_id": "stylist1",
            "stylist_name": "Jane Smith",
            "rating": 5,
            "comment": "Great service!",
            "status": "approved",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "tenant_id": "tenant123",
            "booking_id": "booking2",
            "client_id": "client2",
            "client_name": "Jane Doe",
            "service_id": "service1",
            "service_name": "Haircut",
            "stylist_id": "stylist1",
            "stylist_name": "Jane Smith",
            "rating": 4,
            "comment": "Good experience",
            "status": "approved",
            "created_at": datetime.utcnow()
        }
    ]


@pytest.mark.asyncio
async def test_get_public_reviews_success(mock_db, sample_reviews):
    """Test getting public reviews successfully"""
    from app.services.review_service import ReviewService
    
    # Setup mock
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sample_reviews
    mock_db.reviews.count_documents.return_value = 2
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        skip=0,
        limit=20
    )
    
    assert result["total"] == 2
    assert len(result["reviews"]) == 2
    assert result["reviews"][0]["status"] == "approved"


@pytest.mark.asyncio
async def test_get_public_reviews_pagination(mock_db, sample_reviews):
    """Test pagination of public reviews"""
    from app.services.review_service import ReviewService
    
    # Setup mock for first page
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sample_reviews[:1]
    mock_db.reviews.count_documents.return_value = 2
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        skip=0,
        limit=1
    )
    
    assert result["total"] == 2
    assert len(result["reviews"]) == 1
    assert result["skip"] == 0
    assert result["limit"] == 1


@pytest.mark.asyncio
async def test_get_public_reviews_sorting_by_date(mock_db, sample_reviews):
    """Test sorting public reviews by date"""
    from app.services.review_service import ReviewService
    
    # Setup mock
    sorted_reviews = sorted(sample_reviews, key=lambda x: x["created_at"], reverse=True)
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
    mock_db.reviews.count_documents.return_value = 2
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        sort_by="created_at",
        sort_order="desc",
        skip=0,
        limit=20
    )
    
    assert result["total"] == 2
    assert len(result["reviews"]) == 2


@pytest.mark.asyncio
async def test_get_public_reviews_sorting_by_rating(mock_db, sample_reviews):
    """Test sorting public reviews by rating"""
    from app.services.review_service import ReviewService
    
    # Setup mock
    sorted_reviews = sorted(sample_reviews, key=lambda x: x["rating"], reverse=True)
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
    mock_db.reviews.count_documents.return_value = 2
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        sort_by="rating",
        sort_order="desc",
        skip=0,
        limit=20
    )
    
    assert result["total"] == 2
    assert len(result["reviews"]) == 2


@pytest.mark.asyncio
async def test_get_public_reviews_only_approved(mock_db):
    """Test that only approved reviews are returned"""
    from app.services.review_service import ReviewService
    
    # Setup mock - should only return approved reviews
    approved_reviews = [
        {
            "_id": ObjectId(),
            "tenant_id": "tenant123",
            "status": "approved",
            "rating": 5,
            "client_name": "John",
            "comment": "Great!",
            "created_at": datetime.utcnow()
        }
    ]
    
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = approved_reviews
    mock_db.reviews.count_documents.return_value = 1
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        skip=0,
        limit=20
    )
    
    assert result["total"] == 1
    assert all(review["status"] == "approved" for review in result["reviews"])


@pytest.mark.asyncio
async def test_get_public_rating_aggregation(mock_db):
    """Test getting public rating aggregation"""
    from app.services.review_service import ReviewService
    
    # Setup mock aggregation pipeline
    aggregation_result = [
        {
            "_id": None,
            "average_rating": 4.5,
            "total_reviews": 2,
            "rating_1": 0,
            "rating_2": 0,
            "rating_3": 0,
            "rating_4": 1,
            "rating_5": 1
        }
    ]
    
    mock_db.reviews.aggregate.return_value = aggregation_result
    
    service = ReviewService(mock_db)
    
    result = await service.get_rating_aggregation(tenant_id="tenant123")
    
    assert result["average_rating"] == 4.5
    assert result["total_reviews"] == 2
    assert result["rating_distribution"]["5"] == 1
    assert result["rating_distribution"]["4"] == 1


@pytest.mark.asyncio
async def test_get_public_reviews_empty(mock_db):
    """Test getting public reviews when none exist"""
    from app.services.review_service import ReviewService
    
    # Setup mock
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
    mock_db.reviews.count_documents.return_value = 0
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        skip=0,
        limit=20
    )
    
    assert result["total"] == 0
    assert len(result["reviews"]) == 0


@pytest.mark.asyncio
async def test_get_public_reviews_verified_badge(mock_db):
    """Test that reviews with booking_id show verified badge"""
    from app.services.review_service import ReviewService
    
    # Setup mock
    reviews_with_booking = [
        {
            "_id": ObjectId(),
            "tenant_id": "tenant123",
            "booking_id": "booking123",  # Has booking_id
            "status": "approved",
            "rating": 5,
            "client_name": "John",
            "comment": "Great!",
            "created_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "tenant_id": "tenant123",
            "booking_id": None,  # No booking_id
            "status": "approved",
            "rating": 4,
            "client_name": "Jane",
            "comment": "Good",
            "created_at": datetime.utcnow()
        }
    ]
    
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = reviews_with_booking
    mock_db.reviews.count_documents.return_value = 2
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="tenant123",
        status="approved",
        skip=0,
        limit=20
    )
    
    assert result["reviews"][0]["booking_id"] == "booking123"
    assert result["reviews"][1]["booking_id"] is None


@pytest.mark.asyncio
async def test_get_public_reviews_different_tenant(mock_db):
    """Test that reviews are isolated by tenant"""
    from app.services.review_service import ReviewService
    
    # Setup mock
    mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
    mock_db.reviews.count_documents.return_value = 0
    
    service = ReviewService(mock_db)
    
    result = await service.get_reviews_filtered(
        tenant_id="different_tenant",
        status="approved",
        skip=0,
        limit=20
    )
    
    assert result["total"] == 0
    assert len(result["reviews"]) == 0
    
    # Verify the query was called with correct tenant_id
    mock_db.reviews.find.assert_called()
    call_args = mock_db.reviews.find.call_args
    assert call_args[0][0]["tenant_id"] == "different_tenant"
