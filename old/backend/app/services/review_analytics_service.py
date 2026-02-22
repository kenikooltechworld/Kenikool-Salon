"""
Review Analytics Service - Business logic for review analytics and trends
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging
from calendar import monthrange

logger = logging.getLogger(__name__)


class ReviewAnalyticsService:
    """Service layer for review analytics and trends"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_rating_trend(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> List[Dict]:
        """Get rating trend over time (daily aggregation)"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "status": "approved",
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Aggregate by day
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at"
                            }
                        },
                        "average_rating": {"$avg": "$rating"},
                        "total_reviews": {"$sum": 1}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = list(self.db.reviews.aggregate(pipeline))
            
            # Format results
            trend_data = []
            for result in results:
                trend_data.append({
                    "date": result["_id"],
                    "average_rating": round(result["average_rating"], 2),
                    "total_reviews": result["total_reviews"]
                })
            
            return trend_data
        
        except Exception as e:
            logger.error(f"Error getting rating trend: {e}")
            raise Exception(f"Failed to get rating trend: {str(e)}")
    
    async def get_service_ratings(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get average rating by service"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "status": "approved",
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            # Aggregate by service
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$service_id",
                        "service_name": {"$first": "$service_name"},
                        "average_rating": {"$avg": "$rating"},
                        "total_reviews": {"$sum": 1}
                    }
                },
                {"$sort": {"average_rating": -1}}
            ]
            
            results = list(self.db.reviews.aggregate(pipeline))
            
            # Format results
            service_data = []
            for result in results:
                if result["_id"]:  # Skip null service_id
                    service_data.append({
                        "service_id": result["_id"],
                        "service_name": result["service_name"],
                        "average_rating": round(result["average_rating"], 2),
                        "total_reviews": result["total_reviews"]
                    })
            
            return service_data
        
        except Exception as e:
            logger.error(f"Error getting service ratings: {e}")
            raise Exception(f"Failed to get service ratings: {str(e)}")
    
    async def get_stylist_ratings(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Get average rating by stylist"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "status": "approved",
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            # Aggregate by stylist
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$stylist_id",
                        "stylist_name": {"$first": "$stylist_name"},
                        "average_rating": {"$avg": "$rating"},
                        "total_reviews": {"$sum": 1}
                    }
                },
                {"$sort": {"average_rating": -1}}
            ]
            
            results = list(self.db.reviews.aggregate(pipeline))
            
            # Format results
            stylist_data = []
            for result in results:
                if result["_id"]:  # Skip null stylist_id
                    stylist_data.append({
                        "stylist_id": result["_id"],
                        "stylist_name": result["stylist_name"],
                        "average_rating": round(result["average_rating"], 2),
                        "total_reviews": result["total_reviews"]
                    })
            
            return stylist_data
        
        except Exception as e:
            logger.error(f"Error getting stylist ratings: {e}")
            raise Exception(f"Failed to get stylist ratings: {str(e)}")
    
    async def get_response_rate(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> Dict:
        """Calculate response rate percentage"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "status": "approved",
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Count total approved reviews
            total_reviews = self.db.reviews.count_documents(query)
            
            if total_reviews == 0:
                return {
                    "response_rate": 0.0,
                    "responded_count": 0,
                    "total_reviews": 0
                }
            
            # Count reviews with responses
            query_with_response = {
                **query,
                "response": {"$exists": True, "$ne": None}
            }
            responded_count = self.db.reviews.count_documents(query_with_response)
            
            # Calculate percentage
            response_rate = (responded_count / total_reviews) * 100 if total_reviews > 0 else 0
            
            return {
                "response_rate": round(response_rate, 2),
                "responded_count": responded_count,
                "total_reviews": total_reviews
            }
        
        except Exception as e:
            logger.error(f"Error calculating response rate: {e}")
            raise Exception(f"Failed to calculate response rate: {str(e)}")
    
    async def get_review_volume(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> List[Dict]:
        """Get review volume trend over time (daily)"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Aggregate by day
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m-%d",
                                "date": "$created_at"
                            }
                        },
                        "total_reviews": {"$sum": 1},
                        "approved": {
                            "$sum": {"$cond": [{"$eq": ["$status", "approved"]}, 1, 0]}
                        },
                        "pending": {
                            "$sum": {"$cond": [{"$eq": ["$status", "pending"]}, 1, 0]}
                        },
                        "rejected": {
                            "$sum": {"$cond": [{"$eq": ["$status", "rejected"]}, 1, 0]}
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = list(self.db.reviews.aggregate(pipeline))
            
            # Format results
            volume_data = []
            for result in results:
                volume_data.append({
                    "date": result["_id"],
                    "total_reviews": result["total_reviews"],
                    "approved": result["approved"],
                    "pending": result["pending"],
                    "rejected": result["rejected"]
                })
            
            return volume_data
        
        except Exception as e:
            logger.error(f"Error getting review volume: {e}")
            raise Exception(f"Failed to get review volume: {str(e)}")
    
    async def get_monthly_aggregation(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> List[Dict]:
        """Get monthly aggregation of ratings"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "status": "approved",
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Aggregate by month
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {
                                "format": "%Y-%m",
                                "date": "$created_at"
                            }
                        },
                        "average_rating": {"$avg": "$rating"},
                        "total_reviews": {"$sum": 1},
                        "rating_1": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}
                        },
                        "rating_2": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}
                        },
                        "rating_3": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}
                        },
                        "rating_4": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}
                        },
                        "rating_5": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}
                        }
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = list(self.db.reviews.aggregate(pipeline))
            
            # Format results
            monthly_data = []
            for result in results:
                monthly_data.append({
                    "month": result["_id"],
                    "average_rating": round(result["average_rating"], 2),
                    "total_reviews": result["total_reviews"],
                    "rating_distribution": {
                        "1": result["rating_1"],
                        "2": result["rating_2"],
                        "3": result["rating_3"],
                        "4": result["rating_4"],
                        "5": result["rating_5"]
                    }
                })
            
            return monthly_data
        
        except Exception as e:
            logger.error(f"Error getting monthly aggregation: {e}")
            raise Exception(f"Failed to get monthly aggregation: {str(e)}")
    
    async def get_overall_metrics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> Dict:
        """Get overall metrics for the period"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "created_at": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Get approved reviews only for rating calculation
            approved_query = {**query, "status": "approved"}
            
            # Aggregate metrics
            pipeline = [
                {"$match": approved_query},
                {
                    "$group": {
                        "_id": None,
                        "average_rating": {"$avg": "$rating"},
                        "total_reviews": {"$sum": 1},
                        "rating_1": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 1]}, 1, 0]}
                        },
                        "rating_2": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 2]}, 1, 0]}
                        },
                        "rating_3": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 3]}, 1, 0]}
                        },
                        "rating_4": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 4]}, 1, 0]}
                        },
                        "rating_5": {
                            "$sum": {"$cond": [{"$eq": ["$rating", 5]}, 1, 0]}
                        }
                    }
                }
            ]
            
            results = list(self.db.reviews.aggregate(pipeline))
            
            if not results:
                return {
                    "average_rating": 0.0,
                    "total_reviews": 0,
                    "rating_distribution": {
                        "1": 0,
                        "2": 0,
                        "3": 0,
                        "4": 0,
                        "5": 0
                    },
                    "response_rate": 0.0,
                    "responded_count": 0
                }
            
            result = results[0]
            
            # Get response rate
            total_approved = result["total_reviews"]
            responded_count = self.db.reviews.count_documents({
                **approved_query,
                "response": {"$exists": True, "$ne": None}
            })
            response_rate = (responded_count / total_approved * 100) if total_approved > 0 else 0
            
            return {
                "average_rating": round(result["average_rating"], 2),
                "total_reviews": result["total_reviews"],
                "rating_distribution": {
                    "1": result["rating_1"],
                    "2": result["rating_2"],
                    "3": result["rating_3"],
                    "4": result["rating_4"],
                    "5": result["rating_5"]
                },
                "response_rate": round(response_rate, 2),
                "responded_count": responded_count
            }
        
        except Exception as e:
            logger.error(f"Error getting overall metrics: {e}")
            raise Exception(f"Failed to get overall metrics: {str(e)}")
    
    async def get_complete_analytics(
        self,
        tenant_id: str,
        start_date: datetime,
        end_date: datetime,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> Dict:
        """Get complete analytics dashboard data"""
        try:
            # Get all analytics data in parallel
            rating_trend = await self.get_rating_trend(
                tenant_id, start_date, end_date, service_id, stylist_id
            )
            service_ratings = await self.get_service_ratings(
                tenant_id, start_date, end_date
            ) if not service_id else []
            stylist_ratings = await self.get_stylist_ratings(
                tenant_id, start_date, end_date
            ) if not stylist_id else []
            response_rate = await self.get_response_rate(
                tenant_id, start_date, end_date, service_id, stylist_id
            )
            review_volume = await self.get_review_volume(
                tenant_id, start_date, end_date, service_id, stylist_id
            )
            monthly_aggregation = await self.get_monthly_aggregation(
                tenant_id, start_date, end_date, service_id, stylist_id
            )
            overall_metrics = await self.get_overall_metrics(
                tenant_id, start_date, end_date, service_id, stylist_id
            )
            
            return {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "filters": {
                    "service_id": service_id,
                    "stylist_id": stylist_id
                },
                "overall_metrics": overall_metrics,
                "rating_trend": rating_trend,
                "service_ratings": service_ratings,
                "stylist_ratings": stylist_ratings,
                "response_rate": response_rate,
                "review_volume": review_volume,
                "monthly_aggregation": monthly_aggregation
            }
        
        except Exception as e:
            logger.error(f"Error getting complete analytics: {e}")
            raise Exception(f"Failed to get complete analytics: {str(e)}")
