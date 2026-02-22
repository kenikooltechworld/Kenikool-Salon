"""
Tests for review service with status field
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, AsyncMock, patch
from app.services.review_service import ReviewService
from app.schemas.review import ReviewModerate


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.reviews = Mock()
    db.bookings = Mock()
    db.clients = Mock()
    db.services = Mock()
    db.stylists = Mock()
    return db


@pytest.fixture
def review_service(mock_db):
    """Create a review service instance"""
    return ReviewService(mock_db)


class TestGetReviews:
    """Tests for get_reviews method"""
    
    @pytest.mark.asyncio
    async def test_get_reviews_no_filters(self, review_service, mock_db):
        """Test getting reviews without filters"""
        # Setup
        tenant_id = "tenant123"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "status": "approved",
                "rating": 5,
                "comment": "Great service!",
                "created_at": datetime.utcnow()
            }
        ]
        mock_db.reviews.count_documents.return_value = 1
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_reviews
        
        # Execute
        result = await review_service.get_reviews(tenant_id=tenant_id)
        
        # Assert
        assert result["total"] == 1
        assert len(result["reviews"]) == 1
        assert result["reviews"][0]["status"] == "approved"
        mock_db.reviews.count_documents.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_reviews_with_status_filter(self, review_service, mock_db):
        """Test getting reviews filtered by status"""
        # Setup
        tenant_id = "tenant123"
        status = "approved"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "status": "approved",
                "rating": 5
            }
        ]
        mock_db.reviews.count_documents.return_value = 1
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_reviews
        
        # Execute
        result = await review_service.get_reviews(tenant_id=tenant_id, status=status)
        
        # Assert
        assert result["total"] == 1
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_get_reviews_with_service_filter(self, review_service, mock_db):
        """Test getting reviews filtered by service"""
        # Setup
        tenant_id = "tenant123"
        service_id = "service123"
        mock_reviews = []
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_reviews
        
        # Execute
        result = await review_service.get_reviews(
            tenant_id=tenant_id,
            service_id=service_id
        )
        
        # Assert
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["service_id"] == service_id
    
    @pytest.mark.asyncio
    async def test_get_reviews_with_stylist_filter(self, review_service, mock_db):
        """Test getting reviews filtered by stylist"""
        # Setup
        tenant_id = "tenant123"
        stylist_id = "stylist123"
        mock_reviews = []
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = mock_reviews
        
        # Execute
        result = await review_service.get_reviews(
            tenant_id=tenant_id,
            stylist_id=stylist_id
        )
        
        # Assert
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["stylist_id"] == stylist_id
    
    @pytest.mark.asyncio
    async def test_get_reviews_pagination(self, review_service, mock_db):
        """Test pagination parameters"""
        # Setup
        tenant_id = "tenant123"
        skip = 10
        limit = 50
        mock_db.reviews.count_documents.return_value = 100
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        # Execute
        result = await review_service.get_reviews(
            tenant_id=tenant_id,
            skip=skip,
            limit=limit
        )
        
        # Assert
        assert result["skip"] == skip
        assert result["limit"] == limit
        assert result["total"] == 100


class TestCreateReview:
    """Tests for create_review method"""
    
    @pytest.mark.asyncio
    async def test_create_review_success(self, review_service, mock_db):
        """Test successful review creation"""
        # Setup
        tenant_id = "tenant123"
        booking_id = str(ObjectId())
        client_id = str(ObjectId())
        
        mock_booking = {
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "status": "completed",
            "service_id": ObjectId(),
            "stylist_id": ObjectId()
        }
        mock_client = {"_id": ObjectId(client_id), "name": "John Doe"}
        mock_service = {"_id": ObjectId(), "name": "Haircut"}
        mock_stylist = {"_id": ObjectId(), "name": "Jane Smith"}
        
        mock_db.bookings.find_one.return_value = mock_booking
        mock_db.clients.find_one.return_value = mock_client
        mock_db.services.find_one.return_value = mock_service
        mock_db.stylists.find_one.return_value = mock_stylist
        mock_db.reviews.find_one.return_value = None
        mock_db.reviews.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Execute
        result = await review_service.create_review(
            tenant_id=tenant_id,
            booking_id=booking_id,
            client_id=client_id,
            rating=5,
            comment="Great service!"
        )
        
        # Assert
        assert result["status"] == "pending"
        assert result["rating"] == 5
        assert result["comment"] == "Great service!"
        assert result["client_name"] == "John Doe"
        assert result["service_name"] == "Haircut"
        assert result["stylist_name"] == "Jane Smith"
    
    @pytest.mark.asyncio
    async def test_create_review_booking_not_found(self, review_service, mock_db):
        """Test review creation with non-existent booking"""
        # Setup
        mock_db.bookings.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Booking not found"):
            await review_service.create_review(
                tenant_id="tenant123",
                booking_id="booking123",
                client_id="client123",
                rating=5
            )
    
    @pytest.mark.asyncio
    async def test_create_review_already_reviewed(self, review_service, mock_db):
        """Test review creation when booking already reviewed"""
        # Setup
        booking_id = "booking123"
        mock_booking = {
            "_id": ObjectId(booking_id),
            "status": "completed",
            "service_id": ObjectId(),
            "stylist_id": ObjectId()
        }
        mock_db.bookings.find_one.return_value = mock_booking
        mock_db.reviews.find_one.return_value = {"_id": ObjectId()}  # Already reviewed
        
        # Execute & Assert
        with pytest.raises(ValueError, match="already been reviewed"):
            await review_service.create_review(
                tenant_id="tenant123",
                booking_id=booking_id,
                client_id="client123",
                rating=5
            )


class TestModerateReview:
    """Tests for moderate_review method"""
    
    @pytest.mark.asyncio
    async def test_moderate_review_approve(self, review_service, mock_db):
        """Test approving a review"""
        # Setup
        review_id = str(ObjectId())
        tenant_id = "tenant123"
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id,
            "status": "pending"
        }
        mock_db.reviews.find_one.return_value = mock_review
        mock_db.reviews.update_one.return_value = Mock()
        
        # Execute
        result = await review_service.moderate_review(
            review_id=review_id,
            tenant_id=tenant_id,
            status="approved"
        )
        
        # Assert
        mock_db.reviews.update_one.assert_called_once()
        call_args = mock_db.reviews.update_one.call_args
        assert call_args[0][1]["$set"]["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_moderate_review_reject(self, review_service, mock_db):
        """Test rejecting a review"""
        # Setup
        review_id = str(ObjectId())
        tenant_id = "tenant123"
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id,
            "status": "pending"
        }
        mock_db.reviews.find_one.return_value = mock_review
        mock_db.reviews.update_one.return_value = Mock()
        
        # Execute
        result = await review_service.moderate_review(
            review_id=review_id,
            tenant_id=tenant_id,
            status="rejected"
        )
        
        # Assert
        call_args = mock_db.reviews.update_one.call_args
        assert call_args[0][1]["$set"]["status"] == "rejected"
    
    @pytest.mark.asyncio
    async def test_moderate_review_invalid_status(self, review_service, mock_db):
        """Test moderation with invalid status"""
        # Setup
        review_id = str(ObjectId())
        tenant_id = "tenant123"
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid status"):
            await review_service.moderate_review(
                review_id=review_id,
                tenant_id=tenant_id,
                status="invalid_status"
            )
    
    @pytest.mark.asyncio
    async def test_moderate_review_not_found(self, review_service, mock_db):
        """Test moderation of non-existent review"""
        # Setup
        mock_db.reviews.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Review not found"):
            await review_service.moderate_review(
                review_id="review123",
                tenant_id="tenant123",
                status="approved"
            )


class TestGetRatingAggregation:
    """Tests for get_rating_aggregation method"""
    
    @pytest.mark.asyncio
    async def test_get_rating_aggregation_success(self, review_service, mock_db):
        """Test successful rating aggregation"""
        # Setup
        tenant_id = "tenant123"
        aggregation_result = [{
            "_id": None,
            "average_rating": 4.5,
            "total_reviews": 10,
            "rating_1": 0,
            "rating_2": 1,
            "rating_3": 2,
            "rating_4": 3,
            "rating_5": 4
        }]
        mock_db.reviews.aggregate.return_value = aggregation_result
        
        # Execute
        result = await review_service.get_rating_aggregation(tenant_id=tenant_id)
        
        # Assert
        assert result["average_rating"] == 4.5
        assert result["total_reviews"] == 10
        assert result["rating_distribution"]["5"] == 4
    
    @pytest.mark.asyncio
    async def test_get_rating_aggregation_no_reviews(self, review_service, mock_db):
        """Test rating aggregation with no reviews"""
        # Setup
        tenant_id = "tenant123"
        mock_db.reviews.aggregate.return_value = []
        
        # Execute
        result = await review_service.get_rating_aggregation(tenant_id=tenant_id)
        
        # Assert
        assert result["average_rating"] == 0.0
        assert result["total_reviews"] == 0
        assert all(count == 0 for count in result["rating_distribution"].values())
    
    @pytest.mark.asyncio
    async def test_get_rating_aggregation_by_service(self, review_service, mock_db):
        """Test rating aggregation filtered by service"""
        # Setup
        tenant_id = "tenant123"
        service_id = "service123"
        aggregation_result = [{
            "_id": None,
            "average_rating": 4.0,
            "total_reviews": 5,
            "rating_1": 0,
            "rating_2": 0,
            "rating_3": 1,
            "rating_4": 2,
            "rating_5": 2
        }]
        mock_db.reviews.aggregate.return_value = aggregation_result
        
        # Execute
        result = await review_service.get_rating_aggregation(
            tenant_id=tenant_id,
            service_id=service_id
        )
        
        # Assert
        assert result["average_rating"] == 4.0
        assert result["total_reviews"] == 5
        # Verify the query includes service_id filter
        call_args = mock_db.reviews.aggregate.call_args[0][0]
        assert call_args[0]["$match"]["service_id"] == service_id
    
    @pytest.mark.asyncio
    async def test_get_rating_aggregation_by_stylist(self, review_service, mock_db):
        """Test rating aggregation filtered by stylist"""
        # Setup
        tenant_id = "tenant123"
        stylist_id = "stylist123"
        aggregation_result = [{
            "_id": None,
            "average_rating": 4.8,
            "total_reviews": 5,
            "rating_1": 0,
            "rating_2": 0,
            "rating_3": 0,
            "rating_4": 1,
            "rating_5": 4
        }]
        mock_db.reviews.aggregate.return_value = aggregation_result
        
        # Execute
        result = await review_service.get_rating_aggregation(
            tenant_id=tenant_id,
            stylist_id=stylist_id
        )
        
        # Assert
        assert result["average_rating"] == 4.8
        # Verify the query includes stylist_id filter
        call_args = mock_db.reviews.aggregate.call_args[0][0]
        assert call_args[0]["$match"]["stylist_id"] == stylist_id


class TestStatusFieldMigration:
    """Tests to verify status field is used instead of is_approved"""
    
    @pytest.mark.asyncio
    async def test_review_uses_status_not_is_approved(self, review_service, mock_db):
        """Verify that reviews use status field, not is_approved"""
        # Setup
        tenant_id = "tenant123"
        booking_id = str(ObjectId())
        client_id = str(ObjectId())
        
        mock_booking = {
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "status": "completed",
            "service_id": ObjectId(),
            "stylist_id": ObjectId()
        }
        mock_client = {"_id": ObjectId(client_id), "name": "John Doe"}
        mock_service = {"_id": ObjectId(), "name": "Haircut"}
        mock_stylist = {"_id": ObjectId(), "name": "Jane Smith"}
        
        mock_db.bookings.find_one.return_value = mock_booking
        mock_db.clients.find_one.return_value = mock_client
        mock_db.services.find_one.return_value = mock_service
        mock_db.stylists.find_one.return_value = mock_stylist
        mock_db.reviews.find_one.return_value = None
        mock_db.reviews.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Execute
        result = await review_service.create_review(
            tenant_id=tenant_id,
            booking_id=booking_id,
            client_id=client_id,
            rating=5,
            comment="Great service!"
        )
        
        # Assert - verify status field exists and is_approved does not
        assert "status" in result
        assert "is_approved" not in result
        assert result["status"] == "pending"
    
    @pytest.mark.asyncio
    async def test_get_reviews_filters_by_status(self, review_service, mock_db):
        """Verify that get_reviews filters by status, not is_approved"""
        # Setup
        tenant_id = "tenant123"
        mock_db.reviews.count_documents.return_value = 0
        mock_db.reviews.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
        
        # Execute
        await review_service.get_reviews(tenant_id=tenant_id, status="approved")
        
        # Assert - verify query uses status field
        call_args = mock_db.reviews.find.call_args[0][0]
        assert "status" in call_args
        assert "is_approved" not in call_args
        assert call_args["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_rating_aggregation_uses_status(self, review_service, mock_db):
        """Verify that rating aggregation uses status field"""
        # Setup
        tenant_id = "tenant123"
        mock_db.reviews.aggregate.return_value = []
        
        # Execute
        await review_service.get_rating_aggregation(tenant_id=tenant_id)
        
        # Assert - verify aggregation pipeline uses status field
        call_args = mock_db.reviews.aggregate.call_args[0][0]
        match_query = call_args[0]["$match"]
        assert "status" in match_query
        assert "is_approved" not in match_query
        assert match_query["status"] == "approved"



class TestExportToCSV:
    """Tests for export_to_csv method"""
    
    @pytest.mark.asyncio
    async def test_export_to_csv_success(self, review_service, mock_db):
        """Test successful CSV export"""
        # Setup
        tenant_id = "tenant123"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "John Doe",
                "service_name": "Haircut",
                "stylist_name": "Jane Smith",
                "rating": 5,
                "comment": "Great service!",
                "status": "approved",
                "created_at": datetime(2024, 1, 15, 10, 30, 0),
                "response": {"text": "Thank you!"}
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "Jane Doe",
                "service_name": "Color",
                "stylist_name": "John Smith",
                "rating": 4,
                "comment": "Good service",
                "status": "approved",
                "created_at": datetime(2024, 1, 14, 14, 0, 0),
                "response": None
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_csv(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(result, str)
        assert "date,client_name,service,stylist,rating,comment,status,response" in result
        assert "John Doe" in result
        assert "Jane Doe" in result
        assert "Haircut" in result
        assert "Color" in result
        assert "5" in result
        assert "4" in result
        assert "Great service!" in result
        assert "Thank you!" in result
    
    @pytest.mark.asyncio
    async def test_export_to_csv_with_filters(self, review_service, mock_db):
        """Test CSV export with filters applied"""
        # Setup
        tenant_id = "tenant123"
        status = "approved"
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_csv(
            tenant_id=tenant_id,
            status=status
        )
        
        # Assert
        assert isinstance(result, str)
        # Verify the query was built with filters
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_export_to_csv_empty_results(self, review_service, mock_db):
        """Test CSV export with no reviews"""
        # Setup
        tenant_id = "tenant123"
        mock_db.reviews.find.return_value.sort.return_value = []
        
        # Execute
        result = await review_service.export_to_csv(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(result, str)
        assert "date,client_name,service,stylist,rating,comment,status,response" in result
        # Should only have header row
        lines = result.strip().split('\n')
        assert len(lines) == 1
    
    @pytest.mark.asyncio
    async def test_export_to_csv_with_date_range(self, review_service, mock_db):
        """Test CSV export with date range filter"""
        # Setup
        tenant_id = "tenant123"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_csv(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert
        assert isinstance(result, str)
        # Verify date range was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert "created_at" in call_args


class TestExportToPDF:
    """Tests for export_to_pdf method"""
    
    @pytest.mark.asyncio
    async def test_export_to_pdf_success(self, review_service, mock_db):
        """Test successful PDF export"""
        # Setup
        tenant_id = "tenant123"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "John Doe",
                "service_name": "Haircut",
                "stylist_name": "Jane Smith",
                "rating": 5,
                "comment": "Great service!",
                "status": "approved",
                "created_at": datetime(2024, 1, 15, 10, 30, 0)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "Jane Doe",
                "service_name": "Color",
                "stylist_name": "John Smith",
                "rating": 4,
                "comment": "Good service",
                "status": "approved",
                "created_at": datetime(2024, 1, 14, 14, 0, 0)
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_pdf(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(result, bytes)
        assert len(result) > 0
        # PDF files start with %PDF
        assert result.startswith(b'%PDF')
    
    @pytest.mark.asyncio
    async def test_export_to_pdf_with_filters(self, review_service, mock_db):
        """Test PDF export with filters applied"""
        # Setup
        tenant_id = "tenant123"
        status = "approved"
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_pdf(
            tenant_id=tenant_id,
            status=status
        )
        
        # Assert
        assert isinstance(result, bytes)
        assert result.startswith(b'%PDF')
        # Verify the query was built with filters
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_export_to_pdf_empty_results(self, review_service, mock_db):
        """Test PDF export with no reviews"""
        # Setup
        tenant_id = "tenant123"
        mock_db.reviews.find.return_value.sort.return_value = []
        
        # Execute
        result = await review_service.export_to_pdf(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(result, bytes)
        assert result.startswith(b'%PDF')
        assert len(result) > 0
    
    @pytest.mark.asyncio
    async def test_export_to_pdf_calculates_statistics(self, review_service, mock_db):
        """Test that PDF export calculates summary statistics"""
        # Setup
        tenant_id = "tenant123"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "John Doe",
                "service_name": "Haircut",
                "stylist_name": "Jane Smith",
                "rating": 5,
                "comment": "Great!",
                "status": "approved",
                "created_at": datetime(2024, 1, 15)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "Jane Doe",
                "service_name": "Color",
                "stylist_name": "John Smith",
                "rating": 4,
                "comment": "Good",
                "status": "approved",
                "created_at": datetime(2024, 1, 14)
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "Bob Smith",
                "service_name": "Trim",
                "stylist_name": "Jane Smith",
                "rating": 3,
                "comment": "OK",
                "status": "rejected",
                "created_at": datetime(2024, 1, 13)
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_pdf(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(result, bytes)
        assert result.startswith(b'%PDF')
        # PDF should contain statistics
        assert len(result) > 1000  # Should be substantial with statistics
    
    @pytest.mark.asyncio
    async def test_export_to_pdf_with_date_range(self, review_service, mock_db):
        """Test PDF export with date range filter"""
        # Setup
        tenant_id = "tenant123"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        result = await review_service.export_to_pdf(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert
        assert isinstance(result, bytes)
        assert result.startswith(b'%PDF')
        # Verify date range was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert "created_at" in call_args
