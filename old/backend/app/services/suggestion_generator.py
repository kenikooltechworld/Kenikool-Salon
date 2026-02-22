import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class SuggestionGenerator:
    """Generates AI suggestions based on patterns and predictions"""

    def __init__(self):
        """Initialize suggestion generator"""
        self.suggestions = []

    async def suggest_booking_times(
        self,
        stylist_id: str,
        booking_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest optimal booking times and stylists"""
        try:
            suggestions = []
            
            if 'peak_hours' in booking_patterns:
                peak_hours = booking_patterns['peak_hours']
                suggestions.append({
                    "type": "booking_time",
                    "recommendation": f"Schedule appointments during peak hours: {peak_hours}",
                    "confidence": 0.80,
                    "impact": "high",
                    "reason": "Historical data shows higher demand during these hours"
                })
            
            if 'peak_days' in booking_patterns:
                peak_days = booking_patterns['peak_days']
                suggestions.append({
                    "type": "booking_day",
                    "recommendation": f"Prioritize bookings on: {peak_days}",
                    "confidence": 0.75,
                    "impact": "high",
                    "reason": "These days have highest booking volume"
                })
            
            logger.info(f"Booking suggestions generated: {len(suggestions)}")
            return suggestions

        except Exception as e:
            logger.error(f"Booking suggestion generation failed: {e}")
            return []

    async def suggest_stylist_assignments(
        self,
        staff_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest stylist assignments based on performance"""
        try:
            suggestions = []
            
            if 'top_performers' in staff_patterns:
                top_performers = staff_patterns['top_performers']
                suggestions.append({
                    "type": "stylist_assignment",
                    "recommendation": f"Assign premium clients to top performers",
                    "stylists": top_performers,
                    "confidence": 0.85,
                    "impact": "high",
                    "reason": "Top performers have higher client satisfaction"
                })
            
            logger.info(f"Stylist assignment suggestions generated: {len(suggestions)}")
            return suggestions

        except Exception as e:
            logger.error(f"Stylist suggestion generation failed: {e}")
            return []

    async def suggest_inventory_reorders(
        self,
        inventory_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest inventory reorders"""
        try:
            suggestions = []
            
            if 'low_stock_items' in inventory_patterns:
                low_stock = inventory_patterns['low_stock_items']
                if low_stock:
                    suggestions.append({
                        "type": "inventory_reorder",
                        "recommendation": f"Reorder low stock items: {low_stock}",
                        "items": low_stock,
                        "confidence": 0.90,
                        "impact": "high",
                        "urgency": "immediate",
                        "reason": "Stock levels below minimum threshold"
                    })
            
            if 'fast_moving_items' in inventory_patterns:
                fast_moving = inventory_patterns['fast_moving_items']
                if fast_moving:
                    suggestions.append({
                        "type": "inventory_stock_up",
                        "recommendation": f"Increase stock for fast-moving items: {fast_moving}",
                        "items": fast_moving,
                        "confidence": 0.75,
                        "impact": "medium",
                        "urgency": "soon",
                        "reason": "High demand for these items"
                    })
            
            logger.info(f"Inventory suggestions generated: {len(suggestions)}")
            return suggestions

        except Exception as e:
            logger.error(f"Inventory suggestion generation failed: {e}")
            return []

    async def suggest_client_retention(
        self,
        churn_predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest client retention strategies"""
        try:
            suggestions = []
            
            if 'at_risk_clients' in churn_predictions:
                at_risk = churn_predictions['at_risk_clients']
                high_risk = [c for c in at_risk if c.get('churn_risk') == 'high']
                
                if high_risk:
                    suggestions.append({
                        "type": "client_retention",
                        "recommendation": "Reach out to high-risk clients with special offers",
                        "clients": high_risk,
                        "confidence": 0.80,
                        "impact": "high",
                        "actions": [
                            "Send personalized discount offer",
                            "Schedule follow-up appointment",
                            "Offer loyalty rewards"
                        ],
                        "reason": "Clients haven't visited in 90+ days"
                    })
            
            logger.info(f"Client retention suggestions generated: {len(suggestions)}")
            return suggestions

        except Exception as e:
            logger.error(f"Client retention suggestion generation failed: {e}")
            return []

    async def suggest_upsell_services(
        self,
        service_patterns: Dict[str, Any],
        client_history: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Suggest upsell services"""
        try:
            suggestions = []
            
            if 'most_popular_services' in service_patterns:
                popular = service_patterns['most_popular_services']
                
                suggestions.append({
                    "type": "upsell_service",
                    "recommendation": "Recommend complementary services to clients",
                    "popular_services": popular,
                    "confidence": 0.70,
                    "impact": "medium",
                    "examples": [
                        "Suggest hair treatment with haircut",
                        "Offer nail services with hair services",
                        "Bundle services for discount"
                    ],
                    "reason": "Increase average transaction value"
                })
            
            logger.info(f"Upsell suggestions generated: {len(suggestions)}")
            return suggestions

        except Exception as e:
            logger.error(f"Upsell suggestion generation failed: {e}")
            return []

    async def suggest_staffing_optimization(
        self,
        staffing_predictions: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Suggest staffing optimization"""
        try:
            suggestions = []
            
            if 'recommended_staff' in staffing_predictions:
                recommended = staffing_predictions['recommended_staff']
                
                suggestions.append({
                    "type": "staffing_optimization",
                    "recommendation": f"Optimize staffing to {recommended} stylists",
                    "recommended_count": recommended,
                    "confidence": 0.65,
                    "impact": "medium",
                    "benefits": [
                        "Reduce labor costs",
                        "Improve staff utilization",
                        "Maintain service quality"
                    ],
                    "reason": "Based on historical appointment patterns"
                })
            
            logger.info(f"Staffing suggestions generated: {len(suggestions)}")
            return suggestions

        except Exception as e:
            logger.error(f"Staffing suggestion generation failed: {e}")
            return []

    async def generate_all_suggestions(
        self,
        patterns: Dict[str, Any],
        predictions: Dict[str, Any],
        client_history: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Generate all suggestions"""
        try:
            all_suggestions = []
            
            # Booking suggestions
            if 'booking_patterns' in patterns:
                booking_sugg = await self.suggest_booking_times(
                    "all",
                    patterns['booking_patterns']
                )
                all_suggestions.extend(booking_sugg)
            
            # Stylist suggestions
            if 'staff_patterns' in patterns:
                stylist_sugg = await self.suggest_stylist_assignments(
                    patterns['staff_patterns']
                )
                all_suggestions.extend(stylist_sugg)
            
            # Inventory suggestions
            if 'inventory_patterns' in patterns:
                inventory_sugg = await self.suggest_inventory_reorders(
                    patterns['inventory_patterns']
                )
                all_suggestions.extend(inventory_sugg)
            
            # Client retention suggestions
            if 'churn_predictions' in predictions:
                retention_sugg = await self.suggest_client_retention(
                    predictions['churn_predictions']
                )
                all_suggestions.extend(retention_sugg)
            
            # Upsell suggestions
            if 'service_patterns' in patterns:
                upsell_sugg = await self.suggest_upsell_services(
                    patterns['service_patterns'],
                    client_history or []
                )
                all_suggestions.extend(upsell_sugg)
            
            # Staffing suggestions
            if 'staffing_predictions' in predictions:
                staffing_sugg = await self.suggest_staffing_optimization(
                    predictions['staffing_predictions']
                )
                all_suggestions.extend(staffing_sugg)
            
            self.suggestions = all_suggestions
            logger.info(f"Total suggestions generated: {len(all_suggestions)}")
            return all_suggestions

        except Exception as e:
            logger.error(f"Suggestion generation failed: {e}")
            return []

    def get_suggestions_by_type(self, suggestion_type: str) -> List[Dict[str, Any]]:
        """Get suggestions by type"""
        return [s for s in self.suggestions if s.get('type') == suggestion_type]

    def get_high_impact_suggestions(self) -> List[Dict[str, Any]]:
        """Get high-impact suggestions"""
        return [s for s in self.suggestions if s.get('impact') == 'high']
