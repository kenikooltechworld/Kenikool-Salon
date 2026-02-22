"""
Tests for review template functionality
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, AsyncMock, patch
from app.services.review_template_service import ReviewTemplateService


@pytest.fixture
def mock_db():
    """Create mock database"""
    db = Mock()
    db.review_templates = Mock()
    return db


@pytest.fixture
def template_service(mock_db):
    """Create template service instance"""
    return ReviewTemplateService(mock_db)


class TestTemplateManagement:
    """Test template management functionality"""
    
    def test_get_templates_success(self, template_service, mock_db):
        """Test getting templates"""
        tenant_id = "test-tenant"
        
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
                "name": "Custom",
                "category": "positive",
                "text": "Custom response",
                "is_default": False
            }
        ]
        
        mock_db.review_templates.find.return_value.sort.return_value.sort.return_value = mock_templates
        
        result = template_service.get_templates(tenant_id=tenant_id)
        
        assert len(result) == 2
        assert result[0]["name"] == "Thank You"
        assert result[1]["name"] == "Custom"
    
    def test_get_templates_by_category(self, template_service, mock_db):
        """Test getting templates filtered by category"""
        tenant_id = "test-tenant"
        
        mock_templates = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "name": "Thank You",
                "category": "positive",
                "text": "Thank you!",
                "is_default": True
            }
        ]
        
        mock_db.review_templates.find.return_value.sort.return_value.sort.return_value = mock_templates
        
        result = template_service.get_templates(tenant_id=tenant_id, category="positive")
        
        assert len(result) == 1
        assert result[0]["category"] == "positive"
    
    def test_get_templates_invalid_category(self, template_service, mock_db):
        """Test getting templates with invalid category"""
        with pytest.raises(ValueError, match="Invalid category"):
            template_service.get_templates(tenant_id="test-tenant", category="invalid")
    
    def test_create_template_success(self, template_service, mock_db):
        """Test creating template"""
        tenant_id = "test-tenant"
        template_id = str(ObjectId())
        
        mock_db.review_templates.insert_one.return_value = Mock(inserted_id=ObjectId(template_id))
        
        result = template_service.create_template(
            tenant_id=tenant_id,
            name="Thank You",
            category="positive",
            text="Thank you for your review!"
        )
        
        assert result["name"] == "Thank You"
        assert result["category"] == "positive"
        assert result["is_default"] is False
        mock_db.review_templates.insert_one.assert_called_once()
    
    def test_create_template_empty_name(self, template_service, mock_db):
        """Test creating template with empty name"""
        with pytest.raises(ValueError, match="Template name cannot be empty"):
            template_service.create_template(
                tenant_id="test-tenant",
                name="",
                category="positive",
                text="Text"
            )
    
    def test_create_template_empty_text(self, template_service, mock_db):
        """Test creating template with empty text"""
        with pytest.raises(ValueError, match="Template text cannot be empty"):
            template_service.create_template(
                tenant_id="test-tenant",
                name="Test",
                category="positive",
                text=""
            )
    
    def test_create_template_text_too_long(self, template_service, mock_db):
        """Test creating template with text exceeding limit"""
        with pytest.raises(ValueError, match="Template text cannot exceed 1000 characters"):
            template_service.create_template(
                tenant_id="test-tenant",
                name="Test",
                category="positive",
                text="A" * 1001
            )
    
    def test_create_template_invalid_category(self, template_service, mock_db):
        """Test creating template with invalid category"""
        with pytest.raises(ValueError, match="Invalid category"):
            template_service.create_template(
                tenant_id="test-tenant",
                name="Test",
                category="invalid",
                text="Text"
            )
    
    def test_update_template_success(self, template_service, mock_db):
        """Test updating template"""
        template_id = str(ObjectId())
        tenant_id = "test-tenant"
        
        mock_template = {
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "name": "Old Name",
            "category": "positive",
            "text": "Old text",
            "is_default": False
        }
        
        mock_db.review_templates.find_one.return_value = mock_template
        mock_db.review_templates.update_one.return_value = Mock()
        
        updated_template = {
            **mock_template,
            "name": "New Name",
            "text": "New text"
        }
        mock_db.review_templates.find_one.side_effect = [mock_template, updated_template]
        
        result = template_service.update_template(
            template_id=template_id,
            tenant_id=tenant_id,
            name="New Name",
            text="New text"
        )
        
        assert result["name"] == "New Name"
        assert result["text"] == "New text"
    
    def test_update_default_template_fails(self, template_service, mock_db):
        """Test that default templates cannot be updated"""
        mock_template = {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "is_default": True
        }
        mock_db.review_templates.find_one.return_value = mock_template
        
        with pytest.raises(ValueError, match="Cannot edit default templates"):
            template_service.update_template(
                template_id="template-123",
                tenant_id="test-tenant",
                name="New Name"
            )
    
    def test_delete_template_success(self, template_service, mock_db):
        """Test deleting template"""
        template_id = str(ObjectId())
        tenant_id = "test-tenant"
        
        mock_template = {
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "is_default": False
        }
        
        mock_db.review_templates.find_one.return_value = mock_template
        mock_db.review_templates.delete_one.return_value = Mock()
        
        template_service.delete_template(
            template_id=template_id,
            tenant_id=tenant_id
        )
        
        mock_db.review_templates.delete_one.assert_called_once()
    
    def test_delete_default_template_fails(self, template_service, mock_db):
        """Test that default templates cannot be deleted"""
        mock_template = {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "is_default": True
        }
        mock_db.review_templates.find_one.return_value = mock_template
        
        with pytest.raises(ValueError, match="Cannot delete default templates"):
            template_service.delete_template(
                template_id="template-123",
                tenant_id="test-tenant"
            )
    
    def test_get_template_stats(self, template_service, mock_db):
        """Test getting template statistics"""
        tenant_id = "test-tenant"
        
        mock_db.review_templates.count_documents.side_effect = [5, 2, 2, 1, 3, 2]
        
        result = template_service.get_template_stats(tenant_id=tenant_id)
        
        assert result["total"] == 5
        assert result["by_category"]["positive"] == 2
        assert result["by_category"]["negative"] == 2
        assert result["by_category"]["neutral"] == 1
        assert result["default"] == 3
        assert result["custom"] == 2
    
    def test_duplicate_template_success(self, template_service, mock_db):
        """Test duplicating template"""
        template_id = str(ObjectId())
        tenant_id = "test-tenant"
        new_id = str(ObjectId())
        
        mock_template = {
            "_id": ObjectId(template_id),
            "tenant_id": tenant_id,
            "name": "Original",
            "category": "positive",
            "text": "Original text",
            "is_default": False
        }
        
        mock_db.review_templates.find_one.return_value = mock_template
        mock_db.review_templates.insert_one.return_value = Mock(inserted_id=ObjectId(new_id))
        
        result = template_service.duplicate_template(
            template_id=template_id,
            tenant_id=tenant_id
        )
        
        assert result["name"] == "Original (Copy)"
        assert result["category"] == "positive"
        assert result["text"] == "Original text"
        assert result["is_default"] is False
    
    def test_search_templates(self, template_service, mock_db):
        """Test searching templates"""
        tenant_id = "test-tenant"
        
        mock_templates = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "name": "Thank You",
                "category": "positive",
                "text": "Thank you for your review!",
                "is_default": True
            }
        ]
        
        mock_db.review_templates.find.return_value.sort.return_value.sort.return_value = mock_templates
        
        result = template_service.search_templates(
            tenant_id=tenant_id,
            query="Thank"
        )
        
        assert len(result) == 1
        assert result[0]["name"] == "Thank You"


class TestTemplateValidation:
    """Test template validation"""
    
    def test_template_name_trimmed(self, template_service, mock_db):
        """Test that template names are trimmed"""
        tenant_id = "test-tenant"
        template_id = str(ObjectId())
        
        mock_db.review_templates.insert_one.return_value = Mock(inserted_id=ObjectId(template_id))
        
        result = template_service.create_template(
            tenant_id=tenant_id,
            name="  Thank You  ",
            category="positive",
            text="Thank you!"
        )
        
        assert result["name"] == "Thank You"
    
    def test_template_text_trimmed(self, template_service, mock_db):
        """Test that template text is trimmed"""
        tenant_id = "test-tenant"
        template_id = str(ObjectId())
        
        mock_db.review_templates.insert_one.return_value = Mock(inserted_id=ObjectId(template_id))
        
        result = template_service.create_template(
            tenant_id=tenant_id,
            name="Test",
            category="positive",
            text="  Thank you!  "
        )
        
        assert result["text"] == "Thank you!"
    
    def test_template_text_at_limit(self, template_service, mock_db):
        """Test template text at character limit"""
        tenant_id = "test-tenant"
        template_id = str(ObjectId())
        text = "A" * 1000
        
        mock_db.review_templates.insert_one.return_value = Mock(inserted_id=ObjectId(template_id))
        
        result = template_service.create_template(
            tenant_id=tenant_id,
            name="Test",
            category="positive",
            text=text
        )
        
        assert len(result["text"]) == 1000
