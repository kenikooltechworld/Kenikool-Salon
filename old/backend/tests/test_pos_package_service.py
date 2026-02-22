"""
Unit tests for POS Package Service
Tests package credit checking and redemption at POS
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from app.services.pos_package_service import POSPackageService


class TestGetClientPackages:
    """Tests for get_client_packages method"""
    
    @pytest.mark.asyncio
    async def test_get_client_packages_success(self):
        """Test retrieving client packages at POS"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        client_id = str(ObjectId())
        purchase_id = str(ObjectId())
        service_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "client_id": client_id,
            "status": "active",
            "package_definition_id": str(ObjectId()),
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": purchase_id,
            "service_id": service_id,
            "service_name": "Haircut",
            "remaining_quantity": 2,
            "initial_quantity": 3
        }
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter([mock_purchase]))
        mock_db.package_purchases.find.return_value = mock_cursor
        mock_db.service_credits.find.return_value = [mock_credit]
        
        # Execute
        result = await service.get_client_packages(client_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["client_id"] == client_id
        assert result[0]["total_remaining_credits"] == 2
        assert service_id in result[0]["credit_balance"]
    
    @pytest.mark.asyncio
    async def test_get_client_packages_with_expiration_filter(self):
        """Test retrieving client packages with expiration filtering"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        client_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(),
            "client_id": client_id,
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter([mock_purchase]))
        mock_db.package_purchases.find.return_value = mock_cursor
        mock_db.service_credits.find.return_value = []
        
        # Execute
        result = await service.get_client_packages(client_id, include_expired=False)
        
        # Assert
        assert len(result) == 1
        mock_db.package_purchases.find.assert_called_once()


class TestCheckPackageCreditsForService:
    """Tests for check_package_credits_for_service method"""
    
    @pytest.mark.asyncio
    async def test_check_package_credits_success(self):
        """Test checking package credits for a service"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        client_id = str(ObjectId())
        service_id = str(ObjectId())
        purchase_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "client_id": client_id,
            "status": "active",
            "package_definition_id": str(ObjectId()),
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": purchase_id,
            "service_id": service_id,
            "service_name": "Haircut",
            "remaining_quantity": 2,
            "initial_quantity": 3
        }
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter([mock_purchase]))
        mock_db.package_purchases.find.return_value = mock_cursor
        mock_db.service_credits.find.return_value = [mock_credit]
        
        # Execute
        result = await service.check_package_credits_for_service(client_id, service_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["service_id"] == service_id
        assert result[0]["remaining_credits"] == 2
    
    @pytest.mark.asyncio
    async def test_check_package_credits_no_credits(self):
        """Test checking package credits when no credits available"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        client_id = str(ObjectId())
        service_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(),
            "client_id": client_id,
            "status": "active",
            "package_definition_id": str(ObjectId()),
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter([mock_purchase]))
        mock_db.package_purchases.find.return_value = mock_cursor
        mock_db.service_credits.find.return_value = []
        
        # Execute
        result = await service.check_package_credits_for_service(client_id, service_id)
        
        # Assert
        assert len(result) == 0


class TestValidatePOSRedemption:
    """Tests for validate_pos_redemption method"""
    
    @pytest.mark.asyncio
    async def test_validate_pos_redemption_success(self):
        """Test successful POS redemption validation"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id = str(ObjectId())
        client_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "client_id": client_id,
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30),
            "package_definition_id": str(ObjectId())
        }
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": purchase_id,
            "service_id": service_id,
            "remaining_quantity": 2,
            "status": "available"
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {}
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.validate_pos_redemption(
            purchase_id=purchase_id,
            service_id=service_id,
            client_id=client_id
        )
        
        # Assert
        assert result["valid"] is True
    
    @pytest.mark.asyncio
    async def test_validate_pos_redemption_expired(self):
        """Test POS redemption validation with expired package"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute
        result = await service.validate_pos_redemption(
            purchase_id=str(ObjectId()),
            service_id=str(ObjectId()),
            client_id=str(ObjectId())
        )
        
        # Assert
        assert result["valid"] is False
        assert result["error_code"] == "PACKAGE_EXPIRED"


class TestRedeemPackageCreditAtPOS:
    """Tests for redeem_package_credit_at_pos method"""
    
    @pytest.mark.asyncio
    async def test_redeem_package_credit_success(self):
        """Test successful package credit redemption at POS"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id = str(ObjectId())
        client_id = str(ObjectId())
        staff_id = str(ObjectId())
        credit_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "client_id": client_id,
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30),
            "package_definition_id": str(ObjectId()),
            "tenant_id": "test_tenant"
        }
        
        mock_credit = {
            "_id": ObjectId(credit_id),
            "purchase_id": purchase_id,
            "service_id": service_id,
            "remaining_quantity": 2,
            "service_price": 50.0,
            "status": "available"
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {}
        }
        
        mock_redemption = {
            "_id": str(ObjectId()),
            "service_value": 50.0
        }
        
        # Setup mocks - need to handle multiple find_one calls
        def find_one_side_effect(query):
            if "_id" in query and "ObjectId" in str(query["_id"]):
                # This is for package_purchases
                return mock_purchase
            elif "restrictions" in query or "name" in query:
                # This is for packages
                return mock_package_def
            return None
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.packages.find_one.return_value = mock_package_def
        mock_db.redemption_transactions.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Mock the credit service redeem method
        with patch.object(service.credit_service, 'redeem_credit', new_callable=AsyncMock) as mock_redeem:
            mock_redeem.return_value = mock_redemption
            
            # Execute
            result = await service.redeem_package_credit_at_pos(
                purchase_id=purchase_id,
                service_id=service_id,
                client_id=client_id,
                staff_id=staff_id,
                pos_transaction_id="pos_123",
                quantity=1
            )
            
            # Assert
            assert result["success"] is True
            assert result["service_value"] == 50.0
            mock_redeem.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_redeem_package_credit_validation_fails(self):
        """Test package credit redemption with validation failure"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute & Assert
        with pytest.raises(ValueError):
            await service.redeem_package_credit_at_pos(
                purchase_id=str(ObjectId()),
                service_id=str(ObjectId()),
                client_id=str(ObjectId()),
                staff_id=str(ObjectId()),
                pos_transaction_id="pos_123"
            )


class TestGetPackageRedemptionSummary:
    """Tests for get_package_redemption_summary method"""
    
    @pytest.mark.asyncio
    async def test_get_package_redemption_summary_success(self):
        """Test retrieving package redemption summary"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "status": "active",
            "package_definition_id": str(ObjectId()),
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "name": "Hair Package"
        }
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": purchase_id,
            "service_id": service_id,
            "service_name": "Haircut",
            "remaining_quantity": 2,
            "reserved_quantity": 0,
            "initial_quantity": 3
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        mock_db.service_credits.find.return_value = [mock_credit]
        
        # Execute
        result = await service.get_package_redemption_summary(purchase_id)
        
        # Assert
        assert result["purchase_id"] == purchase_id
        assert result["package_name"] == "Hair Package"
        assert result["status"] == "active"
        assert result["total_remaining"] == 2
        assert result["total_reserved"] == 0
    
    @pytest.mark.asyncio
    async def test_get_package_redemption_summary_not_found(self):
        """Test retrieving summary for non-existent package"""
        # Setup
        mock_db = MagicMock()
        service = POSPackageService(mock_db)
        
        mock_db.package_purchases.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Package purchase not found"):
            await service.get_package_redemption_summary(str(ObjectId()))
