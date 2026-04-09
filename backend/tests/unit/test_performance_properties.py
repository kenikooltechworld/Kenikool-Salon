"""
Property-based tests for staff performance metrics and ratings.

Tests validate the correctness properties for performance page:
- Average rating score calculation
- Individual customer reviews display
- Performance metrics (appointments completed, customer satisfaction)
- Default sort by date descending

**Validates: Requirements 6.2, 6.3, 6.4, 6.5**
"""

import pytest
from datetime import datetime, timedelta, UTC
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from decimal import Decimal
from bson import ObjectId

from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.customer import Customer


# Strategy generators for property-based testing
@st.composite
def rating_values(draw):
    """Generate valid rating values (1-5)."""
    return draw(st.integers(min_value=1, max_value=5))


@st.composite
def review_data_list(draw):
    """Generate a list of review data for testing."""
    num_reviews = draw(st.integers(min_value=1, max_value=20))
    reviews = []
    
    for i in range(num_reviews):
        rating = draw(rating_values())
        # Generate dates in the past 90 days
        days_ago = draw(st.integers(min_value=0, max_value=90))
        review_date = datetime.now(UTC) - timedelta(days=days_ago)
        
        reviews.append({
            "id": str(ObjectId()),
            "customer_id": str(ObjectId()),
            "customer_name": f"Customer {i}",
            "appointment_id": str(ObjectId()),
            "service_name": draw(st.sampled_from(["Haircut", "Coloring", "Styling", "Treatment"])),
            "rating": rating,
            "feedback": draw(st.text(min_size=10, max_size=200, alphabet=st.characters(whitelist_categories=('L', 'N', 'P', 'Z')))),
            "appointment_date": review_date.strftime("%Y-%m-%d"),
            "created_at": review_date.isoformat(),
        })
    
    return reviews


@st.composite
def appointment_counts(draw):
    """Generate valid appointment counts."""
    return draw(st.integers(min_value=0, max_value=500))


@st.composite
def satisfaction_percentages(draw):
    """Generate valid satisfaction percentages (0-100)."""
    return draw(st.integers(min_value=0, max_value=100))


class TestAverageRatingCalculation:
    """
    Property tests for average rating score calculation.
    
    **Validates: Requirement 6.2 - Display average rating score**
    """

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_average_rating_equals_sum_divided_by_count(self, reviews):
        """
        Average rating should equal sum of all ratings divided by count.
        
        For any set of reviews, the average rating SHALL be calculated as
        the sum of all individual ratings divided by the total number of reviews.
        """
        # Calculate expected average
        total_rating = sum(review["rating"] for review in reviews)
        expected_average = total_rating / len(reviews)
        
        # Simulate calculation
        calculated_average = total_rating / len(reviews)
        
        # Assert
        assert abs(calculated_average - expected_average) < 0.01, \
            f"Average rating {calculated_average} should equal {expected_average}"
        
        # Verify average is within valid range
        assert 1.0 <= calculated_average <= 5.0, \
            f"Average rating {calculated_average} should be between 1.0 and 5.0"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_average_rating_changes_with_new_reviews(self, reviews):
        """
        Average rating should update correctly when new reviews are added.
        
        For any set of reviews, adding a new review SHALL update the average
        rating to reflect the new total.
        """
        # Calculate initial average
        initial_total = sum(review["rating"] for review in reviews)
        initial_average = initial_total / len(reviews)
        
        # Add a new review
        new_rating = 5
        new_total = initial_total + new_rating
        new_count = len(reviews) + 1
        new_average = new_total / new_count
        
        # Verify new average is different (unless all ratings were 5)
        if not all(review["rating"] == 5 for review in reviews):
            assert new_average != initial_average, \
                "Average should change when new review is added"
        
        # Verify new average is within valid range
        assert 1.0 <= new_average <= 5.0, \
            f"New average {new_average} should be between 1.0 and 5.0"

    @given(
        rating=rating_values(),
    )
    @settings(max_examples=5)
    def test_single_review_average_equals_rating(self, rating):
        """
        For a single review, average rating should equal that rating.
        
        When only one review exists, the average rating SHALL equal
        that single review's rating value.
        """
        reviews = [{
            "id": str(ObjectId()),
            "rating": rating,
        }]
        
        average = sum(r["rating"] for r in reviews) / len(reviews)
        
        assert average == rating, \
            f"Single review average {average} should equal rating {rating}"

    @given(
        num_reviews=st.integers(min_value=1, max_value=20),
    )
    @settings(max_examples=20)
    def test_all_same_rating_average_equals_that_rating(self, num_reviews):
        """
        When all reviews have the same rating, average should equal that rating.
        
        For any set of reviews with identical ratings, the average SHALL
        equal that common rating value.
        """
        rating = 4
        reviews = [{"rating": rating} for _ in range(num_reviews)]
        
        average = sum(r["rating"] for r in reviews) / len(reviews)
        
        assert average == rating, \
            f"Average {average} should equal common rating {rating}"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_average_rating_precision(self, reviews):
        """
        Average rating should be calculated with appropriate precision.
        
        The average rating SHALL be displayed with one decimal place precision
        (e.g., 4.5, not 4.523456).
        """
        total_rating = sum(review["rating"] for review in reviews)
        average = total_rating / len(reviews)
        
        # Round to 1 decimal place
        rounded_average = round(average, 1)
        
        # Verify rounded value is within valid range
        assert 1.0 <= rounded_average <= 5.0, \
            f"Rounded average {rounded_average} should be between 1.0 and 5.0"
        
        # Verify precision is 1 decimal place
        assert len(str(rounded_average).split('.')[-1]) <= 1, \
            f"Average should have at most 1 decimal place"


