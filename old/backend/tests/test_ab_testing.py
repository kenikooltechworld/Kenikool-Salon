"""
Tests for A/B Testing functionality
"""
import pytest
from app.services.ab_test_service import ab_test_service


@pytest.mark.asyncio
async def test_create_ab_test():
    """Test creating an A/B test"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    traffic_split = {"var_1": 50, "var_2": 50}
    
    ab_test = await ab_test_service.create_ab_test(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        name="Subject Line Test",
        variants=variants,
        traffic_split=traffic_split,
        created_by="test_user"
    )
    
    assert ab_test["name"] == "Subject Line Test"
    assert ab_test["status"] == "draft"
    assert len(ab_test["variants"]) == 2


@pytest.mark.asyncio
async def test_invalid_traffic_split():
    """Test that invalid traffic split raises error"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    # Traffic split doesn't sum to 100
    traffic_split = {"var_1": 40, "var_2": 40}
    
    with pytest.raises(ValueError):
        await ab_test_service.create_ab_test(
            campaign_id="camp_123",
            tenant_id="test_tenant",
            name="Invalid Test",
            variants=variants,
            traffic_split=traffic_split
        )


@pytest.mark.asyncio
async def test_start_ab_test():
    """Test starting an A/B test"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    ab_test = await ab_test_service.create_ab_test(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        name="Start Test",
        variants=variants,
        traffic_split={"var_1": 50, "var_2": 50}
    )
    
    started = await ab_test_service.start_ab_test(str(ab_test["_id"]), "test_tenant")
    assert started["status"] == "running"
    assert started["started_at"] is not None


@pytest.mark.asyncio
async def test_stop_ab_test():
    """Test stopping an A/B test"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    ab_test = await ab_test_service.create_ab_test(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        name="Stop Test",
        variants=variants,
        traffic_split={"var_1": 50, "var_2": 50}
    )
    
    # Start first
    await ab_test_service.start_ab_test(str(ab_test["_id"]), "test_tenant")
    
    # Then stop
    stopped = await ab_test_service.stop_ab_test(str(ab_test["_id"]), "test_tenant")
    assert stopped["status"] == "completed"
    assert stopped["completed_at"] is not None


@pytest.mark.asyncio
async def test_select_winner():
    """Test selecting winning variant"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    ab_test = await ab_test_service.create_ab_test(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        name="Winner Test",
        variants=variants,
        traffic_split={"var_1": 50, "var_2": 50}
    )
    
    updated = await ab_test_service.select_winner(
        test_id=str(ab_test["_id"]),
        tenant_id="test_tenant",
        winner_variant_id="var_1"
    )
    
    assert updated["winner_variant_id"] == "var_1"


@pytest.mark.asyncio
async def test_assign_variant():
    """Test random variant assignment based on traffic split"""
    traffic_split = {"var_1": 50, "var_2": 50}
    
    # Run multiple times to verify distribution
    assignments = []
    for _ in range(100):
        variant = ab_test_service.assign_variant(traffic_split)
        assignments.append(variant)
        assert variant in ["var_1", "var_2"]
    
    # Check rough distribution (should be close to 50/50)
    var_1_count = assignments.count("var_1")
    var_2_count = assignments.count("var_2")
    
    # Allow 20-80 split as acceptable
    assert 20 <= var_1_count <= 80
    assert 20 <= var_2_count <= 80


@pytest.mark.asyncio
async def test_get_ab_test_by_campaign():
    """Test retrieving A/B test by campaign ID"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    created = await ab_test_service.create_ab_test(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        name="Retrieve Test",
        variants=variants,
        traffic_split={"var_1": 50, "var_2": 50}
    )
    
    retrieved = await ab_test_service.get_ab_test_by_campaign("camp_123", "test_tenant")
    assert retrieved is not None
    assert retrieved["campaign_id"] == "camp_123"


@pytest.mark.asyncio
async def test_update_ab_test():
    """Test updating an A/B test"""
    variants = [
        {"id": "var_1", "name": "Variant A", "message_content": "Message A"},
        {"id": "var_2", "name": "Variant B", "message_content": "Message B"}
    ]
    
    ab_test = await ab_test_service.create_ab_test(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        name="Original Name",
        variants=variants,
        traffic_split={"var_1": 50, "var_2": 50}
    )
    
    updated = await ab_test_service.update_ab_test(
        test_id=str(ab_test["_id"]),
        tenant_id="test_tenant",
        name="Updated Name"
    )
    
    assert updated["name"] == "Updated Name"
