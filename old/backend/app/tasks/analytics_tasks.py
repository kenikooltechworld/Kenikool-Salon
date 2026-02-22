"""
Celery tasks for analytics background jobs
"""
from celery import shared_task
import logging
from datetime import datetime, timedelta
from app.services.analytics_service import AnalyticsService
from app.services.data_aggregation_service import DataAggregationService
from app.services.predictive_analytics_service import PredictiveAnalyticsService
from app.services.report_generation_service import ReportGenerationService

logger = logging.getLogger(__name__)

analytics_service = AnalyticsService()
aggregation_service = DataAggregationService()
predictive_service = PredictiveAnalyticsService()
report_service = ReportGenerationService()


@shared_task(bind=True, max_retries=3)
def aggregate_hourly_analytics(self, tenant_id: str):
    """Aggregate hourly analytics data"""
    try:
        logger.info(f"Starting hourly aggregation for tenant {tenant_id}")
        
        # Get current hour
        now = datetime.utcnow()
        hour_start = now.replace(minute=0, second=0, microsecond=0)
        
        # Aggregate metrics
        result = aggregation_service.aggregate_hourly_metrics(tenant_id, hour_start)
        
        logger.info(f"Hourly aggregation completed for tenant {tenant_id}")
        return result
    except Exception as exc:
        logger.error(f"Error in hourly aggregation: {exc}")
        raise self.retry(exc=exc, countdown=60)


@shared_task(bind=True, max_retries=3)
def process_daily_analytics(self, tenant_id: str):
    """Process daily analytics"""
    try:
        logger.info(f"Starting daily analytics processing for tenant {tenant_id}")
        
        # Get yesterday's date
        yesterday = datetime.utcnow().date() - timedelta(days=1)
        start_date = datetime.combine(yesterday, datetime.min.time())
        end_date = datetime.combine(yesterday, datetime.max.time())
        
        # Calculate daily metrics
        client_analytics = aggregation_service.calculate_client_analytics(
            tenant_id, start_date, end_date
        )
        inventory_analytics = aggregation_service.update_inventory_analytics(
            tenant_id, start_date, end_date
        )
        campaign_metrics = aggregation_service.refresh_campaign_metrics(
            tenant_id, start_date, end_date
        )
        
        logger.info(f"Daily analytics processing completed for tenant {tenant_id}")
        return {
            "client_analytics": client_analytics,
            "inventory_analytics": inventory_analytics,
            "campaign_metrics": campaign_metrics
        }
    except Exception as exc:
        logger.error(f"Error in daily analytics processing: {exc}")
        raise self.retry(exc=exc, countdown=300)


@shared_task(bind=True, max_retries=3)
def process_weekly_analytics(self, tenant_id: str):
    """Process weekly analytics"""
    try:
        logger.info(f"Starting weekly analytics processing for tenant {tenant_id}")
        
        # Get last week's date range
        today = datetime.utcnow().date()
        week_start = today - timedelta(days=today.weekday() + 7)
        week_end = week_start + timedelta(days=6)
        
        start_date = datetime.combine(week_start, datetime.min.time())
        end_date = datetime.combine(week_end, datetime.max.time())
        
        # Calculate weekly metrics
        financial_metrics = aggregation_service.calculate_financial_metrics(
            tenant_id, start_date, end_date
        )
        
        logger.info(f"Weekly analytics processing completed for tenant {tenant_id}")
        return financial_metrics
    except Exception as exc:
        logger.error(f"Error in weekly analytics processing: {exc}")
        raise self.retry(exc=exc, countdown=600)


@shared_task(bind=True, max_retries=3)
def train_predictive_models(self, tenant_id: str):
    """Train predictive models"""
    try:
        logger.info(f"Starting predictive model training for tenant {tenant_id}")
        
        # Train demand prediction model
        demand_forecast = predictive_service.predict_demand(
            tenant_id,
            days_ahead=30,
            historical_data=[100 + i * 2 for i in range(90)]
        )
        
        # Train churn prediction model
        churn_predictions = predictive_service.predict_churn(
            tenant_id,
            client_data=[
                {"client_id": f"client_{i}", "days_since_visit": 30 + i*5, "visit_frequency": 5}
                for i in range(10)
            ]
        )
        
        # Train revenue prediction model
        revenue_forecast = predictive_service.predict_revenue(
            tenant_id,
            days_ahead=30,
            historical_revenue=[5000 + i * 50 for i in range(90)]
        )
        
        logger.info(f"Predictive model training completed for tenant {tenant_id}")
        return {
            "demand_forecast": demand_forecast,
            "churn_predictions": churn_predictions,
            "revenue_forecast": revenue_forecast
        }
    except Exception as exc:
        logger.error(f"Error in predictive model training: {exc}")
        raise self.retry(exc=exc, countdown=1800)


@shared_task(bind=True, max_retries=3)
def generate_scheduled_report(self, tenant_id: str, report_id: str, schedule: str):
    """Generate scheduled report"""
    try:
        logger.info(f"Generating scheduled report {report_id} for tenant {tenant_id}")
        
        # Generate report
        report = report_service.generate_custom_report(
            tenant_id,
            f"Scheduled Report {report_id}",
            ["revenue", "bookings", "clients"],
            [],
            {
                "start": datetime.utcnow() - timedelta(days=30),
                "end": datetime.utcnow()
            }
        )
        
        logger.info(f"Scheduled report {report_id} generated for tenant {tenant_id}")
        return report
    except Exception as exc:
        logger.error(f"Error generating scheduled report: {exc}")
        raise self.retry(exc=exc, countdown=300)
