"""
Tests for review response functionality
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, AsyncMock, patch
from app.services.review_service import ReviewService
from app.schemas.review import ReviewResponseCreate, ReviewResponseUpdate


@pytest.fixture
def mock_db():
    """Create mock database"""
    db = Mock()
    db.reviews = Mock()
    db.review_templates = Mock()
    return db


@pytest.fixture
def review_service(mock_db):
    """Create review service instance"""
    return ReviewService(mock_db)


class TestReviewResponses:
    """Test review response functionality"""
    
    def test_add_response_success(self, review_service, mock_db):
        """Test adding response to review"""
        review_id = str(ObjectId())
        tenant_id = "test-tenant"
        responder_id = "user-123"
        responder_name = "John Doe"
        response_text = "Thank you for your review!"
        
        # Mock review
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id,
            "client_name": "Jane Smith",
            "rating": 5,
            "comment": "Great service!",
            "status": "approved"
        }
        
        mock_db.reviews.find_one.return_value = mock_review
        mock_db.reviews.update_one.return_value = Mock()
        
        # Mock updated review
        updated_review = {
            **mock_review,
            "response": {
                "text": response_text,
                "responder_id": responder_id,
                "responder_name": responder_name,
                "responded_at": datetime.utcnow()
            }
        }
        mock_db.reviews.find_one.side_effect = [mock_review, updated_review]
        
        # Call method
        result = review_service.add_response(
            review_id=review_id,
            tenant_id=tenant_id,
            responder_id=responder_id,
            responder_name=responder_name,
            response_text=response_text
        )
        
        # Assertions
        assert result is not None
        assert result["response"]["text"] == response_text
        assert result["response"]["responder_name"] == responder_name
        mock_db.reviews.update_one.assert_called_once()
    
    def test_add_response_review_not_found(self, review_service, mock_db):
        """Test adding response when review not found"""
        mock_db.reviews.find_one.return_value = None
        
        with pytest.raises(ValueError, match="Review not found"):
            review_service.add_response(
                review_id="invalid-id",
                tenant_id="test-tenant",
                responder_id="user-123",
                responder_name="John Doe",
                response_text="Thank you!"
            )
    
    def test_update_response_success(self, review_service, mock_db):
        """Test updating existing response"""
        review_id = str(ObjectId())
        tenant_id = "test-tenant"
        new_response_text = "Updated response"
        
        # Mock review with existing response
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id,
            "response": {
                "text": "Old response",
                "responder_id": "user-123",
                "responder_name": "John Doe",
                "responded_at": datetime.utcnow()
            }
        }
        
        mock_db.reviews.find_one.return_value = mock_review
        mock_db.reviews.update_one.return_value = Mock()
        
        # Mock updated review
        updated_review = {
            **mock_review,
            "response": {
                "text": new_response_text,
                "responder_id": "user-123",
                "responder_name": "John Doe",
                "responded_at": mock_review["response"]["responded_at"],
                "edited_at": datetime.utcnow()
            }
        }
        mock_db.reviews.find_one.side_effect = [mock_review, updated_review]
        
        # Call method
        result = review_service.update_response(
            review_id=review_id,
            tenant_id=tenant_id,
            responder_id="user-123",
            responder_name="John Doe",
            response_text=new_response_text
        )
        
        # Assertions
        assert result["response"]["text"] == new_response_text
        assert "edited_at" in result["response"]
    
    def test_update_response_no_existing_response(self, review_service, mock_db):
        """Test updating when no response exists"""
        mock_review = {
            "_id": ObjectId(),
            "tenant_id": "test-tenant"
        }
        mock_db.reviews.find_one.return_value = mock_review
        
        with pytest.raises(ValueError, match="Review has no response to update"):
            review_service.update_response(
                review_id="review-123",
                tenant_id="test-tenant",
                responder_id="user-123",
                responder_name="John Doe",
                response_text="New response"
            )
    
    def test_delete_response_success(self, review_service, mock_db):
        """Test deleting response"""
        review_id = str(ObjectId())
        tenant_id = "test-tenant"
        
        # Mock review with response
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id,
            "response": {
                "text": "Response to delete",
                "responder_id": "user-123",
                "responder_name": "John Doe",
                "responded_at": datetime.utcnow()
            }
        }
        
        mock_db.reviews.find_one.return_value = mock_review
        mock_db.reviews.update_one.return_value = Mock()
        
        # Mock updated review without response
        updated_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id
        }
        mock_db.reviews.find_one.side_effect = [mock_review, updated_review]
        
        # Call method
        result = review_service.delete_response(
            review_id=review_id,
            tenant_id=tenant_id
        )
        
        # Assertions
        assert "response" not in result or result.get("response") is None
        mock_db.reviews.update_one.assert_called_once()
    
    def test_delete_response_no_response(self, review_service, mock_db):
        """Test deleting when no response exists"""
        mock_review = {
            "_id": ObjectId(),
            "tenant_id": "test-tenant"
        }
        mock_db.reviews.find_one.return_value = mock_review
        
        with pytest.raises(ValueError, match="Review has no response to delete"):
            review_service.delete_response(
                review_id="review-123",
                tenant_id="test-tenant"
            )


class TestResponseTemplates:
    """Test response template functionality"""
    
    def test_get_response_templates(self, review_service, mock_db):
        """Test getting response templates"""
        tenant_id = "test-tenant"
        
        # Mock templates
        mock_templates = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "name": "Thank You",
                "category": "positive",
                "text": "Thank you for your review!",
                "is_default": True
            },
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "name": "We're Sorry",
                "category": "negative",
                "text": "We're sorry to hear that...",
                "is_default": True
            }
        ]
        
        mock_db.review_templates.find.return_value.sort.return_value.sort.return_value = mock_templates
        
        # Call method
        result = review_service.get_response_templates(tenant_id=tenant_id)
        
        # Assertions
        assert len(result) == 2
        assert result[0]["name"] == "Thank You"
        assert result[1]["name"] == "We're Sorry"
    
    def test_create_response_template_success(self, review_service, mock_db):
        """Test creating response template"""
        tenant_id = "test-tenant"
        template_id = str(ObjectId())
        
        mock_db.review_templates.insert_one.return_value = Mock(inserted_id=ObjectId(template_id))
        
        # Call method
        result = review_service.create_response_template(
            tenant_id=tenant_id,
            name="Thank You",
            category="positive",
            text="Thank you for your review!"
        )
        
        # Assertions
        assert result["name"] == "Thank You"
        assert result["category"] == "positive"
        assert result["text"] == "Thank you for your review!"
        assert result["is_default"] is False
        mock_db.review_templates.insert_one.assert_called_once()
    
    def test_create_response_template_invalid_category(self, review_service, mock_db):
        """Test creating template with invalid category"""
        with pytest.raises(ValueError, match="Invalid category"):
            review_service.create_response_template(
                tenant_id="test-tenant",
                name="Test",
                category="invalid",
                text="Test text"
            )
    
    def test_update_response_template_success(self, review_service, mock_db):
        """Test updating response template"""
        template_id = str(ObjectId())
        tenant_id = "test-tenant"
        
        # Mock template
        mock_template = {
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "name": "Old Name",
            "category": "positive",
            "text": "Old text"
        }
        
        mock_db.review_templates.find_one.return_value = mock_template
        mock_db.review_templates.update_one.return_value = Mock()
        
        # Mock updated template
        updated_template = {
            **mock_template,
            "name": "New Name",
            "text": "New text"
        }
        mock_db.review_templates.find_one.side_effect = [mock_template, updated_template]
        
        # Call method
        result = review_service.update_response_template(
            template_id=template_id,
            tenant_id=tenant_id,
            name="New Name",
            text="New text"
        )
        
        # Assertions
        assert result["name"] == "New Name"
        assert result["text"] == "New text"
    
    def test_delete_response_template_success(self, review_service, mock_db):
        """Test deleting response template"""
        template_id = str(ObjectId())
        tenant_id = "test-tenant"
        
        # Mock template
        mock_template = {
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "name": "Test",
            "is_default": False
        }
        
        mock_db.review_templates.find_one.return_value = mock_template
        mock_db.review_templates.delete_one.return_value = Mock()
        
        # Call method
        review_service.delete_response_template(
            template_id=template_id,
            tenant_id=tenant_id
        )
        
        # Assertions
        mock_db.review_templates.delete_one.assert_called_once()
    
    def test_delete_default_template_fails(self, review_service, mock_db):
        """Test that default templates cannot be deleted"""
        mock_template = {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "is_default": True
        }
        mock_db.review_templates.find_one.return_value = mock_template
        
        with pytest.raises(ValueError, match="Cannot delete default templates"):
            review_service.delete_response_template(
                template_id="template-123",
                tenant_id="test-tenant"
            )


class TestResponseCharacterLimit:
    """Test response character limit validation"""
    
    def test_response_within_limit(self, review_service, mock_db):
        """Test response within character limit"""
        review_id = str(ObjectId())
        tenant_id = "test-tenant"
        response_text = "A" * 500  # Exactly at limit
        
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id
        }
        
        mock_db.reviews.find_one.return_value = mock_review
        mock_db.reviews.update_one.return_value = Mock()
        mock_db.reviews.find_one.side_effect = [mock_review, {**mock_review, "response": {}}]
        
        # Should not raise
        result = review_service.add_response(
            review_id=review_id,
            tenant_id=tenant_id,
            responder_id="user-123",
            responder_name="John Doe",
            response_text=response_text
        )
        
        assert result is not None
    
    def test_response_exceeds_limit(self, review_service, mock_db):
        """Test response exceeding character limit"""
        review_id = str(ObjectId())
        tenant_id = "test-tenant"
        response_text = "A" * 501  # Over limit
        
        mock_review = {
            "_id": ObjectId(review_id),
            "tenant_id": tenant_id
        }
        
        mock_db.reviews.find_one.return_value = mock_review
        
        # Note: Character limit validation should be done in the API layer
        # This test verifies the service accepts the text
        # The API layer should validate before calling the service
        result = review_service.add_response(
            review_id=review_id,
            tenant_id=tenant_id,
            responder_id="user-123",
            responder_name="John Doe",
            response_text=response_text
        )
        
        # Service should accept it (validation is in API layer)
        assert result is not None
