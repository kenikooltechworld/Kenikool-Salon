"""
Unit tests for Package Purchase Service
Tests package purchase creation, retrieval, transfer, and refund operations
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from app.services.package_purchase_service import PackagePurchaseService


class TestPackagePurchaseCreation:
    """Tests for create_purchase method"""
    
    @pytest.mark.asyncio
    async def test_create_purchase_success(self):
        """Test successful package purchase creation"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        tenant_id = "test_tenant"
        client_id = str(ObjectId())
        package_def_id = str(ObjectId())
        staff_id = str(ObjectId())
        
        mock_package = {
            "_id": ObjectId(package_def_id),
            "tenant_id": tenant_id,
            "name": "Hair Package",
            "is_active": True,
            "original_price": 100.0,
            "package_price": 80.0,
            "validity_days": 30,
            "is_transferable": True,
            "services": [
                {"service_id": str(ObjectId()), "quantity": 3}
            ]
        }
        
        mock_db.packages.find_one.return_value = mock_package
        mock_db.package_purchases.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_db.service_credits.insert_one.return_value = MagicMock()
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.create_purchase(
            tenant_id=tenant_id,
            client_id=client_id,
            package_definition_id=package_def_id,
            payment_method="card",
            purchased_by_staff_id=staff_id,
            is_gift=False
        )
        
        # Assert
        assert result["client_id"] == client_id
        assert result["status"] == "active"
        assert result["amount_paid"] == 80.0
        assert result["is_gift"] is False
        assert result["expiration_date"] is not None
        assert mock_db.package_purchases.insert_one.called
        assert mock_db.service_credits.insert_one.called
    
    @pytest.mark.asyncio
    async def test_create_gift_purchase(self):
        """Test creating a gift package purchase"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        tenant_id = "test_tenant"
        purchaser_id = str(ObjectId())
        recipient_id = str(ObjectId())
        package_def_id = str(ObjectId())
        staff_id = str(ObjectId())
        
        mock_package = {
            "_id": ObjectId(package_def_id),
            "tenant_id": tenant_id,
            "name": "Gift Package",
            "is_active": True,
            "original_price": 100.0,
            "package_price": 80.0,
            "validity_days": 30,
            "is_giftable": True,
            "services": []
        }
        
        mock_recipient = {
            "_id": ObjectId(recipient_id),
            "tenant_id": tenant_id,
            "name": "Recipient"
        }
        
        mock_db.packages.find_one.return_value = mock_package
        mock_db.clients.find_one.return_value = mock_recipient
        mock_db.package_purchases.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.create_purchase(
            tenant_id=tenant_id,
            client_id=purchaser_id,
            package_definition_id=package_def_id,
            payment_method="card",
            purchased_by_staff_id=staff_id,
            is_gift=True,
            recipient_id=recipient_id,
            gift_message="Happy Birthday!"
        )
        
        # Assert
        assert result["is_gift"] is True
        assert result["client_id"] == recipient_id
        assert result["gift_from_client_id"] == purchaser_id
        assert result["gift_message"] == "Happy Birthday!"
    
    @pytest.mark.asyncio
    async def test_create_purchase_package_not_found(self):
        """Test purchase creation with non-existent package"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        mock_db.packages.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Package definition not found"):
            await service.create_purchase(
                tenant_id="test_tenant",
                client_id=str(ObjectId()),
                package_definition_id=str(ObjectId()),
                payment_method="card",
                purchased_by_staff_id=str(ObjectId())
            )
    
    @pytest.mark.asyncio
    async def test_create_purchase_invalid_recipient(self):
        """Test gift purchase with non-existent recipient"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        mock_package = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "is_active": True,
            "is_giftable": True
        }
        
        mock_db.packages.find_one.return_value = mock_package
        mock_db.clients.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Recipient client not found"):
            await service.create_purchase(
                tenant_id="test_tenant",
                client_id=str(ObjectId()),
                package_definition_id=str(ObjectId()),
                payment_method="card",
                purchased_by_staff_id=str(ObjectId()),
                is_gift=True,
                recipient_id=str(ObjectId())
            )


class TestGetClientPackages:
    """Tests for get_client_packages method"""
    
    @pytest.mark.asyncio
    async def test_get_client_packages_success(self):
        """Test retrieving client packages"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        client_id = str(ObjectId())
        purchase_id = str(ObjectId())
        
        mock_purchases = [
            {
                "_id": ObjectId(purchase_id),
                "client_id": client_id,
                "status": "active",
                "purchase_date": datetime.utcnow()
            }
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter(mock_purchases))
        mock_db.package_purchases.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        
        # Execute
        result = await service.get_client_packages(client_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["client_id"] == client_id
        assert result[0]["status"] == "active"
    
    @pytest.mark.asyncio
    async def test_get_client_packages_with_status_filter(self):
        """Test retrieving client packages with status filter"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        client_id = str(ObjectId())
        
        mock_purchases = [
            {
                "_id": ObjectId(),
                "client_id": client_id,
                "status": "active"
            }
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter(mock_purchases))
        mock_db.package_purchases.find.return_value = mock_cursor
        mock_cursor.sort.return_value = mock_cursor
        
        # Execute
        result = await service.get_client_packages(client_id, status="active")
        
        # Assert
        assert len(result) == 1
        mock_db.package_purchases.find.assert_called_with({
            "client_id": client_id,
            "status": "active"
        })


class TestPackageTransfer:
    """Tests for transfer_package method"""
    
    @pytest.mark.asyncio
    async def test_transfer_package_success(self):
        """Test successful package transfer"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        purchase_id = str(ObjectId())
        from_client_id = str(ObjectId())
        to_client_id = str(ObjectId())
        staff_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "client_id": from_client_id,
            "tenant_id": "test_tenant",
            "is_transferable": True
        }
        
        mock_updated_purchase = {
            "_id": ObjectId(purchase_id),
            "client_id": to_client_id,
            "tenant_id": "test_tenant",
            "is_transferable": True
        }
        
        mock_credits = [
            {
                "_id": ObjectId(),
                "remaining_quantity": 2
            }
        ]
        
        mock_recipient = {
            "_id": ObjectId(to_client_id),
            "tenant_id": "test_tenant"
        }
        
        # Setup find_one to return different values on different calls
        mock_db.package_purchases.find_one.side_effect = [mock_purchase, mock_updated_purchase]
        mock_db.service_credits.find.return_value = mock_credits
        mock_db.clients.find_one.return_value = mock_recipient
        mock_db.package_purchases.update_one.return_value = MagicMock()
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.transfer_package(
            purchase_id=purchase_id,
            from_client_id=from_client_id,
            to_client_id=to_client_id,
            staff_id=staff_id
        )
        
        # Assert
        assert result["client_id"] == to_client_id
        mock_db.package_purchases.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_transfer_non_transferable_package(self):
        """Test transfer of non-transferable package"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "client_id": str(ObjectId()),
            "is_transferable": False
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Package is not transferable"):
            await service.transfer_package(
                purchase_id=str(ObjectId()),
                from_client_id=str(ObjectId()),
                to_client_id=str(ObjectId()),
                staff_id=str(ObjectId())
            )
    
    @pytest.mark.asyncio
    async def test_transfer_package_no_credits(self):
        """Test transfer of package with no remaining credits"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "client_id": str(ObjectId()),
            "is_transferable": True
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find.return_value = []
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Package has no remaining credits"):
            await service.transfer_package(
                purchase_id=str(ObjectId()),
                from_client_id=str(ObjectId()),
                to_client_id=str(ObjectId()),
                staff_id=str(ObjectId())
            )


