"""Recommendation service for personalized service suggestions"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from bson import ObjectId
from collections import Counter, defaultdict

from app.models.customer_recommendation import CustomerPreference, BookingRecommendation
from app.models.appointment import Appointment
from app.models.service import Service
from app.models.staff import Staff
from app.models.customer import Customer


class RecommendationService:
    """Service for generating personalized recommendations"""
    
    @staticmethod
    async def update_customer_preferences(tenant_id: ObjectId, customer_id: ObjectId) -> CustomerPreference:
        """Update customer preferences based on booking history"""
        # Get customer's booking history
        bookings = await Appointment.find(
            Appointment.tenant_id == tenant_id,
            Appointment.customer_id == customer_id,
            Appointment.status.in_(["completed", "confirmed"])
        ).to_list()
        
        if not bookings:
            # Create empty preference record
            preference = CustomerPreference(
                tenant_id=tenant_id,
                customer_id=customer_id
            )
            await preference.insert()
            return preference
        
        # Analyze booking patterns
        service_ids = [b.service_id for b in bookings if b.service_id]
        staff_ids = [b.staff_id for b in bookings if b.staff_id]
        
        # Get services to extract categories
        services = await Service.find(
            Service.id.in_([ObjectId(sid) for sid in service_ids if sid])
        ).to_list()
        
        service_categories = [s.category for s in services if s.category]
        
        # Calculate time slot preferences
        time_slots = []
        days = []
        for booking in bookings:
            if booking.start_time:
                hour = booking.start_time.hour
                if 6 <= hour < 12:
                    time_slots.append("morning")
                elif 12 <= hour < 17:
                    time_slots.append("afternoon")
                else:
                    time_slots.append("evening")
                
                days.append(booking.start_time.strftime("%A").lower())
        
        # Calculate booking frequency
        if len(bookings) > 1:
            sorted_bookings = sorted(bookings, key=lambda x: x.start_time or datetime.min)
            date_diffs = []
            for i in range(1, len(sorted_bookings)):
                if sorted_bookings[i].start_time and sorted_bookings[i-1].start_time:
                    diff = (sorted_bookings[i].start_time - sorted_bookings[i-1].start_time).days
                    if diff > 0:
                        date_diffs.append(diff)
            
            avg_frequency = sum(date_diffs) // len(date_diffs) if date_diffs else None
        else:
            avg_frequency = None
        
        # Calculate average spend
        total_spend = sum([float(b.total_price.to_decimal()) for b in bookings if b.total_price])
        avg_spend = total_spend / len(bookings) if bookings else 0
        
        # Get most common preferences
        most_common_services = [sid for sid, _ in Counter(service_ids).most_common(5)]
        most_common_staff = [sid for sid, _ in Counter(staff_ids).most_common(3)]
        most_common_categories = [cat for cat, _ in Counter(service_categories).most_common(5)]
        most_common_time_slots = [slot for slot, _ in Counter(time_slots).most_common(3)]
        most_common_days = [day for day, _ in Counter(days).most_common(3)]
        
        # Update or create preference
        preference = await CustomerPreference.find_one(
            CustomerPreference.tenant_id == tenant_id,
            CustomerPreference.customer_id == customer_id
        )
        
        if not preference:
            preference = CustomerPreference(
                tenant_id=tenant_id,
                customer_id=customer_id
            )
        
        preference.preferred_services = [ObjectId(sid) for sid in most_common_services if sid]
        preference.preferred_staff = [ObjectId(sid) for sid in most_common_staff if sid]
        preference.preferred_service_categories = most_common_categories
        preference.preferred_time_slots = most_common_time_slots
        preference.preferred_days = most_common_days
        preference.average_booking_frequency_days = avg_frequency
        preference.average_spend = avg_spend
        preference.last_booking_date = max([b.start_time for b in bookings if b.start_time], default=None)
        preference.total_bookings = len(bookings)
        preference.updated_at = datetime.utcnow()
        
        await preference.save()
        return preference
    
    @staticmethod
    async def generate_recommendations(
        tenant_id: ObjectId,
        customer_id: Optional[ObjectId] = None,
        limit: int = 5
    ) -> List[Dict]:
        """Generate personalized recommendations"""
        recommendations = []
        
        if customer_id:
            # Get or update customer preferences
            preference = await CustomerPreference.find_one(
                CustomerPreference.tenant_id == tenant_id,
                CustomerPreference.customer_id == customer_id
            )
            
            if not preference:
                preference = await RecommendationService.update_customer_preferences(tenant_id, customer_id)
            
            # Content-based recommendations (based on past services)
            if preference.preferred_services:
                content_recs = await RecommendationService._content_based_recommendations(
                    tenant_id, preference, limit=3
                )
                recommendations.extend(content_recs)
            
            # Collaborative filtering (what similar customers booked)
            if preference.preferred_service_categories:
                collab_recs = await RecommendationService._collaborative_recommendations(
                    tenant_id, preference, limit=2
                )
                recommendations.extend(collab_recs)
        
        # Fill remaining slots with popular services
        if len(recommendations) < limit:
            popular_recs = await RecommendationService._popular_recommendations(
                tenant_id, limit=limit - len(recommendations)
            )
            recommendations.extend(popular_recs)
        
        # Remove duplicates and limit
        seen_services = set()
        unique_recs = []
        for rec in recommendations:
            if rec["service_id"] not in seen_services:
                seen_services.add(rec["service_id"])
                unique_recs.append(rec)
                if len(unique_recs) >= limit:
                    break
        
        return unique_recs
    
    @staticmethod
    async def _content_based_recommendations(
        tenant_id: ObjectId,
        preference: CustomerPreference,
        limit: int = 3
    ) -> List[Dict]:
        """Generate content-based recommendations"""
        recommendations = []
        
        # Find services in preferred categories that customer hasn't booked
        services = await Service.find(
            Service.tenant_id == tenant_id,
            Service.is_active == True,
            Service.allow_public_booking == True,
            Service.category.in_(preference.preferred_service_categories),
            Service.id.not_in(preference.preferred_services)
        ).limit(limit).to_list()
        
        for service in services:
            # Get preferred staff for this service if available
            staff = None
            if preference.preferred_staff:
                staff = await Staff.find_one(
                    Staff.id.in_(preference.preferred_staff),
                    Staff.services.in_([service.id])
                )
            
            recommendations.append({
                "service_id": str(service.id),
                "service_name": service.name,
                "service_description": service.description,
                "service_price": float(service.price.to_decimal()),
                "service_duration": service.duration_minutes,
                "service_image_url": service.image_url,
                "staff_id": str(staff.id) if staff else None,
                "staff_name": staff.name if staff else None,
                "confidence_score": 0.8,
                "recommendation_type": "content_based",
                "reasoning": f"Based on your interest in {service.category} services"
            })
        
        return recommendations
    
    @staticmethod
    async def _collaborative_recommendations(
        tenant_id: ObjectId,
        preference: CustomerPreference,
        limit: int = 2
    ) -> List[Dict]:
        """Generate collaborative filtering recommendations"""
        recommendations = []
        
        # Find customers with similar booking patterns
        similar_customers = await CustomerPreference.find(
            CustomerPreference.tenant_id == tenant_id,
            CustomerPreference.id != preference.id,
            CustomerPreference.preferred_service_categories.in_(preference.preferred_service_categories)
        ).limit(10).to_list()
        
        # Aggregate services booked by similar customers
        service_scores = defaultdict(int)
        for similar_pref in similar_customers:
            for service_id in similar_pref.preferred_services:
                if service_id not in preference.preferred_services:
                    service_scores[service_id] += 1
        
        # Get top services
        top_service_ids = sorted(service_scores.keys(), key=lambda x: service_scores[x], reverse=True)[:limit]
        
        services = await Service.find(
            Service.id.in_(top_service_ids),
            Service.is_active == True,
            Service.allow_public_booking == True
        ).to_list()
        
        for service in services:
            recommendations.append({
                "service_id": str(service.id),
                "service_name": service.name,
                "service_description": service.description,
                "service_price": float(service.price.to_decimal()),
                "service_duration": service.duration_minutes,
                "service_image_url": service.image_url,
                "staff_id": None,
                "staff_name": None,
                "confidence_score": 0.7,
                "recommendation_type": "collaborative",
                "reasoning": "Customers with similar preferences also booked this"
            })
        
        return recommendations
    
    @staticmethod
    async def _popular_recommendations(
        tenant_id: ObjectId,
        limit: int = 5
    ) -> List[Dict]:
        """Generate popular service recommendations"""
        # Get most booked services in last 30 days
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        bookings = await Appointment.find(
            Appointment.tenant_id == tenant_id,
            Appointment.created_at >= thirty_days_ago,
            Appointment.status.in_(["completed", "confirmed"])
        ).to_list()
        
        service_counts = Counter([b.service_id for b in bookings if b.service_id])
        top_service_ids = [ObjectId(sid) for sid, _ in service_counts.most_common(limit) if sid]
        
        services = await Service.find(
            Service.id.in_(top_service_ids),
            Service.is_active == True,
            Service.allow_public_booking == True
        ).to_list()
        
        recommendations = []
        for service in services:
            recommendations.append({
                "service_id": str(service.id),
                "service_name": service.name,
                "service_description": service.description,
                "service_price": float(service.price.to_decimal()),
                "service_duration": service.duration_minutes,
                "service_image_url": service.image_url,
                "staff_id": None,
                "staff_name": None,
                "confidence_score": 0.6,
                "recommendation_type": "popular",
                "reasoning": "Popular choice among our customers"
            })
        
        return recommendations
    
    @staticmethod
    async def track_recommendation_interaction(
        recommendation_id: str,
        action: str
    ) -> None:
        """Track user interaction with recommendation"""
        recommendation = await BookingRecommendation.get(ObjectId(recommendation_id))
        
        if not recommendation:
            return
        
        if action == "clicked":
            recommendation.clicked = True
            recommendation.shown_to_customer = True
        elif action == "booked":
            recommendation.booked = True
            recommendation.clicked = True
            recommendation.shown_to_customer = True
        
        await recommendation.save()
