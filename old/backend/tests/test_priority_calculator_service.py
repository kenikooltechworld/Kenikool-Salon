"""
Unit tests for Priority Calculator Service
Validates: Requirements 6.1, 6.2, 6.3
"""
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.priority_calculator_service import PriorityCalculatorService


class TestPriorityCalculatorService:
    """Test priority calculator service"""
    
    def test_calculate_priority_new_entry_no_preferences(self):
        """Test priority for new entry with no preferences (0 days wait)"""
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": None,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score only (100)
        assert priority == 100.0
    
    def test_calculate_priority_15_day_old_entry(self):
        """Test priority for 15-day-old entry"""
        entry = {
            "created_at": datetime.utcnow() - timedelta(days=15),
            "preferred_date": None,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score (100) + wait time (15 days)
        assert priority == 115.0
    
    def test_calculate_priority_with_future_preferred_date(self):
        """Test priority with preferred date in future (within 7 days)"""
        future_date = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d')
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": future_date,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score (100) + preferred date bonus (20)
        assert priority == 120.0
    
    def test_calculate_priority_with_past_preferred_date(self):
        """Test priority with preferred date in past"""
        past_date = (datetime.utcnow() - timedelta(days=5)).strftime('%Y-%m-%d')
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": past_date,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score (100) + preferred date penalty (-10)
        assert priority == 90.0
    
    def test_calculate_priority_with_far_future_preferred_date(self):
        """Test priority with preferred date far in future (beyond 7 days)"""
        far_future_date = (datetime.utcnow() + timedelta(days=30)).strftime('%Y-%m-%d')
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": far_future_date,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score only (100) - no bonus for dates beyond 7 days
        assert priority == 100.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_calculate_priority_with_loyalty_bonus(self, mock_get_db):
        """Test priority with client loyalty bonus"""
        # Mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 2  # 2 previous bookings
        
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": None,
            "client_id": "client-123",
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score (100) + loyalty bonus (2 * 5 = 10)
        assert priority == 110.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_calculate_priority_with_max_loyalty_bonus(self, mock_get_db):
        """Test priority with maximum loyalty bonus (3+ bookings)"""
        # Mock database
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 5  # 5 previous bookings
        
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": None,
            "client_id": "client-123",
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score (100) + max loyalty bonus (15)
        assert priority == 115.0
    
    def test_calculate_priority_combined_factors(self):
        """Test priority calculation with multiple factors combined"""
        future_date = (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%d')
        entry = {
            "created_at": datetime.utcnow() - timedelta(days=10),
            "preferred_date": future_date,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        # Base score (100) + wait time (10) + preferred date bonus (20)
        assert priority == 130.0
    
    def test_wait_time_score_new_entry(self):
        """Test wait time score for new entry"""
        score = PriorityCalculatorService._calculate_wait_time_score(datetime.utcnow())
        
        assert score == 0.0
    
    def test_wait_time_score_1_day_old(self):
        """Test wait time score for 1-day-old entry"""
        score = PriorityCalculatorService._calculate_wait_time_score(
            datetime.utcnow() - timedelta(days=1)
        )
        
        assert score == 1.0
    
    def test_wait_time_score_15_days_old(self):
        """Test wait time score for 15-day-old entry"""
        score = PriorityCalculatorService._calculate_wait_time_score(
            datetime.utcnow() - timedelta(days=15)
        )
        
        assert score == 15.0
    
    def test_wait_time_score_capped_at_max(self):
        """Test wait time score is capped at maximum"""
        score = PriorityCalculatorService._calculate_wait_time_score(
            datetime.utcnow() - timedelta(days=100)
        )
        
        # Should be capped at 30
        assert score == 30.0
    
    def test_wait_time_score_none_created_at(self):
        """Test wait time score with None created_at"""
        score = PriorityCalculatorService._calculate_wait_time_score(None)
        
        assert score == 0.0
    
    def test_wait_time_score_string_created_at_iso_format(self):
        """Test wait time score with ISO format string"""
        iso_date = (datetime.utcnow() - timedelta(days=5)).isoformat()
        score = PriorityCalculatorService._calculate_wait_time_score(iso_date)
        
        assert score == 5.0
    
    def test_date_preference_score_no_preferred_date(self):
        """Test date preference score with no preferred date"""
        score = PriorityCalculatorService._calculate_date_preference_score(None)
        
        assert score == 0.0
    
    def test_date_preference_score_today(self):
        """Test date preference score for today"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        score = PriorityCalculatorService._calculate_date_preference_score(today)
        
        # Today is within 7-day window
        assert score == 20.0
    
    def test_date_preference_score_3_days_future(self):
        """Test date preference score for 3 days in future"""
        future_date = (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d')
        score = PriorityCalculatorService._calculate_date_preference_score(future_date)
        
        # Within 7-day window
        assert score == 20.0
    
    def test_date_preference_score_7_days_future(self):
        """Test date preference score for exactly 7 days in future"""
        future_date = (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d')
        score = PriorityCalculatorService._calculate_date_preference_score(future_date)
        
        # Exactly at boundary
        assert score == 20.0
    
    def test_date_preference_score_8_days_future(self):
        """Test date preference score for 8 days in future"""
        future_date = (datetime.utcnow() + timedelta(days=8)).strftime('%Y-%m-%d')
        score = PriorityCalculatorService._calculate_date_preference_score(future_date)
        
        # Beyond 7-day window
        assert score == 0.0
    
    def test_date_preference_score_yesterday(self):
        """Test date preference score for yesterday"""
        yesterday = (datetime.utcnow() - timedelta(days=1)).strftime('%Y-%m-%d')
        score = PriorityCalculatorService._calculate_date_preference_score(yesterday)
        
        # Past date
        assert score == -10.0
    
    def test_date_preference_score_30_days_ago(self):
        """Test date preference score for 30 days ago"""
        past_date = (datetime.utcnow() - timedelta(days=30)).strftime('%Y-%m-%d')
        score = PriorityCalculatorService._calculate_date_preference_score(past_date)
        
        # Past date
        assert score == -10.0
    
    def test_date_preference_score_iso_format(self):
        """Test date preference score with ISO format datetime"""
        future_date = datetime.utcnow() + timedelta(days=2)
        score = PriorityCalculatorService._calculate_date_preference_score(
            future_date.isoformat()
        )
        
        assert score == 20.0
    
    def test_date_preference_score_invalid_format(self):
        """Test date preference score with invalid format"""
        score = PriorityCalculatorService._calculate_date_preference_score("invalid-date")
        
        assert score == 0.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_no_previous_bookings(self, mock_get_db):
        """Test loyalty score with no previous bookings"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 0
        
        score = PriorityCalculatorService._calculate_loyalty_score("client-123")
        
        assert score == 0.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_1_previous_booking(self, mock_get_db):
        """Test loyalty score with 1 previous booking"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 1
        
        score = PriorityCalculatorService._calculate_loyalty_score("client-123")
        
        assert score == 5.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_3_previous_bookings(self, mock_get_db):
        """Test loyalty score with 3 previous bookings"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 3
        
        score = PriorityCalculatorService._calculate_loyalty_score("client-123")
        
        assert score == 15.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_capped_at_max(self, mock_get_db):
        """Test loyalty score is capped at maximum"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 10
        
        score = PriorityCalculatorService._calculate_loyalty_score("client-123")
        
        # Should be capped at 15
        assert score == 15.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_none_client_identifier(self, mock_get_db):
        """Test loyalty score with None client identifier"""
        score = PriorityCalculatorService._calculate_loyalty_score(None)
        
        assert score == 0.0
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_by_email(self, mock_get_db):
        """Test loyalty score lookup by email"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 2
        
        score = PriorityCalculatorService._calculate_loyalty_score("client@example.com")
        
        assert score == 10.0
        # Verify the query was made with email
        mock_db.bookings.count_documents.assert_called_once()
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_database_error_handling(self, mock_get_db):
        """Test loyalty score handles database errors gracefully"""
        mock_get_db.side_effect = Exception("Database error")
        
        score = PriorityCalculatorService._calculate_loyalty_score("client-123")
        
        # Should return 0 on error
        assert score == 0.0
    
    def test_priority_constants_are_correct(self):
        """Test that priority calculation constants are set correctly"""
        assert PriorityCalculatorService.BASE_SCORE == 100
        assert PriorityCalculatorService.MAX_WAIT_TIME_BONUS == 30
        assert PriorityCalculatorService.PREFERRED_DATE_MATCH_BONUS == 20
        assert PriorityCalculatorService.PREFERRED_DATE_PENALTY == -10
        assert PriorityCalculatorService.LOYALTY_BONUS_PER_BOOKING == 5
        assert PriorityCalculatorService.MAX_LOYALTY_BONUS == 15
        assert PriorityCalculatorService.PREFERRED_DATE_WINDOW_DAYS == 7
    
    def test_priority_score_is_float(self):
        """Test that priority score is always returned as float"""
        entry = {
            "created_at": datetime.utcnow(),
            "preferred_date": None,
            "client_id": None,
            "client_email": None
        }
        
        priority = PriorityCalculatorService.calculate_priority(entry)
        
        assert isinstance(priority, float)
    
    def test_wait_time_score_is_float(self):
        """Test that wait time score is always returned as float"""
        score = PriorityCalculatorService._calculate_wait_time_score(datetime.utcnow())
        
        assert isinstance(score, float)
    
    def test_date_preference_score_is_float(self):
        """Test that date preference score is always returned as float"""
        score = PriorityCalculatorService._calculate_date_preference_score(None)
        
        assert isinstance(score, float)
    
    @patch('app.services.priority_calculator_service.Database.get_db')
    def test_loyalty_score_is_float(self, mock_get_db):
        """Test that loyalty score is always returned as float"""
        mock_db = MagicMock()
        mock_get_db.return_value = mock_db
        mock_db.bookings.count_documents.return_value = 0
        
        score = PriorityCalculatorService._calculate_loyalty_score("client-123")
        
        assert isinstance(score, float)
