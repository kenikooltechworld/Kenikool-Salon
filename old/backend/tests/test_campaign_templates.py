"""
Tests for Campaign Templates functionality
"""
import pytest
from datetime import datetime
from app.services.template_service import template_service


@pytest.mark.asyncio
async def test_create_template():
    """Test creating a campaign template"""
    template = await template_service.create_template(
        tenant_id="test_tenant",
        name="Test Template",
        category="promotional",
        channels=["sms", "email"],
        message_templates={
            "sms": "Hello {{client_name}}",
            "email": "Welcome {{client_name}}"
        },
        variables=["client_name"],
        created_by="test_user"
    )
    
    assert template["name"] == "Test Template"
    assert template["category"] == "promotional"
    assert "sms" in template["channels"]
    assert template["is_system"] == False


@pytest.mark.asyncio
async def test_get_template():
    """Test retrieving a template"""
    created = await template_service.create_template(
        tenant_id="test_tenant",
        name="Retrieve Test",
        category="seasonal",
        channels=["email"],
        message_templates={"email": "Seasonal offer"},
        variables=[],
        created_by="test_user"
    )
    
    retrieved = await template_service.get_template(str(created["_id"]), "test_tenant")
    assert retrieved is not None
    assert retrieved["name"] == "Retrieve Test"


@pytest.mark.asyncio
async def test_extract_variables():
    """Test variable extraction from template content"""
    content = "Hello {{client_name}}, you have {{points}} points"
    variables = template_service.extract_variables(content)
    
    assert "client_name" in variables
    assert "points" in variables
    assert len(variables) == 2


@pytest.mark.asyncio
async def test_render_template():
    """Test template rendering with variable substitution"""
    content = "Hello {{client_name}}, enjoy {{discount}}% off"
    variables = {"client_name": "John", "discount": "20"}
    
    rendered = template_service.render_template(content, variables)
    assert rendered == "Hello John, enjoy 20% off"


@pytest.mark.asyncio
async def test_get_templates_by_category():
    """Test filtering templates by category"""
    # Create templates
    await template_service.create_template(
        tenant_id="test_tenant",
        name="Promo 1",
        category="promotional",
        channels=["sms"],
        message_templates={"sms": "Promo"},
        variables=[],
        created_by="test_user"
    )
    
    await template_service.create_template(
        tenant_id="test_tenant",
        name="Birthday 1",
        category="birthday",
        channels=["email"],
        message_templates={"email": "Happy Birthday"},
        variables=[],
        created_by="test_user"
    )
    
    # Get promotional templates
    promos = await template_service.get_templates(
        tenant_id="test_tenant",
        category="promotional"
    )
    
    assert len(promos) >= 1
    assert all(t["category"] == "promotional" for t in promos)


@pytest.mark.asyncio
async def test_update_template():
    """Test updating a template"""
    created = await template_service.create_template(
        tenant_id="test_tenant",
        name="Original",
        category="promotional",
        channels=["sms"],
        message_templates={"sms": "Original"},
        variables=[],
        created_by="test_user"
    )
    
    updated = await template_service.update_template(
        template_id=str(created["_id"]),
        tenant_id="test_tenant",
        name="Updated"
    )
    
    assert updated["name"] == "Updated"


@pytest.mark.asyncio
async def test_delete_template():
    """Test deleting a custom template"""
    created = await template_service.create_template(
        tenant_id="test_tenant",
        name="To Delete",
        category="promotional",
        channels=["sms"],
        message_templates={"sms": "Delete me"},
        variables=[],
        created_by="test_user",
        is_system=False
    )
    
    success = await template_service.delete_template(str(created["_id"]), "test_tenant")
    assert success == True


@pytest.mark.asyncio
async def test_cannot_delete_system_template():
    """Test that system templates cannot be deleted"""
    created = await template_service.create_template(
        tenant_id="test_tenant",
        name="System Template",
        category="birthday",
        channels=["sms"],
        message_templates={"sms": "System"},
        variables=[],
        created_by="system",
        is_system=True
    )
    
    success = await template_service.delete_template(str(created["_id"]), "test_tenant")
    assert success == False


@pytest.mark.asyncio
async def test_seed_system_templates():
    """Test seeding system templates"""
    await template_service.seed_system_templates("test_tenant")
    
    templates = await template_service.get_templates("test_tenant")
    system_templates = [t for t in templates if t.get("is_system")]
    
    assert len(system_templates) >= 6  # At least 6 system templates


@pytest.mark.asyncio
async def test_get_categories():
    """Test getting template categories"""
    await template_service.create_template(
        tenant_id="test_tenant",
        name="Promo",
        category="promotional",
        channels=["sms"],
        message_templates={"sms": "Promo"},
        variables=[],
        created_by="test_user"
    )
    
    categories = await template_service.get_categories("test_tenant")
    assert "promotional" in categories