class TestPackageRefund:
    """Tests for refund_package method"""
    
    @pytest.mark.asyncio
    async def test_refund_package_success(self):
        """Test successful package refund"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        purchase_id = str(ObjectId())
        staff_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "tenant_id": "test_tenant",
            "client_id": str(ObjectId()),
            "status": "active",
            "amount_paid": 80.0,
            "payment_transaction_id": "txn_123"
        }
        
        mock_updated_purchase = {
            "_id": ObjectId(purchase_id),
            "tenant_id": "test_tenant",
            "client_id": str(ObjectId()),
            "status": "cancelled",
            "amount_paid": 80.0,
            "payment_transaction_id": "txn_123"
        }
        
        mock_credits = [
            {
                "_id": ObjectId(),
                "initial_quantity": 3,
                "remaining_quantity": 2
            },
            {
                "_id": ObjectId(),
                "initial_quantity": 2,
                "remaining_quantity": 1
            }
        ]
        
        # Setup find_one to return different values on different calls
        mock_db.package_purchases.find_one.side_effect = [mock_purchase, mock_updated_purchase]
        mock_db.service_credits.find.return_value = mock_credits
        mock_db.package_purchases.update_one.return_value = MagicMock()
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.refund_package(
            purchase_id=purchase_id,
            reason="Customer request",
            staff_id=staff_id
        )
        
        # Assert
        assert result["status"] == "cancelled"
        mock_db.package_purchases.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_refund_fully_redeemed_package(self):
        """Test refund of fully redeemed package"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "fully_redeemed"
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Cannot refund fully redeemed package"):
            await service.refund_package(
                purchase_id=str(ObjectId()),
                reason="Customer request",
                staff_id=str(ObjectId())
            )


class TestExtendExpiration:
    """Tests for extend_expiration method"""
    
    @pytest.mark.asyncio
    async def test_extend_expiration_success(self):
        """Test successful expiration extension"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        purchase_id = str(ObjectId())
        staff_id = str(ObjectId())
        original_expiration = datetime.utcnow() + timedelta(days=10)
        new_expiration = original_expiration + timedelta(days=30)
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "tenant_id": "test_tenant",
            "client_id": str(ObjectId()),
            "expiration_date": original_expiration
        }
        
        mock_updated_purchase = {
            "_id": ObjectId(purchase_id),
            "tenant_id": "test_tenant",
            "client_id": str(ObjectId()),
            "expiration_date": new_expiration
        }
        
        # Setup find_one to return different values on different calls
        mock_db.package_purchases.find_one.side_effect = [mock_purchase, mock_updated_purchase]
        mock_db.package_purchases.update_one.return_value = MagicMock()
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.extend_expiration(
            purchase_id=purchase_id,
            additional_days=30,
            staff_id=staff_id
        )
        
        # Assert
        assert result["expiration_date"] > original_expiration
        mock_db.package_purchases.update_one.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extend_expiration_no_current_date(self):
        """Test extending expiration when no current expiration date"""
        # Setup
        mock_db = MagicMock()
        service = PackagePurchaseService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": str(ObjectId()),
            "expiration_date": None
        }
        
        mock_updated_purchase = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": str(ObjectId()),
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        # Setup find_one to return different values on different calls
        mock_db.package_purchases.find_one.side_effect = [mock_purchase, mock_updated_purchase]
        mock_db.package_purchases.update_one.return_value = MagicMock()
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.extend_expiration(
            purchase_id=str(ObjectId()),
            additional_days=30,
            staff_id=str(ObjectId())
        )
        
        # Assert
        assert result["expiration_date"] is not None
        mock_db.package_purchases.update_one.assert_called_once()
