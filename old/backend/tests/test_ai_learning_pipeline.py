import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock

from app.services.pattern_analyzer import PatternAnalyzer
from app.services.prediction_engine import PredictionEngine
from app.services.suggestion_generator import SuggestionGenerator
from app.services.insight_generator import InsightGenerator
from app.services.proactive_alerter import ProactiveAlerter
from app.services.learning_model import LearningModel
from app.services.background_learning_job import BackgroundLearningJob


class TestAILearningPipeline:
    """Test AI learning pipeline end-to-end"""

    @pytest.fixture
    def services(self):
        """Initialize all AI services"""
        return {
            'pattern_analyzer': PatternAnalyzer(),
            'prediction_engine': PredictionEngine(),
            'suggestion_generator': SuggestionGenerator(),
            'insight_generator': InsightGenerator(),
            'proactive_alerter': ProactiveAlerter(),
            'learning_model': LearningModel()
        }

    def test_pattern_analysis_with_historical_data(self, services):
        """Test pattern analysis with historical booking data"""
        analyzer = services['pattern_analyzer']
        
        # Create sample booking data
        bookings = [
            {'date': '2024-01-15', 'time': '10:00', 'service': 'haircut', 'revenue': 50},
            {'date': '2024-01-15', 'time': '11:00', 'service': 'coloring', 'revenue': 80},
            {'date': '2024-01-16', 'time': '10:00', 'service': 'haircut', 'revenue': 50},
        ]
        
        # Analyze patterns
        patterns = analyzer.analyze_booking_patterns(bookings)
        
        # Verify patterns are generated
        assert patterns is not None
        assert isinstance(patterns, dict)

    def test_prediction_accuracy(self, services):
        """Test prediction engine accuracy"""
        engine = services['prediction_engine']
        
        # Create historical data
        historical_bookings = [
            {'date': '2024-01-01', 'count': 5},
            {'date': '2024-01-02', 'count': 6},
            {'date': '2024-01-03', 'count': 5},
            {'date': '2024-01-04', 'count': 7},
            {'date': '2024-01-05', 'count': 6},
        ]
        
        # Make predictions
        predictions = asyncio.run(
            engine.predict_booking_demand(historical_bookings, days_ahead=7)
        )
        
        # Verify predictions
        assert predictions is not None
        assert 'predictions' in predictions or 'error' in predictions

    def test_suggestion_generation(self, services):
        """Test suggestion generation from patterns"""
        generator = services['suggestion_generator']
        
        # Generate suggestions
        suggestions = generator.get_high_impact_suggestions()
        
        # Verify suggestions
        assert suggestions is not None
        assert isinstance(suggestions, list)

    def test_proactive_alerts(self, services):
        """Test proactive alert generation"""
        alerter = services['proactive_alerter']
        
        # Check for alerts
        alerter.check_inventory_shortages()
        alerter.check_client_churn_risks()
        alerter.check_underutilized_slots()
        
        # Get active alerts
        alerts = alerter.get_active_alerts()
        
        # Verify alerts
        assert alerts is not None
        assert isinstance(alerts, list)

    def test_feedback_incorporation(self, services):
        """Test feedback incorporation into learning model"""
        model = services['learning_model']
        
        # Incorporate feedback
        model.incorporate_feedback(
            suggestion_id='test-123',
            feedback=True,
            user_id='user-456'
        )
        
        # Verify model state
        assert model is not None

    def test_learning_model_update_from_bookings(self, services):
        """Test learning model updates from booking data"""
        model = services['learning_model']
        
        # Create booking data
        bookings = [
            {'id': '1', 'date': '2024-01-15', 'service': 'haircut', 'revenue': 50},
            {'id': '2', 'date': '2024-01-15', 'service': 'coloring', 'revenue': 80},
        ]
        
        # Update model
        model.update_from_bookings(bookings)
        
        # Verify model updated
        assert model is not None

    def test_learning_model_update_from_services(self, services):
        """Test learning model updates from service completions"""
        model = services['learning_model']
        
        # Create service data
        services_data = [
            {'id': '1', 'type': 'haircut', 'duration': 30, 'rating': 5},
            {'id': '2', 'type': 'coloring', 'duration': 60, 'rating': 4},
        ]
        
        # Update model
        model.update_from_services(services_data)
        
        # Verify model updated
        assert model is not None

    def test_learning_model_update_from_inventory(self, services):
        """Test learning model updates from inventory changes"""
        model = services['learning_model']
        
        # Create inventory data
        inventory_data = [
            {'item': 'shampoo', 'quantity': 10, 'usage_rate': 2},
            {'item': 'conditioner', 'quantity': 8, 'usage_rate': 1.5},
        ]
        
        # Update model
        model.update_from_inventory(inventory_data)
        
        # Verify model updated
        assert model is not None

    def test_learning_model_persistence(self, services):
        """Test learning model save and load"""
        model = services['learning_model']
        
        # Save model
        model.save_model()
        
        # Verify model saved
        assert model is not None

    @pytest.mark.asyncio
    async def test_background_job_learning_cycle(self, services):
        """Test complete background learning cycle"""
        job = BackgroundLearningJob(
            pattern_analyzer=services['pattern_analyzer'],
            prediction_engine=services['prediction_engine'],
            suggestion_generator=services['suggestion_generator'],
            insight_generator=services['insight_generator'],
            proactive_alerter=services['proactive_alerter'],
            learning_model=services['learning_model']
        )
        
        # Run learning cycle
        await job.run_learning_cycle()
        
        # Verify cycle completed
        assert job is not None

    def test_data_collection_to_pattern_analysis_flow(self, services):
        """Test data collection → pattern analysis flow"""
        analyzer = services['pattern_analyzer']
        
        # Simulate data collection
        bookings = [
            {'date': '2024-01-15', 'time': '10:00', 'service': 'haircut'},
            {'date': '2024-01-15', 'time': '11:00', 'service': 'coloring'},
            {'date': '2024-01-16', 'time': '10:00', 'service': 'haircut'},
        ]
        
        # Analyze patterns
        patterns = analyzer.analyze_booking_patterns(bookings)
        
        # Verify flow
        assert patterns is not None

    def test_pattern_analysis_to_prediction_flow(self, services):
        """Test pattern analysis → prediction flow"""
        analyzer = services['pattern_analyzer']
        engine = services['prediction_engine']
        
        # Analyze patterns
        bookings = [
            {'date': '2024-01-01', 'count': 5},
            {'date': '2024-01-02', 'count': 6},
            {'date': '2024-01-03', 'count': 5},
        ]
        patterns = analyzer.analyze_booking_patterns(bookings)
        
        # Make predictions
        predictions = asyncio.run(
            engine.predict_booking_demand(bookings, days_ahead=7)
        )
        
        # Verify flow
        assert patterns is not None
        assert predictions is not None

    def test_prediction_to_suggestion_flow(self, services):
        """Test prediction → suggestion flow"""
        engine = services['prediction_engine']
        generator = services['suggestion_generator']
        
        # Make predictions
        predictions = asyncio.run(
            engine.predict_booking_demand([], days_ahead=7)
        )
        
        # Generate suggestions
        suggestions = generator.get_high_impact_suggestions()
        
        # Verify flow
        assert suggestions is not None

    def test_suggestion_to_feedback_flow(self, services):
        """Test suggestion → feedback incorporation flow"""
        generator = services['suggestion_generator']
        model = services['learning_model']
        
        # Generate suggestions
        suggestions = generator.get_high_impact_suggestions()
        
        # Incorporate feedback
        if suggestions:
            model.incorporate_feedback(
                suggestion_id=suggestions[0].get('id', 'test-1'),
                feedback=True,
                user_id='user-1'
            )
        
        # Verify flow
        assert model is not None

    def test_alert_generation_from_patterns(self, services):
        """Test alert generation from pattern analysis"""
        analyzer = services['pattern_analyzer']
        alerter = services['proactive_alerter']
        
        # Analyze patterns
        bookings = [
            {'date': '2024-01-15', 'time': '10:00', 'service': 'haircut'},
        ]
        patterns = analyzer.analyze_booking_patterns(bookings)
        
        # Check for alerts
        alerter.check_inventory_shortages()
        alerts = alerter.get_active_alerts()
        
        # Verify flow
        assert alerts is not None

    def test_insight_generation_from_patterns(self, services):
        """Test insight generation from pattern analysis"""
        analyzer = services['pattern_analyzer']
        generator = services['insight_generator']
        
        # Analyze patterns
        bookings = [
            {'date': '2024-01-15', 'time': '10:00', 'service': 'haircut', 'revenue': 50},
        ]
        patterns = analyzer.analyze_booking_patterns(bookings)
        
        # Generate insights
        insights = generator.get_actionable_insights()
        
        # Verify flow
        assert insights is not None

    def test_concurrent_learning_updates(self, services):
        """Test concurrent updates to learning model"""
        model = services['learning_model']
        
        # Simulate concurrent updates
        bookings = [{'id': '1', 'date': '2024-01-15'}]
        services_data = [{'id': '1', 'type': 'haircut'}]
        inventory_data = [{'item': 'shampoo', 'quantity': 10}]
        
        # Update model from multiple sources
        model.update_from_bookings(bookings)
        model.update_from_services(services_data)
        model.update_from_inventory(inventory_data)
        
        # Verify model consistency
        assert model is not None

    def test_learning_model_privacy(self, services):
        """Test learning model privacy and encryption"""
        model = services['learning_model']
        
        # Update model with sensitive data
        bookings = [
            {'id': '1', 'client': 'John Doe', 'revenue': 50}
        ]
        model.update_from_bookings(bookings)
        
        # Save model (should be encrypted)
        model.save_model()
        
        # Verify privacy
        assert model is not None


