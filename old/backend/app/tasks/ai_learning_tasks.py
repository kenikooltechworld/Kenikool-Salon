"""
AI Learning Background Tasks
Implements scheduled pattern analysis and learning model updates
Implements Requirements 21.1, 21.2, 21.3, 21.4, 21.5, 28.1
"""

from datetime import datetime, timedelta
from typing import List
import logging
from celery import shared_task
from pymongo.database import Database as PyMongoDatabase

from app.database import get_database
from app.services.pattern_analyzer import PatternAnalyzer
from app.services.prediction_engine import PredictionEngine
from app.services.suggestion_generator import SuggestionGenerator
from app.services.insight_generator import InsightGenerator
from app.services.proactive_alerter import ProactiveAlerter
from app.services.learning_model import LearningModel
from app.services.booking_service import BookingService
from app.services.client_service import ClientService
from app.services.inventory_service import InventoryService
from app.services import analytics_service
from app.services.notification_service import NotificationService
from app.clients.deepseek_client import DeepSeekClient
from app.clients.kimi_client import KimiClient

logger = logging.getLogger(__name__)


@shared_task(name="run_daily_ai_learning")
def run_daily_ai_learning():
    """
    Main scheduled task for daily AI learning and analysis
    Runs during off-peak hours (2 AM) to minimize performance impact
    Implements Requirements 21.1, 21.2, 21.3, 21.4, 21.5, 28.1
    """
    logger.info("Starting daily AI learning job")
    
    try:
        db = get_database()
        
        # Get all active salons
        salons = list(db.tenants.find({"is_active": True}))
        logger.info(f"Processing AI learning for {len(salons)} salons")
        
        success_count = 0
        error_count = 0
        
        for salon in salons:
            try:
                salon_id = str(salon["_id"])
                logger.info(f"Processing salon: {salon_id}")
                
                # Run pattern analysis
                analyze_salon_patterns(salon_id, db)
                
                # Update learning models
                update_learning_models(salon_id, db)
                
                # Generate proactive alerts
                generate_proactive_alerts(salon_id, db)
                
                success_count += 1
                logger.info(f"Successfully processed salon: {salon_id}")
                
            except Exception as e:
                error_count += 1
                logger.error(f"Error processing salon {salon.get('_id')}: {str(e)}", exc_info=True)
                continue
        
        logger.info(
            f"Daily AI learning job completed. "
            f"Success: {success_count}, Errors: {error_count}"
        )
        
        return {
            "success": True,
            "salons_processed": success_count,
            "errors": error_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Fatal error in daily AI learning job: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


def analyze_salon_patterns(salon_id: str, db: PyMongoDatabase):
    """
    Analyze patterns for a specific salon
    Implements Requirements 21.1, 21.2, 21.3, 21.4, 21.5
    """
    logger.info(f"Analyzing patterns for salon: {salon_id}")
    
    # Initialize services
    booking_service = BookingService(db)
    client_service = ClientService(db)
    inventory_service = InventoryService(db)
    
    pattern_analyzer = PatternAnalyzer(db)
    
    # Analyze all pattern types
    try:
        # Booking patterns
        booking_patterns = pattern_analyzer.analyze_booking_patterns(salon_id)
        logger.info(f"Analyzed booking patterns for salon {salon_id}")
        
        # Service patterns
        service_patterns = pattern_analyzer.analyze_service_patterns(salon_id)
        logger.info(f"Analyzed service patterns for salon {salon_id}")
        
        # Inventory patterns
        inventory_patterns = pattern_analyzer.analyze_inventory_patterns(salon_id)
        logger.info(f"Analyzed inventory patterns for salon {salon_id}")
        
        # Revenue patterns
        revenue_patterns = pattern_analyzer.analyze_revenue_patterns(salon_id)
        logger.info(f"Analyzed revenue patterns for salon {salon_id}")
        
        # Staff patterns
        staff_patterns = pattern_analyzer.analyze_staff_patterns(salon_id)
        logger.info(f"Analyzed staff patterns for salon {salon_id}")
        
        # Store patterns in database for future use
        db.ai_patterns.update_one(
            {"salon_id": salon_id},
            {
                "$set": {
                    "salon_id": salon_id,
                    "booking_patterns": booking_patterns.__dict__ if hasattr(booking_patterns, '__dict__') else {},
                    "service_patterns": service_patterns.__dict__ if hasattr(service_patterns, '__dict__') else {},
                    "inventory_patterns": inventory_patterns.__dict__ if hasattr(inventory_patterns, '__dict__') else {},
                    "revenue_patterns": revenue_patterns.__dict__ if hasattr(revenue_patterns, '__dict__') else {},
                    "staff_patterns": staff_patterns.__dict__ if hasattr(staff_patterns, '__dict__') else {},
                    "last_analyzed": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )
        
        logger.info(f"Successfully stored patterns for salon {salon_id}")
        
    except Exception as e:
        logger.error(f"Error analyzing patterns for salon {salon_id}: {str(e)}", exc_info=True)
        raise


def update_learning_models(salon_id: str, db: PyMongoDatabase):
    """
    Update learning models with recent salon activity
    Implements Requirements 28.1, 28.2, 28.3
    """
    logger.info(f"Updating learning models for salon: {salon_id}")
    
    try:
        # Initialize learning model
        model_storage_path = f"./data/models/{salon_id}"
        learning_model = LearningModel(db, model_storage_path)
        
        # Get recent bookings (last 24 hours)
        yesterday = datetime.utcnow() - timedelta(days=1)
        recent_bookings = list(db.bookings.find({
            "salon_id": salon_id,
            "created_at": {"$gte": yesterday}
        }))
        
        # Update model with recent bookings
        for booking in recent_bookings:
            try:
                learning_model.update_from_booking(booking)
            except Exception as e:
                logger.warning(f"Error updating model from booking {booking.get('_id')}: {str(e)}")
                continue
        
        logger.info(f"Updated learning model with {len(recent_bookings)} bookings")
        
        # Get completed services (last 24 hours)
        completed_services = list(db.bookings.find({
            "salon_id": salon_id,
            "status": "completed",
            "completed_at": {"$gte": yesterday}
        }))
        
        # Update model with completed services
        for service in completed_services:
            try:
                learning_model.update_from_service_completion(service)
            except Exception as e:
                logger.warning(f"Error updating model from service {service.get('_id')}: {str(e)}")
                continue
        
        logger.info(f"Updated learning model with {len(completed_services)} completed services")
        
        # Get inventory changes (last 24 hours)
        inventory_changes = list(db.inventory_transactions.find({
            "salon_id": salon_id,
            "created_at": {"$gte": yesterday}
        }))
        
        # Update model with inventory changes
        for change in inventory_changes:
            try:
                learning_model.update_from_inventory_change(change)
            except Exception as e:
                logger.warning(f"Error updating model from inventory change {change.get('_id')}: {str(e)}")
                continue
        
        logger.info(f"Updated learning model with {len(inventory_changes)} inventory changes")
        
        # Get model metrics
        metrics = learning_model.get_model_accuracy_metrics()
        logger.info(f"Learning model metrics for salon {salon_id}: {metrics.__dict__ if hasattr(metrics, '__dict__') else metrics}")
        
    except Exception as e:
        logger.error(f"Error updating learning models for salon {salon_id}: {str(e)}", exc_info=True)
        raise


def generate_proactive_alerts(salon_id: str, db: PyMongoDatabase):
    """
    Generate and send proactive alerts based on predictions
    Implements Requirements 25.1, 25.2, 25.3, 25.4, 25.5
    """
    logger.info(f"Generating proactive alerts for salon: {salon_id}")
    
    try:
        # Initialize services
        deepseek_client = DeepSeekClient()
        kimi_client = KimiClient()
        notification_service = NotificationService(db)
        
        booking_service = BookingService(db)
        client_service = ClientService(db)
        inventory_service = InventoryService(db)
        
        pattern_analyzer = PatternAnalyzer(db)
        
        prediction_engine = PredictionEngine(deepseek_client)
        
        suggestion_generator = SuggestionGenerator(
            pattern_analyzer=pattern_analyzer,
            prediction_engine=prediction_engine,
            kimi_client=kimi_client
        )
        
        proactive_alerter = ProactiveAlerter(
            prediction_engine=prediction_engine,
            suggestion_generator=suggestion_generator,
            notification_service=notification_service
        )
        
        # Check and generate alerts
        alerts = proactive_alerter.check_and_alert(salon_id)
        
        logger.info(f"Generated {len(alerts)} proactive alerts for salon {salon_id}")
        
        # Store alerts in database
        for alert in alerts:
            db.ai_alerts.insert_one({
                "salon_id": salon_id,
                "alert_id": alert.id,
                "type": alert.type.value if hasattr(alert.type, 'value') else str(alert.type),
                "severity": alert.severity,
                "title": alert.title,
                "message": alert.message,
                "action_required": alert.action_required,
                "suggested_actions": alert.suggested_actions,
                "data": alert.data,
                "acknowledged": alert.acknowledged,
                "created_at": alert.created_at,
                "updated_at": datetime.utcnow()
            })
        
        logger.info(f"Stored {len(alerts)} alerts for salon {salon_id}")
        
    except Exception as e:
        logger.error(f"Error generating proactive alerts for salon {salon_id}: {str(e)}", exc_info=True)
        raise


@shared_task(name="generate_ai_suggestions")
def generate_ai_suggestions(salon_id: str):
    """
    Generate AI suggestions for a specific salon on-demand
    Can be triggered manually or by specific events
    Implements Requirements 22.1, 23.1, 24.1
    """
    logger.info(f"Generating AI suggestions for salon: {salon_id}")
    
    try:
        db = get_database()
        
        # Initialize services
        deepseek_client = DeepSeekClient()
        kimi_client = KimiClient()
        
        booking_service = BookingService(db)
        client_service = ClientService(db)
        inventory_service = InventoryService(db)
        
        pattern_analyzer = PatternAnalyzer(db)
        
        prediction_engine = PredictionEngine(deepseek_client)
        
        suggestion_generator = SuggestionGenerator(
            pattern_analyzer=pattern_analyzer,
            prediction_engine=prediction_engine,
            kimi_client=kimi_client
        )
        
        # Generate all types of suggestions
        booking_suggestions = suggestion_generator.generate_booking_suggestions(salon_id)
        inventory_suggestions = suggestion_generator.generate_inventory_suggestions(salon_id)
        retention_suggestions = suggestion_generator.generate_client_retention_suggestions(salon_id)
        
        all_suggestions = booking_suggestions + inventory_suggestions + retention_suggestions
        
        logger.info(f"Generated {len(all_suggestions)} suggestions for salon {salon_id}")
        
        # Store suggestions in database
        for suggestion in all_suggestions:
            db.ai_suggestions.insert_one({
                "salon_id": salon_id,
                "suggestion_id": suggestion.id,
                "type": suggestion.type.value if hasattr(suggestion.type, 'value') else str(suggestion.type),
                "title": suggestion.title,
                "description": suggestion.description,
                "confidence": suggestion.confidence,
                "reasoning": suggestion.reasoning,
                "action_data": suggestion.action_data,
                "created_at": suggestion.created_at,
                "expires_at": suggestion.expires_at,
                "was_accepted": suggestion.was_accepted,
                "user_feedback": suggestion.user_feedback,
                "updated_at": datetime.utcnow()
            })
        
        logger.info(f"Stored {len(all_suggestions)} suggestions for salon {salon_id}")
        
        return {
            "success": True,
            "salon_id": salon_id,
            "suggestions_generated": len(all_suggestions),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating suggestions for salon {salon_id}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "salon_id": salon_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task(name="generate_ai_insights")
def generate_ai_insights(salon_id: str):
    """
    Generate AI insights for a specific salon on-demand
    Implements Requirements 24.1, 24.2, 24.3, 24.4, 24.5
    """
    logger.info(f"Generating AI insights for salon: {salon_id}")
    
    try:
        db = get_database()
        
        # Initialize services
        kimi_client = KimiClient()
        
        booking_service = BookingService(db)
        client_service = ClientService(db)
        inventory_service = InventoryService(db)
        
        pattern_analyzer = PatternAnalyzer(db)
        
        insight_generator = InsightGenerator(
            pattern_analyzer=pattern_analyzer,
            kimi_client=kimi_client
        )
        
        # Generate all types of insights
        performance_insights = insight_generator.generate_performance_insights(salon_id)
        opportunity_insights = insight_generator.generate_opportunity_insights(salon_id)
        risk_insights = insight_generator.generate_risk_insights(salon_id)
        
        all_insights = performance_insights + opportunity_insights + risk_insights
        
        logger.info(f"Generated {len(all_insights)} insights for salon {salon_id}")
        
        # Store insights in database
        for insight in all_insights:
            db.ai_insights.insert_one({
                "salon_id": salon_id,
                "insight_id": insight.id,
                "type": insight.type.value if hasattr(insight.type, 'value') else str(insight.type),
                "title": insight.title,
                "description": insight.description,
                "impact_level": insight.impact_level,
                "data_points": insight.data_points,
                "recommendations": insight.recommendations,
                "created_at": insight.created_at,
                "updated_at": datetime.utcnow()
            })
        
        logger.info(f"Stored {len(all_insights)} insights for salon {salon_id}")
        
        return {
            "success": True,
            "salon_id": salon_id,
            "insights_generated": len(all_insights),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating insights for salon {salon_id}: {str(e)}", exc_info=True)
        return {
            "success": False,
            "salon_id": salon_id,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }


@shared_task(name="cleanup_old_ai_data")
def cleanup_old_ai_data():
    """
    Clean up old AI suggestions, insights, and alerts
    Runs weekly to prevent database bloat
    """
    logger.info("Starting AI data cleanup job")
    
    try:
        db = get_database()
        
        # Delete suggestions older than 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        suggestions_deleted = db.ai_suggestions.delete_many({
            "created_at": {"$lt": thirty_days_ago}
        }).deleted_count
        
        # Delete acknowledged alerts older than 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        alerts_deleted = db.ai_alerts.delete_many({
            "acknowledged": True,
            "created_at": {"$lt": seven_days_ago}
        }).deleted_count
        
        # Delete insights older than 60 days
        sixty_days_ago = datetime.utcnow() - timedelta(days=60)
        insights_deleted = db.ai_insights.delete_many({
            "created_at": {"$lt": sixty_days_ago}
        }).deleted_count
        
        logger.info(
            f"AI data cleanup completed. "
            f"Suggestions deleted: {suggestions_deleted}, "
            f"Alerts deleted: {alerts_deleted}, "
            f"Insights deleted: {insights_deleted}"
        )
        
        return {
            "success": True,
            "suggestions_deleted": suggestions_deleted,
            "alerts_deleted": alerts_deleted,
            "insights_deleted": insights_deleted,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error in AI data cleanup job: {str(e)}", exc_info=True)
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
