"""
Tests for Advanced Scheduling functionality
"""
import pytest
from datetime import datetime, timedelta
from app.services.advanced_scheduling_service import advanced_scheduling_service


@pytest.mark.asyncio
async def test_calculate_next_execution_daily():
    """Test calculating next execution for daily recurrence"""
    next_exec = advanced_scheduling_service.calculate_next_execution(
        recurrence_type="daily",
        recurrence_config={}
    )
    
    now = datetime.utcnow()
    expected = now + timedelta(days=1)
    
    # Allow 1 minute difference
    assert abs((next_exec - expected).total_seconds()) < 60


@pytest.mark.asyncio
async def test_calculate_next_execution_weekly():
    """Test calculating next execution for weekly recurrence"""
    next_exec = advanced_scheduling_service.calculate_next_execution(
        recurrence_type="weekly",
        recurrence_config={"day_of_week": 0}  # Monday
    )
    
    assert next_exec is not None
    assert isinstance(next_exec, datetime)


@pytest.mark.asyncio
async def test_calculate_next_execution_monthly():
    """Test calculating next execution for monthly recurrence"""
    next_exec = advanced_scheduling_service.calculate_next_execution(
        recurrence_type="monthly",
        recurrence_config={"day_of_month": 15}
    )
    
    assert next_exec is not None
    assert isinstance(next_exec, datetime)


@pytest.mark.asyncio
async def test_calculate_optimal_send_time():
    """Test calculating optimal send time for a client"""
    optimal_time = await advanced_scheduling_service.calculate_optimal_send_time(
        client_id="client_123",
        tenant_id="test_tenant"
    )
    
    # Should return time in HH:MM format
    assert isinstance(optimal_time, str)
    assert ":" in optimal_time
    parts = optimal_time.split(":")
    assert len(parts) == 2
    assert 0 <= int(parts[0]) <= 23
    assert 0 <= int(parts[1]) <= 59


@pytest.mark.asyncio
async def test_get_next_execution_time():
    """Test getting next execution time for a campaign"""
    # This would require a campaign to exist in the database
    # For now, test that it returns None for non-existent campaign
    next_time = await advanced_scheduling_service.get_next_execution_time(
        campaign_id="nonexistent",
        tenant_id="test_tenant"
    )
    
    assert next_time is None


@pytest.mark.asyncio
async def test_get_recurring_campaigns():
    """Test getting all recurring campaigns"""
    campaigns = await advanced_scheduling_service.get_recurring_campaigns("test_tenant")
    
    # Should return a list (may be empty)
    assert isinstance(campaigns, list)


@pytest.mark.asyncio
async def test_get_triggered_campaigns():
    """Test getting campaigns triggered by specific event"""
    campaigns = await advanced_scheduling_service.get_triggered_campaigns(
        tenant_id="test_tenant",
        trigger_event="post_booking"
    )
    
    # Should return a list (may be empty)
    assert isinstance(campaigns, list)
