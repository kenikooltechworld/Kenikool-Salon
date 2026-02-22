"""
Tests for Opt-Out Management functionality
"""
import pytest
from app.services.opt_out_service import opt_out_service


@pytest.mark.asyncio
async def test_create_opt_out():
    """Test creating an opt-out preference"""
    opt_out = await opt_out_service.create_opt_out(
        client_id="client_123",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": True},
        reason="Too many messages"
    )
    
    assert opt_out["client_id"] == "client_123"
    assert opt_out["channels"]["sms"] == True
    assert opt_out["channels"]["whatsapp"] == False


@pytest.mark.asyncio
async def test_get_opt_out():
    """Test retrieving opt-out preferences"""
    created = await opt_out_service.create_opt_out(
        client_id="client_123",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": False}
    )
    
    retrieved = await opt_out_service.get_opt_out("client_123", "test_tenant")
    assert retrieved is not None
    assert retrieved["client_id"] == "client_123"


@pytest.mark.asyncio
async def test_is_opted_out():
    """Test checking if client is opted out of a channel"""
    await opt_out_service.create_opt_out(
        client_id="client_123",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": True}
    )
    
    # Check opted out channels
    assert await opt_out_service.is_opted_out("client_123", "test_tenant", "sms") == True
    assert await opt_out_service.is_opted_out("client_123", "test_tenant", "email") == True
    assert await opt_out_service.is_opted_out("client_123", "test_tenant", "whatsapp") == False


@pytest.mark.asyncio
async def test_filter_opted_out_clients():
    """Test filtering out opted-out clients"""
    # Create opt-outs
    await opt_out_service.create_opt_out(
        client_id="client_1",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": False}
    )
    
    await opt_out_service.create_opt_out(
        client_id="client_2",
        tenant_id="test_tenant",
        channels={"sms": False, "whatsapp": False, "email": False}
    )
    
    # Filter for SMS
    client_ids = ["client_1", "client_2", "client_3"]
    filtered = await opt_out_service.filter_opted_out_clients(
        client_ids=client_ids,
        tenant_id="test_tenant",
        channel="sms"
    )
    
    # client_1 is opted out of SMS, so should be filtered
    assert "client_1" not in filtered
    assert "client_2" in filtered
    assert "client_3" in filtered


@pytest.mark.asyncio
async def test_update_opt_out():
    """Test updating opt-out preferences"""
    await opt_out_service.create_opt_out(
        client_id="client_123",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": False}
    )
    
    updated = await opt_out_service.update_opt_out(
        client_id="client_123",
        tenant_id="test_tenant",
        channels={"sms": False, "whatsapp": True, "email": True}
    )
    
    assert updated["channels"]["sms"] == False
    assert updated["channels"]["whatsapp"] == True


@pytest.mark.asyncio
async def test_delete_opt_out():
    """Test deleting opt-out preference"""
    await opt_out_service.create_opt_out(
        client_id="client_123",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": False}
    )
    
    success = await opt_out_service.delete_opt_out("client_123", "test_tenant")
    assert success == True
    
    # Verify it's deleted
    retrieved = await opt_out_service.get_opt_out("client_123", "test_tenant")
    assert retrieved is None


@pytest.mark.asyncio
async def test_generate_unsubscribe_link():
    """Test generating unsubscribe link token"""
    token = await opt_out_service.generate_unsubscribe_link(
        client_id="client_123",
        tenant_id="test_tenant",
        channel="sms"
    )
    
    assert token is not None
    assert len(token) > 0


@pytest.mark.asyncio
async def test_process_unsubscribe():
    """Test processing unsubscribe link"""
    # Generate token
    token = await opt_out_service.generate_unsubscribe_link(
        client_id="client_123",
        tenant_id="test_tenant",
        channel="sms"
    )
    
    # Process unsubscribe
    success = await opt_out_service.process_unsubscribe(token, "test_tenant")
    assert success == True
    
    # Verify opt-out was created
    opt_out = await opt_out_service.get_opt_out("client_123", "test_tenant")
    assert opt_out is not None
    assert opt_out["channels"]["sms"] == True


@pytest.mark.asyncio
async def test_get_opt_outs():
    """Test retrieving all opt-outs for a tenant"""
    await opt_out_service.create_opt_out(
        client_id="client_1",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": False}
    )
    
    await opt_out_service.create_opt_out(
        client_id="client_2",
        tenant_id="test_tenant",
        channels={"sms": False, "whatsapp": True, "email": False}
    )
    
    opt_outs = await opt_out_service.get_opt_outs("test_tenant")
    assert len(opt_outs) >= 2


@pytest.mark.asyncio
async def test_get_opt_out_count():
    """Test getting opt-out count"""
    await opt_out_service.create_opt_out(
        client_id="client_1",
        tenant_id="test_tenant",
        channels={"sms": True, "whatsapp": False, "email": False}
    )
    
    count = await opt_out_service.get_opt_out_count("test_tenant")
    assert count >= 1
