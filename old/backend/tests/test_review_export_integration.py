"""
Integration tests for review export functionality
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from app.api.reviews import router
from app.services.review_service import ReviewService


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


class TestExportEndpoints:
    """Tests for export API endpoints"""
    
    @pytest.mark.asyncio
    async def test_export_csv_endpoint(self, review_service, mock_db):
        """Test CSV export endpoint"""
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
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        csv_content = await review_service.export_to_csv(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(csv_content, str)
        assert "date,client_name,service,stylist,rating,comment,status,response" in csv_content
        assert "John Doe" in csv_content
        assert "Haircut" in csv_content
        assert "5" in csv_content
        assert "Great service!" in csv_content
    
    @pytest.mark.asyncio
    async def test_export_pdf_endpoint(self, review_service, mock_db):
        """Test PDF export endpoint"""
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
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        pdf_bytes = await review_service.export_to_pdf(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF')
        assert len(pdf_bytes) > 0
    
    @pytest.mark.asyncio
    async def test_export_csv_with_status_filter(self, review_service, mock_db):
        """Test CSV export with status filter"""
        # Setup
        tenant_id = "tenant123"
        status = "approved"
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        csv_content = await review_service.export_to_csv(
            tenant_id=tenant_id,
            status=status
        )
        
        # Assert
        assert isinstance(csv_content, str)
        # Verify filter was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["status"] == "approved"
    
    @pytest.mark.asyncio
    async def test_export_pdf_with_rating_filter(self, review_service, mock_db):
        """Test PDF export with rating filter"""
        # Setup
        tenant_id = "tenant123"
        rating = [4, 5]
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        pdf_bytes = await review_service.export_to_pdf(
            tenant_id=tenant_id,
            rating=rating
        )
        
        # Assert
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF')
        # Verify filter was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["rating"]["$in"] == rating
    
    @pytest.mark.asyncio
    async def test_export_csv_with_service_filter(self, review_service, mock_db):
        """Test CSV export with service filter"""
        # Setup
        tenant_id = "tenant123"
        service_id = "service123"
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        csv_content = await review_service.export_to_csv(
            tenant_id=tenant_id,
            service_id=service_id
        )
        
        # Assert
        assert isinstance(csv_content, str)
        # Verify filter was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["service_id"] == service_id
    
    @pytest.mark.asyncio
    async def test_export_pdf_with_stylist_filter(self, review_service, mock_db):
        """Test PDF export with stylist filter"""
        # Setup
        tenant_id = "tenant123"
        stylist_id = "stylist123"
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        pdf_bytes = await review_service.export_to_pdf(
            tenant_id=tenant_id,
            stylist_id=stylist_id
        )
        
        # Assert
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF')
        # Verify filter was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["stylist_id"] == stylist_id
    
    @pytest.mark.asyncio
    async def test_export_csv_with_date_range(self, review_service, mock_db):
        """Test CSV export with date range filter"""
        # Setup
        tenant_id = "tenant123"
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        csv_content = await review_service.export_to_csv(
            tenant_id=tenant_id,
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert
        assert isinstance(csv_content, str)
        # Verify date range was applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert "created_at" in call_args
        assert call_args["created_at"]["$gte"] == start_date
        assert call_args["created_at"]["$lte"] == end_date
    
    @pytest.mark.asyncio
    async def test_export_pdf_with_multiple_filters(self, review_service, mock_db):
        """Test PDF export with multiple filters"""
        # Setup
        tenant_id = "tenant123"
        status = "approved"
        rating = [4, 5]
        service_id = "service123"
        mock_reviews = []
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        pdf_bytes = await review_service.export_to_pdf(
            tenant_id=tenant_id,
            status=status,
            rating=rating,
            service_id=service_id
        )
        
        # Assert
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF')
        # Verify all filters were applied
        call_args = mock_db.reviews.find.call_args[0][0]
        assert call_args["status"] == status
        assert call_args["rating"]["$in"] == rating
        assert call_args["service_id"] == service_id
    
    @pytest.mark.asyncio
    async def test_export_csv_handles_null_values(self, review_service, mock_db):
        """Test CSV export handles null/missing values gracefully"""
        # Setup
        tenant_id = "tenant123"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": "John Doe",
                "service_name": None,  # Missing service
                "stylist_name": "Jane Smith",
                "rating": 5,
                "comment": None,  # Missing comment
                "status": "approved",
                "created_at": datetime(2024, 1, 15),
                # No response field
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        csv_content = await review_service.export_to_csv(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(csv_content, str)
        assert "John Doe" in csv_content
        # Should handle missing values without errors
        lines = csv_content.strip().split('\n')
        assert len(lines) == 2  # Header + 1 data row
    
    @pytest.mark.asyncio
    async def test_export_pdf_calculates_statistics_correctly(self, review_service, mock_db):
        """Test PDF export calculates statistics correctly"""
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
        pdf_bytes = await review_service.export_to_pdf(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(pdf_bytes, bytes)
        assert pdf_bytes.startswith(b'%PDF')
        # PDF should be substantial with statistics
        assert len(pdf_bytes) > 1000
    
    @pytest.mark.asyncio
    async def test_export_csv_escapes_special_characters(self, review_service, mock_db):
        """Test CSV export properly escapes special characters"""
        # Setup
        tenant_id = "tenant123"
        mock_reviews = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "client_name": 'John "The Great" Doe',
                "service_name": "Hair, Cut & Style",
                "stylist_name": "Jane Smith",
                "rating": 5,
                "comment": 'Great service! "Highly recommended"',
                "status": "approved",
                "created_at": datetime(2024, 1, 15),
                "response": None
            }
        ]
        mock_db.reviews.find.return_value.sort.return_value = mock_reviews
        
        # Execute
        csv_content = await review_service.export_to_csv(tenant_id=tenant_id)
        
        # Assert
        assert isinstance(csv_content, str)
        # CSV should properly escape quotes and commas
        assert 'John "The Great" Doe' in csv_content or 'John \\"The Great\\" Doe' in csv_content
        assert "Hair, Cut & Style" in csv_content or '"Hair, Cut & Style"' in csv_content
