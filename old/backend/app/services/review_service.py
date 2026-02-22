"""
Review service - Business logic for review management
"""
from datetime import datetime
from typing import Dict, List, Optional
from bson import ObjectId
import logging
import csv
from io import StringIO, BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

logger = logging.getLogger(__name__)


class ReviewService:
    """Service layer for review management"""
    
    def __init__(self, db):
        self.db = db
    
    def _build_filter_query(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        rating: Optional[List[int]] = None,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_response: Optional[bool] = None,
        has_photos: Optional[bool] = None,
        is_flagged: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Dict:
        """Build MongoDB query from filter parameters"""
        query = {"tenant_id": tenant_id}
        
        # Status filter
        if status is not None:
            query["status"] = status
        
        # Rating filter (can be multiple ratings)
        if rating:
            query["rating"] = {"$in": rating}
        
        # Service filter
        if service_id:
            query["service_id"] = service_id
        
        # Stylist filter
        if stylist_id:
            query["stylist_id"] = stylist_id
        
        # Date range filter
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            if date_query:
                query["created_at"] = date_query
        
        # Has response filter
        if has_response is not None:
            if has_response:
                query["response"] = {"$exists": True, "$ne": None}
            else:
                query["$or"] = [
                    {"response": {"$exists": False}},
                    {"response": None}
                ]
        
        # Has photos filter
        if has_photos is not None:
            if has_photos:
                query["photos"] = {"$exists": True, "$ne": [], "$type": "array"}
            else:
                query["$or"] = [
                    {"photos": {"$exists": False}},
                    {"photos": []}
                ]
        
        # Is flagged filter
        if is_flagged is not None:
            if is_flagged:
                query["flags"] = {"$exists": True, "$ne": [], "$type": "array"}
            else:
                query["$or"] = [
                    {"flags": {"$exists": False}},
                    {"flags": []}
                ]
        
        # Text search filter
        if search:
            query["$text"] = {"$search": search}
        
        return query
    
    async def get_reviews_filtered(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        rating: Optional[List[int]] = None,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_response: Optional[bool] = None,
        has_photos: Optional[bool] = None,
        is_flagged: Optional[bool] = None,
        search: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Get reviews with advanced filtering and search"""
        try:
            # Build query
            query = self._build_filter_query(
                tenant_id=tenant_id,
                status=status,
                rating=rating,
                service_id=service_id,
                stylist_id=stylist_id,
                start_date=start_date,
                end_date=end_date,
                has_response=has_response,
                has_photos=has_photos,
                is_flagged=is_flagged,
                search=search
            )
            
            # Get total count
            total = self.db.reviews.count_documents(query)
            
            # Determine sort order
            sort_direction = -1 if sort_order == "desc" else 1
            
            # Handle special sorting for helpful_votes (sort by array length)
            if sort_by == "helpful_votes":
                # Use aggregation pipeline for sorting by array length
                pipeline = [
                    {"$match": query},
                    {
                        "$addFields": {
                            "helpful_votes_count": {
                                "$cond": [
                                    {"$isArray": "$helpful_votes"},
                                    {"$size": "$helpful_votes"},
                                    0
                                ]
                            }
                        }
                    },
                    {"$sort": {"helpful_votes_count": sort_direction}},
                    {"$skip": skip},
                    {"$limit": limit}
                ]
                reviews = list(self.db.reviews.aggregate(pipeline))
            else:
                # Get reviews with sorting and pagination
                cursor = self.db.reviews.find(query).sort(sort_by, sort_direction).skip(skip).limit(limit)
                reviews = list(cursor)
            
            # Convert ObjectId to string
            for review in reviews:
                review["_id"] = str(review["_id"])
            
            return {
                "reviews": reviews,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error getting filtered reviews: {e}")
            raise Exception(f"Failed to get reviews: {str(e)}")
    
    async def get_reviews(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Get list of reviews with filtering (legacy method)"""
        try:
            # Build query
            query = {"tenant_id": tenant_id}
            
            if status is not None:
                query["status"] = status
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Get total count
            total = self.db.reviews.count_documents(query)
            
            # Get reviews
            cursor = self.db.reviews.find(query).sort("created_at", -1).skip(skip).limit(limit)
            reviews = list(cursor)
            
            # Convert ObjectId to string
            for review in reviews:
                review["_id"] = str(review["_id"])
            
            return {
                "reviews": reviews,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error getting reviews: {e}")
            raise Exception(f"Failed to get reviews: {str(e)}")
    
    async def get_filter_counts(self, tenant_id: str) -> Dict:
        """Get counts for all filter options"""
        try:
            base_query = {"tenant_id": tenant_id}
            
            # Count by status
            status_counts = {}
            for status in ["pending", "approved", "rejected"]:
                count = self.db.reviews.count_documents({**base_query, "status": status})
                status_counts[status] = count
            
            # Count by rating
            rating_counts = {}
            for rating in [1, 2, 3, 4, 5]:
                count = self.db.reviews.count_documents({**base_query, "rating": rating})
                rating_counts[str(rating)] = count
            
            # Count by service
            service_pipeline = [
                {"$match": base_query},
                {"$group": {"_id": "$service_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            service_counts = {}
            for doc in self.db.reviews.aggregate(service_pipeline):
                if doc["_id"]:
                    service_counts[doc["_id"]] = doc["count"]
            
            # Count by stylist
            stylist_pipeline = [
                {"$match": base_query},
                {"$group": {"_id": "$stylist_id", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            stylist_counts = {}
            for doc in self.db.reviews.aggregate(stylist_pipeline):
                if doc["_id"]:
                    stylist_counts[doc["_id"]] = doc["count"]
            
            # Count reviews with responses
            has_response_count = self.db.reviews.count_documents({
                **base_query,
                "response": {"$exists": True, "$ne": None}
            })
            
            # Count reviews with photos
            has_photos_count = self.db.reviews.count_documents({
                **base_query,
                "photos": {"$exists": True, "$ne": [], "$type": "array"}
            })
            
            # Count flagged reviews
            is_flagged_count = self.db.reviews.count_documents({
                **base_query,
                "flags": {"$exists": True, "$ne": [], "$type": "array"}
            })
            
            return {
                "status": status_counts,
                "rating": rating_counts,
                "services": service_counts,
                "stylists": stylist_counts,
                "has_response": has_response_count,
                "has_photos": has_photos_count,
                "is_flagged": is_flagged_count,
                "total": self.db.reviews.count_documents(base_query)
            }
        
        except Exception as e:
            logger.error(f"Error getting filter counts: {e}")
            raise Exception(f"Failed to get filter counts: {str(e)}")
    
    async def create_review(
        self,
        tenant_id: str,
        booking_id: str,
        client_id: str,
        rating: int,
        comment: Optional[str] = None
    ) -> Dict:
        """Create a new review"""
        try:
            # Check if booking exists and is completed
            booking = self.db.bookings.find_one({
                "_id": ObjectId(booking_id),
                "tenant_id": tenant_id,
                "status": "completed"
            })
            
            if not booking:
                raise ValueError("Booking not found or not completed")
            
            # Check if already reviewed
            existing = self.db.reviews.find_one({"booking_id": booking_id})
            if existing:
                raise ValueError("Booking has already been reviewed")
            
            # Get client info
            client = self.db.clients.find_one({"_id": ObjectId(client_id)})
            if not client:
                raise ValueError("Client not found")
            
            # Get service info
            service = self.db.services.find_one({"_id": ObjectId(booking["service_id"])})
            if not service:
                raise ValueError("Service not found")
            
            # Get stylist info
            stylist = self.db.stylists.find_one({"_id": ObjectId(booking["stylist_id"])})
            if not stylist:
                raise ValueError("Stylist not found")
            
            # Create review
            review_data = {
                "tenant_id": tenant_id,
                "booking_id": booking_id,
                "client_id": client_id,
                "client_name": client.get("name", ""),
                "service_id": str(booking["service_id"]),
                "service_name": service.get("name", ""),
                "stylist_id": str(booking["stylist_id"]),
                "stylist_name": stylist.get("name", ""),
                "rating": rating,
                "comment": comment,
                "status": "pending",  # Requires moderation
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.reviews.insert_one(review_data)
            
            # Send notification
            try:
                from app.services.notification_service import NotificationService
                await NotificationService.create_review_notification(
                    db=self.db,
                    tenant_id=tenant_id,
                    client_name=client.get("name", "A client"),
                    rating=rating,
                    service_name=service.get("name", "a service")
                )
            except Exception as e:
                logger.warning(f"Failed to create review notification: {e}")
            review_data["_id"] = str(result.inserted_id)
            
            return review_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating review: {e}")
            raise Exception(f"Failed to create review: {str(e)}")
    
    async def moderate_review(
        self,
        review_id: str,
        tenant_id: str,
        status: str
    ) -> Dict:
        """Moderate a review (approve or reject)"""
        try:
            # Validate status
            if status not in ["approved", "rejected", "pending"]:
                raise ValueError("Invalid status. Must be 'approved', 'rejected', or 'pending'")
            
            # Find review
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Update status
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow()
            }
            
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {"$set": update_data}
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error moderating review: {e}")
            raise Exception(f"Failed to moderate review: {str(e)}")
    
    async def bulk_moderate_reviews(
        self,
        tenant_id: str,
        review_ids: List[str],
        action: str
    ) -> Dict:
        """Bulk moderate reviews (approve, reject, or delete)"""
        try:
            # Validate action
            if action not in ["approved", "rejected", "deleted"]:
                raise ValueError("Invalid action. Must be 'approved', 'rejected', or 'deleted'")
            
            # Convert string IDs to ObjectIds
            object_ids = []
            for review_id in review_ids:
                try:
                    object_ids.append(ObjectId(review_id))
                except Exception:
                    logger.warning(f"Invalid review ID: {review_id}")
            
            if not object_ids:
                raise ValueError("No valid review IDs provided")
            
            # Build query to ensure tenant isolation
            query = {
                "_id": {"$in": object_ids},
                "tenant_id": tenant_id
            }
            
            # Count matching reviews
            matched_count = self.db.reviews.count_documents(query)
            
            if matched_count == 0:
                raise ValueError("No reviews found for the given IDs")
            
            # Perform bulk update
            if action == "deleted":
                # Soft delete
                update_data = {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            else:
                # Update status
                update_data = {
                    "status": action,
                    "updated_at": datetime.utcnow()
                }
            
            result = self.db.reviews.update_many(
                query,
                {"$set": update_data}
            )
            
            return {
                "success": True,
                "action": action,
                "matched_count": matched_count,
                "modified_count": result.modified_count,
                "message": f"Successfully {action} {result.modified_count} review(s)"
            }
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error bulk moderating reviews: {e}")
            raise Exception(f"Failed to bulk moderate reviews: {str(e)}")
    
    async def get_rating_aggregation(
        self,
        tenant_id: str,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None
    ) -> Dict:
        """Get rating aggregation for tenant, service, or stylist"""
        try:
            # Build query
            query = {
                "tenant_id": tenant_id,
                "status": "approved"
            }
            
            if service_id:
                query["service_id"] = service_id
            
            if stylist_id:
                query["stylist_id"] = stylist_id
            
            # Aggregate ratings
            pipeline = [
                {"$match": query},
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
                    }
                }
            
            result = results[0]
            
            return {
                "average_rating": round(result["average_rating"], 2),
                "total_reviews": result["total_reviews"],
                "rating_distribution": {
                    "1": result["rating_1"],
                    "2": result["rating_2"],
                    "3": result["rating_3"],
                    "4": result["rating_4"],
                    "5": result["rating_5"]
                }
            }
        
        except Exception as e:
            logger.error(f"Error getting rating aggregation: {e}")
            return {
                "average_rating": 0.0,
                "total_reviews": 0,
                "rating_distribution": {
                    "1": 0,
                    "2": 0,
                    "3": 0,
                    "4": 0,
                    "5": 0
                }
            }
    
    async def add_response(
        self,
        review_id: str,
        tenant_id: str,
        responder_id: str,
        responder_name: str,
        response_text: str
    ) -> Dict:
        """Add owner response to review"""
        try:
            # Find review
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Create response object
            response_data = {
                "text": response_text,
                "responder_id": responder_id,
                "responder_name": responder_name,
                "responded_at": datetime.utcnow()
            }
            
            # Update review with response
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "response": response_data,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error adding response: {e}")
            raise Exception(f"Failed to add response: {str(e)}")
    
    async def update_response(
        self,
        review_id: str,
        tenant_id: str,
        responder_id: str,
        responder_name: str,
        response_text: str
    ) -> Dict:
        """Update existing review response"""
        try:
            # Find review
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            if not review.get("response"):
                raise ValueError("Review has no response to update")
            
            # Get old response for edit history
            old_response = review.get("response", {})
            
            # Create new response object
            response_data = {
                "text": response_text,
                "responder_id": responder_id,
                "responder_name": responder_name,
                "responded_at": old_response.get("responded_at", datetime.utcnow()),
                "edited_at": datetime.utcnow()
            }
            
            # Update review with new response
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "response": response_data,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating response: {e}")
            raise Exception(f"Failed to update response: {str(e)}")
    
    async def delete_response(
        self,
        review_id: str,
        tenant_id: str
    ) -> Dict:
        """Delete review response"""
        try:
            # Find review
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            if not review.get("response"):
                raise ValueError("Review has no response to delete")
            
            # Remove response
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$unset": {"response": ""},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting response: {e}")
            raise Exception(f"Failed to delete response: {str(e)}")
    
    async def get_response_templates(self, tenant_id: str) -> List[Dict]:
        """Get response templates for tenant"""
        try:
            templates = list(self.db.review_templates.find({
                "tenant_id": tenant_id
            }).sort("is_default", -1).sort("created_at", -1))
            
            for template in templates:
                template["_id"] = str(template["_id"])
            
            return templates
        
        except Exception as e:
            logger.error(f"Error getting response templates: {e}")
            raise Exception(f"Failed to get templates: {str(e)}")
    
    async def create_response_template(
        self,
        tenant_id: str,
        name: str,
        category: str,
        text: str
    ) -> Dict:
        """Create custom response template"""
        try:
            # Validate category
            if category not in ["positive", "negative", "neutral"]:
                raise ValueError("Invalid category. Must be 'positive', 'negative', or 'neutral'")
            
            template_data = {
                "tenant_id": tenant_id,
                "name": name,
                "category": category,
                "text": text,
                "is_default": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            result = self.db.review_templates.insert_one(template_data)
            template_data["_id"] = str(result.inserted_id)
            
            return template_data
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error creating template: {e}")
            raise Exception(f"Failed to create template: {str(e)}")
    
    async def update_response_template(
        self,
        template_id: str,
        tenant_id: str,
        name: Optional[str] = None,
        category: Optional[str] = None,
        text: Optional[str] = None
    ) -> Dict:
        """Update response template"""
        try:
            # Find template
            template = self.db.review_templates.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            
            if not template:
                raise ValueError("Template not found")
            
            # Build update data
            update_data = {"updated_at": datetime.utcnow()}
            
            if name is not None:
                update_data["name"] = name
            
            if category is not None:
                if category not in ["positive", "negative", "neutral"]:
                    raise ValueError("Invalid category")
                update_data["category"] = category
            
            if text is not None:
                update_data["text"] = text
            
            # Update template
            self.db.review_templates.update_one(
                {"_id": ObjectId(template_id)},
                {"$set": update_data}
            )
            
            # Get updated template
            updated_template = self.db.review_templates.find_one({"_id": ObjectId(template_id)})
            updated_template["_id"] = str(updated_template["_id"])
            
            return updated_template
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error updating template: {e}")
            raise Exception(f"Failed to update template: {str(e)}")
    
    async def delete_response_template(
        self,
        template_id: str,
        tenant_id: str
    ) -> None:
        """Delete response template"""
        try:
            # Find template
            template = self.db.review_templates.find_one({
                "_id": ObjectId(template_id),
                "tenant_id": tenant_id
            })
            
            if not template:
                raise ValueError("Template not found")
            
            if template.get("is_default"):
                raise ValueError("Cannot delete default templates")
            
            # Delete template
            self.db.review_templates.delete_one({"_id": ObjectId(template_id)})
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error deleting template: {e}")
            raise Exception(f"Failed to delete template: {str(e)}")
    
    async def export_to_csv(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        rating: Optional[List[int]] = None,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_response: Optional[bool] = None,
        has_photos: Optional[bool] = None,
        is_flagged: Optional[bool] = None,
        search: Optional[str] = None
    ) -> str:
        """Export reviews to CSV format with applied filters"""
        try:
            # Build query with filters
            query = self._build_filter_query(
                tenant_id=tenant_id,
                status=status,
                rating=rating,
                service_id=service_id,
                stylist_id=stylist_id,
                start_date=start_date,
                end_date=end_date,
                has_response=has_response,
                has_photos=has_photos,
                is_flagged=is_flagged,
                search=search
            )
            
            # Get all matching reviews (no pagination for export)
            cursor = self.db.reviews.find(query).sort("created_at", -1)
            reviews = list(cursor)
            
            # Create CSV output
            output = StringIO()
            fieldnames = [
                'date',
                'client_name',
                'service',
                'stylist',
                'rating',
                'comment',
                'status',
                'response'
            ]
            
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write review rows
            for review in reviews:
                # Get response text if exists
                response_text = ""
                if review.get("response"):
                    response_text = review["response"].get("text", "")
                
                # Format date
                created_at = review.get("created_at")
                date_str = ""
                if created_at:
                    if isinstance(created_at, datetime):
                        date_str = created_at.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        date_str = str(created_at)
                
                # Write row
                writer.writerow({
                    'date': date_str,
                    'client_name': review.get("client_name", ""),
                    'service': review.get("service_name", ""),
                    'stylist': review.get("stylist_name", ""),
                    'rating': review.get("rating", ""),
                    'comment': review.get("comment", ""),
                    'status': review.get("status", ""),
                    'response': response_text
                })
            
            return output.getvalue()
        
        except Exception as e:
            logger.error(f"Error exporting reviews to CSV: {e}")
            raise Exception(f"Failed to export reviews to CSV: {str(e)}")
    
    async def export_to_pdf(
        self,
        tenant_id: str,
        status: Optional[str] = None,
        rating: Optional[List[int]] = None,
        service_id: Optional[str] = None,
        stylist_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        has_response: Optional[bool] = None,
        has_photos: Optional[bool] = None,
        is_flagged: Optional[bool] = None,
        search: Optional[str] = None
    ) -> bytes:
        """Export reviews to PDF format with summary statistics"""
        try:
            # Build query with filters
            query = self._build_filter_query(
                tenant_id=tenant_id,
                status=status,
                rating=rating,
                service_id=service_id,
                stylist_id=stylist_id,
                start_date=start_date,
                end_date=end_date,
                has_response=has_response,
                has_photos=has_photos,
                is_flagged=is_flagged,
                search=search
            )
            
            # Get all matching reviews
            cursor = self.db.reviews.find(query).sort("created_at", -1)
            reviews = list(cursor)
            
            # Create PDF buffer
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=30,
                alignment=TA_CENTER
            )
            
            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=14,
                textColor=colors.HexColor('#374151'),
                spaceAfter=12,
                spaceBefore=12
            )
            
            # Add title
            elements.append(Paragraph("Review Export Report", title_style))
            elements.append(Spacer(1, 0.2 * inch))
            
            # Add summary statistics
            elements.append(Paragraph("Summary Statistics", heading_style))
            
            # Calculate statistics
            total_reviews = len(reviews)
            approved_count = sum(1 for r in reviews if r.get("status") == "approved")
            rejected_count = sum(1 for r in reviews if r.get("status") == "rejected")
            pending_count = sum(1 for r in reviews if r.get("status") == "pending")
            
            # Calculate average rating (only approved reviews)
            approved_reviews = [r for r in reviews if r.get("status") == "approved"]
            avg_rating = 0.0
            if approved_reviews:
                avg_rating = sum(r.get("rating", 0) for r in approved_reviews) / len(approved_reviews)
            
            # Rating distribution
            rating_dist = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for review in approved_reviews:
                rating = review.get("rating", 0)
                if rating in rating_dist:
                    rating_dist[rating] += 1
            
            # Create summary table
            summary_data = [
                ["Metric", "Value"],
                ["Total Reviews", str(total_reviews)],
                ["Approved", str(approved_count)],
                ["Rejected", str(rejected_count)],
                ["Pending", str(pending_count)],
                ["Average Rating", f"{avg_rating:.2f}"],
            ]
            
            summary_table = Table(summary_data, colWidths=[3 * inch, 2 * inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            
            elements.append(summary_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Add rating distribution
            elements.append(Paragraph("Rating Distribution", heading_style))
            
            rating_data = [["Rating", "Count"]]
            for rating in [5, 4, 3, 2, 1]:
                rating_data.append([f"{rating} Stars", str(rating_dist[rating])])
            
            rating_table = Table(rating_data, colWidths=[2 * inch, 2 * inch])
            rating_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
            ]))
            
            elements.append(rating_table)
            elements.append(Spacer(1, 0.3 * inch))
            
            # Add reviews table if there are reviews
            if reviews:
                elements.append(PageBreak())
                elements.append(Paragraph("Detailed Reviews", heading_style))
                elements.append(Spacer(1, 0.2 * inch))
                
                # Create reviews table
                review_data = [["Date", "Client", "Service", "Rating", "Status", "Comment"]]
                
                for review in reviews[:50]:  # Limit to 50 reviews per PDF for performance
                    # Format date
                    created_at = review.get("created_at")
                    date_str = ""
                    if created_at:
                        if isinstance(created_at, datetime):
                            date_str = created_at.strftime("%Y-%m-%d")
                        else:
                            date_str = str(created_at)[:10]
                    
                    # Truncate comment to 50 chars
                    comment = review.get("comment", "")
                    if len(comment) > 50:
                        comment = comment[:47] + "..."
                    
                    review_data.append([
                        date_str,
                        review.get("client_name", "")[:20],
                        review.get("service_name", "")[:15],
                        str(review.get("rating", "")),
                        review.get("status", ""),
                        comment
                    ])
                
                review_table = Table(review_data, colWidths=[1 * inch, 1.2 * inch, 1.2 * inch, 0.6 * inch, 0.8 * inch, 1.4 * inch])
                review_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e5e7eb')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f9fafb')),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
                    ('FONTSIZE', (0, 1), (-1, -1), 8),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ]))
                
                elements.append(review_table)
                
                # Add note if more than 50 reviews
                if len(reviews) > 50:
                    elements.append(Spacer(1, 0.2 * inch))
                    note_style = ParagraphStyle(
                        'Note',
                        parent=styles['Normal'],
                        fontSize=9,
                        textColor=colors.HexColor('#6b7280'),
                        alignment=TA_CENTER
                    )
                    elements.append(Paragraph(
                        f"Showing first 50 of {len(reviews)} reviews. Export to CSV for complete data.",
                        note_style
                    ))
            
            # Build PDF
            doc.build(elements)
            
            # Get PDF bytes
            pdf_bytes = buffer.getvalue()
            buffer.close()
            
            return pdf_bytes
        
        except Exception as e:
            logger.error(f"Error exporting reviews to PDF: {e}")
            raise Exception(f"Failed to export reviews to PDF: {str(e)}")
    
    async def upload_review_photo(
        self,
        review_id: str,
        tenant_id: str,
        file_content: bytes,
        filename: str,
        content_type: str
    ) -> Dict:
        """Upload photo to review"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Check photo limit
            photos = review.get("photos", [])
            if len(photos) >= 5:
                raise ValueError("Maximum 5 photos per review")
            
            # Generate photo ID
            photo_id = str(ObjectId())
            
            # Store file in cloud storage (using simple file storage for now)
            # In production, use S3, GCS, or similar
            photo_url = f"/api/reviews/{review_id}/photos/{photo_id}"
            
            # Create photo object
            photo = {
                "id": photo_id,
                "url": photo_url,
                "filename": filename,
                "content_type": content_type,
                "size": len(file_content),
                "uploaded_at": datetime.utcnow()
            }
            
            # Add photo to review
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$push": {"photos": photo},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Store file content (in production, use cloud storage)
            # For now, store in database
            self.db.review_photos.insert_one({
                "_id": ObjectId(photo_id),
                "review_id": review_id,
                "tenant_id": tenant_id,
                "content": file_content,
                "content_type": content_type,
                "filename": filename,
                "created_at": datetime.utcnow()
            })
            
            return photo
        
        except ValueError as e:
            logger.error(f"Validation error uploading photo: {e}")
            raise
        except Exception as e:
            logger.error(f"Error uploading review photo: {e}")
            raise Exception(f"Failed to upload photo: {str(e)}")
    
    async def delete_review_photo(
        self,
        review_id: str,
        photo_id: str,
        tenant_id: str,
        user_id: str
    ) -> Dict:
        """Delete photo from review"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Remove photo from review
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$pull": {"photos": {"id": photo_id}},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Delete photo file
            self.db.review_photos.delete_one({
                "_id": ObjectId(photo_id),
                "review_id": review_id,
                "tenant_id": tenant_id
            })
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error deleting photo: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting review photo: {e}")
            raise Exception(f"Failed to delete photo: {str(e)}")
    
    async def flag_review(
        self,
        review_id: str,
        tenant_id: str,
        user_id: str,
        reason: str,
        details: str = ""
    ) -> Dict:
        """Flag review as inappropriate"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Check if already flagged by this user
            flags = review.get("flags", [])
            if any(f.get("flagged_by") == user_id for f in flags):
                raise ValueError("You have already flagged this review")
            
            # Create flag object
            flag = {
                "reason": reason,
                "details": details,
                "flagged_by": user_id,
                "flagged_at": datetime.utcnow()
            }
            
            # Add flag to review
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$push": {"flags": flag},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error flagging review: {e}")
            raise
        except Exception as e:
            logger.error(f"Error flagging review: {e}")
            raise Exception(f"Failed to flag review: {str(e)}")
    
    async def unflag_review(
        self,
        review_id: str,
        tenant_id: str
    ) -> Dict:
        """Unflag review (remove all flags)"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Remove all flags
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "flags": [],
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error unflagging review: {e}")
            raise
        except Exception as e:
            logger.error(f"Error unflagging review: {e}")
            raise Exception(f"Failed to unflag review: {str(e)}")
    
    async def award_review_points(
        self,
        review_id: str,
        tenant_id: str,
        client_id: str,
        points: int = 50
    ) -> Dict:
        """Award loyalty points for review submission"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Check if points already awarded
            if review.get("points_awarded"):
                raise ValueError("Points already awarded for this review")
            
            # Import loyalty service
            from app.services.loyalty_service import LoyaltyService
            
            # Award points
            transaction = LoyaltyService.earn_points(
                tenant_id=tenant_id,
                client_id=client_id,
                points=points,
                reference_type="review",
                reference_id=review_id,
                description=f"Points awarded for review submission"
            )
            
            # Mark points as awarded
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "points_awarded": True,
                        "points_awarded_at": datetime.utcnow(),
                        "points_amount": points,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            logger.info(f"Awarded {points} points to client {client_id} for review {review_id}")
            
            return {
                "review": updated_review,
                "transaction": transaction,
                "points_awarded": points
            }
        
        except ValueError as e:
            logger.error(f"Validation error awarding points: {e}")
            raise
        except Exception as e:
            logger.error(f"Error awarding review points: {e}")
            raise Exception(f"Failed to award points: {str(e)}")
    
    async def vote_helpful(
        self,
        review_id: str,
        tenant_id: str,
        user_id: str
    ) -> Dict:
        """Vote review as helpful"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Check if already voted
            helpful_votes = review.get("helpful_votes", [])
            if user_id in helpful_votes:
                raise ValueError("You have already voted this review as helpful")
            
            # Add vote
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$push": {"helpful_votes": user_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error voting helpful: {e}")
            raise
        except Exception as e:
            logger.error(f"Error voting helpful: {e}")
            raise Exception(f"Failed to vote helpful: {str(e)}")
    
    async def remove_helpful_vote(
        self,
        review_id: str,
        tenant_id: str,
        user_id: str
    ) -> Dict:
        """Remove helpful vote from review"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Check if voted
            helpful_votes = review.get("helpful_votes", [])
            if user_id not in helpful_votes:
                raise ValueError("You have not voted this review as helpful")
            
            # Remove vote
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$pull": {"helpful_votes": user_id},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error removing helpful vote: {e}")
            raise
        except Exception as e:
            logger.error(f"Error removing helpful vote: {e}")
            raise Exception(f"Failed to remove helpful vote: {str(e)}")
    
    async def soft_delete_review(
        self,
        review_id: str,
        tenant_id: str,
        deleted_by: str,
        deletion_reason: str
    ) -> Dict:
        """Soft delete a review"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Soft delete
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "is_deleted": True,
                        "deleted_by": deleted_by,
                        "deleted_at": datetime.utcnow(),
                        "deletion_reason": deletion_reason,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            logger.info(f"Soft deleted review {review_id} by {deleted_by}")
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error soft deleting review: {e}")
            raise
        except Exception as e:
            logger.error(f"Error soft deleting review: {e}")
            raise Exception(f"Failed to soft delete review: {str(e)}")
    
    async def restore_review(
        self,
        review_id: str,
        tenant_id: str
    ) -> Dict:
        """Restore a soft-deleted review"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            if not review.get("is_deleted"):
                raise ValueError("Review is not deleted")
            
            # Restore
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "is_deleted": False,
                        "updated_at": datetime.utcnow()
                    },
                    "$unset": {
                        "deleted_by": "",
                        "deleted_at": "",
                        "deletion_reason": ""
                    }
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            logger.info(f"Restored review {review_id}")
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error restoring review: {e}")
            raise
        except Exception as e:
            logger.error(f"Error restoring review: {e}")
            raise Exception(f"Failed to restore review: {str(e)}")
    
    async def edit_review_comment(
        self,
        review_id: str,
        tenant_id: str,
        new_comment: str,
        edited_by: str
    ) -> Dict:
        """Edit review comment and track edit history"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Create edit history entry
            edit_entry = {
                "original_text": review.get("comment", ""),
                "edited_text": new_comment,
                "edited_by": edited_by,
                "edited_at": datetime.utcnow()
            }
            
            # Update review with new comment and edit history
            self.db.reviews.update_one(
                {"_id": ObjectId(review_id)},
                {
                    "$set": {
                        "comment": new_comment,
                        "updated_at": datetime.utcnow()
                    },
                    "$push": {"edit_history": edit_entry}
                }
            )
            
            # Get updated review
            updated_review = self.db.reviews.find_one({"_id": ObjectId(review_id)})
            updated_review["_id"] = str(updated_review["_id"])
            
            logger.info(f"Edited review {review_id} by {edited_by}")
            
            return updated_review
        
        except ValueError as e:
            logger.error(f"Validation error editing review: {e}")
            raise
        except Exception as e:
            logger.error(f"Error editing review: {e}")
            raise Exception(f"Failed to edit review: {str(e)}")
    
    async def get_deleted_reviews(
        self,
        tenant_id: str,
        skip: int = 0,
        limit: int = 20
    ) -> Dict:
        """Get soft-deleted reviews"""
        try:
            # Build query for deleted reviews
            query = {
                "tenant_id": tenant_id,
                "is_deleted": True
            }
            
            # Get total count
            total = self.db.reviews.count_documents(query)
            
            # Get deleted reviews
            cursor = self.db.reviews.find(query).sort("deleted_at", -1).skip(skip).limit(limit)
            reviews = list(cursor)
            
            # Convert ObjectId to string
            for review in reviews:
                review["_id"] = str(review["_id"])
            
            return {
                "reviews": reviews,
                "total": total,
                "skip": skip,
                "limit": limit
            }
        
        except Exception as e:
            logger.error(f"Error getting deleted reviews: {e}")
            raise Exception(f"Failed to get deleted reviews: {str(e)}")
    
    async def get_edit_history(
        self,
        review_id: str,
        tenant_id: str
    ) -> List[Dict]:
        """Get edit history for a review"""
        try:
            # Validate review exists
            review = self.db.reviews.find_one({
                "_id": ObjectId(review_id),
                "tenant_id": tenant_id
            })
            
            if not review:
                raise ValueError("Review not found")
            
            # Return edit history
            edit_history = review.get("edit_history", [])
            
            return edit_history
        
        except ValueError as e:
            logger.error(f"Validation error getting edit history: {e}")
            raise
        except Exception as e:
            logger.error(f"Error getting edit history: {e}")
            raise Exception(f"Failed to get edit history: {str(e)}")


# Legacy module-level functions

async def get_rating_aggregation(
    tenant_id: str,
    service_id: str = None,
    stylist_id: str = None,
    db = None
) -> Dict:
    """Legacy function - use ReviewService instead"""
    service = ReviewService(db)
    return await service.get_rating_aggregation(tenant_id, service_id, stylist_id)


async def check_if_reviewed(
    booking_id: str,
    db = None
) -> bool:
    """Check if a booking has already been reviewed"""
    try:
        review = db.reviews.find_one({"booking_id": booking_id})
        return review is not None
    
    except Exception as e:
        logger.error(f"Error checking if reviewed: {e}")
        return False
