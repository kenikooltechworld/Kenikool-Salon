"""
Tests for review search functionality with text index
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, MagicMock
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
def sample_reviews_for_search():
    """Create sample review data for search testing"""
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
            "service_name": "Color Treatment",
            "stylist_id": "stylist_2",
            "stylist_name": "Bob",
            "rating": 4,
            "comment": "Great color treatment, very satisfied with the results",
            "status": "approved",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
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
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    return reviews_data


class TestTextSearch:
    """Tests for text search functionality"""
    
    @pytest.mark.asyncio
    async def test_search_by_comment_text(self, review_service, mock_db, sample_reviews_for_search):
        """Test searching reviews by comment text"""
        tenant_id = "test_tenant_1"
        search_query = "excellent"
        
        # Filter reviews containing "excellent"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "excellent" in r["comment"].lower()
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 1
        assert "excellent" in result["reviews"][0]["comment"].lower()
    
    @pytest.mark.asyncio
    async def test_search_by_client_name(self, review_service, mock_db, sample_reviews_for_search):
        """Test searching reviews by client name"""
        tenant_id = "test_tenant_1"
        search_query = "Alice"
        
        # Filter reviews with client name containing "Alice"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "Alice" in r["client_name"]
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 1
        assert "Alice" in result["reviews"][0]["client_name"]
    
    @pytest.mark.asyncio
    async def test_search_by_service_name(self, review_service, mock_db, sample_reviews_for_search):
        """Test searching reviews by service name"""
        tenant_id = "test_tenant_1"
        search_query = "Color"
        
        # Filter reviews with service name containing "Color"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "Color" in r["service_name"]
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 2
        assert all("Color" in r["service_name"] for r in result["reviews"])
    
    @pytest.mark.asyncio
    async def test_search_by_stylist_name(self, review_service, mock_db, sample_reviews_for_search):
        """Test searching reviews by stylist name"""
        tenant_id = "test_tenant_1"
        search_query = "Bob"
        
        # Filter reviews with stylist name containing "Bob"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "Bob" in r["stylist_name"]
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 2
        assert all("Bob" in r["stylist_name"] for r in result["reviews"])
    
    @pytest.mark.asyncio
    async def test_search_multiple_word_query(self, review_service, mock_db, sample_reviews_for_search):
        """Test searching with multiple words"""
        tenant_id = "test_tenant_1"
        search_query = "professional service"
        
        # Filter reviews containing both words
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "professional" in r["comment"].lower() and "service" in r["comment"].lower()
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 1
        assert "professional" in result["reviews"][0]["comment"].lower()
    
    @pytest.mark.asyncio
    async def test_search_case_insensitive(self, review_service, mock_db, sample_reviews_for_search):
        """Test that search is case insensitive"""
        tenant_id = "test_tenant_1"
        search_query = "EXCELLENT"
        
        # Filter reviews containing "excellent" (case insensitive)
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "excellent" in r["comment"].lower()
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 1
    
    @pytest.mark.asyncio
    async def test_search_no_results(self, review_service, mock_db):
        """Test search with no matching results"""
        tenant_id = "test_tenant_1"
        search_query = "nonexistent"
        
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        assert result["total"] == 0
        assert result["reviews"] == []
    
    @pytest.mark.asyncio
    async def test_search_empty_query(self, review_service, mock_db, sample_reviews_for_search):
        """Test search with empty query returns all reviews"""
        tenant_id = "test_tenant_1"
        search_query = ""
        
        mock_db.reviews.count_documents.return_value = len(sample_reviews_for_search)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sample_reviews_for_search
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query if search_query else None
        )
        
        assert result["total"] == len(sample_reviews_for_search)


class TestSearchWithFilters:
    """Tests for combining search with other filters"""
    
    @pytest.mark.asyncio
    async def test_search_combined_with_status_filter(self, review_service, mock_db, sample_reviews_for_search):
        """Test search combined with status filter"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter by search and status
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "service" in r["comment"].lower() and r["status"] == "approved"
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            status="approved"
        )
        
        assert result["total"] == 1
        assert result["reviews"][0]["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_search_combined_with_rating_filter(self, review_service, mock_db, sample_reviews_for_search):
        """Test search combined with rating filter"""
        tenant_id = "test_tenant_1"
        search_query = "satisfied"
        
        # Filter by search and rating
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "satisfied" in r["comment"].lower() and r["rating"] >= 4
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            rating=[4, 5]
        )
        
        assert result["total"] == 1
        assert result["reviews"][0]["rating"] >= 4
    
    @pytest.mark.asyncio
    async def test_search_combined_with_service_filter(self, review_service, mock_db, sample_reviews_for_search):
        """Test search combined with service filter"""
        tenant_id = "test_tenant_1"
        search_query = "color"
        
        # Filter by search and service
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "color" in r["comment"].lower() and r["service_id"] == "service_2"
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            service_id="service_2"
        )
        
        assert result["total"] == 2
        assert all(r["service_id"] == "service_2" for r in result["reviews"])
    
    @pytest.mark.asyncio
    async def test_search_combined_with_stylist_filter(self, review_service, mock_db, sample_reviews_for_search):
        """Test search combined with stylist filter"""
        tenant_id = "test_tenant_1"
        search_query = "best"
        
        # Filter by search and stylist
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "best" in r["comment"].lower() and r["stylist_id"] == "stylist_2"
        ]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = matching_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            stylist_id="stylist_2"
        )
        
        assert result["total"] == 1
        assert result["reviews"][0]["stylist_id"] == "stylist_2"


