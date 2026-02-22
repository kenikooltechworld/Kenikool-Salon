import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class InsightGenerator:
    """Generates business insights from data"""

    def __init__(self):
        """Initialize insight generator"""
        self.insights = []

    async def generate_performance_insights(
        self,
        revenue_patterns: Dict[str, Any],
        staff_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate performance insights"""
        try:
            insights = []
            
            # Revenue insights
            if 'daily_revenue_avg' in revenue_patterns:
                daily_avg = revenue_patterns['daily_revenue_avg']
                insights.append({
                    "type": "performance",
                    "category": "revenue",
                    "title": "Daily Revenue Performance",
                    "description": f"Average daily revenue is ${daily_avg:.2f}",
                    "metric": daily_avg,
                    "trend": "stable",
                    "actionable": True
                })
            
            # Staff performance insights
            if 'top_performers' in staff_patterns:
                top_performers = staff_patterns['top_performers']
                if top_performers:
                    insights.append({
                        "type": "performance",
                        "category": "staff",
                        "title": "Top Performing Stylists",
                        "description": f"Your top stylists are driving {len(top_performers)} of your revenue",
                        "performers": top_performers,
                        "actionable": True
                    })
            
            logger.info(f"Performance insights generated: {len(insights)}")
            return insights

        except Exception as e:
            logger.error(f"Performance insight generation failed: {e}")
            return []

    async def generate_opportunity_insights(
        self,
        booking_patterns: Dict[str, Any],
        service_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate opportunity insights"""
        try:
            insights = []
            
            # Booking opportunity
            if 'peak_hours' in booking_patterns:
                peak_hours = booking_patterns['peak_hours']
                insights.append({
                    "type": "opportunity",
                    "category": "booking",
                    "title": "Peak Hour Opportunity",
                    "description": f"Peak booking hours are {peak_hours}. Consider staffing optimization.",
                    "peak_hours": peak_hours,
                    "potential_revenue_increase": "15-20%",
                    "actionable": True
                })
            
            # Service opportunity
            if 'most_popular_services' in service_patterns:
                popular = service_patterns['most_popular_services']
                if popular:
                    insights.append({
                        "type": "opportunity",
                        "category": "service",
                        "title": "Popular Service Opportunity",
                        "description": f"Your most popular services are {[s.get('service') for s in popular[:3]]}",
                        "popular_services": popular,
                        "potential_revenue_increase": "10-15%",
                        "actionable": True
                    })
            
            logger.info(f"Opportunity insights generated: {len(insights)}")
            return insights

        except Exception as e:
            logger.error(f"Opportunity insight generation failed: {e}")
            return []

    async def generate_risk_insights(
        self,
        churn_predictions: Dict[str, Any],
        inventory_patterns: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate risk insights"""
        try:
            insights = []
            
            # Churn risk
            if 'high_risk_count' in churn_predictions:
                high_risk = churn_predictions['high_risk_count']
                if high_risk > 0:
                    insights.append({
                        "type": "risk",
                        "category": "client_churn",
                        "title": "Client Churn Risk",
                        "description": f"{high_risk} clients are at high risk of churning",
                        "at_risk_count": high_risk,
                        "potential_revenue_loss": f"${high_risk * 150:.2f}",
                        "severity": "high",
                        "actionable": True,
                        "recommended_action": "Implement retention campaign"
                    })
            
            # Inventory risk
            if 'low_stock_items' in inventory_patterns:
                low_stock = inventory_patterns['low_stock_items']
                if low_stock:
                    insights.append({
                        "type": "risk",
                        "category": "inventory",
                        "title": "Low Stock Risk",
                        "description": f"{len(low_stock)} items are running low on stock",
                        "items": low_stock,
                        "severity": "medium",
                        "actionable": True,
                        "recommended_action": "Place reorder immediately"
                    })
            
            logger.info(f"Risk insights generated: {len(insights)}")
            return insights

        except Exception as e:
            logger.error(f"Risk insight generation failed: {e}")
            return []

    async def generate_natural_language_insights(
        self,
        all_insights: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate natural language insight summaries"""
        try:
            summaries = []
            
            for insight in all_insights:
                if insight.get('type') == 'performance':
                    if insight.get('category') == 'revenue':
                        summary = f"Your salon is performing well with an average daily revenue of ${insight.get('metric', 0):.2f}."
                        summaries.append(summary)
                    elif insight.get('category') == 'staff':
                        summary = f"Your top stylists are key revenue drivers. Consider investing in their development."
                        summaries.append(summary)
                
                elif insight.get('type') == 'opportunity':
                    if insight.get('category') == 'booking':
                        summary = f"You have an opportunity to increase revenue by 15-20% by optimizing peak hour staffing."
                        summaries.append(summary)
                    elif insight.get('category') == 'service':
                        summary = f"Your popular services are driving demand. Consider expanding these offerings."
                        summaries.append(summary)
                
                elif insight.get('type') == 'risk':
                    if insight.get('category') == 'client_churn':
                        summary = f"Alert: {insight.get('at_risk_count', 0)} clients are at risk of leaving. Take action now."
                        summaries.append(summary)
                    elif insight.get('category') == 'inventory':
                        summary = f"Warning: {len(insight.get('items', []))} items are running low. Reorder soon."
                        summaries.append(summary)
            
            logger.info(f"Natural language insights generated: {len(summaries)}")
            return summaries

        except Exception as e:
            logger.error(f"Natural language insight generation failed: {e}")
            return []

    async def generate_all_insights(
        self,
        patterns: Dict[str, Any],
        predictions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate all insights"""
        try:
            all_insights = []
            
            # Performance insights
            if 'revenue_patterns' in patterns and 'staff_patterns' in patterns:
                perf_insights = await self.generate_performance_insights(
                    patterns['revenue_patterns'],
                    patterns['staff_patterns']
                )
                all_insights.extend(perf_insights)
            
            # Opportunity insights
            if 'booking_patterns' in patterns and 'service_patterns' in patterns:
                opp_insights = await self.generate_opportunity_insights(
                    patterns['booking_patterns'],
                    patterns['service_patterns']
                )
                all_insights.extend(opp_insights)
            
            # Risk insights
            if 'churn_predictions' in predictions and 'inventory_patterns' in patterns:
                risk_insights = await self.generate_risk_insights(
                    predictions.get('churn_predictions', {}),
                    patterns['inventory_patterns']
                )
                all_insights.extend(risk_insights)
            
            # Natural language summaries
            summaries = await self.generate_natural_language_insights(all_insights)
            
            self.insights = all_insights
            
            result = {
                "insights": all_insights,
                "summaries": summaries,
                "total_insights": len(all_insights),
                "performance_insights": len([i for i in all_insights if i.get('type') == 'performance']),
                "opportunity_insights": len([i for i in all_insights if i.get('type') == 'opportunity']),
                "risk_insights": len([i for i in all_insights if i.get('type') == 'risk'])
            }
            
            logger.info(f"All insights generated: {result}")
            return result

        except Exception as e:
            logger.error(f"Insight generation failed: {e}")
            return {"error": str(e)}

    def get_insights_by_type(self, insight_type: str) -> List[Dict[str, Any]]:
        """Get insights by type"""
        return [i for i in self.insights if i.get('type') == insight_type]

    def get_actionable_insights(self) -> List[Dict[str, Any]]:
        """Get actionable insights"""
        return [i for i in self.insights if i.get('actionable', False)]
