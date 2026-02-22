"""
Unit tests for Package Recommendation Service
Tests package recommendations based on booking history and savings calculations
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import MagicMock, AsyncMock, patch

from app.services.package_recommendation_service import PackageRecommendationService


class TestPackageRecommendationService:
    """Tests for PackageRecommendationService"""
    
    @pytest.mark.asyncio
    async def test_get_recommendations_with_booking_history(self):
        """Test getting recommendations for client with booking history"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        client_id = str(ObjectId())
        tenant_id = "test_tenant"
        service_id_1 = str(ObjectId())
        service_id_2 = str(ObjectId())
        package_id = str(ObjectId())
        
        # Mock bookings
        mock_bookings = [
            {
                "_id": ObjectId(),
                "client_id": client_id,
                "service_id": service_id_1,
                "booking_date": datetime.utcnow(),
                "status": "completed"
            },
            {
                "_id": ObjectId(),
                "client_id": client_id,
                "service_id": service_id_1,
                "booking_date": datetime.utcnow(),
                "status": "completed"
            },
            {
                "_id": ObjectId(),
                "client_id": client_id,
                "service_id": service_id_2,
                "booking_date": datetime.utcnow(),
                "status": "completed"
            }
        ]
        
        # Mock packages
        mock_packages = [
            {
                "_id": ObjectId(package_id),
                "tenant_id": tenant_id,
                "name": "Hair Package",
                "description": "3 haircuts + 2 treatments",
                "is_active": True,
                "package_price": 150.0,
                "original_price": 200.0,
                "discount_percentage": 25,
                "validity_days": 30,
                "services": [
                    {"service_id": service_id_1, "quantity": 3},
                    {"service_id": service_id_2, "quantity": 2}
                ]
            }
        ]
        
        # Setup mock returns
        mock_db.bookings.find.return_value.sort.return_value.limit.return_value = mock_bookings
        mock_db.packages.find.return_value = mock_packages
        mock_db.package_purchases.find_one.return_value = None  # No existing purchase
        
        # Mock services for savings calculation
        def services_find_one(query):
            service_id = query.get("_id")
            if service_id == ObjectId(service_id_1):
                return {"_id": ObjectId(service_id_1), "price": 50.0}
            elif service_id == ObjectId(service_id_2):
                return {"_id": ObjectId(service_id_2), "price": 40.0}
            return None
        
        mock_db.services.find_one.side_effect = services_find_one
        
        # Mock calculate_potential_savings to return a fixed value
        with patch.object(service, 'calculate_potential_savings', new_callable=AsyncMock) as mock_savings:
            mock_savings.return_value = 40.0
            
            # Execute
            recommendations = await service.get_recommendations_for_client(
                client_id=client_id,
                tenant_id=tenant_id,
                limit=5
            )
            
            # Assert
            assert len(recommendations) > 0
            assert recommendations[0]["package_id"] == package_id
            assert recommendations[0]["package_name"] == "Hair Package"
            assert recommendations[0]["potential_savings"] == 40.0
            assert len(recommendations[0]["matching_services"]) == 2
    
    @pytest.mark.asyncio
    async def test_get_recommendations_no_booking_history(self):
        """Test getting popular packages when client has no booking history"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        client_id = str(ObjectId())
        tenant_id = "test_tenant"
        package_id = str(ObjectId())
        
        # Mock empty bookings
        mock_db.bookings.find.return_value.sort.return_value.limit.return_value = []
        
        # Mock packages
        mock_packages = [
            {
                "_id": ObjectId(package_id),
                "tenant_id": tenant_id,
                "name": "Starter Package",
                "description": "Perfect for new clients",
                "is_active": True,
                "package_price": 100.0,
                "original_price": 150.0,
                "discount_percentage": 33,
                "validity_days": 30,
                "services": []
            }
        ]
        
        # Setup mock returns
        mock_db.packages.find.return_value = mock_packages
        mock_db.package_purchases.count_documents.return_value = 10
        mock_db.redemption_transactions.count_documents.return_value = 5
        
        # Execute
        recommendations = await service.get_recommendations_for_client(
            client_id=client_id,
            tenant_id=tenant_id,
            limit=5
        )
        
        # Assert - should return popular packages
        assert len(recommendations) > 0
        assert recommendations[0]["package_id"] == package_id
    
    @pytest.mark.asyncio
    async def test_get_recommendations_excludes_owned_packages(self):
        """Test that recommendations exclude packages already owned by client"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        client_id = str(ObjectId())
        tenant_id = "test_tenant"
        service_id = str(ObjectId())
        owned_package_id = str(ObjectId())
        available_package_id = str(ObjectId())
        
        # Mock bookings
        mock_bookings = [
            {
                "_id": ObjectId(),
                "client_id": client_id,
                "service_id": service_id,
                "booking_date": datetime.utcnow(),
                "status": "completed"
            }
        ]
        
        # Mock packages
        mock_packages = [
            {
                "_id": ObjectId(owned_package_id),
                "tenant_id": tenant_id,
                "name": "Owned Package",
                "is_active": True,
                "package_price": 100.0,
                "original_price": 150.0,
                "discount_percentage": 33,
                "services": [{"service_id": service_id, "quantity": 1}]
            },
            {
                "_id": ObjectId(available_package_id),
                "tenant_id": tenant_id,
                "name": "Available Package",
                "is_active": True,
                "package_price": 120.0,
                "original_price": 180.0,
                "discount_percentage": 33,
                "services": [{"service_id": service_id, "quantity": 2}]
            }
        ]
        
        # Setup mock returns
        mock_db.bookings.find.return_value.sort.return_value.limit.return_value = mock_bookings
        mock_db.packages.find.return_value = mock_packages
        
        # Mock existing purchase for owned package
        def find_one_side_effect(query):
            if query.get("package_definition_id") == owned_package_id:
                return {"_id": ObjectId(), "status": "active"}
            return None
        
        mock_db.package_purchases.find_one.side_effect = find_one_side_effect
        mock_db.services.find_one.return_value = {"_id": ObjectId(service_id), "price": 50.0}
        
        # Execute
        recommendations = await service.get_recommendations_for_client(
            client_id=client_id,
            tenant_id=tenant_id,
            limit=5
        )
        
        # Assert - should only include available package
        assert len(recommendations) == 1
        assert recommendations[0]["package_id"] == available_package_id
    
    @pytest.mark.asyncio
    async def test_calculate_potential_savings(self):
        """Test calculating potential savings for a package"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        tenant_id = "test_tenant"
        package_id = str(ObjectId())
        service_id_1 = str(ObjectId())
        service_id_2 = str(ObjectId())
        
        # Mock package
        mock_package = {
            "_id": ObjectId(package_id),
            "tenant_id": tenant_id,
            "name": "Test Package",
            "package_price": 100.0,
            "services": [
                {"service_id": service_id_1, "quantity": 2},
                {"service_id": service_id_2, "quantity": 1}
            ]
        }
        
        # Mock services
        mock_services = {
            service_id_1: {"_id": ObjectId(service_id_1), "price": 50.0},
            service_id_2: {"_id": ObjectId(service_id_2), "price": 40.0}
        }
        
        # Setup mock returns
        mock_db.packages.find_one.return_value = mock_package
        
        def services_find_one(query):
            service_id = query.get("_id")
            if service_id == ObjectId(service_id_1):
                return {"_id": ObjectId(service_id_1), "price": 50.0}
            elif service_id == ObjectId(service_id_2):
                return {"_id": ObjectId(service_id_2), "price": 40.0}
            return None
        
        mock_db.services.find_one.side_effect = services_find_one
        
        # Execute
        savings = await service.calculate_potential_savings(
            client_id=str(ObjectId()),
            package_definition_id=package_id,
            tenant_id=tenant_id
        )
        
        # Assert
        # Individual cost: (50 * 2) + (40 * 1) = 140
        # Package price: 100
        # Savings: 140 - 100 = 40
        assert savings == 40.0
    
    @pytest.mark.asyncio
    async def test_calculate_potential_savings_no_savings(self):
        """Test calculating savings when package price equals individual cost"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        tenant_id = "test_tenant"
        package_id = str(ObjectId())
        service_id = str(ObjectId())
        
        # Mock package with no savings
        mock_package = {
            "_id": ObjectId(package_id),
            "tenant_id": tenant_id,
            "name": "No Savings Package",
            "package_price": 100.0,
            "services": [
                {"service_id": service_id, "quantity": 2}
            ]
        }
        
        # Mock service
        mock_db.packages.find_one.return_value = mock_package
        mock_db.services.find_one.return_value = {"_id": ObjectId(service_id), "price": 50.0}
        
        # Execute
        savings = await service.calculate_potential_savings(
            client_id=str(ObjectId()),
            package_definition_id=package_id,
            tenant_id=tenant_id
        )
        
        # Assert
        # Individual cost: 50 * 2 = 100
        # Package price: 100
        # Savings: 0
        assert savings == 0.0
    
    @pytest.mark.asyncio
    async def test_calculate_potential_savings_package_not_found(self):
        """Test calculating savings when package doesn't exist"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        tenant_id = "test_tenant"
        package_id = str(ObjectId())
        
        # Mock package not found
        mock_db.packages.find_one.return_value = None
        
        # Execute
        savings = await service.calculate_potential_savings(
            client_id=str(ObjectId()),
            package_definition_id=package_id,
            tenant_id=tenant_id
        )
        
        # Assert
        assert savings == 0.0
    
    @pytest.mark.asyncio
    async def test_get_popular_packages(self):
        """Test getting popular packages"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        tenant_id = "test_tenant"
        package_id_1 = str(ObjectId())
        package_id_2 = str(ObjectId())
        
        # Mock packages
        mock_packages = [
            {
                "_id": ObjectId(package_id_1),
                "tenant_id": tenant_id,
                "name": "Popular Package",
                "description": "Most popular",
                "is_active": True,
                "package_price": 100.0,
                "original_price": 150.0,
                "discount_percentage": 33,
                "validity_days": 30,
                "services": []
            },
            {
                "_id": ObjectId(package_id_2),
                "tenant_id": tenant_id,
                "name": "Less Popular Package",
                "description": "Less popular",
                "is_active": True,
                "package_price": 80.0,
                "original_price": 120.0,
                "discount_percentage": 33,
                "validity_days": 30,
                "services": []
            }
        ]
        
        # Setup mock returns
        mock_db.packages.find.return_value = mock_packages
        
        # Mock purchase counts
        def count_documents_side_effect(query):
            if query.get("package_definition_id") == package_id_1:
                return 10  # More popular
            return 5
        
        mock_db.package_purchases.count_documents.side_effect = count_documents_side_effect
        mock_db.redemption_transactions.count_documents.return_value = 20
        
        # Execute
        popular = await service.get_popular_packages(
            tenant_id=tenant_id,
            limit=5
        )
        
        # Assert
        assert len(popular) == 2
        assert popular[0]["package_id"] == package_id_1  # Most popular first
        assert popular[0]["popularity_score"] > popular[1]["popularity_score"]
    
    @pytest.mark.asyncio
    async def test_get_popular_packages_limit(self):
        """Test that popular packages respects limit parameter"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        tenant_id = "test_tenant"
        
        # Mock 5 packages
        mock_packages = [
            {
                "_id": ObjectId(),
                "tenant_id": tenant_id,
                "name": f"Package {i}",
                "is_active": True,
                "package_price": 100.0,
                "original_price": 150.0,
                "discount_percentage": 33,
                "services": []
            }
            for i in range(5)
        ]
        
        # Setup mock returns
        mock_db.packages.find.return_value = mock_packages
        mock_db.package_purchases.count_documents.return_value = 10
        mock_db.redemption_transactions.count_documents.return_value = 5
        
        # Execute with limit of 2
        popular = await service.get_popular_packages(
            tenant_id=tenant_id,
            limit=2
        )
        
        # Assert
        assert len(popular) == 2
    
    @pytest.mark.asyncio
    async def test_recommendations_sorted_by_relevance_and_savings(self):
        """Test that recommendations are sorted by relevance score and savings"""
        # Setup
        mock_db = MagicMock()
        service = PackageRecommendationService(mock_db)
        
        client_id = str(ObjectId())
        tenant_id = "test_tenant"
        service_id_1 = str(ObjectId())
        service_id_2 = str(ObjectId())
        package_id_1 = str(ObjectId())
        package_id_2 = str(ObjectId())
        
        # Mock bookings - more frequent for service_id_1
        mock_bookings = [
            {"_id": ObjectId(), "client_id": client_id, "service_id": service_id_1, "status": "completed"},
            {"_id": ObjectId(), "client_id": client_id, "service_id": service_id_1, "status": "completed"},
            {"_id": ObjectId(), "client_id": client_id, "service_id": service_id_1, "status": "completed"},
            {"_id": ObjectId(), "client_id": client_id, "service_id": service_id_2, "status": "completed"},
        ]
        
        # Mock packages
        mock_packages = [
            {
                "_id": ObjectId(package_id_1),
                "tenant_id": tenant_id,
                "name": "High Relevance Package",
                "is_active": True,
                "package_price": 100.0,
                "original_price": 150.0,
                "discount_percentage": 33,
                "services": [
                    {"service_id": service_id_1, "quantity": 3},  # High relevance
                    {"service_id": service_id_2, "quantity": 1}
                ]
            },
            {
                "_id": ObjectId(package_id_2),
                "tenant_id": tenant_id,
                "name": "Low Relevance Package",
                "is_active": True,
                "package_price": 80.0,
                "original_price": 200.0,
                "discount_percentage": 60,
                "services": [
                    {"service_id": service_id_2, "quantity": 2}  # Low relevance
                ]
            }
        ]
        
        # Setup mock returns
        mock_db.bookings.find.return_value.sort.return_value.limit.return_value = mock_bookings
        mock_db.packages.find.return_value = mock_packages
        mock_db.package_purchases.find_one.return_value = None
        mock_db.services.find_one.side_effect = lambda query: {
            service_id_1: {"_id": ObjectId(service_id_1), "price": 50.0},
            service_id_2: {"_id": ObjectId(service_id_2), "price": 40.0}
        }.get(query["_id"])
        
        # Execute
        recommendations = await service.get_recommendations_for_client(
            client_id=client_id,
            tenant_id=tenant_id,
            limit=5
        )
        
        # Assert - high relevance package should be first
        assert len(recommendations) >= 1
        assert recommendations[0]["package_id"] == package_id_1