class TestSearchWithPagination:
    """Tests for search with pagination"""
    
    @pytest.mark.asyncio
    async def test_search_with_pagination(self, review_service, mock_db, sample_reviews_for_search):
        """Test search results with pagination"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter reviews containing "service"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "service" in r["comment"].lower()
        ]
        
        # Get first page (limit 2)
        first_page = matching_reviews[:2]
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = first_page
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            skip=0,
            limit=2
        )
        
        assert result["total"] == len(matching_reviews)
        assert len(result["reviews"]) == 2
        assert result["skip"] == 0
        assert result["limit"] == 2


class TestSearchWithSorting:
    """Tests for search with sorting"""
    
    @pytest.mark.asyncio
    async def test_search_sorted_by_rating(self, review_service, mock_db, sample_reviews_for_search):
        """Test search results sorted by rating"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter reviews containing "service"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "service" in r["comment"].lower()
        ]
        
        # Sort by rating descending
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["rating"], reverse=True)
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            sort_by="rating",
            sort_order="desc"
        )
        
        ratings = [r["rating"] for r in result["reviews"]]
        assert ratings == sorted(ratings, reverse=True)
    
    @pytest.mark.asyncio
    async def test_search_sorted_by_date(self, review_service, mock_db, sample_reviews_for_search):
        """Test search results sorted by date"""
        tenant_id = "test_tenant_1"
        search_query = "service"
        
        # Filter reviews containing "service"
        matching_reviews = [
            r for r in sample_reviews_for_search 
            if "service" in r["comment"].lower()
        ]
        
        # Sort by created_at descending
        sorted_reviews = sorted(matching_reviews, key=lambda x: x["created_at"], reverse=True)
        
        mock_db.reviews.count_documents.return_value = len(matching_reviews)
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = sorted_reviews
        
        result = await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query,
            sort_by="created_at",
            sort_order="desc"
        )
        
        assert len(result["reviews"]) > 0


class TestSearchQueryBuilding:
    """Tests for search query building"""
    
    @pytest.mark.asyncio
    async def test_search_query_includes_text_operator(self, review_service, mock_db):
        """Test that search query includes $text operator"""
        tenant_id = "test_tenant_1"
        search_query = "excellent"
        
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        # Verify the query includes $text operator
        call_args = mock_db.reviews.find.call_args[0][0]
        assert "$text" in call_args
        assert "$search" in call_args["$text"]
        assert call_args["$text"]["$search"] == search_query
    
    @pytest.mark.asyncio
    async def test_search_query_with_tenant_filter(self, review_service, mock_db):
        """Test that search query includes tenant_id filter"""
        tenant_id = "test_tenant_1"
        search_query = "excellent"
        
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        await review_service.get_reviews_filtered(
            tenant_id=tenant_id,
            search=search_query
        )
        
        # Verify the query includes tenant_id
        call_args = mock_db.reviews.find.call_args[0][0]
        assert "tenant_id" in call_args
        assert call_args["tenant_id"] == tenant_id
