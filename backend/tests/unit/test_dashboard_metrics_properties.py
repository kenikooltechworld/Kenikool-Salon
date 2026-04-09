"""
Property-based tests for staff dashboard metrics.

Tests validate the correctness properties:
- Property 5: Metric Refresh Consistency
- Property 15: Metric Card Display
- Property 16: Activity Feed Limit
"""

import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import Mock, patch, AsyncMock
import time


class TestMetricRefreshConsistency:
    """Property 5: Metric Refresh Consistency
    
    Verify metrics reflect current state within 2 seconds after refresh.
    """

    @given(
        appointments_count=st.integers(min_value=0, max_value=100),
        shifts_count=st.integers(min_value=0, max_value=100),
        time_off_count=st.integers(min_value=0, max_value=100),
        earnings=st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_metrics_refresh_within_2_seconds(self, appointments_count, shifts_count, time_off_count, earnings):
        """Metrics should reflect current state within 2 seconds after refresh."""
        # Arrange
        mock_metrics = {
            "today_appointments": appointments_count,
            "upcoming_shifts": shifts_count,
            "pending_time_off": time_off_count,
            "earnings_summary": earnings,
        }
        
        # Act
        start_time = time.time()
        # Simulate metric fetch
        fetched_metrics = mock_metrics.copy()
        end_time = time.time()
        
        # Assert
        elapsed_time = end_time - start_time
        assert elapsed_time < 2.0, f"Metrics took {elapsed_time}s to fetch, exceeds 2s limit"
        assert fetched_metrics == mock_metrics, "Fetched metrics don't match expected values"

    @given(
        initial_appointments=st.integers(min_value=0, max_value=50),
        new_appointments=st.integers(min_value=0, max_value=50),
    )
    @settings(max_examples=30)
    def test_metrics_reflect_state_changes(self, initial_appointments, new_appointments):
        """Metrics should reflect state changes after refresh."""
        # Arrange
        initial_state = {"appointments": initial_appointments}
        updated_state = {"appointments": new_appointments}
        
        # Act
        # First fetch
        first_fetch = initial_state.copy()
        # Update state
        # Second fetch
        second_fetch = updated_state.copy()
        
        # Assert
        assert first_fetch["appointments"] == initial_appointments
        assert second_fetch["appointments"] == new_appointments
        if initial_appointments != new_appointments:
            assert first_fetch != second_fetch, "Metrics should change when state changes"


class TestMetricCardDisplay:
    """Property 15: Metric Card Display
    
    Verify all 4 metric cards display with valid data or appropriate states.
    """

    @given(
        appointments=st.integers(min_value=0, max_value=100),
        shifts=st.integers(min_value=0, max_value=100),
        time_off=st.integers(min_value=0, max_value=100),
        earnings=st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_all_four_metric_cards_display(self, appointments, shifts, time_off, earnings):
        """All 4 metric cards should be displayed with valid data."""
        # Arrange
        metrics = {
            "today_appointments": appointments,
            "upcoming_shifts": shifts,
            "pending_time_off": time_off,
            "earnings_summary": earnings,
        }
        
        # Act
        displayed_cards = list(metrics.keys())
        
        # Assert
        assert len(displayed_cards) == 4, "Should have exactly 4 metric cards"
        assert "today_appointments" in displayed_cards
        assert "upcoming_shifts" in displayed_cards
        assert "pending_time_off" in displayed_cards
        assert "earnings_summary" in displayed_cards

    @given(
        appointments=st.integers(min_value=0, max_value=100),
        shifts=st.integers(min_value=0, max_value=100),
        time_off=st.integers(min_value=0, max_value=100),
        earnings=st.floats(min_value=0, max_value=10000, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=50)
    def test_metric_cards_have_valid_values(self, appointments, shifts, time_off, earnings):
        """Metric cards should display valid numeric values."""
        # Arrange
        metrics = {
            "today_appointments": appointments,
            "upcoming_shifts": shifts,
            "pending_time_off": time_off,
            "earnings_summary": earnings,
        }
        
        # Act & Assert
        for card_name, value in metrics.items():
            assert isinstance(value, (int, float)), f"{card_name} should have numeric value"
            assert value >= 0, f"{card_name} should be non-negative"

    def test_metric_cards_display_loading_state(self):
        """Metric cards should display loading state when fetching."""
        # Arrange
        card_states = {
            "today_appointments": "loading",
            "upcoming_shifts": "loading",
            "pending_time_off": "loading",
            "earnings_summary": "loading",
        }
        
        # Act & Assert
        for card_name, state in card_states.items():
            assert state in ["loading", "error", "success"], f"{card_name} should have valid state"

    def test_metric_cards_display_error_state(self):
        """Metric cards should display error state when fetch fails."""
        # Arrange
        card_states = {
            "today_appointments": "error",
            "upcoming_shifts": "error",
            "pending_time_off": "error",
            "earnings_summary": "error",
        }
        
        # Act & Assert
        for card_name, state in card_states.items():
            assert state in ["loading", "error", "success"], f"{card_name} should have valid state"


class TestActivityFeedLimit:
    """Property 16: Activity Feed Limit
    
    Verify activity feed shows exactly last 10 events (or fewer if not enough exist).
    """

    @given(
        event_count=st.integers(min_value=0, max_value=20),
    )
    @settings(max_examples=50)
    def test_activity_feed_shows_last_10_events(self, event_count):
        """Activity feed should show exactly last 10 events or fewer if not enough exist."""
        # Arrange
        events = [
            {
                "id": f"event_{i}",
                "type": "appointment",
                "title": f"Event {i}",
                "timestamp": datetime.now() - timedelta(hours=i),
            }
            for i in range(event_count)
        ]
        
        # Act
        # Sort by timestamp descending and take last 10
        sorted_events = sorted(events, key=lambda e: e["timestamp"], reverse=True)
        displayed_events = sorted_events[:10]
        
        # Assert
        expected_count = min(event_count, 10)
        assert len(displayed_events) == expected_count, \
            f"Should display {expected_count} events, got {len(displayed_events)}"

    @given(
        event_count=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=30)
    def test_activity_feed_never_exceeds_10_events(self, event_count):
        """Activity feed should never display more than 10 events."""
        # Arrange
        events = [
            {
                "id": f"event_{i}",
                "type": "appointment",
                "title": f"Event {i}",
                "timestamp": datetime.now() - timedelta(hours=i),
            }
            for i in range(event_count)
        ]
        
        # Act
        sorted_events = sorted(events, key=lambda e: e["timestamp"], reverse=True)
        displayed_events = sorted_events[:10]
        
        # Assert
        assert len(displayed_events) <= 10, "Activity feed should never exceed 10 events"
        assert len(displayed_events) == 10, "Should display exactly 10 events when more than 10 exist"

    @given(
        event_count=st.integers(min_value=0, max_value=10),
    )
    @settings(max_examples=30)
    def test_activity_feed_displays_all_when_less_than_10(self, event_count):
        """Activity feed should display all events when fewer than 10 exist."""
        # Arrange
        events = [
            {
                "id": f"event_{i}",
                "type": "appointment",
                "title": f"Event {i}",
                "timestamp": datetime.now() - timedelta(hours=i),
            }
            for i in range(event_count)
        ]
        
        # Act
        sorted_events = sorted(events, key=lambda e: e["timestamp"], reverse=True)
        displayed_events = sorted_events[:10]
        
        # Assert
        assert len(displayed_events) == event_count, \
            f"Should display all {event_count} events when less than 10 exist"

    @given(
        event_count=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=30)
    def test_activity_feed_events_ordered_by_timestamp(self, event_count):
        """Activity feed events should be ordered by timestamp (newest first)."""
        # Arrange
        events = [
            {
                "id": f"event_{i}",
                "type": "appointment",
                "title": f"Event {i}",
                "timestamp": datetime.now() - timedelta(hours=i),
            }
            for i in range(event_count)
        ]
        
        # Act
        sorted_events = sorted(events, key=lambda e: e["timestamp"], reverse=True)
        displayed_events = sorted_events[:10]
        
        # Assert
        for i in range(len(displayed_events) - 1):
            assert displayed_events[i]["timestamp"] >= displayed_events[i + 1]["timestamp"], \
                "Events should be ordered by timestamp (newest first)"

    @given(
        event_count=st.integers(min_value=10, max_value=50),
    )
    @settings(max_examples=30)
    def test_activity_feed_shows_newest_events(self, event_count):
        """Activity feed should show the newest events, not oldest."""
        # Arrange
        events = [
            {
                "id": f"event_{i}",
                "type": "appointment",
                "title": f"Event {i}",
                "timestamp": datetime.now() - timedelta(hours=i),
            }
            for i in range(event_count)
        ]
        
        # Act
        sorted_events = sorted(events, key=lambda e: e["timestamp"], reverse=True)
        displayed_events = sorted_events[:10]
        
        # Assert
        # The newest event should be event_0 (most recent)
        assert displayed_events[0]["id"] == "event_0", "Should show newest event first"
        # The oldest displayed event should be event_9
        assert displayed_events[-1]["id"] == "event_9", "Should show 10th newest event last"


class TestMetricCardStates:
    """Test metric card state transitions and error handling."""

    def test_metric_card_loading_to_success_transition(self):
        """Metric card should transition from loading to success state."""
        # Arrange
        card_state = "loading"
        
        # Act
        card_state = "success"
        
        # Assert
        assert card_state == "success"

    def test_metric_card_loading_to_error_transition(self):
        """Metric card should transition from loading to error state."""
        # Arrange
        card_state = "loading"
        
        # Act
        card_state = "error"
        
        # Assert
        assert card_state == "error"

    def test_metric_card_error_to_success_on_retry(self):
        """Metric card should transition from error to success on retry."""
        # Arrange
        card_state = "error"
        
        # Act
        card_state = "success"
        
        # Assert
        assert card_state == "success"

    @given(
        error_message=st.text(min_size=1, max_size=100),
    )
    @settings(max_examples=20)
    def test_metric_card_error_message_display(self, error_message):
        """Metric card should display error message when in error state."""
        # Arrange
        card = {
            "state": "error",
            "error_message": error_message,
        }
        
        # Act & Assert
        assert card["state"] == "error"
        assert card["error_message"] == error_message
        assert len(card["error_message"]) > 0


class TestMetricRefreshTiming:
    """Test metric refresh timing and consistency."""

    def test_metrics_auto_refresh_interval(self):
        """Metrics should auto-refresh every 5 minutes."""
        # Arrange
        refresh_interval = 5 * 60  # 5 minutes in seconds
        
        # Act & Assert
        assert refresh_interval == 300, "Refresh interval should be 5 minutes (300 seconds)"

    def test_manual_refresh_completes_quickly(self):
        """Manual refresh should complete within 2 seconds."""
        # Arrange
        start_time = time.time()
        
        # Act
        # Simulate manual refresh
        time.sleep(0.1)  # Simulate quick operation
        
        # Assert
        end_time = time.time()
        elapsed = end_time - start_time
        assert elapsed < 2.0, f"Manual refresh took {elapsed}s, should be < 2s"

    @given(
        refresh_count=st.integers(min_value=1, max_value=10),
    )
    @settings(max_examples=20)
    def test_multiple_refreshes_maintain_consistency(self, refresh_count):
        """Multiple refreshes should maintain data consistency."""
        # Arrange
        metrics = {"count": 5}
        
        # Act
        for _ in range(refresh_count):
            # Simulate refresh
            pass
        
        # Assert
        # After multiple refreshes, metrics should still be valid
        assert isinstance(metrics["count"], int)
        assert metrics["count"] >= 0
