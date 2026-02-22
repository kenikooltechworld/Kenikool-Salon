"""
Package Recommendation Service - Provides package recommendations based on client booking history
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from bson import ObjectId
import logging

logger = logging.getLogger(__name__)


class PackageRecommendationService:
    """Service for generating package recommendations for clients"""
    
    def __init__(self, db):
        self.db = db
    
    async def get_recommendations_for_client(
        self,
        client_id: str,
        tenant_id: str,
        limit: int = 5
    ) -> List[Dict]:
        """
        Get recommended packages for a client based on their booking history
        
        Requirements: 19.1, 19.2, 19.5
        Properties: 29 (Recommendation Relevance)
        
        Args:
            client_id: Client ID
            tenant_id: Tenant ID
            limit: Maximum number of recommendations to return
            
        Returns:
            List of recommended packages with savings information
        """
        try:
            # Get client's booking history
            bookings = list(self.db.bookings.find({
                "client_id": client_id,
                "tenant_id": tenant_id,
                "status": {"$in": ["completed", "confirmed"]}
            }).sort("booking_date", -1).limit(50))
            
            if not bookings:
                # If no booking history, recommend popular starter packages
                return await self.get_popular_packages(tenant_id, limit)
            
            # Extract services from booking history
            service_frequency = {}
            for booking in bookings:
                service_id = booking.get("service_id")
                if service_id:
                    service_frequency[service_id] = service_frequency.get(service_id, 0) + 1
            
            # Get all active packages for tenant
            packages = list(self.db.packages.find({
                "tenant_id": tenant_id,
                "is_active": True
            }))
            
            # Score packages based on service overlap with booking history
            recommendations = []
            
            for package in packages:
                # Check if client already owns this package
                existing_purchase = self.db.package_purchases.find_one({
                    "client_id": client_id,
                    "package_definition_id": str(package["_id"]),
                    "status": {"$in": ["active", "fully_redeemed"]}
                })
                
                if existing_purchase:
                    continue  # Skip packages already owned
                
                # Calculate relevance score based on service overlap
                package_services = package.get("services", [])
                relevance_score = 0
                matching_services = []
                
                for service_item in package_services:
                    service_id = service_item.get("service_id")
                    if service_id in service_frequency:
                        # Weight by frequency and quantity
                        relevance_score += service_frequency[service_id] * service_item.get("quantity", 1)
                        matching_services.append({
                            "service_id": service_id,
                            "frequency": service_frequency[service_id],
                            "quantity": service_item.get("quantity", 1)
                        })
                
                # Only include packages with at least one matching service
                if relevance_score > 0:
                    # Calculate potential savings
                    savings = await self.calculate_potential_savings(
                        client_id,
                        str(package["_id"]),
                        tenant_id
                    )
                    
                    recommendations.append({
                        "package_id": str(package["_id"]),
                        "package_name": package.get("name"),
                        "description": package.get("description"),
                        "package_price": package.get("package_price"),
                        "original_price": package.get("original_price"),
                        "discount_percentage": package.get("discount_percentage"),
                        "validity_days": package.get("validity_days"),
                        "potential_savings": savings,
                        "relevance_score": relevance_score,
                        "matching_services": matching_services,
                        "services": [
                            {
                                "service_id": s.get("service_id"),
                                "quantity": s.get("quantity", 1)
                            }
                            for s in package_services
                        ]
                    })
            
            # Sort by relevance score (highest first) and then by potential savings
            recommendations.sort(
                key=lambda x: (-x["relevance_score"], -x["potential_savings"])
            )
            
            return recommendations[:limit]
        
        except Exception as e:
            logger.error(f"Error getting recommendations for client {client_id}: {e}")
            raise Exception(f"Failed to get recommendations: {str(e)}")
    
    async def calculate_potential_savings(
        self,
        client_id: str,
        package_definition_id: str,
        tenant_id: str
    ) -> float:
        """
        Calculate potential savings for a package recommendation
        
        Requirements: 19.3
        Properties: 30 (Savings Calculation)
        
        Args:
            client_id: Client ID
            package_definition_id: Package definition ID
            tenant_id: Tenant ID
            
        Returns:
            Potential savings amount
        """
        try:
            # Get package definition
            package = self.db.packages.find_one({
                "_id": ObjectId(package_definition_id),
                "tenant_id": tenant_id
            })
            
            if not package:
                return 0.0
            
            # Calculate individual service cost
            services = package.get("services", [])
            individual_service_cost = 0.0
            
            for service_item in services:
                service_id = service_item.get("service_id")
                quantity = service_item.get("quantity", 1)
                
                service = self.db.services.find_one({
                    "_id": ObjectId(service_id)
                })
                
                if service:
                    individual_service_cost += service.get("price", 0) * quantity
            
            # Calculate savings
            package_price = package.get("package_price", 0)
            savings = individual_service_cost - package_price
            
            return max(0.0, savings)  # Return 0 if no savings
        
        except Exception as e:
            logger.error(f"Error calculating savings for package {package_definition_id}: {e}")
            return 0.0
    
    async def get_popular_packages(
        self,
        tenant_id: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Get popular starter packages for clients with no booking history
        
        Requirements: 19.4
        
        Args:
            tenant_id: Tenant ID
            limit: Maximum number of packages to return
            
        Returns:
            List of popular packages
        """
        try:
            # Get all active packages
            packages = list(self.db.packages.find({
                "tenant_id": tenant_id,
                "is_active": True
            }))
            
            # Score packages by popularity (number of purchases)
            package_scores = []
            
            for package in packages:
                # Count purchases
                purchase_count = self.db.package_purchases.count_documents({
                    "package_definition_id": str(package["_id"]),
                    "tenant_id": tenant_id
                })
                
                # Count redemptions
                redemption_count = self.db.redemption_transactions.count_documents({
                    "tenant_id": tenant_id
                })
                
                # Calculate popularity score
                popularity_score = purchase_count * 2 + redemption_count
                
                # Get package services
                package_services = package.get("services", [])
                
                package_scores.append({
                    "package_id": str(package["_id"]),
                    "package_name": package.get("name"),
                    "description": package.get("description"),
                    "package_price": package.get("package_price"),
                    "original_price": package.get("original_price"),
                    "discount_percentage": package.get("discount_percentage"),
                    "validity_days": package.get("validity_days"),
                    "popularity_score": popularity_score,
                    "purchase_count": purchase_count,
                    "services": [
                        {
                            "service_id": s.get("service_id"),
                            "quantity": s.get("quantity", 1)
                        }
                        for s in package_services
                    ]
                })
            
            # Sort by popularity score (highest first)
            package_scores.sort(key=lambda x: -x["popularity_score"])
            
            return package_scores[:limit]
        
        except Exception as e:
            logger.error(f"Error getting popular packages for tenant {tenant_id}: {e}")
            raise Exception(f"Failed to get popular packages: {str(e)}")
