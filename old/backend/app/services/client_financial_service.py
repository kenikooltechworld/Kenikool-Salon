"""
Client Financial Service
Handles financial analytics and summaries for clients
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from bson import ObjectId
from app.database import Database


class ClientFinancialService:
    """Service for managing client financial data and analytics"""

    @staticmethod
    def get_financial_summary(client_id: str, tenant_id: str) -> Optional[Dict[str, Any]]:
        """
        Get comprehensive financial summary for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            Financial summary dictionary or None if client not found
        """
        db = Database.get_db()
        
        # Verify client exists
        client = db.clients.find_one({
            "_id": ObjectId(client_id),
            "tenant_id": tenant_id
        })
        
        if not client:
            return None
        
        # Get all completed bookings for this client
        bookings = list(db.bookings.find({
            "client_id": client_id,
            "tenant_id": tenant_id,
            "status": "completed"
        }).sort("booking_date", -1))
        
        if not bookings:
            return {
                "client_id": client_id,
                "total_revenue": 0,
                "average_transaction": 0,
                "transaction_count": 0,
                "revenue_by_month": [],
                "revenue_by_service_category": [],
                "payment_method_preferences": {},
                "tip_average": 0,
                "tip_total": 0,
                "last_transaction_date": None,
                "first_transaction_date": None
            }
        
        # Calculate basic metrics
        total_revenue = sum(b.get("total_price", 0) for b in bookings)
        transaction_count = len(bookings)
        average_transaction = total_revenue / transaction_count if transaction_count > 0 else 0
        
        # Calculate tip metrics
        tip_total = sum(b.get("tip_amount", 0) for b in bookings)
        tip_average = tip_total / transaction_count if transaction_count > 0 else 0
        
        # Get date range
        last_transaction_date = bookings[0].get("booking_date") if bookings else None
        first_transaction_date = bookings[-1].get("booking_date") if bookings else None
        
        # Calculate revenue by month (last 12 months)
        revenue_by_month = ClientFinancialService._calculate_revenue_by_month(bookings)
        
        # Calculate revenue by service category
        revenue_by_service_category = ClientFinancialService._calculate_revenue_by_category(
            bookings, tenant_id
        )
        
        # Calculate payment method preferences
        payment_method_preferences = ClientFinancialService._calculate_payment_preferences(bookings)
        
        return {
            "client_id": client_id,
            "total_revenue": round(total_revenue, 2),
            "average_transaction": round(average_transaction, 2),
            "transaction_count": transaction_count,
            "revenue_by_month": revenue_by_month,
            "revenue_by_service_category": revenue_by_service_category,
            "payment_method_preferences": payment_method_preferences,
            "tip_average": round(tip_average, 2),
            "tip_total": round(tip_total, 2),
            "last_transaction_date": last_transaction_date,
            "first_transaction_date": first_transaction_date
        }
    
    @staticmethod
    def _calculate_revenue_by_month(bookings: List[Dict]) -> List[Dict[str, Any]]:
        """Calculate revenue grouped by month for last 12 months"""
        now = datetime.now()
        twelve_months_ago = now - timedelta(days=365)
        
        # Initialize month buckets
        month_revenue = {}
        for i in range(12):
            month_date = now - timedelta(days=30 * i)
            month_key = month_date.strftime("%Y-%m")
            month_revenue[month_key] = {
                "month": month_key,
                "month_name": month_date.strftime("%B %Y"),
                "revenue": 0,
                "transaction_count": 0
            }
        
        # Aggregate bookings by month
        for booking in bookings:
            booking_date = booking.get("booking_date")
            if not booking_date or booking_date < twelve_months_ago:
                continue
            
            month_key = booking_date.strftime("%Y-%m")
            if month_key in month_revenue:
                month_revenue[month_key]["revenue"] += booking.get("total_price", 0)
                month_revenue[month_key]["transaction_count"] += 1
        
        # Convert to sorted list
        result = sorted(month_revenue.values(), key=lambda x: x["month"], reverse=True)
        
        # Round revenue values
        for item in result:
            item["revenue"] = round(item["revenue"], 2)
        
        return result
    
    @staticmethod
    def _calculate_revenue_by_category(bookings: List[Dict], tenant_id: str) -> List[Dict[str, Any]]:
        """Calculate revenue grouped by service category"""
        db = Database.get_db()
        category_revenue = {}
        
        for booking in bookings:
            service_ids = booking.get("service_ids", [])
            booking_revenue = booking.get("total_price", 0)
            
            if not service_ids:
                continue
            
            # Get services for this booking
            services = list(db.services.find({
                "_id": {"$in": [ObjectId(sid) if isinstance(sid, str) else sid for sid in service_ids]},
                "tenant_id": tenant_id
            }))
            
            # Distribute revenue across services
            revenue_per_service = booking_revenue / len(service_ids) if service_ids else 0
            
            for service in services:
                category = service.get("category", "Uncategorized")
                
                if category not in category_revenue:
                    category_revenue[category] = {
                        "category": category,
                        "revenue": 0,
                        "transaction_count": 0
                    }
                
                category_revenue[category]["revenue"] += revenue_per_service
                category_revenue[category]["transaction_count"] += 1
        
        # Convert to sorted list
        result = sorted(
            category_revenue.values(),
            key=lambda x: x["revenue"],
            reverse=True
        )
        
        # Round revenue values
        for item in result:
            item["revenue"] = round(item["revenue"], 2)
        
        return result
    
    @staticmethod
    def _calculate_payment_preferences(bookings: List[Dict]) -> Dict[str, Any]:
        """Calculate payment method usage statistics"""
        payment_methods = {}
        
        for booking in bookings:
            method = booking.get("payment_method", "Unknown")
            
            if method not in payment_methods:
                payment_methods[method] = {
                    "method": method,
                    "count": 0,
                    "total_amount": 0
                }
            
            payment_methods[method]["count"] += 1
            payment_methods[method]["total_amount"] += booking.get("total_price", 0)
        
        # Calculate percentages and round amounts
        total_transactions = sum(pm["count"] for pm in payment_methods.values())
        
        for method_data in payment_methods.values():
            method_data["percentage"] = round(
                (method_data["count"] / total_transactions * 100) if total_transactions > 0 else 0,
                1
            )
            method_data["total_amount"] = round(method_data["total_amount"], 2)
        
        return payment_methods
    
    @staticmethod
    def get_package_history(client_id: str, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Get package purchase history for a client
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            
        Returns:
            List of package purchases with usage tracking
        """
        db = Database.get_db()
        
        # Get package purchases from bookings or dedicated package_purchases collection
        packages = list(db.package_purchases.find({
            "client_id": client_id,
            "tenant_id": tenant_id
        }).sort("purchase_date", -1))
        
        result = []
        for package in packages:
            package_id = package.get("package_id")
            
            # Get package details
            package_details = db.service_packages.find_one({
                "_id": ObjectId(package_id) if isinstance(package_id, str) else package_id,
                "tenant_id": tenant_id
            })
            
            if not package_details:
                continue
            
            result.append({
                "purchase_id": str(package["_id"]),
                "package_id": str(package_id),
                "package_name": package_details.get("name", "Unknown Package"),
                "purchase_date": package.get("purchase_date"),
                "expiry_date": package.get("expiry_date"),
                "total_sessions": package.get("total_sessions", 0),
                "used_sessions": package.get("used_sessions", 0),
                "remaining_sessions": package.get("total_sessions", 0) - package.get("used_sessions", 0),
                "purchase_price": package.get("purchase_price", 0),
                "status": package.get("status", "active")
            })
        
        return result