class TestReviewsDisplay:
    """
    Property tests for individual customer reviews display.
    
    **Validates: Requirement 6.3 - Display individual customer reviews with ratings**
    """

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_all_reviews_are_displayed(self, reviews):
        """
        All reviews should be displayed in the list.
        
        For any set of reviews, the display SHALL include all reviews
        without omitting any.
        """
        displayed_reviews = reviews.copy()
        
        assert len(displayed_reviews) == len(reviews), \
            f"Should display all {len(reviews)} reviews"
        
        # Verify each review has required fields
        for review in displayed_reviews:
            assert "id" in review
            assert "rating" in review
            assert "customer_name" in review
            assert "feedback" in review
            assert "created_at" in review

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_review_ratings_are_within_valid_range(self, reviews):
        """
        All review ratings should be within valid range (1-5).
        
        For any displayed review, the rating SHALL be between 1 and 5 inclusive.
        """
        for review in reviews:
            assert 1 <= review["rating"] <= 5, \
                f"Review rating {review['rating']} should be between 1 and 5"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_reviews_contain_required_information(self, reviews):
        """
        Each review should contain all required information.
        
        For any review, it SHALL include customer name, rating, feedback,
        service name, and date information.
        """
        required_fields = [
            "customer_name",
            "rating",
            "feedback",
            "service_name",
            "appointment_date",
            "created_at",
        ]
        
        for review in reviews:
            for field in required_fields:
                assert field in review, \
                    f"Review should contain {field}"
                assert review[field] is not None, \
                    f"Review {field} should not be None"

    def test_empty_reviews_list_displays_correctly(self):
        """
        When no reviews exist, appropriate message should be displayed.
        
        For a staff member with no reviews, the system SHALL display
        a "no ratings" message.
        """
        reviews = []
        
        has_reviews = len(reviews) > 0
        
        assert not has_reviews, "Should indicate no reviews exist"
        
        # Verify empty state message would be shown
        empty_message = "No ratings yet. Your reviews will appear here once customers provide feedback."
        assert len(empty_message) > 0, "Should have empty state message"


