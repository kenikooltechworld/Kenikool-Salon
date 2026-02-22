"""
Tests for review filtering functionality
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, MagicMock, patch
from app.services.review_service import ReviewService


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.reviews = Mock()
    return db


@pytest.fixture
def review_service(mock_db):
    """Create a review service instance"""
    return ReviewService(mock_db)


@pytest.fixture
def sample_reviews_data():
    """Create sample review data for testing"""
    tenant_id = "test_tenant_1"
    
    # Create sample reviews with various attributes
    reviews_data = [
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_1",
            "client_id": "client_1",
            "client_name": "John Doe",
            "service_id": "service_1",
            "service_name": "Haircut",
            "stylist_id": "stylist_1",
            "stylist_name": "Alice",
            "rating": 5,
            "comment": "Excellent service and great haircut",
            "status": "approved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_2",
            "client_id": "client_2",
            "client_name": "Jane Smith",
            "service_id": "service_2",
            "service_name": "Color",
            "stylist_id": "stylist_2",
            "stylist_name": "Bob",
            "rating": 4,
            "comment": "Good color treatment",
            "status": "approved",
            "response": {
                "text": "Thank you for your feedback!",
                "responder_name": "Owner",
                "responded_at": datetime.utcnow()
            },
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(days=5)
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_3",
            "client_id": "client_3",
            "client_name": "Bob Johnson",
            "service_id": "service_1",
            "service_name": "Haircut",
            "stylist_id": "stylist_1",
            "stylist_name": "Alice",
            "rating": 3,
            "comment": "Average experience",
            "status": "pending",
            "created_at": datetime.utcnow() - timedelta(days=10),
            "updated_at": datetime.utcnow() - timedelta(days=10)
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_4",
            "client_id": "client_4",
            "client_name": "Alice Brown",
            "service_id": "service_2",
            "service_name": "Color",
            "stylist_id": "stylist_2",
            "stylist_name": "Bob",
            "rating": 2,
            "comment": "Not satisfied with the result",
            "status": "rejected",
            "photos": [
                {"id": "photo_1", "url": "http://example.com/photo1.jpg", "uploaded_at": datetime.utcnow()}
            ],
            "created_at": datetime.utcnow() - timedelta(days=15),
            "updated_at": datetime.utcnow() - timedelta(days=15)
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_5",
            "client_id": "client_5",
            "client_name": "Charlie Davis",
            "service_id": "service_1",
            "service_name": "Haircut",
            "stylist_id": "stylist_1",
            "stylist_name": "Alice",
            "rating": 1,
            "comment": "Terrible experience",
            "status": "approved",
            "flags": [
                {"reason": "offensive", "flagged_by": "admin_1", "flagged_at": datetime.utcnow()}
            ],
            "created_at": datetime.utcnow() - timedelta(days=20),
            "updated_at": datetime.utcnow() - timedelta(days=20)
        }
    ]
    
    return reviews_data


class TestFilterByStatus:
    """Tests for filtering by status"""
    
    @pytest.mark.asyncio
    async def test_filter_by_approved_status(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by approved status"""
        tenant_id = "test_tenant_1"
        
        # Filter approved reviews
        approved_reviews = [r for r in sample_reviews_data if r["status"] == "approved"]
        
        mock_db.reviews.count_documents.return_value = len(approved_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = approved_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved"
        )
        
        assert result["total"] == 3
        assert all(review["status"] == "approved" for review in result["reviews"])
    
    @pytest.mark.asyncio
    async def test_filter_by_pending_status(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by pending status"""
        tenant_id = "test_tenant_1"
        
        # Filter pending reviews
        pending_reviews = [r for r in sample_reviews_data if r["status"] == "pending"]
        
        mock_db.reviews.count_documents.return_value = len(pending_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = pending_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="pending"
        )
        
        assert result["total"] == 1
        assert result["reviews"][0]["status"] == "pending"


class TestFilterByRating:
    """Tests for filtering by rating"""
    
    @pytest.mark.asyncio
    async def test_filter_by_single_rating(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by single rating"""
        tenant_id = "test_tenant_1"
        
        # Filter by rating 5
        rating_5_reviews = [r for r in sample_reviews_data if r["rating"] == 5]
        
        mock_db.reviews.count_documents.return_value = len(rating_5_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = rating_5_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            rating=[5]
        )
        
        assert result["total"] == 1
        assert result["reviews"][0]["rating"] == 5
    
    @pytest.mark.asyncio
    async def test_filter_by_multiple_ratings(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by multiple ratings"""
        tenant_id = "test_tenant_1"
        
        # Filter by ratings 4 and 5
        multi_rating_reviews = [r for r in sample_reviews_data if r["rating"] in [4, 5]]
        
        mock_db.reviews.count_documents.return_value = len(multi_rating_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = multi_rating_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            rating=[4, 5]
        )
        
        assert result["total"] == 2
        assert all(review["rating"] in [4, 5] for review in result["reviews"])


class TestFilterByService:
    """Tests for filtering by service"""
    
    @pytest.mark.asyncio
    async def test_filter_by_service(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by service"""
        tenant_id = "test_tenant_1"
        
        # Filter by service_1
        service_reviews = [r for r in sample_reviews_data if r["service_id"] == "service_1"]
        
        mock_db.reviews.count_documents.return_value = len(service_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = service_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            service_id="service_1"
        )
        
        assert result["total"] == 3
        assert all(review["service_id"] == "service_1" for review in result["reviews"])


class TestFilterByStylist:
    """Tests for filtering by stylist"""
    
    @pytest.mark.asyncio
    async def test_filter_by_stylist(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by stylist"""
        tenant_id = "test_tenant_1"
        
        # Filter by stylist_2
        stylist_reviews = [r for r in sample_reviews_data if r["stylist_id"] == "stylist_2"]
        
        mock_db.reviews.count_documents.return_value = len(stylist_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = stylist_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            stylist_id="stylist_2"
        )
        
        assert result["total"] == 2
        assert all(review["stylist_id"] == "stylist_2" for review in result["reviews"])


class TestFilterByDateRange:
    """Tests for filtering by date range"""
    
    @pytest.mark.asyncio
    async def test_filter_by_date_range(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews by date range"""
        tenant_id = "test_tenant_1"
        
        # Filter reviews from last 7 days
        start_date = datetime.utcnow() - timedelta(days=7)
        recent_reviews = [r for r in sample_reviews_data if r["created_at"] >= start_date]
        
        mock_db.reviews.count_documents.return_value = len(recent_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = recent_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            start_date=start_date
        )
        
        assert result["total"] == 2


class TestFilterByResponse:
    """Tests for filtering by response status"""
    
    @pytest.mark.asyncio
    async def test_filter_by_has_response(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews with response"""
        tenant_id = "test_tenant_1"
        
        # Filter reviews with response
        with_response = [r for r in sample_reviews_data if "response" in r and r["response"] is not None]
        
        mock_db.reviews.count_documents.return_value = len(with_response)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = with_response
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            has_response=True
        )
        
        assert result["total"] == 1
        assert "response" in result["reviews"][0]


class TestFilterByPhotos:
    """Tests for filtering by photos"""
    
    @pytest.mark.asyncio
    async def test_filter_by_has_photos(self, review_service, mock_db, sample_reviews_data):
        """Test filtering reviews with photos"""
        tenant_id = "test_tenant_1"
        
        # Filter reviews with photos
        with_photos = [r for r in sample_reviews_data if "photos" in r and r["photos"]]
        
        mock_db.reviews.count_documents.return_value = len(with_photos)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = with_photos
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            has_photos=True
        )
        
        assert result["total"] == 1
        assert "photos" in result["reviews"][0]


class TestFilterByFlags:
    """Tests for filtering by flagged status"""
    
    @pytest.mark.asyncio
    async def test_filter_by_is_flagged(self, review_service, mock_db, sample_reviews_data):
        """Test filtering flagged reviews"""
        tenant_id = "test_tenant_1"
        
        # Filter flagged reviews
        flagged = [r for r in sample_reviews_data if "flags" in r and r["flags"]]
        
        mock_db.reviews.count_documents.return_value = len(flagged)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = flagged
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            is_flagged=True
        )
        
        assert result["total"] == 1
        assert "flags" in result["reviews"][0]


class TestCombinedFilters:
    """Tests for combining multiple filters"""
    
    @pytest.mark.asyncio
    async def test_combined_status_and_service(self, review_service, mock_db, sample_reviews_data):
        """Test combining status and service filters"""
        tenant_id = "test_tenant_1"
        
        # Filter by status and service
        combined = [r for r in sample_reviews_data if r["status"] == "approved" and r["service_id"] == "service_1"]
        
        mock_db.reviews.count_documents.return_value = len(combined)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = combined
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved",
            service_id="service_1"
        )
        
        assert result["total"] == 2
        assert all(r["status"] == "approved" and r["service_id"] == "service_1" for r in result["reviews"])


class TestSorting:
    """Tests for sorting reviews"""
    
    @pytest.mark.asyncio
    async def test_sort_by_rating_descending(self, review_service, mock_db, sample_reviews_data):
        """Test sorting by rating descending"""
        tenant_id = "test_tenant_1"
        
        # Sort by rating descending
        sorted_reviews = sorted(sample_reviews_data, key=lambda x: x["rating"], reverse=True)
        
        mock_db.reviews.count_documents.return_value = len(sorted_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            sort_by="rating",
            sort_order="desc"
        )
        
        ratings = [review["rating"] for review in result["reviews"]]
        assert ratings == sorted(ratings, reverse=True)


class TestPagination:
    """Tests for pagination"""
    
    @pytest.mark.asyncio
    async def test_pagination_first_page(self, review_service, mock_db, sample_reviews_data):
        """Test getting first page"""
        tenant_id = "test_tenant_1"
        
        # Get first page
        first_page = sample_reviews_data[:2]
        
        mock_db.reviews.count_documents.return_value = len(sample_reviews_data)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = first_page
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            skip=0,
            limit=2
        )
        
        assert len(result["reviews"]) == 2
        assert result["skip"] == 0
        assert result["limit"] == 2
        assert result["total"] == 5
    
    @pytest.mark.asyncio
    async def test_pagination_second_page(self, review_service, mock_db, sample_reviews_data):
        """Test getting second page"""
        tenant_id = "test_tenant_1"
        
        # Get second page
        second_page = sample_reviews_data[2:4]
        
        mock_db.reviews.count_documents.return_value = len(sample_reviews_data)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = second_page
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            skip=2,
            limit=2
        )
        
        assert len(result["reviews"]) == 2
        assert result["skip"] == 2


class TestFilterCounts:
    """Tests for filter counts aggregation"""
    
    @pytest.mark.asyncio
    async def test_get_filter_counts(self, review_service, mock_db, sample_reviews_data):
        """Test getting filter counts"""
        tenant_id = "test_tenant_1"
        
        # Mock aggregation pipeline for services
        service_agg = [
            {"_id": "service_1", "count": 3},
            {"_id": "service_2", "count": 2}
        ]
        
        # Mock aggregation pipeline for stylists
        stylist_agg = [
            {"_id": "stylist_1", "count": 3},
            {"_id": "stylist_2", "count": 2}
        ]
        
        # Setup mocks
        mock_db.reviews.count_documents.side_effect = [
            3,  # approved
            1,  # pending
            1,  # rejected
            1,  # rating 5
            1,  # rating 4
            1,  # rating 3
            1,  # rating 2
            1,  # rating 1
            1,  # has_response
            1,  # has_photos
            1,  # is_flagged
            5   # total
        ]
        
        mock_db.reviews.aggregate.side_effect = [
            iter(service_agg),
            iter(stylist_agg)
        ]
        
        counts = await review_service.get_filter_counts(tenant_id=tenant_id)
        
        # Verify structure
        assert "status" in counts
        assert "rating" in counts
        assert "services" in counts
        assert "stylists" in counts
        assert "has_response" in counts
        assert "has_photos" in counts
        assert "is_flagged" in counts
        assert "total" in counts


class TestEmptyResults:
    """Tests for empty results"""
    
    @pytest.mark.asyncio
    async def test_empty_result(self, review_service, mock_db):
        """Test filtering with no results"""
        tenant_id = "test_tenant_nonexistent"
        
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved"
        )
        
        assert result["total"] == 0
        assert result["reviews"] == []
