"""White Label Performance Monitoring Service

Monitors performance metrics for white-labeled sites including:
- Page load times with custom branding
- Email open rates for branded emails
- Comparison of branded vs default site performance
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from statistics import mean, median, stdev

logger = logging.getLogger(__name__)


class WhiteLabelPerformanceMonitoring:
    """Service for monitoring white label site performance"""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize performance monitoring service
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.performance_collection = db.white_label_performance_metrics
        self.analytics_collection = db.white_label_analytics
        self.alerts_collection = db.white_label_performance_alerts

    async def get_page_load_metrics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        domain: Optional[str] = None,
        page_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get detailed page load time metrics
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for metrics
            end_date: End date for metrics
            domain: Optional specific domain to filter
            page_type: Optional specific page type to filter
            
        Returns:
            Page load metrics
        """
        try:
            query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }

            if domain:
                query["domain"] = domain

            if page_type:
                query["page_type"] = page_type

            # Get all load time measurements
            measurements = await self.performance_collection.find(query).to_list(None)

            if not measurements:
                return {
                    "total_measurements": 0,
                    "average_load_time_ms": 0,
                    "median_load_time_ms": 0,
                    "min_load_time_ms": 0,
                    "max_load_time_ms": 0,
                    "std_deviation_ms": 0,
                    "p95_load_time_ms": 0,
                    "p99_load_time_ms": 0,
                    "measurements": [],
                }

            load_times = [m["load_time_ms"] for m in measurements]
            load_times.sort()

            # Calculate percentiles
            p95_index = int(len(load_times) * 0.95)
            p99_index = int(len(load_times) * 0.99)

            p95_load_time = load_times[p95_index] if p95_index < len(load_times) else load_times[-1]
            p99_load_time = load_times[p99_index] if p99_index < len(load_times) else load_times[-1]

            # Calculate standard deviation
            try:
                std_dev = stdev(load_times) if len(load_times) > 1 else 0
            except:
                std_dev = 0

            return {
                "total_measurements": len(measurements),
                "average_load_time_ms": round(mean(load_times), 2),
                "median_load_time_ms": round(median(load_times), 2),
                "min_load_time_ms": round(min(load_times), 2),
                "max_load_time_ms": round(max(load_times), 2),
                "std_deviation_ms": round(std_dev, 2),
                "p95_load_time_ms": round(p95_load_time, 2),
                "p99_load_time_ms": round(p99_load_time, 2),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting page load metrics: {e}")
            raise

    async def get_resource_timing_analysis(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyze resource timing breakdown
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analysis
            end_date: End date for analysis
            domain: Optional specific domain to filter
            
        Returns:
            Resource timing analysis
        """
        try:
            query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
                "resource_timing": {"$exists": True, "$ne": {}},
            }

            if domain:
                query["domain"] = domain

            # Get measurements with resource timing
            measurements = await self.performance_collection.find(query).to_list(None)

            if not measurements:
                return {
                    "total_measurements": 0,
                    "resource_breakdown": {},
                    "slowest_resources": [],
                }

            # Aggregate resource timings
            resource_totals = {}
            resource_counts = {}

            for measurement in measurements:
                if "resource_timing" in measurement:
                    for resource, time_ms in measurement["resource_timing"].items():
                        if resource not in resource_totals:
                            resource_totals[resource] = 0
                            resource_counts[resource] = 0
                        resource_totals[resource] += time_ms
                        resource_counts[resource] += 1

            # Calculate averages
            resource_breakdown = {}
            for resource, total in resource_totals.items():
                count = resource_counts[resource]
                resource_breakdown[resource] = {
                    "average_ms": round(total / count, 2),
                    "total_ms": round(total, 2),
                    "measurements": count,
                }

            # Sort by average time
            slowest_resources = sorted(
                resource_breakdown.items(),
                key=lambda x: x[1]["average_ms"],
                reverse=True
            )[:10]

            return {
                "total_measurements": len(measurements),
                "resource_breakdown": resource_breakdown,
                "slowest_resources": [
                    {
                        "resource": name,
                        "average_ms": data["average_ms"],
                        "total_ms": data["total_ms"],
                        "measurements": data["measurements"],
                    }
                    for name, data in slowest_resources
                ],
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error analyzing resource timing: {e}")
            raise

    async def get_email_performance_metrics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        campaign_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get email performance metrics including open rates and timing
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for metrics
            end_date: End date for metrics
            campaign_id: Optional specific campaign to filter
            
        Returns:
            Email performance metrics
        """
        try:
            query = {
                "tenant_id": tenant_id,
                "opened_at": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }

            if campaign_id:
                query["campaign_id"] = campaign_id

            # Get email tracking data
            email_records = await self.db.white_label_email_tracking.find(query).to_list(None)

            if not email_records:
                return {
                    "total_emails": 0,
                    "total_opens": 0,
                    "open_rate_percent": 0,
                    "average_time_to_open_hours": 0,
                    "opens_by_hour": {},
                    "opens_by_day": {},
                }

            # Calculate metrics
            total_emails = len(email_records)
            opened_emails = [e for e in email_records if e.get("opened")]
            total_opens = len(opened_emails)
            open_rate = (total_opens / total_emails * 100) if total_emails > 0 else 0

            # Calculate time to open
            times_to_open = []
            for email in opened_emails:
                if "opened_at" in email and "timestamp" in email:
                    time_diff = email["opened_at"] - email.get("timestamp", email["opened_at"])
                    times_to_open.append(time_diff.total_seconds() / 3600)  # Convert to hours

            avg_time_to_open = mean(times_to_open) if times_to_open else 0

            # Get opens by hour of day
            opens_by_hour = {}
            for email in opened_emails:
                if "opened_at" in email:
                    hour = email["opened_at"].hour
                    opens_by_hour[hour] = opens_by_hour.get(hour, 0) + 1

            # Get opens by day of week
            opens_by_day = {}
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            for email in opened_emails:
                if "opened_at" in email:
                    day = day_names[email["opened_at"].weekday()]
                    opens_by_day[day] = opens_by_day.get(day, 0) + 1

            return {
                "total_emails": total_emails,
                "total_opens": total_opens,
                "open_rate_percent": round(open_rate, 2),
                "average_time_to_open_hours": round(avg_time_to_open, 2),
                "opens_by_hour": opens_by_hour,
                "opens_by_day": opens_by_day,
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting email performance metrics: {e}")
            raise

    async def compare_performance_metrics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Compare performance between branded and default sites
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for comparison
            end_date: End date for comparison
            
        Returns:
            Performance comparison data
        """
        try:
            # Get branded site performance (custom domains)
            branded_query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
                "domain": {"$ne": None},
            }

            branded_measurements = await self.performance_collection.find(branded_query).to_list(None)

            # Get default site performance (no custom domain)
            default_query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
                "domain": None,
            }

            default_measurements = await self.performance_collection.find(default_query).to_list(None)

            # Calculate metrics for both
            def calculate_metrics(measurements):
                if not measurements:
                    return {
                        "total_measurements": 0,
                        "average_load_time_ms": 0,
                        "median_load_time_ms": 0,
                        "min_load_time_ms": 0,
                        "max_load_time_ms": 0,
                    }

                load_times = [m["load_time_ms"] for m in measurements]
                load_times.sort()

                return {
                    "total_measurements": len(measurements),
                    "average_load_time_ms": round(mean(load_times), 2),
                    "median_load_time_ms": round(median(load_times), 2),
                    "min_load_time_ms": round(min(load_times), 2),
                    "max_load_time_ms": round(max(load_times), 2),
                }

            branded_metrics = calculate_metrics(branded_measurements)
            default_metrics = calculate_metrics(default_measurements)

            # Calculate differences
            avg_diff = branded_metrics["average_load_time_ms"] - default_metrics["average_load_time_ms"]
            avg_diff_percent = (
                (avg_diff / default_metrics["average_load_time_ms"] * 100)
                if default_metrics["average_load_time_ms"] > 0
                else 0
            )

            return {
                "branded_site": branded_metrics,
                "default_site": default_metrics,
                "performance_difference": {
                    "average_load_time_diff_ms": round(avg_diff, 2),
                    "average_load_time_diff_percent": round(avg_diff_percent, 2),
                    "branded_faster": avg_diff < 0,
                },
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error comparing performance metrics: {e}")
            raise

    async def create_performance_alert(
        self,
        tenant_id: str,
        alert_type: str,
        severity: str,
        message: str,
        metric_value: float,
        threshold: float,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Create a performance alert
        
        Args:
            tenant_id: Tenant ID
            alert_type: Type of alert (slow_page_load, high_email_bounce, etc.)
            severity: Severity level (info, warning, critical)
            message: Alert message
            metric_value: Current metric value
            threshold: Threshold that was exceeded
            domain: Optional domain associated with alert
            
        Returns:
            Alert record
        """
        try:
            alert_record = {
                "tenant_id": tenant_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "metric_value": metric_value,
                "threshold": threshold,
                "domain": domain,
                "created_at": datetime.utcnow(),
                "acknowledged": False,
            }

            result = await self.alerts_collection.insert_one(alert_record)
            alert_record["_id"] = str(result.inserted_id)

            return alert_record
        except Exception as e:
            logger.error(f"Error creating performance alert: {e}")
            raise

    async def get_performance_alerts(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        severity: Optional[str] = None,
        acknowledged: Optional[bool] = None,
    ) -> List[Dict[str, Any]]:
        """Get performance alerts
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for alerts
            end_date: End date for alerts
            severity: Optional severity filter
            acknowledged: Optional acknowledged status filter
            
        Returns:
            List of alerts
        """
        try:
            query = {
                "tenant_id": tenant_id,
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            }

            if severity:
                query["severity"] = severity

            if acknowledged is not None:
                query["acknowledged"] = acknowledged

            alerts = await self.alerts_collection.find(query).sort("created_at", -1).to_list(None)

            return [
                {
                    **alert,
                    "_id": str(alert["_id"]),
                    "created_at": alert["created_at"].isoformat(),
                }
                for alert in alerts
            ]
        except Exception as e:
            logger.error(f"Error getting performance alerts: {e}")
            raise

    async def acknowledge_alert(
        self,
        alert_id: str,
        tenant_id: str,
    ) -> bool:
        """Acknowledge a performance alert
        
        Args:
            alert_id: Alert ID
            tenant_id: Tenant ID
            
        Returns:
            True if acknowledged successfully
        """
        try:
            from bson import ObjectId

            result = await self.alerts_collection.update_one(
                {
                    "_id": ObjectId(alert_id),
                    "tenant_id": tenant_id,
                },
                {
                    "$set": {
                        "acknowledged": True,
                        "acknowledged_at": datetime.utcnow(),
                    }
                },
            )

            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error acknowledging alert: {e}")
            raise

    async def check_performance_thresholds(
        self,
        tenant_id: str,
        domain: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Check if performance metrics exceed thresholds and create alerts
        
        Args:
            tenant_id: Tenant ID
            domain: Optional specific domain to check
            
        Returns:
            List of alerts created
        """
        try:
            alerts_created = []

            # Check page load time threshold (3000ms)
            query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": datetime.utcnow() - timedelta(hours=1),
                },
            }

            if domain:
                query["domain"] = domain

            measurements = await self.performance_collection.find(query).to_list(None)

            if measurements:
                load_times = [m["load_time_ms"] for m in measurements]
                avg_load_time = mean(load_times)

                if avg_load_time > 3000:
                    alert = await self.create_performance_alert(
                        tenant_id=tenant_id,
                        alert_type="slow_page_load",
                        severity="warning" if avg_load_time < 5000 else "critical",
                        message=f"Average page load time is {avg_load_time:.0f}ms (threshold: 3000ms)",
                        metric_value=avg_load_time,
                        threshold=3000,
                        domain=domain,
                    )
                    alerts_created.append(alert)

            return alerts_created
        except Exception as e:
            logger.error(f"Error checking performance thresholds: {e}")
            raise