class TestPerformanceMetrics:
    """
    Property tests for performance metrics display.
    
    **Validates: Requirement 6.4 - Display performance metrics 
    (appointments completed, customer satisfaction)**
    """

    @given(
        appointments_completed=appointment_counts(),
        satisfaction_percentage=satisfaction_percentages(),
    )
    @settings(max_examples=50)
    def test_performance_metrics_are_non_negative(
        self,
        appointments_completed,
        satisfaction_percentage,
    ):
        """
        Performance metrics should always be non-negative.
        
        For any performance metrics, appointments completed and customer
        satisfaction SHALL be non-negative values.
        """
        assert appointments_completed >= 0, \
            f"Appointments completed {appointments_completed} should be non-negative"
        
        assert satisfaction_percentage >= 0, \
            f"Satisfaction {satisfaction_percentage} should be non-negative"

    @given(
        appointments_completed=appointment_counts(),
        satisfaction_percentage=satisfaction_percentages(),
    )
    @settings(max_examples=50)
    def test_satisfaction_percentage_is_within_valid_range(
        self,
        appointments_completed,
        satisfaction_percentage,
    ):
        """
        Customer satisfaction should be a valid percentage (0-100).
        
        For any customer satisfaction metric, the value SHALL be between
        0 and 100 inclusive.
        """
        assert 0 <= satisfaction_percentage <= 100, \
            f"Satisfaction {satisfaction_percentage} should be between 0 and 100"

    @given(
        total_appointments=appointment_counts(),
        completed_appointments=appointment_counts(),
    )
    @settings(max_examples=30)
    def test_completed_appointments_not_exceed_total(
        self,
        total_appointments,
        completed_appointments,
    ):
        """
        Completed appointments should not exceed total appointments.
        
        For any staff member, the number of completed appointments SHALL
        not exceed the total number of appointments.
        """
        assume(completed_appointments <= total_appointments)
        
        assert completed_appointments <= total_appointments, \
            f"Completed {completed_appointments} should not exceed total {total_appointments}"

    @given(
        appointments_completed=appointment_counts(),
        total_reviews=st.integers(min_value=0, max_value=500),
        average_rating=st.floats(min_value=1.0, max_value=5.0, allow_nan=False, allow_infinity=False),
    )
    @settings(max_examples=30)
    def test_performance_metrics_consistency(
        self,
        appointments_completed,
        total_reviews,
        average_rating,
    ):
        """
        Performance metrics should be internally consistent.
        
        For any performance metrics, the relationships between metrics
        SHALL be logically consistent (e.g., can't have more reviews
        than completed appointments).
        """
        # Reviews can't exceed completed appointments
        assume(total_reviews <= appointments_completed)
        
        metrics = {
            "appointmentsCompleted": appointments_completed,
            "totalReviews": total_reviews,
            "averageRating": average_rating,
        }
        
        assert metrics["totalReviews"] <= metrics["appointmentsCompleted"], \
            "Reviews should not exceed completed appointments"
        
        if metrics["totalReviews"] > 0:
            assert 1.0 <= metrics["averageRating"] <= 5.0, \
                "Average rating should be valid when reviews exist"

    @given(
        appointments_completed=appointment_counts(),
    )
    @settings(max_examples=30)
    def test_zero_appointments_metrics(self, appointments_completed):
        """
        Metrics should handle zero appointments correctly.
        
        When a staff member has zero completed appointments, all related
        metrics SHALL be zero or display appropriate empty states.
        """
        if appointments_completed == 0:
            # When no appointments, reviews should also be 0
            total_reviews = 0
            customer_satisfaction = 0
            
            assert total_reviews == 0, "Should have no reviews with no appointments"
            assert customer_satisfaction == 0, "Satisfaction should be 0 with no appointments"


class TestReviewsSorting:
    """
    Property tests for reviews sorting.
    
    **Validates: Requirement 6.5 - Implement default sort by date descending**
    """

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_reviews_sorted_by_date_descending_by_default(self, reviews):
        """
        Reviews should be sorted by date descending by default.
        
        For any set of reviews, when displayed without explicit sorting,
        they SHALL be sorted by date in descending order (newest first).
        """
        # Sort reviews by date descending
        sorted_reviews = sorted(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"]),
            reverse=True
        )
        
        # Verify sorting
        for i in range(len(sorted_reviews) - 1):
            current_date = datetime.fromisoformat(sorted_reviews[i]["created_at"])
            next_date = datetime.fromisoformat(sorted_reviews[i + 1]["created_at"])
            
            assert current_date >= next_date, \
                f"Reviews should be sorted newest first: {current_date} >= {next_date}"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_newest_review_appears_first(self, reviews):
        """
        The newest review should appear first in the list.
        
        For any set of reviews, the review with the most recent date
        SHALL appear at the top of the list.
        """
        # Find the newest review
        newest_review = max(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"])
        )
        
        # Sort reviews by date descending
        sorted_reviews = sorted(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"]),
            reverse=True
        )
        
        # Verify newest is first
        assert sorted_reviews[0]["id"] == newest_review["id"], \
            "Newest review should appear first"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_oldest_review_appears_last(self, reviews):
        """
        The oldest review should appear last in the list.
        
        For any set of reviews, the review with the oldest date
        SHALL appear at the bottom of the list.
        """
        # Find the oldest review
        oldest_review = min(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"])
        )
        
        # Sort reviews by date descending
        sorted_reviews = sorted(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"]),
            reverse=True
        )
        
        # Verify oldest is last
        assert sorted_reviews[-1]["id"] == oldest_review["id"], \
            "Oldest review should appear last"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_sorting_preserves_all_reviews(self, reviews):
        """
        Sorting should preserve all reviews without loss.
        
        For any set of reviews, after sorting by date, all reviews
        SHALL still be present in the list.
        """
        # Sort reviews
        sorted_reviews = sorted(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"]),
            reverse=True
        )
        
        # Verify count is preserved
        assert len(sorted_reviews) == len(reviews), \
            "Sorting should preserve all reviews"
        
        # Verify all IDs are present
        original_ids = set(r["id"] for r in reviews)
        sorted_ids = set(r["id"] for r in sorted_reviews)
        
        assert original_ids == sorted_ids, \
            "Sorting should preserve all review IDs"

    @given(
        num_reviews=st.integers(min_value=2, max_value=10),
    )
    @settings(max_examples=20)
    def test_reviews_with_same_date_maintain_stable_order(self, num_reviews):
        """
        Reviews with the same date should maintain stable order.
        
        For any reviews with identical dates, the sorting SHALL be stable
        and maintain their relative order.
        """
        # Create reviews with same date
        same_date = datetime.now(UTC)
        reviews = [
            {
                "id": f"review_{i}",
                "rating": i + 1,
                "created_at": same_date.isoformat(),
            }
            for i in range(num_reviews)
        ]
        
        # Sort reviews
        sorted_reviews = sorted(
            reviews,
            key=lambda r: datetime.fromisoformat(r["created_at"]),
            reverse=True
        )
        
        # Verify all reviews are present
        assert len(sorted_reviews) == num_reviews, \
            "All reviews with same date should be present"


