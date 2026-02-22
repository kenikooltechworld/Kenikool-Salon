"""
Package analytics service - Business logic for package analytics and reporting
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PackageAnalyticsService:
    """Service layer for package analytics and reporting"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_sales_metrics(
        self,
        tenant_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get package sales metrics for a tenant
        
        Requirements: 5.1, 16.4
        
        Returns:
            Dict with sales metrics
        """
        try:
            # Default to last 30 days if not specified
            if not end_date:
                end_date = datetime.utcnow()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Get all package purchases in date range
            purchases = list(self.db.package_purchases.find({
                "tenant_id": tenant_id,
                "purchase_date": {
                    "$gte": start_date,
                    "$lte": end_date
                }
            }))
            
            # Calculate metrics
            total_sales = sum(p.get("amount_paid", 0) for p in purchases)
            total_purchases = len(purchases)
            average_purchase_value = total_sales / total_purchases if total_purchases > 0 else 0
            
            # Get package definitions for breakdown
            package_sales = {}
            for purchase in purchases:
                package_def_id = purchase.get("package_definition_id")
                if package_def_id not in package_sales:
                    package_def = self.db.packages.find_one({
                        "_id": ObjectId(package_def_id)
                    })
                    package_sales[package_def_id] = {
                        "package_name": package_def.get("name", "Unknown") if package_def else "Unknown",
                        "total_sales": 0,
                        "total_purchases": 0,
                        "average_value": 0
                    }
                
                package_sales[package_def_id]["total_sales"] += purchase.get("amount_paid", 0)
                package_sales[package_def_id]["total_purchases"] += 1
            
            # Calculate averages
            for package_id in package_sales:
                if package_sales[package_id]["total_purchases"] > 0:
                    package_sales[package_id]["average_value"] = (
                        package_sales[package_id]["total_sales"] / 
                        package_sales[package_id]["total_purchases"]
                    )
            
            return {
                "period": {
                    "start_date": start_date,
                    "end_date": end_date
                },
                "total_sales": total_sales,
                "total_purchases": total_purchases,
                "average_purchase_value": average_purchase_value,
                "package_breakdown": package_sales
            }
        
        except Exception as e:
            logger.error(f"Error getting sales metrics: {e}")
            raise Exception(f"Failed to get sales metrics: {str(e)}")
    
    async def get_redemption_metrics(
        self,
        tenant_id: str,
        package_definition_id: Optional[str] = None
    ) -> Dict:
        """
        Get package redemption metrics
        
        Requirements: 5.2, 16.1
        
        Returns:
            Dict with redemption metrics
        """
        try:
            # Get all package purchases for tenant
            query = {"tenant_id": tenant_id}
            purchases = list(self.db.package_purchases.find(query))
            
            total_packages = len(purchases)
            total_redeemed = 0
            total_credits_purchased = 0
            total_credits_redeemed = 0
            average_redemption_time = 0
            
            redemption_times = []
            
            for purchase in purchases:
                purchase_id = str(purchase["_id"])
                
                # Get service credits for this purchase
                credits = list(self.db.service_credits.find({
                    "purchase_id": purchase_id
                }))
                
                for credit in credits:
                    total_credits_purchased += credit.get("initial_quantity", 0)
                    total_credits_redeemed += (
                        credit.get("initial_quantity", 0) - 
                        credit.get("remaining_quantity", 0)
                    )
                
                # Get redemption transactions
                redemptions = list(self.db.redemption_transactions.find({
                    "purchase_id": purchase_id
                }))
                
                if redemptions:
                    total_redeemed += 1
                    
                    # Calculate time to first redemption
                    first_redemption = min(r.get("redemption_date") for r in redemptions)
                    purchase_date = purchase.get("purchase_date")
                    if first_redemption and purchase_date:
                        time_diff = (first_redemption - purchase_date).total_seconds() / 86400  # Convert to days
                        redemption_times.append(time_diff)
            
            if redemption_times:
                average_redemption_time = sum(redemption_times) / len(redemption_times)
            
            redemption_rate = (total_redeemed / total_packages * 100) if total_packages > 0 else 0
            credit_redemption_rate = (
                (total_credits_redeemed / total_credits_purchased * 100) 
                if total_credits_purchased > 0 else 0
            )
            
            return {
                "total_packages": total_packages,
                "total_redeemed": total_redeemed,
                "redemption_rate": redemption_rate,
                "total_credits_purchased": total_credits_purchased,
                "total_credits_redeemed": total_credits_redeemed,
                "credit_redemption_rate": credit_redemption_rate,
                "average_time_to_redemption_days": average_redemption_time
            }
        
        except Exception as e:
            logger.error(f"Error getting redemption metrics: {e}")
            raise Exception(f"Failed to get redemption metrics: {str(e)}")
    
    async def get_performance_metrics(
        self,
        tenant_id: str
    ) -> Dict:
        """
        Get package performance metrics
        
        Requirements: 16.2, 16.3, 16.5, 16.6
        
        Returns:
            Dict with performance metrics
        """
        try:
            # Get all package purchases
            purchases = list(self.db.package_purchases.find({
                "tenant_id": tenant_id
            }))
            
            total_packages = len(purchases)
            fully_redeemed = 0
            expired_with_unused = 0
            active_packages = 0
            
            total_value_purchased = 0
            total_value_redeemed = 0
            total_value_expired = 0
            
            for purchase in purchases:
                purchase_id = str(purchase["_id"])
                amount_paid = purchase.get("amount_paid", 0)
                total_value_purchased += amount_paid
                
                # Check status
                if purchase.get("status") == "fully_redeemed":
                    fully_redeemed += 1
                    total_value_redeemed += amount_paid
                elif purchase.get("status") == "active":
                    active_packages += 1
                elif purchase.get("status") == "expired":
                    expired_with_unused += 1
                    
                    # Calculate unused value
                    credits = list(self.db.service_credits.find({
                        "purchase_id": purchase_id
                    }))
                    
                    for credit in credits:
                        unused_quantity = credit.get("remaining_quantity", 0)
                        service_price = credit.get("service_price", 0)
                        total_value_expired += unused_quantity * service_price
            
            # Calculate percentages
            fully_redeemed_pct = (fully_redeemed / total_packages * 100) if total_packages > 0 else 0
            expired_pct = (expired_with_unused / total_packages * 100) if total_packages > 0 else 0
            
            # Calculate ROI (revenue from packages vs individual services)
            # This is a simplified calculation
            roi = (total_value_redeemed / total_value_purchased * 100) if total_value_purchased > 0 else 0
            
            return {
                "total_packages": total_packages,
                "fully_redeemed_packages": fully_redeemed,
                "fully_redeemed_percentage": fully_redeemed_pct,
                "active_packages": active_packages,
                "expired_packages_with_unused": expired_with_unused,
                "expired_percentage": expired_pct,
                "total_value_purchased": total_value_purchased,
                "total_value_redeemed": total_value_redeemed,
                "total_value_expired": total_value_expired,
                "roi_percentage": roi
            }
        
        except Exception as e:
            logger.error(f"Error getting performance metrics: {e}")
            raise Exception(f"Failed to get performance metrics: {str(e)}")
    
    async def get_expiration_report(
        self,
        tenant_id: str
    ) -> Dict:
        """
        Get package expiration report
        
        Requirements: 5.5, 6.5
        
        Returns:
            Dict with expiration data
        """
        try:
            now = datetime.utcnow()
            
            # Get all package purchases
            purchases = list(self.db.package_purchases.find({
                "tenant_id": tenant_id
            }))
            
            expired_packages = []
            expiring_soon = []
            active_packages = []
            
            for purchase in purchases:
                purchase_id = str(purchase["_id"])
                expiration_date = purchase.get("expiration_date")
                
                if not expiration_date:
                    continue
                
                # Get package definition
                package_def = self.db.packages.find_one({
                    "_id": ObjectId(purchase.get("package_definition_id"))
                })
                
                # Calculate unused value
                credits = list(self.db.service_credits.find({
                    "purchase_id": purchase_id
                }))
                
                unused_value = 0
                for credit in credits:
                    unused_quantity = credit.get("remaining_quantity", 0)
                    service_price = credit.get("service_price", 0)
                    unused_value += unused_quantity * service_price
                
                package_info = {
                    "purchase_id": purchase_id,
                    "package_name": package_def.get("name", "Unknown") if package_def else "Unknown",
                    "client_id": purchase.get("client_id"),
                    "purchase_date": purchase.get("purchase_date"),
                    "expiration_date": expiration_date,
                    "amount_paid": purchase.get("amount_paid", 0),
                    "unused_value": unused_value,
                    "status": purchase.get("status")
                }
                
                if expiration_date < now:
                    expired_packages.append(package_info)
                elif expiration_date - now <= timedelta(days=7):
                    expiring_soon.append(package_info)
                else:
                    active_packages.append(package_info)
            
            total_expired_value = sum(p.get("unused_value", 0) for p in expired_packages)
            expiration_rate = (
                (len(expired_packages) / len(purchases) * 100) 
                if len(purchases) > 0 else 0
            )
            
            return {
                "expired_packages": expired_packages,
                "total_expired": len(expired_packages),
                "total_expired_value": total_expired_value,
                "expiring_soon_packages": expiring_soon,
                "total_expiring_soon": len(expiring_soon),
                "active_packages": active_packages,
                "total_active": len(active_packages),
                "expiration_rate_percentage": expiration_rate
            }
        
        except Exception as e:
            logger.error(f"Error getting expiration report: {e}")
            raise Exception(f"Failed to get expiration report: {str(e)}")
    
    async def get_package_roi(
        self,
        tenant_id: str,
        package_definition_id: str
    ) -> Dict:
        """
        Get ROI metrics for a specific package
        
        Requirements: 16.6
        
        Returns:
            Dict with ROI metrics
        """
        try:
            # Get package definition
            package_def = self.db.packages.find_one({
                "_id": ObjectId(package_definition_id),
                "tenant_id": tenant_id
            })
            
            if not package_def:
                raise ValueError("Package definition not found")
            
            # Get all purchases of this package
            purchases = list(self.db.package_purchases.find({
                "package_definition_id": package_definition_id,
                "tenant_id": tenant_id
            }))
            
            total_purchases = len(purchases)
            total_revenue = sum(p.get("amount_paid", 0) for p in purchases)
            
            # Calculate individual service cost
            services = package_def.get("services", [])
            individual_service_cost = 0
            
            for service_item in services:
                service_id = service_item.get("service_id")
                quantity = service_item.get("quantity", 1)
                
                service = self.db.services.find_one({
                    "_id": ObjectId(service_id)
                })
                
                if service:
                    individual_service_cost += service.get("price", 0) * quantity
            
            # Calculate metrics
            package_price = package_def.get("package_price", 0)
            savings_per_package = individual_service_cost - package_price
            total_savings = savings_per_package * total_purchases
            
            # Calculate redemption value
            total_redeemed_value = 0
            for purchase in purchases:
                purchase_id = str(purchase["_id"])
                redemptions = list(self.db.redemption_transactions.find({
                    "purchase_id": purchase_id
                }))
                
                for redemption in redemptions:
                    total_redeemed_value += redemption.get("service_value", 0)
            
            # ROI calculation
            roi = ((total_redeemed_value - total_revenue) / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                "package_id": package_definition_id,
                "package_name": package_def.get("name", "Unknown"),
                "total_purchases": total_purchases,
                "total_revenue": total_revenue,
                "individual_service_cost": individual_service_cost,
                "package_price": package_price,
                "savings_per_package": savings_per_package,
                "total_savings": total_savings,
                "total_redeemed_value": total_redeemed_value,
                "roi_percentage": roi
            }
        
        except ValueError as e:
            raise e
        except Exception as e:
            logger.error(f"Error getting package ROI: {e}")
            raise Exception(f"Failed to get package ROI: {str(e)}")
