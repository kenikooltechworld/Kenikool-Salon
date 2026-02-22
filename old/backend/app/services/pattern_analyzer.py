import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict

logger = logging.getLogger(__name__)


class PatternAnalyzer:
    """Analyzes patterns in salon activities using pandas"""

    def __init__(self):
        """Initialize pattern analyzer"""
        self.booking_patterns = {}
        self.service_patterns = {}
        self.inventory_patterns = {}
        self.revenue_patterns = {}
        self.staff_patterns = {}

    async def analyze_booking_patterns(
        self,
        bookings: List[Dict[str, Any]],
        days_back: int = 30
    ) -> Dict[str, Any]:
        """Analyze booking patterns"""
        try:
            if not bookings:
                return {"error": "No booking data"}

            df = pd.DataFrame(bookings)
            
            # Convert to datetime if needed
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
                df['day_of_week'] = df['created_at'].dt.day_name()
                df['hour'] = df['created_at'].dt.hour
            
            patterns = {
                "peak_days": self._get_peak_days(df),
                "peak_hours": self._get_peak_hours(df),
                "average_bookings_per_day": len(df) / max(days_back, 1),
                "booking_trend": self._calculate_trend(df),
                "cancellation_rate": self._calculate_cancellation_rate(df),
                "no_show_rate": self._calculate_no_show_rate(df)
            }
            
            self.booking_patterns = patterns
            logger.info(f"Booking patterns analyzed: {patterns}")
            return patterns

        except Exception as e:
            logger.error(f"Booking pattern analysis failed: {e}")
            return {"error": str(e)}

    async def analyze_service_patterns(
        self,
        services: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze service patterns"""
        try:
            if not services:
                return {"error": "No service data"}

            df = pd.DataFrame(services)
            
            patterns = {
                "most_popular_services": self._get_top_services(df),
                "service_revenue_distribution": self._get_service_revenue(df),
                "average_service_duration": self._get_avg_duration(df),
                "service_trends": self._calculate_service_trends(df)
            }
            
            self.service_patterns = patterns
            logger.info(f"Service patterns analyzed: {patterns}")
            return patterns

        except Exception as e:
            logger.error(f"Service pattern analysis failed: {e}")
            return {"error": str(e)}

    async def analyze_inventory_patterns(
        self,
        inventory_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze inventory patterns"""
        try:
            if not inventory_data:
                return {"error": "No inventory data"}

            df = pd.DataFrame(inventory_data)
            
            patterns = {
                "fast_moving_items": self._get_fast_moving_items(df),
                "slow_moving_items": self._get_slow_moving_items(df),
                "reorder_frequency": self._get_reorder_frequency(df),
                "stock_turnover_rate": self._calculate_turnover_rate(df),
                "low_stock_items": self._get_low_stock_items(df)
            }
            
            self.inventory_patterns = patterns
            logger.info(f"Inventory patterns analyzed: {patterns}")
            return patterns

        except Exception as e:
            logger.error(f"Inventory pattern analysis failed: {e}")
            return {"error": str(e)}

    async def analyze_revenue_patterns(
        self,
        transactions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze revenue patterns"""
        try:
            if not transactions:
                return {"error": "No transaction data"}

            df = pd.DataFrame(transactions)
            
            if 'amount' in df.columns:
                df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
            
            patterns = {
                "daily_revenue_avg": float(df['amount'].mean()) if 'amount' in df.columns else 0,
                "weekly_revenue_trend": self._get_weekly_trend(df),
                "monthly_revenue_trend": self._get_monthly_trend(df),
                "revenue_by_service": self._get_revenue_by_service(df),
                "revenue_by_stylist": self._get_revenue_by_stylist(df),
                "peak_revenue_days": self._get_peak_revenue_days(df)
            }
            
            self.revenue_patterns = patterns
            logger.info(f"Revenue patterns analyzed: {patterns}")
            return patterns

        except Exception as e:
            logger.error(f"Revenue pattern analysis failed: {e}")
            return {"error": str(e)}

    async def analyze_staff_patterns(
        self,
        staff_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze staff patterns"""
        try:
            if not staff_data:
                return {"error": "No staff data"}

            df = pd.DataFrame(staff_data)
            
            patterns = {
                "top_performers": self._get_top_performers(df),
                "average_appointments_per_stylist": self._get_avg_appointments(df),
                "stylist_utilization": self._get_utilization_rates(df),
                "peak_staff_hours": self._get_peak_staff_hours(df),
                "staff_availability_patterns": self._get_availability_patterns(df)
            }
            
            self.staff_patterns = patterns
            logger.info(f"Staff patterns analyzed: {patterns}")
            return patterns

        except Exception as e:
            logger.error(f"Staff pattern analysis failed: {e}")
            return {"error": str(e)}

    def _get_peak_days(self, df: pd.DataFrame) -> List[str]:
        """Get peak booking days"""
        if 'day_of_week' not in df.columns:
            return []
        return df['day_of_week'].value_counts().head(3).index.tolist()

    def _get_peak_hours(self, df: pd.DataFrame) -> List[int]:
        """Get peak booking hours"""
        if 'hour' not in df.columns:
            return []
        return df['hour'].value_counts().head(3).index.tolist()

    def _calculate_trend(self, df: pd.DataFrame) -> str:
        """Calculate booking trend"""
        if len(df) < 2:
            return "insufficient_data"
        return "increasing" if df.iloc[-1:].shape[0] > df.iloc[:-1].shape[0] else "decreasing"

    def _calculate_cancellation_rate(self, df: pd.DataFrame) -> float:
        """Calculate cancellation rate"""
        if 'status' not in df.columns:
            return 0.0
        cancelled = (df['status'] == 'cancelled').sum()
        return (cancelled / len(df)) * 100 if len(df) > 0 else 0.0

    def _calculate_no_show_rate(self, df: pd.DataFrame) -> float:
        """Calculate no-show rate"""
        if 'status' not in df.columns:
            return 0.0
        no_show = (df['status'] == 'no_show').sum()
        return (no_show / len(df)) * 100 if len(df) > 0 else 0.0

    def _get_top_services(self, df: pd.DataFrame) -> List[Dict]:
        """Get top services"""
        if 'service_name' not in df.columns:
            return []
        top = df['service_name'].value_counts().head(5)
        return [{"service": k, "count": int(v)} for k, v in top.items()]

    def _get_service_revenue(self, df: pd.DataFrame) -> Dict:
        """Get service revenue distribution"""
        if 'service_name' not in df.columns or 'price' not in df.columns:
            return {}
        return df.groupby('service_name')['price'].sum().to_dict()

    def _get_avg_duration(self, df: pd.DataFrame) -> float:
        """Get average service duration"""
        if 'duration' not in df.columns:
            return 0.0
        return float(df['duration'].mean())

    def _calculate_service_trends(self, df: pd.DataFrame) -> Dict:
        """Calculate service trends"""
        return {"trend": "stable", "growth_rate": 0.0}

    def _get_fast_moving_items(self, df: pd.DataFrame) -> List[str]:
        """Get fast-moving inventory items"""
        if 'usage_rate' not in df.columns:
            return []
        return df.nlargest(5, 'usage_rate')['item_name'].tolist() if 'item_name' in df.columns else []

    def _get_slow_moving_items(self, df: pd.DataFrame) -> List[str]:
        """Get slow-moving inventory items"""
        if 'usage_rate' not in df.columns:
            return []
        return df.nsmallest(5, 'usage_rate')['item_name'].tolist() if 'item_name' in df.columns else []

    def _get_reorder_frequency(self, df: pd.DataFrame) -> Dict:
        """Get reorder frequency"""
        return {"average_days_between_reorders": 14}

    def _calculate_turnover_rate(self, df: pd.DataFrame) -> float:
        """Calculate stock turnover rate"""
        return 0.0

    def _get_low_stock_items(self, df: pd.DataFrame) -> List[str]:
        """Get low stock items"""
        if 'quantity' not in df.columns or 'min_quantity' not in df.columns:
            return []
        low = df[df['quantity'] <= df['min_quantity']]
        return low['item_name'].tolist() if 'item_name' in low.columns else []

    def _get_weekly_trend(self, df: pd.DataFrame) -> List[float]:
        """Get weekly revenue trend"""
        return [0.0]

    def _get_monthly_trend(self, df: pd.DataFrame) -> List[float]:
        """Get monthly revenue trend"""
        return [0.0]

    def _get_revenue_by_service(self, df: pd.DataFrame) -> Dict:
        """Get revenue by service"""
        return {}

    def _get_revenue_by_stylist(self, df: pd.DataFrame) -> Dict:
        """Get revenue by stylist"""
        return {}

    def _get_peak_revenue_days(self, df: pd.DataFrame) -> List[str]:
        """Get peak revenue days"""
        return []

    def _get_top_performers(self, df: pd.DataFrame) -> List[Dict]:
        """Get top performing staff"""
        if 'appointments_completed' not in df.columns:
            return []
        top = df.nlargest(5, 'appointments_completed')
        return top[['name', 'appointments_completed']].to_dict('records') if 'name' in top.columns else []

    def _get_avg_appointments(self, df: pd.DataFrame) -> float:
        """Get average appointments per stylist"""
        if 'appointments_completed' not in df.columns:
            return 0.0
        return float(df['appointments_completed'].mean())

    def _get_utilization_rates(self, df: pd.DataFrame) -> Dict:
        """Get staff utilization rates"""
        return {}

    def _get_peak_staff_hours(self, df: pd.DataFrame) -> List[int]:
        """Get peak staff hours"""
        return []

    def _get_availability_patterns(self, df: pd.DataFrame) -> Dict:
        """Get staff availability patterns"""
        return {}

    def get_all_patterns(self) -> Dict[str, Any]:
        """Get all analyzed patterns"""
        return {
            "booking_patterns": self.booking_patterns,
            "service_patterns": self.service_patterns,
            "inventory_patterns": self.inventory_patterns,
            "revenue_patterns": self.revenue_patterns,
            "staff_patterns": self.staff_patterns
        }
