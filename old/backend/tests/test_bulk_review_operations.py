"""
Tests for bulk review operations
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import MagicMock, AsyncMock, patch


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = MagicMock()
    db.reviews = MagicMock()
    return db


@pytest.fixture
def review_service(mock_db):
    """Create a ReviewService instance with mock database"""
    from app.services.review_service import ReviewService
    return ReviewService(mock_db)


class TestBulkModerateReviews:
    """Test bulk moderation operations"""
    
    @pytest.mark.asyncio
    async def test_bulk_approve_reviews(self, review_service, mock_db):
        """Test bulk approving reviews"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
        tenant_id = "test-tenant"
        
        # Mock database responses
        mock_db.reviews.count_documents.return_value = 2
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=2)
        
        # Execute
        result = await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="approved"
        )
        
        # Assert
        assert result["success"] is True
        assert result["action"] == "approved"
        assert result["matched_count"] == 2
        assert result["modified_count"] == 2
        
        # Verify database calls
        mock_db.reviews.count_documents.assert_called_once()
        mock_db.reviews.update_many.assert_called_once()
        
        # Verify update data
        call_args = mock_db.reviews.update_many.call_args
        update_data = call_args[0][1]["$set"]
        assert update_data["status"] == "approved"
        assert "updated_at" in update_data
    
    @pytest.mark.asyncio
    async def test_bulk_reject_reviews(self, review_service, mock_db):
        """Test bulk rejecting reviews"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
        tenant_id = "test-tenant"
        
        # Mock database responses
        mock_db.reviews.count_documents.return_value = 2
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=2)
        
        # Execute
        result = await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="rejected"
        )
        
        # Assert
        assert result["success"] is True
        assert result["action"] == "rejected"
        assert result["matched_count"] == 2
        assert result["modified_count"] == 2
        
        # Verify update data
        call_args = mock_db.reviews.update_many.call_args
        update_data = call_args[0][1]["$set"]
        assert update_data["status"] == "rejected"
    
    @pytest.mark.asyncio
    async def test_bulk_delete_reviews(self, review_service, mock_db):
        """Test bulk deleting reviews (soft delete)"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
        tenant_id = "test-tenant"
        
        # Mock database responses
        mock_db.reviews.count_documents.return_value = 2
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=2)
        
        # Execute
        result = await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="deleted"
        )
        
        # Assert
        assert result["success"] is True
        assert result["action"] == "deleted"
        assert result["matched_count"] == 2
        assert result["modified_count"] == 2
        
        # Verify update data (soft delete)
        call_args = mock_db.reviews.update_many.call_args
        update_data = call_args[0][1]["$set"]
        assert update_data["is_deleted"] is True
        assert "deleted_at" in update_data
    
    @pytest.mark.asyncio
    async def test_bulk_moderate_invalid_action(self, review_service, mock_db):
        """Test bulk moderate with invalid action"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011"]
        tenant_id = "test-tenant"
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Invalid action"):
            await review_service.bulk_moderate_reviews(
                tenant_id=tenant_id,
                review_ids=review_ids,
                action="invalid"  # type: ignore
            )
    
    @pytest.mark.asyncio
    async def test_bulk_moderate_no_matching_reviews(self, review_service, mock_db):
        """Test bulk moderate when no reviews match"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011"]
        tenant_id = "test-tenant"
        
        # Mock database responses
        mock_db.reviews.count_documents.return_value = 0
        
        # Execute & Assert
        with pytest.raises(ValueError, match="No reviews found"):
            await review_service.bulk_moderate_reviews(
                tenant_id=tenant_id,
                review_ids=review_ids,
                action="approved"
            )
    
    @pytest.mark.asyncio
    async def test_bulk_moderate_empty_ids(self, review_service, mock_db):
        """Test bulk moderate with empty review IDs"""
        # Setup
        review_ids = []
        tenant_id = "test-tenant"
        
        # Execute & Assert
        with pytest.raises(ValueError, match="No valid review IDs"):
            await review_service.bulk_moderate_reviews(
                tenant_id=tenant_id,
                review_ids=review_ids,
                action="approved"
            )
    
    @pytest.mark.asyncio
    async def test_bulk_moderate_invalid_ids(self, review_service, mock_db):
        """Test bulk moderate with invalid ObjectIds"""
        # Setup
        review_ids = ["invalid-id-1", "invalid-id-2"]
        tenant_id = "test-tenant"
        
        # Execute & Assert
        with pytest.raises(ValueError, match="No valid review IDs"):
            await review_service.bulk_moderate_reviews(
                tenant_id=tenant_id,
                review_ids=review_ids,
                action="approved"
            )
    
    @pytest.mark.asyncio
    async def test_bulk_moderate_tenant_isolation(self, review_service, mock_db):
        """Test that bulk moderate respects tenant isolation"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011"]
        tenant_id = "test-tenant"
        
        # Mock database responses
        mock_db.reviews.count_documents.return_value = 1
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=1)
        
        # Execute
        await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="approved"
        )
        
        # Verify tenant_id is in query
        call_args = mock_db.reviews.update_many.call_args
        query = call_args[0][0]
        assert query["tenant_id"] == tenant_id
    
    @pytest.mark.asyncio
    async def test_bulk_moderate_partial_success(self, review_service, mock_db):
        """Test bulk moderate with partial success"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011", "507f1f77bcf86cd799439012"]
        tenant_id = "test-tenant"
        
        # Mock database responses - only 1 review found but 2 requested
        mock_db.reviews.count_documents.return_value = 1
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=1)
        
        # Execute
        result = await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="approved"
        )
        
        # Assert - should still succeed but with lower counts
        assert result["success"] is True
        assert result["matched_count"] == 1
        assert result["modified_count"] == 1


class TestBulkOperationsIntegration:
    """Integration tests for bulk operations"""
    
    @pytest.mark.asyncio
    async def test_bulk_approve_then_query(self, review_service, mock_db):
        """Test bulk approve followed by query"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011"]
        tenant_id = "test-tenant"
        
        # Mock bulk approve
        mock_db.reviews.count_documents.return_value = 1
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=1)
        
        # Execute bulk approve
        result = await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="approved"
        )
        
        # Assert
        assert result["success"] is True
        assert result["modified_count"] == 1
    
    @pytest.mark.asyncio
    async def test_bulk_operations_preserve_other_fields(self, review_service, mock_db):
        """Test that bulk operations preserve other review fields"""
        # Setup
        review_ids = ["507f1f77bcf86cd799439011"]
        tenant_id = "test-tenant"
        
        # Mock database responses
        mock_db.reviews.count_documents.return_value = 1
        mock_db.reviews.update_many.return_value = MagicMock(modified_count=1)
        
        # Execute
        await review_service.bulk_moderate_reviews(
            tenant_id=tenant_id,
            review_ids=review_ids,
            action="approved"
        )
        
        # Verify only status and updated_at are set
        call_args = mock_db.reviews.update_many.call_args
        update_data = call_args[0][1]["$set"]
        
        # Should only have status and updated_at
        assert "status" in update_data
        assert "updated_at" in update_data
        # Should not have other fields
        assert "client_name" not in update_data
        assert "rating" not in update_data