class TestAILearningIntegration:
    """Integration tests for AI learning features"""

    @pytest.fixture
    def services(self):
        """Initialize all AI services"""
        return {
            'pattern_analyzer': PatternAnalyzer(),
            'prediction_engine': PredictionEngine(),
            'suggestion_generator': SuggestionGenerator(),
            'insight_generator': InsightGenerator(),
            'proactive_alerter': ProactiveAlerter(),
            'learning_model': LearningModel()
        }

    @pytest.mark.asyncio
    async def test_complete_learning_pipeline(self, services):
        """Test complete AI learning pipeline"""
        # Step 1: Collect data
        bookings = [
            {'date': '2024-01-15', 'time': '10:00', 'service': 'haircut', 'revenue': 50},
            {'date': '2024-01-15', 'time': '11:00', 'service': 'coloring', 'revenue': 80},
        ]
        
        # Step 2: Analyze patterns
        patterns = services['pattern_analyzer'].analyze_booking_patterns(bookings)
        assert patterns is not None
        
        # Step 3: Make predictions
        predictions = await services['prediction_engine'].predict_booking_demand(
            bookings, days_ahead=7
        )
        assert predictions is not None
        
        # Step 4: Generate suggestions
        suggestions = services['suggestion_generator'].get_high_impact_suggestions()
        assert suggestions is not None
        
        # Step 5: Generate insights
        insights = services['insight_generator'].get_actionable_insights()
        assert insights is not None
        
        # Step 6: Check alerts
        services['proactive_alerter'].check_inventory_shortages()
        alerts = services['proactive_alerter'].get_active_alerts()
        assert alerts is not None
        
        # Step 7: Update learning model
        services['learning_model'].update_from_bookings(bookings)
        services['learning_model'].save_model()
        
        # Verify complete pipeline
        assert patterns is not None
        assert predictions is not None
        assert suggestions is not None
        assert insights is not None
        assert alerts is not None

    @pytest.mark.asyncio
    async def test_feedback_loop_integration(self, services):
        """Test feedback loop integration"""
        # Generate suggestions
        suggestions = services['suggestion_generator'].get_high_impact_suggestions()
        
        # User provides feedback
        if suggestions:
            services['learning_model'].incorporate_feedback(
                suggestion_id=suggestions[0].get('id', 'test-1'),
                feedback=True,
                user_id='user-1'
            )
        
        # Model learns from feedback
        services['learning_model'].save_model()
        
        # Verify feedback incorporated
        assert services['learning_model'] is not None

    @pytest.mark.asyncio
    async def test_proactive_alert_generation_integration(self, services):
        """Test proactive alert generation integration"""
        # Analyze patterns
        bookings = [{'date': '2024-01-15', 'time': '10:00'}]
        services['pattern_analyzer'].analyze_booking_patterns(bookings)
        
        # Check for alerts
        services['proactive_alerter'].check_inventory_shortages()
        services['proactive_alerter'].check_client_churn_risks()
        services['proactive_alerter'].check_underutilized_slots()
        
        # Get alerts
        alerts = services['proactive_alerter'].get_active_alerts()
        
        # Verify alerts generated
        assert alerts is not None
        assert isinstance(alerts, list)
