import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.theme_template_service import ThemeTemplateService
from app.models.theme_template import ThemeTemplate


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = AsyncMock(spec=AsyncIOMotorDatabase)
    db.theme_templates = AsyncMock()
    return db


@pytest.fixture
def template_service(mock_db):
    """Create a template service with mock database"""
    return ThemeTemplateService(mock_db)


@pytest.fixture
def sample_branding():
    """Sample branding configuration"""
    return {
        "primary_color": "#8B7355",
        "secondary_color": "#D4A574",
        "accent_color": "#E8D5C4",
        "font_family": "Playfair Display",
        "company_name": "Test Spa",
    }


class TestThemeTemplateCreation:
    """Tests for template creation"""

    @pytest.mark.asyncio
    async def test_create_template_success(self, template_service, sample_branding):
        """Test successful template creation"""
        # Mock the insert_one response
        mock_result = AsyncMock()
        mock_result.inserted_id = "template_123"
        template_service.collection.insert_one = AsyncMock(return_value=mock_result)

        template = await template_service.create_template(
            name="Modern Spa",
            category="spa",
            branding=sample_branding,
            description="Modern spa template",
            is_system=True,
        )

        assert template.name == "Modern Spa"
        assert template.category == "spa"
        assert template.branding == sample_branding
        assert template.is_system is True
        template_service.collection.insert_one.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_template_invalid_category(self, template_service, sample_branding):
        """Test template creation with invalid category"""
        with pytest.raises(ValueError, match="Invalid category"):
            await template_service.create_template(
                name="Test",
                category="invalid",
                branding=sample_branding,
            )

    @pytest.mark.asyncio
    async def test_create_template_invalid_branding(self, template_service):
        """Test template creation with invalid branding"""
        with pytest.raises(ValueError, match="Branding must be a dictionary"):
            await template_service.create_template(
                name="Test",
                category="spa",
                branding="not a dict",
            )

    @pytest.mark.asyncio
    async def test_create_template_all_categories(self, template_service, sample_branding):
        """Test creating templates for all valid categories"""
        categories = ["spa", "barber", "salon", "modern", "classic"]
        
        for category in categories:
            mock_result = AsyncMock()
            mock_result.inserted_id = f"template_{category}"
            template_service.collection.insert_one = AsyncMock(return_value=mock_result)

            template = await template_service.create_template(
                name=f"Template {category}",
                category=category,
                branding=sample_branding,
            )

            assert template.category == category


class TestThemeTemplateRetrieval:
    """Tests for template retrieval"""

    @pytest.mark.asyncio
    async def test_get_template_success(self, template_service, sample_branding):
        """Test successful template retrieval"""
        mock_template = {
            "_id": "template_123",
            "name": "Modern Spa",
            "category": "spa",
            "branding": sample_branding,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "is_premium": False,
            "description": None,
            "preview_image_url": None,
            "tenant_id": None,
            "created_by": None,
            "updated_at": datetime.utcnow(),
        }
        template_service.collection.find_one = AsyncMock(return_value=mock_template)

        template = await template_service.get_template("template_123")

        assert template is not None
        assert template.name == "Modern Spa"
        assert template.category == "spa"

    @pytest.mark.asyncio
    async def test_get_template_not_found(self, template_service):
        """Test template retrieval when not found"""
        template_service.collection.find_one = AsyncMock(return_value=None)

        template = await template_service.get_template("nonexistent")

        assert template is None

    @pytest.mark.asyncio
    async def test_get_templates_with_category_filter(self, template_service, sample_branding):
        """Test retrieving templates with category filter"""
        mock_templates = [
            {
                "_id": "template_1",
                "name": "Spa 1",
                "category": "spa",
                "branding": sample_branding,
                "is_system": True,
                "created_at": datetime.utcnow(),
            },
            {
                "_id": "template_2",
                "name": "Spa 2",
                "category": "spa",
                "branding": sample_branding,
                "is_system": True,
                "created_at": datetime.utcnow(),
            },
        ]

        # Mock cursor
        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(mock_templates)
        template_service.collection.find = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)

        templates = await template_service.get_templates(category="spa")

        assert len(templates) == 2
        assert all(t.category == "spa" for t in templates)

    @pytest.mark.asyncio
    async def test_get_templates_by_category(self, template_service, sample_branding):
        """Test getting templates by specific category"""
        mock_templates = [
            {
                "_id": "template_1",
                "name": "Barber 1",
                "category": "barber",
                "branding": sample_branding,
                "is_system": True,
                "created_at": datetime.utcnow(),
            },
        ]

        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(mock_templates)
        template_service.collection.find = MagicMock(return_value=mock_cursor)

        templates = await template_service.get_templates_by_category("barber")

        assert len(templates) == 1
        assert templates[0].category == "barber"


