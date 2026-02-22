"""
Tests for Campaign Integrations functionality
"""
import pytest
from app.services.campaign_integrations_service import campaign_integrations_service


@pytest.mark.asyncio
async def test_filter_by_loyalty_tier():
    """Test filtering clients by loyalty tier"""
    client_ids = ["client_1", "client_2", "client_3"]
    
    filtered = await campaign_integrations_service.filter_by_loyalty_tier(
        client_ids=client_ids,
        tenant_id="test_tenant",
        loyalty_tiers=["gold", "platinum"]
    )
    
    # Should return a list
    assert isinstance(filtered, list)


@pytest.mark.asyncio
async def test_get_loyalty_tier_stats():
    """Test getting loyalty tier statistics"""
    stats = await campaign_integrations_service.get_loyalty_tier_stats("test_tenant")
    
    # Should return a dictionary
    assert isinstance(stats, dict)


@pytest.mark.asyncio
async def test_generate_promo_codes():
    """Test generating promo codes for campaign"""
    client_ids = ["client_1", "client_2", "client_3"]
    
    codes = await campaign_integrations_service.generate_promo_codes(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        client_ids=client_ids,
        discount_percentage=20,
        expiry_days=30
    )
    
    # Should return a dictionary with client_id -> code mapping
    assert isinstance(codes, dict)
    assert len(codes) == len(client_ids)
    
    # Each code should be unique
    code_values = list(codes.values())
    assert len(code_values) == len(set(code_values))


@pytest.mark.asyncio
async def test_track_promo_code_usage():
    """Test tracking promo code usage"""
    stats = await campaign_integrations_service.track_promo_code_usage(
        campaign_id="camp_123",
        tenant_id="test_tenant"
    )
    
    # Should return stats dictionary
    assert isinstance(stats, dict)
    assert "total_codes" in stats or len(stats) == 0


@pytest.mark.asyncio
async def test_generate_booking_urls():
    """Test generating booking URLs"""
    client_ids = ["client_1", "client_2"]
    
    urls = await campaign_integrations_service.generate_booking_urls(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        client_ids=client_ids
    )
    
    # Should return a dictionary with client_id -> url mapping
    assert isinstance(urls, dict)
    assert len(urls) == len(client_ids)


@pytest.mark.asyncio
async def test_get_campaign_booking_stats():
    """Test getting booking statistics"""
    stats = await campaign_integrations_service.get_campaign_booking_stats(
        campaign_id="camp_123",
        tenant_id="test_tenant"
    )
    
    # Should return stats dictionary
    assert isinstance(stats, dict)
    assert "total_bookings" in stats or len(stats) == 0


@pytest.mark.asyncio
async def test_include_gift_cards():
    """Test generating gift cards for campaign"""
    client_ids = ["client_1", "client_2"]
    
    gift_cards = await campaign_integrations_service.include_gift_cards(
        campaign_id="camp_123",
        tenant_id="test_tenant",
        client_ids=client_ids,
        gift_card_amount=50.0
    )
    
    # Should return a dictionary with client_id -> code mapping
    assert isinstance(gift_cards, dict)
    assert len(gift_cards) == len(client_ids)


@pytest.mark.asyncio
async def test_track_gift_card_redemptions():
    """Test tracking gift card redemptions"""
    stats = await campaign_integrations_service.track_gift_card_redemptions(
        campaign_id="camp_123",
        tenant_id="test_tenant"
    )
    
    # Should return stats dictionary
    assert isinstance(stats, dict)
    assert "total_cards" in stats or len(stats) == 0


@pytest.mark.asyncio
async def test_calculate_campaign_roi():
    """Test calculating campaign ROI"""
    roi = await campaign_integrations_service.calculate_campaign_roi(
        campaign_id="camp_123",
        tenant_id="test_tenant"
    )
    
    # Should return ROI dictionary or empty dict if campaign not found
    assert isinstance(roi, dict)
    if roi:
        assert "total_cost" in roi
        assert "total_revenue" in roi
        assert "roi_percentage" in roi
