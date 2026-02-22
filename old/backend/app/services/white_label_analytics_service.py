"""White Label Analytics Service

Tracks analytics for white-labeled sites including:
- Custom domain visits
- Conversion rates
- Branding element effectiveness
- Page load times
- Email open rates
"""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

logger = logging.getLogger(__name__)


class WhiteLabelAnalyticsService:
    """Service for tracking and analyzing white label site performance"""

    def __init__(self, db: AsyncIOMotorDatabase):
        """Initialize white label analytics service
        
        Args:
            db: MongoDB database instance
        """
        self.db = db
        self.analytics_collection = db.white_label_analytics
        self.domain_visits_collection = db.white_label_domain_visits
        self.email_tracking_collection = db.white_label_email_tracking
        self.performance_collection = db.white_label_performance_metrics

    async def track_domain_visit(
        self,
        tenant_id: str,
        domain: str,
        page_type: str,
        user_agent: str,
        ip_address: str,
        referrer: Optional[str] = None,
        session_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Track a visit to a white-labeled domain
        
        Args:
            tenant_id: Tenant ID
            domain: Custom domain visited
            page_type: Type of page (home, booking, checkout, etc.)
            user_agent: User agent string
            ip_address: Visitor IP address
            referrer: HTTP referrer
            session_id: Session ID for tracking user journey
            
        Returns:
            Visit tracking record
        """
        try:
            visit_record = {
                "tenant_id": tenant_id,
                "domain": domain,
                "page_type": page_type,
                "user_agent": user_agent,
                "ip_address": ip_address,
                "referrer": referrer,
                "session_id": session_id or str(ObjectId()),
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }

            result = await self.domain_visits_collection.insert_one(visit_record)
            visit_record["_id"] = str(result.inserted_id)

            return visit_record
        except Exception as e:
            logger.error(f"Error tracking domain visit: {e}")
            raise

    async def track_conversion(
        self,
        tenant_id: str,
        domain: str,
        session_id: str,
        conversion_type: str,
        conversion_value: float,
        booking_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Track a conversion on white-labeled site
        
        Args:
            tenant_id: Tenant ID
            domain: Custom domain
            session_id: Session ID
            conversion_type: Type of conversion (booking, purchase, signup, etc.)
            conversion_value: Value of conversion (booking amount, etc.)
            booking_id: Associated booking ID if applicable
            
        Returns:
            Conversion tracking record
        """
        try:
            conversion_record = {
                "tenant_id": tenant_id,
                "domain": domain,
                "session_id": session_id,
                "conversion_type": conversion_type,
                "conversion_value": conversion_value,
                "booking_id": booking_id,
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }

            result = await self.domain_visits_collection.insert_one(conversion_record)
            conversion_record["_id"] = str(result.inserted_id)

            return conversion_record
        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
            raise

    async def track_email_open(
        self,
        tenant_id: str,
        email_id: str,
        recipient_email: str,
        campaign_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Track email open for branded emails
        
        Args:
            tenant_id: Tenant ID
            email_id: Email message ID
            recipient_email: Recipient email address
            campaign_id: Associated campaign ID if applicable
            
        Returns:
            Email tracking record
        """
        try:
            email_record = {
                "tenant_id": tenant_id,
                "email_id": email_id,
                "recipient_email": recipient_email,
                "campaign_id": campaign_id,
                "opened": True,
                "opened_at": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }

            result = await self.email_tracking_collection.insert_one(email_record)
            email_record["_id"] = str(result.inserted_id)

            return email_record
        except Exception as e:
            logger.error(f"Error tracking email open: {e}")
            raise

    async def track_page_load_time(
        self,
        tenant_id: str,
        domain: str,
        page_type: str,
        load_time_ms: float,
        resource_timing: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:
        """Track page load time for white-labeled site
        
        Args:
            tenant_id: Tenant ID
            domain: Custom domain
            page_type: Type of page
            load_time_ms: Total page load time in milliseconds
            resource_timing: Breakdown of resource load times
            
        Returns:
            Performance tracking record
        """
        try:
            perf_record = {
                "tenant_id": tenant_id,
                "domain": domain,
                "page_type": page_type,
                "load_time_ms": load_time_ms,
                "resource_timing": resource_timing or {},
                "timestamp": datetime.utcnow(),
                "date": datetime.utcnow().date().isoformat(),
            }

            result = await self.performance_collection.insert_one(perf_record)
            perf_record["_id"] = str(result.inserted_id)

            return perf_record
        except Exception as e:
            logger.error(f"Error tracking page load time: {e}")
            raise

    async def get_traffic_analytics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get traffic analytics for white-labeled site
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analytics
            end_date: End date for analytics
            domain: Optional specific domain to filter
            
        Returns:
            Traffic analytics data
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

            # Get total visits
            total_visits = await self.domain_visits_collection.count_documents(query)

            # Get visits by page type
            page_type_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$page_type",
                    "count": {"$sum": 1},
                }},
                {"$sort": {"count": -1}},
            ]
            page_type_data = await self.domain_visits_collection.aggregate(page_type_pipeline).to_list(None)

            # Get visits by domain (if not filtered to specific domain)
            domain_pipeline = [
                {"$match": {"tenant_id": tenant_id, "timestamp": query["timestamp"]}},
                {"$group": {
                    "_id": "$domain",
                    "count": {"$sum": 1},
                }},
                {"$sort": {"count": -1}},
            ]
            domain_data = await self.domain_visits_collection.aggregate(domain_pipeline).to_list(None)

            # Get unique visitors (by IP)
            unique_visitors_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$ip_address",
                }},
            ]
            unique_visitors = await self.domain_visits_collection.aggregate(unique_visitors_pipeline).to_list(None)

            # Get referrer data
            referrer_pipeline = [
                {"$match": {**query, "referrer": {"$ne": None}}},
                {"$group": {
                    "_id": "$referrer",
                    "count": {"$sum": 1},
                }},
                {"$sort": {"count": -1}},
                {"$limit": 10},
            ]
            referrer_data = await self.domain_visits_collection.aggregate(referrer_pipeline).to_list(None)

            return {
                "total_visits": total_visits,
                "unique_visitors": len(unique_visitors),
                "page_type_breakdown": [
                    {"page_type": item["_id"], "visits": item["count"]}
                    for item in page_type_data
                ],
                "domain_breakdown": [
                    {"domain": item["_id"], "visits": item["count"]}
                    for item in domain_data
                ],
                "top_referrers": [
                    {"referrer": item["_id"], "visits": item["count"]}
                    for item in referrer_data
                ],
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting traffic analytics: {e}")
            raise

    async def get_conversion_analytics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get conversion analytics for white-labeled site
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analytics
            end_date: End date for analytics
            domain: Optional specific domain to filter
            
        Returns:
            Conversion analytics data
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

            # Get total conversions
            total_conversions = await self.domain_visits_collection.count_documents({
                **query,
                "conversion_type": {"$exists": True},
            })

            # Get conversions by type
            conversion_type_pipeline = [
                {"$match": {**query, "conversion_type": {"$exists": True}}},
                {"$group": {
                    "_id": "$conversion_type",
                    "count": {"$sum": 1},
                    "total_value": {"$sum": "$conversion_value"},
                }},
                {"$sort": {"count": -1}},
            ]
            conversion_type_data = await self.domain_visits_collection.aggregate(conversion_type_pipeline).to_list(None)

            # Calculate conversion rate
            total_visits = await self.domain_visits_collection.count_documents(query)
            conversion_rate = (total_conversions / total_visits * 100) if total_visits > 0 else 0

            # Get total conversion value
            total_value_pipeline = [
                {"$match": {**query, "conversion_type": {"$exists": True}}},
                {"$group": {
                    "_id": None,
                    "total": {"$sum": "$conversion_value"},
                }},
            ]
            total_value_data = await self.domain_visits_collection.aggregate(total_value_pipeline).to_list(None)
            total_value = total_value_data[0]["total"] if total_value_data else 0

            return {
                "total_conversions": total_conversions,
                "conversion_rate_percent": round(conversion_rate, 2),
                "total_conversion_value": total_value,
                "average_conversion_value": round(total_value / total_conversions, 2) if total_conversions > 0 else 0,
                "conversions_by_type": [
                    {
                        "type": item["_id"],
                        "count": item["count"],
                        "total_value": item["total_value"],
                        "average_value": round(item["total_value"] / item["count"], 2),
                    }
                    for item in conversion_type_data
                ],
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting conversion analytics: {e}")
            raise

    async def get_email_analytics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        campaign_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get email analytics for branded emails
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analytics
            end_date: End date for analytics
            campaign_id: Optional specific campaign to filter
            
        Returns:
            Email analytics data
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

            # Get total emails sent (count all email records)
            total_emails = await self.email_tracking_collection.count_documents({
                "tenant_id": tenant_id,
                "opened_at": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
            })

            # Get opened emails
            opened_emails = await self.email_tracking_collection.count_documents({
                **query,
                "opened": True,
            })

            # Calculate open rate
            open_rate = (opened_emails / total_emails * 100) if total_emails > 0 else 0

            # Get opens by campaign
            campaign_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$campaign_id",
                    "opens": {"$sum": 1},
                }},
                {"$sort": {"opens": -1}},
            ]
            campaign_data = await self.email_tracking_collection.aggregate(campaign_pipeline).to_list(None)

            return {
                "total_emails_sent": total_emails,
                "total_opens": opened_emails,
                "open_rate_percent": round(open_rate, 2),
                "opens_by_campaign": [
                    {
                        "campaign_id": item["_id"],
                        "opens": item["opens"],
                    }
                    for item in campaign_data
                ],
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting email analytics: {e}")
            raise

    async def get_performance_analytics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get performance analytics for white-labeled site
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analytics
            end_date: End date for analytics
            domain: Optional specific domain to filter
            
        Returns:
            Performance analytics data
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

            # Get average load time
            load_time_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": None,
                    "avg_load_time": {"$avg": "$load_time_ms"},
                    "min_load_time": {"$min": "$load_time_ms"},
                    "max_load_time": {"$max": "$load_time_ms"},
                    "count": {"$sum": 1},
                }},
            ]
            load_time_data = await self.performance_collection.aggregate(load_time_pipeline).to_list(None)

            # Get load time by page type
            page_type_pipeline = [
                {"$match": query},
                {"$group": {
                    "_id": "$page_type",
                    "avg_load_time": {"$avg": "$load_time_ms"},
                    "count": {"$sum": 1},
                }},
                {"$sort": {"avg_load_time": -1}},
            ]
            page_type_data = await self.performance_collection.aggregate(page_type_pipeline).to_list(None)

            # Get load time by domain
            domain_pipeline = [
                {"$match": {"tenant_id": tenant_id, "timestamp": query["timestamp"]}},
                {"$group": {
                    "_id": "$domain",
                    "avg_load_time": {"$avg": "$load_time_ms"},
                    "count": {"$sum": 1},
                }},
                {"$sort": {"avg_load_time": -1}},
            ]
            domain_data = await self.performance_collection.aggregate(domain_pipeline).to_list(None)

            if load_time_data:
                avg_load_time = load_time_data[0]["avg_load_time"]
                min_load_time = load_time_data[0]["min_load_time"]
                max_load_time = load_time_data[0]["max_load_time"]
                measurement_count = load_time_data[0]["count"]
            else:
                avg_load_time = 0
                min_load_time = 0
                max_load_time = 0
                measurement_count = 0

            return {
                "average_load_time_ms": round(avg_load_time, 2),
                "min_load_time_ms": round(min_load_time, 2),
                "max_load_time_ms": round(max_load_time, 2),
                "measurement_count": measurement_count,
                "load_time_by_page_type": [
                    {
                        "page_type": item["_id"],
                        "avg_load_time_ms": round(item["avg_load_time"], 2),
                        "measurements": item["count"],
                    }
                    for item in page_type_data
                ],
                "load_time_by_domain": [
                    {
                        "domain": item["_id"],
                        "avg_load_time_ms": round(item["avg_load_time"], 2),
                        "measurements": item["count"],
                    }
                    for item in domain_data
                ],
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting performance analytics: {e}")
            raise

    async def get_branding_effectiveness(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Get branding element effectiveness metrics
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Branding effectiveness data
        """
        try:
            # Get traffic and conversion data
            traffic_data = await self.get_traffic_analytics(tenant_id, start_date, end_date)
            conversion_data = await self.get_conversion_analytics(tenant_id, start_date, end_date)
            email_data = await self.get_email_analytics(tenant_id, start_date, end_date)

            # Calculate engagement metrics
            total_visits = traffic_data["total_visits"]
            total_conversions = conversion_data["total_conversions"]
            email_opens = email_data["total_opens"]

            engagement_rate = (
                (total_conversions + email_opens) / total_visits * 100
                if total_visits > 0
                else 0
            )

            return {
                "engagement_rate_percent": round(engagement_rate, 2),
                "conversion_rate_percent": conversion_data["conversion_rate_percent"],
                "email_open_rate_percent": email_data["open_rate_percent"],
                "total_visits": total_visits,
                "total_conversions": total_conversions,
                "total_email_opens": email_opens,
                "top_performing_pages": traffic_data["page_type_breakdown"][:5],
                "top_referrers": traffic_data["top_referrers"][:5],
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error getting branding effectiveness: {e}")
            raise

    async def compare_branded_vs_default(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> Dict[str, Any]:
        """Compare performance of branded vs default site
        
        Args:
            tenant_id: Tenant ID
            start_date: Start date for analytics
            end_date: End date for analytics
            
        Returns:
            Comparison data
        """
        try:
            # Get branded site metrics (custom domains)
            branded_query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
                "domain": {"$ne": None},
            }

            branded_visits = await self.domain_visits_collection.count_documents(branded_query)
            branded_conversions = await self.domain_visits_collection.count_documents({
                **branded_query,
                "conversion_type": {"$exists": True},
            })

            # Get default site metrics (no custom domain)
            default_query = {
                "tenant_id": tenant_id,
                "timestamp": {
                    "$gte": start_date,
                    "$lte": end_date,
                },
                "domain": None,
            }

            default_visits = await self.domain_visits_collection.count_documents(default_query)
            default_conversions = await self.domain_visits_collection.count_documents({
                **default_query,
                "conversion_type": {"$exists": True},
            })

            # Calculate rates
            branded_conversion_rate = (
                (branded_conversions / branded_visits * 100) if branded_visits > 0 else 0
            )
            default_conversion_rate = (
                (default_conversions / default_visits * 100) if default_visits > 0 else 0
            )

            # Calculate improvement
            improvement = branded_conversion_rate - default_conversion_rate

            return {
                "branded_site": {
                    "visits": branded_visits,
                    "conversions": branded_conversions,
                    "conversion_rate_percent": round(branded_conversion_rate, 2),
                },
                "default_site": {
                    "visits": default_visits,
                    "conversions": default_conversions,
                    "conversion_rate_percent": round(default_conversion_rate, 2),
                },
                "improvement_percent": round(improvement, 2),
                "date_range": {
                    "start": start_date.isoformat(),
                    "end": end_date.isoformat(),
                },
            }
        except Exception as e:
            logger.error(f"Error comparing branded vs default: {e}")
            raise