class TestThemeTemplateUpdate:
    """Tests for template updates"""

    @pytest.mark.asyncio
    async def test_update_template_success(self, template_service, sample_branding):
        """Test successful template update"""
        updated_branding = sample_branding.copy()
        updated_branding["primary_color"] = "#FF0000"

        mock_updated = {
            "_id": "template_123",
            "name": "Updated Spa",
            "category": "spa",
            "branding": updated_branding,
            "is_system": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "is_premium": False,
            "description": None,
            "preview_image_url": None,
            "tenant_id": None,
            "created_by": None,
        }
        template_service.collection.find_one_and_update = AsyncMock(
            return_value=mock_updated
        )

        template = await template_service.update_template(
            "template_123",
            name="Updated Spa",
            branding=updated_branding,
        )

        assert template is not None
        assert template.name == "Updated Spa"
        assert template.branding["primary_color"] == "#FF0000"

    @pytest.mark.asyncio
    async def test_update_template_invalid_branding(self, template_service):
        """Test updating template with invalid branding"""
        with pytest.raises(ValueError, match="Branding must be a dictionary"):
            await template_service.update_template(
                "template_123",
                branding="not a dict",
            )


class TestThemeTemplateDelete:
    """Tests for template deletion"""

    @pytest.mark.asyncio
    async def test_delete_template_success(self, template_service):
        """Test successful template deletion"""
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        template_service.collection.delete_one = AsyncMock(return_value=mock_result)

        success = await template_service.delete_template("template_123")

        assert success is True

    @pytest.mark.asyncio
    async def test_delete_template_not_found(self, template_service):
        """Test deleting non-existent template"""
        mock_result = AsyncMock()
        mock_result.deleted_count = 0
        template_service.collection.delete_one = AsyncMock(return_value=mock_result)

        success = await template_service.delete_template("nonexistent")

        assert success is False


class TestThemeTemplateDuplication:
    """Tests for template duplication"""

    @pytest.mark.asyncio
    async def test_duplicate_template_success(self, template_service, sample_branding):
        """Test successful template duplication"""
        original = {
            "_id": "template_123",
            "name": "Original Spa",
            "category": "spa",
            "branding": sample_branding,
            "description": "Original description",
            "is_system": True,
            "created_at": datetime.utcnow(),
        }

        duplicated = {
            "_id": "template_456",
            "name": "Duplicated Spa",
            "category": "spa",
            "branding": sample_branding,
            "description": "Original description",
            "is_system": False,
            "tenant_id": "tenant_123",
            "created_at": datetime.utcnow(),
        }

        # Mock get_template
        template_service.get_template = AsyncMock(return_value=ThemeTemplate(**original))

        # Mock create_template
        template_service.collection.insert_one = AsyncMock()
        template_service.collection.insert_one.return_value.inserted_id = "template_456"

        duplicated_template = await template_service.duplicate_template(
            "template_123",
            "Duplicated Spa",
            tenant_id="tenant_123",
        )

        assert duplicated_template is not None
        assert duplicated_template.name == "Duplicated Spa"
        assert duplicated_template.is_system is False

    @pytest.mark.asyncio
    async def test_duplicate_nonexistent_template(self, template_service):
        """Test duplicating non-existent template"""
        template_service.get_template = AsyncMock(return_value=None)

        result = await template_service.duplicate_template(
            "nonexistent",
            "New Name",
        )

        assert result is None


