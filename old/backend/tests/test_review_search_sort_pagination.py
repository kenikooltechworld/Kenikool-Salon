"""
Integration tests for review search, sorting, and pagination
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock
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
def comprehensive_reviews_data():
    """Create comprehensive review data for integration testing"""
    tenant_id = "test_tenant_1"
    
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
            "comment": "Excellent haircut and very professional service",
            "status": "approved",
            "helpful_votes": ["user1", "user2", "user3"],
            "created_at": datetime.utcnow() - timedelta(days=1),
            "updated_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_2",
            "client_id": "client_2",
            "client_name": "Jane Smith",
            "service_id": "service_2",
            "service_name": "Color Treatment",
            "stylist_id": "stylist_2",
            "stylist_name": "Bob",
            "rating": 4,
            "comment": "Great color treatment, very satisfied with the results",
            "status": "approved",
            "helpful_votes": ["user1", "user2"],
            "created_at": datetime.utcnow() - timedelta(days=2),
            "updated_at": datetime.utcnow() - timedelta(days=2)
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
            "comment": "Average haircut, could be better",
            "status": "pending",
            "helpful_votes": ["user1"],
            "created_at": datetime.utcnow() - timedelta(days=3),
            "updated_at": datetime.utcnow() - timedelta(days=3)
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_4",
            "client_id": "client_4",
            "client_name": "Alice Brown",
            "service_id": "service_3",
            "service_name": "Styling",
            "stylist_id": "stylist_2",
            "stylist_name": "Bob",
            "rating": 5,
            "comment": "Amazing styling service, Alice is the best stylist",
            "status": "approved",
            "helpful_votes": ["user1", "user2", "user3", "user4"],
            "created_at": datetime.utcnow() - timedelta(days=4),
            "updated_at": datetime.utcnow() - timedelta(days=4)
        },
        {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "booking_id": "booking_5",
            "client_id": "client_5",
            "client_name": "Charlie Davis",
            "service_id": "service_2",
            "service_name": "Color Treatment",
            "stylist_id": "stylist_1",
            "stylist_name": "Alice",
            "rating": 2,
            "comment": "Not satisfied with the color, it faded too quickly",
            "status": "approved",
            "helpful_votes": [],
            "created_at": datetime.utcnow() - timedelta(days=5),
            "updated_at": datetime.utcnow() - timedelta(days=5)
        }
    ]
    
    return reviews_data


class TestSearchSortPaginationIntegration:
    """Integration tests for search, sort, and pagination"""
    
    @pytest.mark.asyncio
    async def test_search_with_sorting_by_rating(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test search combined with sorting by rating"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter by search and sort by rating descending
        matching_reviews = [
            r for r in comprehensive_reviews_data 
            if "service" in r["comment"].lower()
        ]
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["rating"], reverse=True)
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            sort_by="rating",
            sort_order="desc"
        )
        
        assert result["total"] == 1
        assert result["reviews"][0]["rating"] == 5
    
    @pytest.mark.asyncio
    async def test_search_with_sorting_by_date(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test search combined with sorting by date"""
        tenant_id = "test_tenant_1"
        search_query = "color"
        
        # Filter by search and sort by date descending
        matching_reviews = [
            r for r in comprehensive_reviews_data 
            if "color" in r["comment"].lower()
        ]
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["created_at"], reverse=True)
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            sort_by="created_at",
            sort_order="desc"
        )
        
        assert result["total"] == 2
        # Verify sorted by date descending
        dates = [r["created_at"] for r in result["reviews"]]
        assert dates == sorted(dates, reverse=True)
    
    @pytest.mark.asyncio
    async def test_search_with_pagination(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test search with pagination"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter by search
        matching_reviews = [
            r for r in comprehensive_reviews_data 
            if "service" in r["comment"].lower()
        ]
        
        # Get first page (limit 1)
        first_page = matching_reviews[:1]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = first_page
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            skip=0,
            limit=1
        )
        
        assert result["total"] == len(matching_reviews)
        assert len(result["reviews"]) == 1
        assert result["skip"] == 0
        assert result["limit"] == 1
    
    @pytest.mark.asyncio
    async def test_search_sort_pagination_combined(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test search, sort, and pagination all together"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter by search, sort by rating, and paginate
        matching_reviews = [
            r for r in comprehensive_reviews_data 
            if "service" in r["comment"].lower()
        ]
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["rating"], reverse=True)
        paginated_reviews = sorted_reviews[0:1]  # First page with limit 1
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = paginated_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            sort_by="rating",
            sort_order="desc",
            skip=0,
            limit=1
        )
        
        assert result["total"] == len(matching_reviews)
        assert len(result["reviews"]) == 1
        assert result["reviews"][0]["rating"] == 5
    
    @pytest.mark.asyncio
    async def test_filter_search_sort_pagination(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test filtering, search, sort, and pagination together"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter by status, search, sort by rating, and paginate
        matching_reviews = [
            r for r in comprehensive_reviews_data 
            if r["status"] == "approved" and "service" in r["comment"].lower()
        ]
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["rating"], reverse=True)
        paginated_reviews = sorted_reviews[0:1]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = paginated_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved",
            search=search_query,
            sort_by="rating",
            sort_order="desc",
            skip=0,
            limit=1
        )
        
        assert result["total"] == len(matching_reviews)
        assert len(result["reviews"]) == 1
        assert result["reviews"][0]["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_multiple_filters_with_search_and_sort(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test multiple filters combined with search and sort"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter by status, rating, and search, then sort
        matching_reviews = [
            r for r in comprehensive_reviews_data 
            if r["status"] == "approved" and r["rating"] >= 4 and "service" in r["comment"].lower()
        ]
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["rating"], reverse=True)
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            status="approved",
            rating=[4, 5],
            search=search_query,
            sort_by="rating",
            sort_order="desc"
        )
        
        assert result["total"] == len(matching_reviews)
        assert all(r["status"] == "approved" for r in result["reviews"])
        assert all(r["rating"] >= 4 for r in result["reviews"])
    
    @pytest.mark.asyncio
    async def test_sort_by_helpful_votes(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test sorting by helpful votes"""
        tenant_id = "test_tenant_1"
        
        # Sort by helpful votes descending
        sorted_reviews = sorted(
            comprehensive_reviews_data,
            key=lambda x: len(x.get("helpful_votes", [])),
            reverse=True
        )
        
        mock_db.reviews.count_documents.return_value = len(comprehensive_reviews_data)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            sort_by="helpful_votes",
            sort_order="desc"
        )
        
        assert result["total"] == len(comprehensive_reviews_data)
        # Verify sorted by helpful votes
        vote_counts = [len(r.get("helpful_votes", [])) for r in result["reviews"]]
        assert vote_counts == sorted(vote_counts, reverse=True)
    
    @pytest.mark.asyncio
    async def test_pagination_across_multiple_pages(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test pagination across multiple pages"""
        tenant_id = "test_tenant_1"
        
        # Test page 1
        page1_reviews = comprehensive_reviews_data[0:2]
        mock_db.reviews.count_documents.return_value = len(comprehensive_reviews_data)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = page1_reviews
        
        result_page1 = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            skip=0,
            limit=2
        )
        
        assert len(result_page1["reviews"]) == 2
        assert result_page1["skip"] == 0
        
        # Test page 2
        page2_reviews = comprehensive_reviews_data[2:4]
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = page2_reviews
        
        result_page2 = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            skip=2,
            limit=2
        )
        
        assert len(result_page2["reviews"]) == 2
        assert result_page2["skip"] == 2
        
        # Test page 3 (partial)
        page3_reviews = comprehensive_reviews_data[4:5]
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = page3_reviews
        
        result_page3 = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            skip=4,
            limit=2
        )
        
        assert len(result_page3["reviews"]) == 1
        assert result_page3["skip"] == 4
    
    @pytest.mark.asyncio
    async def test_search_with_no_results_and_pagination(
        self, review_service, mock_db
    ):
        """Test search with no results and pagination"""
        tenant_id = "test_tenant_1"
        search_query = "nonexistent"
        
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            skip=0,
            limit=20
        )
        
        assert result["total"] == 0
        assert result["reviews"] == []
        assert result["skip"] == 0
        assert result["limit"] == 20
    
    @pytest.mark.asyncio
    async def test_sort_order_ascending(
        self, review_service, mock_db, comprehensive_reviews_data
    ):
        """Test sorting in ascending order"""
        tenant_id = "test_tenant_1"
        
        # Sort by rating ascending
        sorted_reviews = sorted(comprehensive_reviews_data, key=lambda x: x["rating"])
        
        mock_db.reviews.count_documents.return_value = len(comprehensive_reviews_data)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            sort_by="rating",
            sort_order="asc"
        )
        
        ratings = [r["rating"] for r in result["reviews"]]
        assert ratings == sorted(ratings)