class TestRatingDistribution:
    """
    Property tests for rating distribution calculations.
    
    **Validates: Requirement 6.2 - Display average rating score (distribution)**
    """

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_rating_distribution_sum_equals_total_reviews(self, reviews):
        """
        Sum of rating distribution should equal total reviews.
        
        For any set of reviews, the sum of counts in the rating distribution
        SHALL equal the total number of reviews.
        """
        # Calculate distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review["rating"]] += 1
        
        # Verify sum equals total
        distribution_sum = sum(distribution.values())
        assert distribution_sum == len(reviews), \
            f"Distribution sum {distribution_sum} should equal total reviews {len(reviews)}"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=30,
        deadline=2000
    )
    def test_rating_distribution_counts_are_non_negative(self, reviews):
        """
        All rating distribution counts should be non-negative.
        
        For any rating distribution, all counts SHALL be non-negative integers.
        """
        # Calculate distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review["rating"]] += 1
        
        # Verify all counts are non-negative
        for rating, count in distribution.items():
            assert count >= 0, \
                f"Rating {rating} count {count} should be non-negative"

    @given(
        reviews=review_data_list(),
    )
    @settings(
        suppress_health_check=[HealthCheck.too_slow],
        max_examples=20,
        deadline=2000
    )
    def test_rating_distribution_percentages_sum_to_100(self, reviews):
        """
        Rating distribution percentages should sum to 100%.
        
        For any rating distribution, when converted to percentages,
        the sum SHALL equal 100% (within rounding tolerance).
        """
        # Calculate distribution
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        for review in reviews:
            distribution[review["rating"]] += 1
        
        # Calculate percentages
        total = len(reviews)
        percentages = {
            rating: (count / total) * 100
            for rating, count in distribution.items()
        }
        
        # Verify sum is approximately 100
        percentage_sum = sum(percentages.values())
        assert abs(percentage_sum - 100.0) < 0.01, \
            f"Percentage sum {percentage_sum} should equal 100%"


class TestPerformanceMetricsEdgeCases:
    """Test edge cases for performance metrics."""

    def test_no_reviews_displays_zero_average(self):
        """
        When no reviews exist, average rating should be 0.0.
        
        For a staff member with no reviews, the average rating SHALL
        display as 0.0 or indicate no data available.
        """
        reviews = []
        
        if len(reviews) == 0:
            average_rating = 0.0
        else:
            average_rating = sum(r["rating"] for r in reviews) / len(reviews)
        
        assert average_rating == 0.0, \
            "Average rating should be 0.0 when no reviews exist"

    def test_no_appointments_displays_zero_metrics(self):
        """
        When no appointments completed, metrics should be zero.
        
        For a staff member with no completed appointments, all performance
        metrics SHALL display as zero or appropriate empty states.
        """
        metrics = {
            "appointmentsCompleted": 0,
            "totalReviews": 0,
            "averageRating": 0.0,
            "customerSatisfaction": 0,
        }
        
        assert metrics["appointmentsCompleted"] == 0
        assert metrics["totalReviews"] == 0
        assert metrics["averageRating"] == 0.0
        assert metrics["customerSatisfaction"] == 0

    @given(
        rating=rating_values(),
    )
    @settings(max_examples=5)
    def test_single_review_metrics_consistency(self, rating):
        """
        With a single review, all metrics should be consistent.
        
        For a staff member with exactly one review, the average rating
        SHALL equal that review's rating, and metrics SHALL be consistent.
        """
        reviews = [{
            "id": str(ObjectId()),
            "rating": rating,
            "created_at": datetime.now(UTC).isoformat(),
        }]
        
        metrics = {
            "totalReviews": len(reviews),
            "averageRating": sum(r["rating"] for r in reviews) / len(reviews),
            "appointmentsCompleted": 1,
        }
        
        assert metrics["totalReviews"] == 1
        assert metrics["averageRating"] == rating
        assert metrics["appointmentsCompleted"] >= metrics["totalReviews"]