class TestDefaultTemplates:
    """Tests for default template creation"""

    @pytest.mark.asyncio
    async def test_create_default_templates(self, template_service):
        """Test creating default system templates"""
        # Mock insert_one for each template
        template_ids = [
            "spa_template",
            "barber_template",
            "salon_template",
            "modern_template",
            "classic_template",
        ]

        insert_calls = []
        for template_id in template_ids:
            mock_result = AsyncMock()
            mock_result.inserted_id = template_id
            insert_calls.append(mock_result)

        template_service.collection.insert_one = AsyncMock(side_effect=insert_calls)

        templates = await template_service.create_default_templates()

        assert len(templates) == 5
        assert templates[0].category == "spa"
        assert templates[1].category == "barber"
        assert templates[2].category == "salon"
        assert templates[3].category == "modern"
        assert templates[4].category == "classic"

        # Verify all are system templates
        assert all(t.is_system for t in templates)


class TestTemplateFiltering:
    """Tests for template filtering and counting"""

    @pytest.mark.asyncio
    async def test_get_system_templates(self, template_service, sample_branding):
        """Test retrieving system templates"""
        mock_templates = [
            {
                "_id": "template_1",
                "name": "System Template 1",
                "category": "spa",
                "branding": sample_branding,
                "is_system": True,
                "created_at": datetime.utcnow(),
                "is_premium": False,
                "description": None,
                "preview_image_url": None,
                "tenant_id": None,
                "created_by": None,
                "updated_at": datetime.utcnow(),
            },
        ]

        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(mock_templates)
        template_service.collection.find = MagicMock(return_value=mock_cursor)

        templates = await template_service.get_system_templates()

        assert len(templates) == 1
        assert templates[0].is_system is True

    @pytest.mark.asyncio
    async def test_get_tenant_templates(self, template_service, sample_branding):
        """Test retrieving tenant templates including system templates"""
        mock_templates = [
            {
                "_id": "template_1",
                "name": "Tenant Template",
                "category": "spa",
                "branding": sample_branding,
                "is_system": False,
                "tenant_id": "tenant_123",
                "created_at": datetime.utcnow(),
                "is_premium": False,
                "description": None,
                "preview_image_url": None,
                "created_by": None,
                "updated_at": datetime.utcnow(),
            },
            {
                "_id": "template_2",
                "name": "System Template",
                "category": "barber",
                "branding": sample_branding,
                "is_system": True,
                "created_at": datetime.utcnow(),
                "is_premium": False,
                "description": None,
                "preview_image_url": None,
                "tenant_id": None,
                "created_by": None,
                "updated_at": datetime.utcnow(),
            },
        ]

        mock_cursor = AsyncMock()
        mock_cursor.__aiter__.return_value = iter(mock_templates)
        template_service.collection.find = MagicMock(return_value=mock_cursor)

        templates = await template_service.get_tenant_templates("tenant_123")

        assert len(templates) == 2

    @pytest.mark.asyncio
    async def test_count_templates(self, template_service):
        """Test counting templates"""
        template_service.collection.count_documents = AsyncMock(return_value=5)

        count = await template_service.count_templates()

        assert count == 5

    @pytest.mark.asyncio
    async def test_count_templates_with_filters(self, template_service):
        """Test counting templates with filters"""
        template_service.collection.count_documents = AsyncMock(return_value=2)

        count = await template_service.count_templates(category="spa", is_system=True)

        assert count == 2


class TestTemplateValidation:
    """Tests for template validation"""

    @pytest.mark.asyncio
    async def test_invalid_category_in_get_by_category(self, template_service):
        """Test getting templates by invalid category"""
        with pytest.raises(ValueError, match="Invalid category"):
            await template_service.get_templates_by_category("invalid_category")

    @pytest.mark.asyncio
    async def test_template_model_validation(self, sample_branding):
        """Test ThemeTemplate model validation"""
        template = ThemeTemplate(
            name="Test Template",
            category="spa",
            branding=sample_branding,
            is_system=True,
        )

        assert template.name == "Test Template"
        assert template.category == "spa"
        assert template.is_system is True
        assert template.is_premium is False
