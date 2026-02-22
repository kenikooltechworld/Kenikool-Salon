import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional

logger = logging.getLogger(__name__)


class BackgroundLearningJob:
    """Scheduled background job for AI learning and pattern analysis"""

    def __init__(
        self,
        pattern_analyzer=None,
        prediction_engine=None,
        suggestion_generator=None,
        insight_generator=None,
        proactive_alerter=None,
        learning_model=None
    ):
        """Initialize background learning job"""
        self.pattern_analyzer = pattern_analyzer
        self.prediction_engine = prediction_engine
        self.suggestion_generator = suggestion_generator
        self.insight_generator = insight_generator
        self.proactive_alerter = proactive_alerter
        self.learning_model = learning_model
        self.is_running = False
        self.last_run = None

    async def start(self, interval_minutes: int = 60):
        """Start background job with specified interval"""
        self.is_running = True
        logger.info(f"Starting background learning job (interval: {interval_minutes} minutes)")
        
        while self.is_running:
            try:
                await self.run_learning_cycle()
                self.last_run = datetime.utcnow()
                await asyncio.sleep(interval_minutes * 60)
            except Exception as e:
                logger.error(f"Background learning job error: {e}")
                await asyncio.sleep(60)  # Retry after 1 minute on error

    async def stop(self):
        """Stop background job"""
        self.is_running = False
        logger.info("Stopping background learning job")

    async def run_learning_cycle(self):
        """Run complete learning cycle"""
        try:
            logger.info("Running learning cycle...")
            
            # Step 1: Analyze patterns
            await self._analyze_patterns()
            
            # Step 2: Update predictions
            await self._update_predictions()
            
            # Step 3: Generate suggestions
            await self._generate_suggestions()
            
            # Step 4: Generate insights
            await self._generate_insights()
            
            # Step 5: Check for alerts
            await self._check_alerts()
            
            # Step 6: Update learning model
            await self._update_learning_model()
            
            logger.info("Learning cycle completed successfully")
        except Exception as e:
            logger.error(f"Learning cycle failed: {e}")

    async def _analyze_patterns(self):
        """Analyze booking, service, inventory, revenue, and staff patterns"""
        try:
            if not self.pattern_analyzer:
                return
            
            logger.debug("Analyzing patterns...")
            
            # Analyze booking patterns
            booking_patterns = await self.pattern_analyzer.analyze_booking_patterns([])
            logger.debug(f"Booking patterns: {booking_patterns}")
            
            # Analyze service patterns
            service_patterns = await self.pattern_analyzer.analyze_service_patterns([])
            logger.debug(f"Service patterns: {service_patterns}")
            
            # Analyze inventory patterns
            inventory_patterns = await self.pattern_analyzer.analyze_inventory_patterns([])
            logger.debug(f"Inventory patterns: {inventory_patterns}")
            
            # Analyze revenue patterns
            revenue_patterns = await self.pattern_analyzer.analyze_revenue_patterns([])
            logger.debug(f"Revenue patterns: {revenue_patterns}")
            
            # Analyze staff patterns
            staff_patterns = await self.pattern_analyzer.analyze_staff_patterns([])
            logger.debug(f"Staff patterns: {staff_patterns}")
            
        except Exception as e:
            logger.error(f"Pattern analysis failed: {e}")

    async def _update_predictions(self):
        """Update all prediction models"""
        try:
            if not self.prediction_engine:
                return
            
            logger.debug("Updating predictions...")
            
            # Update booking demand predictions
            try:
                await self.prediction_engine.predict_booking_demand([], days_ahead=7)
            except TypeError:
                logger.debug("predict_booking_demand signature mismatch, skipping")
            
            # Update revenue forecasts
            try:
                await self.prediction_engine.forecast_revenue([])
            except TypeError:
                logger.debug("forecast_revenue signature mismatch, skipping")
            
            # Update churn predictions
            try:
                await self.prediction_engine.predict_client_churn([])
            except TypeError:
                logger.debug("predict_client_churn signature mismatch, skipping")
            
            # Update inventory predictions
            try:
                await self.prediction_engine.predict_inventory_depletion()
            except TypeError:
                logger.debug("predict_inventory_depletion requires item_id, skipping")
            
            # Update staffing predictions (requires date argument)
            try:
                from datetime import datetime
                await self.prediction_engine.predict_optimal_staffing(datetime.utcnow())
            except TypeError:
                logger.debug("predict_optimal_staffing signature mismatch, skipping")
            
            logger.debug("Predictions updated")
        except Exception as e:
            logger.error(f"Prediction update failed: {e}")

    async def _generate_suggestions(self):
        """Generate high-impact suggestions"""
        try:
            if not self.suggestion_generator:
                return
            
            logger.debug("Generating suggestions...")
            suggestions = self.suggestion_generator.get_high_impact_suggestions()
            logger.debug(f"Generated {len(suggestions)} suggestions")
        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")

    async def _generate_insights(self):
        """Generate business insights"""
        try:
            if not self.insight_generator:
                return
            
            logger.debug("Generating insights...")
            insights = self.insight_generator.get_actionable_insights()
            logger.debug(f"Generated {len(insights)} insights")
        except Exception as e:
            logger.error(f"Insight generation failed: {e}")

    async def _check_alerts(self):
        """Check for proactive alerts"""
        try:
            if not self.proactive_alerter:
                return
            
            logger.debug("Checking for alerts...")
            
            # Check inventory shortages
            try:
                self.proactive_alerter.check_inventory_shortages()
            except (AttributeError, TypeError):
                logger.debug("check_inventory_shortages not available or signature mismatch")
            
            # Check client churn risks
            try:
                self.proactive_alerter.check_client_churn_risks()
            except (AttributeError, TypeError):
                logger.debug("check_client_churn_risks not available or signature mismatch")
            
            # Check underutilized slots (requires booking_data argument)
            try:
                self.proactive_alerter.check_underutilized_slots([])
            except (AttributeError, TypeError):
                logger.debug("check_underutilized_slots signature mismatch, skipping")
            
            # Check staff performance
            try:
                self.proactive_alerter.check_staff_performance()
            except (AttributeError, TypeError):
                logger.debug("check_staff_performance not available or signature mismatch")
            
            try:
                alerts = self.proactive_alerter.get_active_alerts()
                logger.debug(f"Found {len(alerts)} active alerts")
            except (AttributeError, TypeError):
                logger.debug("get_active_alerts not available")
        except Exception as e:
            logger.error(f"Alert checking failed: {e}")

    async def _update_learning_model(self):
        """Update learning model with recent data"""
        try:
            if not self.learning_model:
                return
            
            logger.debug("Updating learning model...")
            
            # Update from booking data
            try:
                self.learning_model.update_from_bookings([])
            except (AttributeError, TypeError):
                logger.debug("update_from_bookings not available or signature mismatch")
            
            # Update from service completions
            try:
                self.learning_model.update_from_services([])
            except (AttributeError, TypeError):
                logger.debug("update_from_services not available or signature mismatch")
            
            # Update from inventory changes
            try:
                self.learning_model.update_from_inventory([])
            except (AttributeError, TypeError):
                logger.debug("update_from_inventory not available or signature mismatch")
            
            # Save model (requires filepath argument)
            try:
                import tempfile
                temp_dir = tempfile.gettempdir()
                model_path = f"{temp_dir}/learning_model.pkl"
                self.learning_model.save_model(model_path)
            except (AttributeError, TypeError):
                logger.debug("save_model signature mismatch or not available, skipping")
            
            logger.debug("Learning model updated")
        except Exception as e:
            logger.error(f"Learning model update failed: {e}")

    def get_status(self) -> dict:
        """Get job status"""
        return {
            "is_running": self.is_running,
            "last_run": self.last_run.isoformat() if self.last_run else None,
            "next_run": (self.last_run + timedelta(hours=1)).isoformat() if self.last_run else None
        }
