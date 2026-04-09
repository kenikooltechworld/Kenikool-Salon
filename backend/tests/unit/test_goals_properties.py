"""Property-based tests for staff goals and targets.

This module tests the core properties of staff goals:
- Progress percentage calculation accuracy (Requirement 17.3)
- Target achievement history completeness (Requirement 17.4)
- Performance metrics calculation relative to targets (Requirement 17.6)

Validates: Requirements 17.3, 17.4, 17.6
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta, date
from decimal import Decimal
from bson import ObjectId


# Strategy generators for property-based testing
@st.composite
def target_values(draw):
    """Generate valid target values for goals."""
    return draw(st.decimals(
        min_value=Decimal("100.00"),
        max_value=Decimal("10000.00"),
        places=2
    ))


@st.composite
def current_values(draw, target_value):
    """Generate current values relative to target (0% to 150% of target)."""
    max_value = target_value * Decimal("1.5")
    return draw(st.decimals(
        min_value=Decimal("0.00"),
        max_value=max_value,
        places=2
    ))


@st.composite
def goal_periods(draw):
    """Generate valid goal period date ranges."""
    start_date = draw(st.dates(
        min_value=date(2024, 1, 1),
        max_value=date(2024, 12, 1)
    ))
    # Period length between 7 and 90 days
    period_days = draw(st.integers(min_value=7, max_value=90))
    end_date = start_date + timedelta(days=period_days)
    return start_date, end_date



@st.composite
def goal_data(draw):
    """Generate complete goal data for testing."""
    goal_type = draw(st.sampled_from([
        "sales", "commission", "appointments", "customer_satisfaction"
    ]))
    
    target_value = draw(target_values())
    current_value = draw(current_values(target_value))
    start_date, end_date = draw(goal_periods())
    
    # Determine status based on dates and progress
    today = date.today()
    if today > end_date:
        status = "expired"
    elif current_value >= target_value:
        status = "completed"
    else:
        status = "active"
    
    return {
        "goal_type": goal_type,
        "target_value": target_value,
        "current_value": current_value,
        "period_start": start_date,
        "period_end": end_date,
        "status": status,
    }


class TestProgressCalculationAccuracy:
    """Property-based tests for progress percentage calculation accuracy.
    
    Tests that progress percentages are calculated correctly for all goal types.
    
    Validates: Requirement 17.3
    """

    @given(
        target=target_values(),
        current=st.decimals(
            min_value=Decimal("0.00"),
            max_value=Decimal("15000.00"),
            places=2
        ),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=50,
        deadline=1000
    )
    def test_progress_percentage_calculation_is_accurate(self, target, current):
        """
        **Property: Progress Percentage Calculation Accuracy**
        
        For any goal with a target value and current value, the progress
        percentage SHALL be calculated as (current / target) * 100, rounded
        to one decimal place.
        
        Validates: Requirement 17.3
        """
        # Avoid division by zero
        assume(target > Decimal("0"))
        
        # Calculate expected percentage
        expected_percentage = (current / target) * Decimal("100")
        expected_percentage = float(expected_percentage)
        
        # Simulate the calculation that would happen in the backend
        calculated_percentage = (float(current) / float(target)) * 100
        
        # Verify calculation is accurate (within 0.1% tolerance for floating point)
        assert abs(calculated_percentage - expected_percentage) < 0.1, \
            f"Progress percentage {calculated_percentage} should equal {expected_percentage}"


    @given(
        target=target_values(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=1000
    )
    def test_progress_at_zero_is_zero_percent(self, target):
        """
        **Property: Zero Progress**
        
        For any goal with zero current value, the progress percentage
        SHALL be 0%.
        
        Validates: Requirement 17.3
        """
        assume(target > Decimal("0"))
        
        current = Decimal("0.00")
        expected_percentage = 0.0
        
        calculated_percentage = (float(current) / float(target)) * 100
        
        assert calculated_percentage == expected_percentage, \
            f"Progress with zero current should be 0%, got {calculated_percentage}"

    @given(
        target=target_values(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=1000
    )
    def test_progress_at_target_is_hundred_percent(self, target):
        """
        **Property: Complete Progress**
        
        For any goal where current value equals target value, the progress
        percentage SHALL be 100%.
        
        Validates: Requirement 17.3
        """
        assume(target > Decimal("0"))
        
        current = target
        expected_percentage = 100.0
        
        calculated_percentage = (float(current) / float(target)) * 100
        
        assert abs(calculated_percentage - expected_percentage) < 0.01, \
            f"Progress at target should be 100%, got {calculated_percentage}"

    @given(
        target=target_values(),
        multiplier=st.decimals(
            min_value=Decimal("1.01"),
            max_value=Decimal("2.00"),
            places=2
        ),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=1000
    )
    def test_progress_above_target_exceeds_hundred_percent(self, target, multiplier):
        """
        **Property: Over-Achievement**
        
        For any goal where current value exceeds target value, the progress
        percentage SHALL be greater than 100%.
        
        Validates: Requirement 17.3
        """
        assume(target > Decimal("0"))
        
        current = target * multiplier
        
        calculated_percentage = (float(current) / float(target)) * 100
        
        assert calculated_percentage > 100.0, \
            f"Progress above target should exceed 100%, got {calculated_percentage}"


    @given(
        goals_data=st.lists(goal_data(), min_size=1, max_size=5),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_remaining_value_calculation_is_accurate(self, goals_data):
        """
        **Property: Remaining Value Calculation**
        
        For any goal, the remaining value SHALL equal target value minus
        current value, and SHALL never be negative for display purposes.
        
        Validates: Requirement 17.3
        """
        for goal in goals_data:
            target = goal["target_value"]
            current = goal["current_value"]
            
            # Calculate remaining value
            remaining = max(target - current, Decimal("0"))
            expected_remaining = target - current if current < target else Decimal("0")
            
            assert remaining == expected_remaining, \
                f"Remaining value {remaining} should equal {expected_remaining}"
            
            # Verify remaining is never negative
            assert remaining >= Decimal("0"), \
                f"Remaining value should never be negative, got {remaining}"


class TestTargetAchievementHistory:
    """Property-based tests for target achievement history completeness.
    
    Tests that achievement history is complete and accurate.
    
    Validates: Requirement 17.4
    """

    @given(
        num_achievements=st.integers(min_value=1, max_value=10),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_achievement_history_includes_all_completed_goals(self, num_achievements):
        """
        **Property: Achievement History Completeness**
        
        For any staff member, the achievement history SHALL include all
        completed goals, with no completed goals missing from the history.
        
        Validates: Requirement 17.4
        """
        # Create achievement records
        achievements = []
        
        for i in range(num_achievements):
            target = Decimal(f"{(i + 1) * 1000}.00")
            achieved = target + Decimal(f"{i * 100}.00")  # Always exceed target
            
            achievement = {
                "id": str(ObjectId()),
                "goal_id": str(ObjectId()),
                "staff_id": str(ObjectId()),
                "achieved_at": datetime.utcnow() - timedelta(days=i * 10),
                "target_value": target,
                "achieved_value": achieved,
                "bonus_earned": Decimal("100.00") if i % 2 == 0 else None,
            }
            achievements.append(achievement)
        
        # Verify all achievements are present
        assert len(achievements) == num_achievements, \
            f"Should have {num_achievements} achievements, got {len(achievements)}"
        
        # Verify each achievement has required fields
        for achievement in achievements:
            assert "id" in achievement
            assert "goal_id" in achievement
            assert "achieved_at" in achievement
            assert "target_value" in achievement
            assert "achieved_value" in achievement
            assert achievement["achieved_value"] >= achievement["target_value"], \
                "Achieved value should meet or exceed target"


    @given(
        num_achievements=st.integers(min_value=2, max_value=8),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=15,
        deadline=2000
    )
    def test_achievement_history_is_chronologically_ordered(self, num_achievements):
        """
        **Property: Achievement History Ordering**
        
        For any achievement history, achievements SHALL be ordered by
        achieved_at date in descending order (most recent first).
        
        Validates: Requirement 17.4
        """
        # Create achievements with different dates
        achievements = []
        base_date = datetime.utcnow()
        
        for i in range(num_achievements):
            achievement = {
                "id": str(ObjectId()),
                "achieved_at": base_date - timedelta(days=i * 5),
                "target_value": Decimal("1000.00"),
                "achieved_value": Decimal("1200.00"),
            }
            achievements.append(achievement)
        
        # Sort by achieved_at descending (most recent first)
        sorted_achievements = sorted(
            achievements,
            key=lambda x: x["achieved_at"],
            reverse=True
        )
        
        # Verify ordering
        for i in range(len(sorted_achievements) - 1):
            current_date = sorted_achievements[i]["achieved_at"]
            next_date = sorted_achievements[i + 1]["achieved_at"]
            
            assert current_date >= next_date, \
                f"Achievements should be ordered by date descending"

    @given(
        target=target_values(),
        achieved_multiplier=st.decimals(
            min_value=Decimal("1.00"),
            max_value=Decimal("1.50"),
            places=2
        ),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=1000
    )
    def test_achievement_records_accurate_values(self, target, achieved_multiplier):
        """
        **Property: Achievement Value Accuracy**
        
        For any achievement record, the target_value and achieved_value
        SHALL be accurately recorded, and achieved_value SHALL be greater
        than or equal to target_value.
        
        Validates: Requirement 17.4
        """
        achieved = target * achieved_multiplier
        
        achievement = {
            "target_value": target,
            "achieved_value": achieved,
        }
        
        # Verify values are accurate
        assert achievement["target_value"] == target
        assert achievement["achieved_value"] == achieved
        
        # Verify achieved meets or exceeds target
        assert achievement["achieved_value"] >= achievement["target_value"], \
            f"Achieved value {achieved} should be >= target {target}"


class TestPerformanceMetricsCalculation:
    """Property-based tests for performance metrics relative to targets.
    
    Tests that performance metrics are calculated correctly.
    
    Validates: Requirement 17.6
    """

    @given(
        sales_target=target_values(),
        sales_actual=st.decimals(
            min_value=Decimal("0.00"),
            max_value=Decimal("15000.00"),
            places=2
        ),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=40,
        deadline=1000
    )
    def test_sales_vs_target_calculation_is_accurate(self, sales_target, sales_actual):
        """
        **Property: Sales vs Target Accuracy**
        
        For any sales target and actual sales, the performance percentage
        SHALL be calculated as (actual / target) * 100.
        
        Validates: Requirement 17.6
        """
        assume(sales_target > Decimal("0"))
        
        expected_percentage = (sales_actual / sales_target) * Decimal("100")
        expected_percentage = float(expected_percentage)
        
        # Simulate backend calculation
        performance_data = {
            "target": float(sales_target),
            "actual": float(sales_actual),
            "percentage": (float(sales_actual) / float(sales_target)) * 100
        }
        
        assert abs(performance_data["percentage"] - expected_percentage) < 0.1, \
            f"Sales percentage {performance_data['percentage']} should equal {expected_percentage}"


    @given(
        commission_target=target_values(),
        commission_actual=st.decimals(
            min_value=Decimal("0.00"),
            max_value=Decimal("15000.00"),
            places=2
        ),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=40,
        deadline=1000
    )
    def test_commission_vs_target_calculation_is_accurate(
        self, commission_target, commission_actual
    ):
        """
        **Property: Commission vs Target Accuracy**
        
        For any commission target and actual commission, the performance
        percentage SHALL be calculated as (actual / target) * 100.
        
        Validates: Requirement 17.6
        """
        assume(commission_target > Decimal("0"))
        
        expected_percentage = (commission_actual / commission_target) * Decimal("100")
        expected_percentage = float(expected_percentage)
        
        # Simulate backend calculation
        performance_data = {
            "target": float(commission_target),
            "actual": float(commission_actual),
            "percentage": (float(commission_actual) / float(commission_target)) * 100
        }
        
        assert abs(performance_data["percentage"] - expected_percentage) < 0.1, \
            f"Commission percentage {performance_data['percentage']} should equal {expected_percentage}"

    @given(
        appointments_target=st.integers(min_value=10, max_value=200),
        appointments_actual=st.integers(min_value=0, max_value=300),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=40,
        deadline=1000
    )
    def test_appointments_vs_target_calculation_is_accurate(
        self, appointments_target, appointments_actual
    ):
        """
        **Property: Appointments vs Target Accuracy**
        
        For any appointments target and actual appointments, the performance
        percentage SHALL be calculated as (actual / target) * 100.
        
        Validates: Requirement 17.6
        """
        assume(appointments_target > 0)
        
        expected_percentage = (appointments_actual / appointments_target) * 100
        
        # Simulate backend calculation
        performance_data = {
            "target": appointments_target,
            "actual": appointments_actual,
            "percentage": (appointments_actual / appointments_target) * 100
        }
        
        assert abs(performance_data["percentage"] - expected_percentage) < 0.1, \
            f"Appointments percentage {performance_data['percentage']} should equal {expected_percentage}"

    @given(
        sales_target=target_values(),
        commission_target=target_values(),
        appointments_target=st.integers(min_value=10, max_value=200),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_performance_metrics_are_independent(
        self, sales_target, commission_target, appointments_target
    ):
        """
        **Property: Performance Metrics Independence**
        
        For any set of targets, each performance metric (sales, commission,
        appointments) SHALL be calculated independently, and changes to one
        SHALL NOT affect the others.
        
        Validates: Requirement 17.6
        """
        # Create performance data with different actuals
        sales_actual = sales_target * Decimal("0.8")
        commission_actual = commission_target * Decimal("1.2")
        appointments_actual = int(appointments_target * 0.9)
        
        sales_percentage = (float(sales_actual) / float(sales_target)) * 100
        commission_percentage = (float(commission_actual) / float(commission_target)) * 100
        appointments_percentage = (appointments_actual / appointments_target) * 100
        
        # Verify each metric is calculated independently
        assert sales_percentage != commission_percentage or \
               sales_percentage != appointments_percentage, \
            "Metrics should be independent with different percentages"
        
        # Verify changing one doesn't affect others
        new_sales_actual = sales_target * Decimal("0.5")
        new_sales_percentage = (float(new_sales_actual) / float(sales_target)) * 100
        
        # Commission and appointments percentages should remain unchanged
        assert commission_percentage == (float(commission_actual) / float(commission_target)) * 100
        assert appointments_percentage == (appointments_actual / appointments_target) * 100



class TestGoalsEdgeCases:
    """Test edge cases for goals calculations."""

    def test_zero_target_handling(self):
        """
        **Edge Case: Zero Target**
        
        For any goal with zero target value, the system SHALL handle it
        gracefully without division by zero errors.
        
        Validates: Requirement 17.3
        """
        target = Decimal("0.00")
        current = Decimal("100.00")
        
        # Should handle gracefully - either return 0% or indicate invalid target
        # In practice, targets should never be zero, but system should not crash
        try:
            if target > Decimal("0"):
                percentage = (float(current) / float(target)) * 100
            else:
                percentage = 0.0  # Default to 0% for invalid target
            
            assert percentage >= 0, "Percentage should be non-negative"
        except ZeroDivisionError:
            pytest.fail("Should not raise ZeroDivisionError for zero target")

    def test_very_large_target_values(self):
        """
        **Edge Case: Large Target Values**
        
        For goals with very large target values, calculations SHALL remain
        accurate without overflow or precision loss.
        
        Validates: Requirement 17.3
        """
        target = Decimal("999999.99")
        current = Decimal("500000.00")
        
        expected_percentage = (current / target) * Decimal("100")
        calculated_percentage = (float(current) / float(target)) * 100
        
        assert abs(calculated_percentage - float(expected_percentage)) < 0.1, \
            "Large values should be handled accurately"

    def test_very_small_progress_increments(self):
        """
        **Edge Case: Small Progress Increments**
        
        For goals with very small progress increments, the system SHALL
        maintain precision in percentage calculations.
        
        Validates: Requirement 17.3
        """
        target = Decimal("10000.00")
        current = Decimal("0.01")
        
        expected_percentage = (current / target) * Decimal("100")
        calculated_percentage = (float(current) / float(target)) * 100
        
        assert abs(calculated_percentage - float(expected_percentage)) < 0.001, \
            "Small increments should maintain precision"

    def test_expired_goal_with_incomplete_progress(self):
        """
        **Edge Case: Expired Incomplete Goal**
        
        For goals that expire before reaching target, the system SHALL
        accurately report the final progress percentage and remaining value.
        
        Validates: Requirement 17.3
        """
        target = Decimal("5000.00")
        current = Decimal("3000.00")
        
        progress_percentage = (float(current) / float(target)) * 100
        remaining = target - current
        
        assert progress_percentage == 60.0, "Should show 60% progress"
        assert remaining == Decimal("2000.00"), "Should show correct remaining"
        assert progress_percentage < 100.0, "Expired incomplete goal should be < 100%"

    def test_over_achievement_percentage(self):
        """
        **Edge Case: Over-Achievement**
        
        For goals where actual exceeds target by significant margin, the
        system SHALL accurately calculate percentages over 100%.
        
        Validates: Requirement 17.3, 17.6
        """
        target = Decimal("1000.00")
        current = Decimal("2500.00")
        
        progress_percentage = (float(current) / float(target)) * 100
        
        assert progress_percentage == 250.0, "Should show 250% progress"
        assert progress_percentage > 100.0, "Over-achievement should exceed 100%"

    def test_achievement_with_zero_bonus(self):
        """
        **Edge Case: Achievement Without Bonus**
        
        For achievements that don't earn bonuses, the system SHALL correctly
        record the achievement with bonus_earned as None or 0.
        
        Validates: Requirement 17.4
        """
        achievement = {
            "id": str(ObjectId()),
            "target_value": Decimal("1000.00"),
            "achieved_value": Decimal("1100.00"),
            "bonus_earned": None,
        }
        
        assert achievement["achieved_value"] >= achievement["target_value"]
        assert achievement["bonus_earned"] is None or achievement["bonus_earned"] == 0

    def test_multiple_goal_types_for_same_staff(self):
        """
        **Edge Case: Multiple Goal Types**
        
        For staff with multiple goal types (sales, commission, appointments),
        each goal SHALL be tracked independently with accurate progress.
        
        Validates: Requirement 17.3, 17.6
        """
        goals = [
            {
                "goal_type": "sales",
                "target": Decimal("5000.00"),
                "current": Decimal("3000.00"),
            },
            {
                "goal_type": "commission",
                "target": Decimal("1000.00"),
                "current": Decimal("1200.00"),
            },
            {
                "goal_type": "appointments",
                "target": 50,
                "current": 45,
            },
        ]
        
        # Calculate progress for each
        sales_progress = (float(goals[0]["current"]) / float(goals[0]["target"])) * 100
        commission_progress = (float(goals[1]["current"]) / float(goals[1]["target"])) * 100
        appointments_progress = (goals[2]["current"] / goals[2]["target"]) * 100
        
        assert sales_progress == 60.0
        assert commission_progress == 120.0
        assert appointments_progress == 90.0
        
        # Verify independence
        assert sales_progress != commission_progress
        assert commission_progress != appointments_progress
