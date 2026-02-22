"""
Unit tests for Service Credit Service
Tests service credit initialization, reservation, release, and redemption operations
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from app.services.service_credit_service import ServiceCreditService


class TestCreditInitialization:
    """Tests for initialize_credits method"""
    
    @pytest.mark.asyncio
    async def test_initialize_credits_success(self):
        """Test successful service credit initialization"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id_1 = str(ObjectId())
        service_id_2 = str(ObjectId())
        
        mock_service_1 = {
            "_id": ObjectId(service_id_1),
            "name": "Haircut",
            "price": 50.0
        }
        
        mock_service_2 = {
            "_id": ObjectId(service_id_2),
            "name": "Color",
            "price": 100.0
        }
        
        mock_db.services.find_one.side_effect = [mock_service_1, mock_service_2]
        mock_db.service_credits.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        
        # Execute
        result = await service.initialize_credits(
            purchase_id=purchase_id,
            service_quantities={
                service_id_1: 3,
                service_id_2: 2
            }
        )
        
        # Assert
        assert len(result) == 2
        assert result[0]["initial_quantity"] == 3
        assert result[0]["remaining_quantity"] == 3
        assert result[0]["status"] == "available"
        assert result[1]["initial_quantity"] == 2
        assert result[1]["remaining_quantity"] == 2
        assert mock_db.service_credits.insert_one.call_count == 2
    
    @pytest.mark.asyncio
    async def test_initialize_credits_service_not_found(self):
        """Test credit initialization with non-existent service"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        mock_db.services.find_one.return_value = None
        
        # Execute
        result = await service.initialize_credits(
            purchase_id=str(ObjectId()),
            service_quantities={str(ObjectId()): 3}
        )
        
        # Assert - should skip non-existent service
        assert len(result) == 0
        assert mock_db.service_credits.insert_one.call_count == 0


class TestGetAvailableCredits:
    """Tests for get_available_credits method"""
    
    @pytest.mark.asyncio
    async def test_get_available_credits_success(self):
        """Test retrieving available credits"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        purchase_id = str(ObjectId())
        credit_id = str(ObjectId())
        
        mock_credits = [
            {
                "_id": ObjectId(credit_id),
                "purchase_id": purchase_id,
                "service_id": str(ObjectId()),
                "remaining_quantity": 2,
                "status": "available"
            }
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter(mock_credits))
        mock_db.service_credits.find.return_value = mock_cursor
        
        # Execute
        result = await service.get_available_credits(purchase_id)
        
        # Assert
        assert len(result) == 1
        assert result[0]["remaining_quantity"] == 2
        assert result[0]["status"] == "available"
    
    @pytest.mark.asyncio
    async def test_get_available_credits_for_specific_service(self):
        """Test retrieving available credits for specific service"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id = str(ObjectId())
        
        mock_credits = [
            {
                "_id": ObjectId(),
                "purchase_id": purchase_id,
                "service_id": service_id,
                "remaining_quantity": 2,
                "status": "available"
            }
        ]
        
        mock_cursor = MagicMock()
        mock_cursor.__iter__ = MagicMock(return_value=iter(mock_credits))
        mock_db.service_credits.find.return_value = mock_cursor
        
        # Execute
        result = await service.get_available_credits(purchase_id, service_id=service_id)
        
        # Assert
        assert len(result) == 1
        mock_db.service_credits.find.assert_called_once()
        call_args = mock_db.service_credits.find.call_args[0][0]
        assert call_args["service_id"] == service_id


class TestReserveCredit:
    """Tests for reserve_credit method"""
    
    @pytest.mark.asyncio
    async def test_reserve_credit_success(self):
        """Test successful credit reservation"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id = str(ObjectId())
        booking_id = str(ObjectId())
        credit_id = str(ObjectId())
        
        mock_credit = {
            "_id": ObjectId(credit_id),
            "purchase_id": purchase_id,
            "service_id": service_id,
            "remaining_quantity": 3,
            "reserved_quantity": 0,
            "status": "available"
        }
        
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.credit_reservations.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_db.service_credits.update_one.return_value = MagicMock()
        
        # Execute
        result = await service.reserve_credit(
            purchase_id=purchase_id,
            service_id=service_id,
            booking_id=booking_id,
            quantity=1
        )
        
        # Assert
        assert result["credit_id"] == credit_id
        assert result["booking_id"] == booking_id
        assert result["status"] == "active"
        assert mock_db.credit_reservations.insert_one.called
        assert mock_db.service_credits.update_one.called
    
    @pytest.mark.asyncio
    async def test_reserve_credit_insufficient_credits(self):
        """Test reservation with insufficient credits"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        mock_db.service_credits.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Insufficient credits available"):
            await service.reserve_credit(
                purchase_id=str(ObjectId()),
                service_id=str(ObjectId()),
                booking_id=str(ObjectId()),
                quantity=5
            )


class TestReleaseCredit:
    """Tests for release_credit method"""
    
    @pytest.mark.asyncio
    async def test_release_credit_success(self):
        """Test successful credit release"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        reservation_id = str(ObjectId())
        credit_id = str(ObjectId())
        
        mock_reservation = {
            "_id": ObjectId(reservation_id),
            "credit_id": credit_id,
            "status": "active"
        }
        
        mock_credit = {
            "_id": ObjectId(credit_id),
            "reserved_quantity": 1
        }
        
        mock_updated_reservation = {
            "_id": ObjectId(reservation_id),
            "credit_id": credit_id,
            "status": "released"
        }
        
        # Setup find_one to return different values on different calls
        mock_db.credit_reservations.find_one.side_effect = [mock_reservation, mock_updated_reservation]
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.service_credits.update_one.return_value = MagicMock()
        mock_db.credit_reservations.update_one.return_value = MagicMock()
        
        # Execute
        result = await service.release_credit(
            reservation_id=reservation_id,
            quantity=1
        )
        
        # Assert
        assert result["status"] == "released"
        assert mock_db.service_credits.update_one.called
        assert mock_db.credit_reservations.update_one.called
    
    @pytest.mark.asyncio
    async def test_release_credit_not_found(self):
        """Test release of non-existent reservation"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        mock_db.credit_reservations.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Reservation not found"):
            await service.release_credit(
                reservation_id=str(ObjectId()),
                quantity=1
            )


class TestRedeemCredit:
    """Tests for redeem_credit method"""
    
    @pytest.mark.asyncio
    async def test_redeem_credit_success(self):
        """Test successful credit redemption"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        credit_id = str(ObjectId())
        purchase_id = str(ObjectId())
        staff_id = str(ObjectId())
        client_id = str(ObjectId())
        
        mock_credit = {
            "_id": ObjectId(credit_id),
            "purchase_id": purchase_id,
            "service_id": str(ObjectId()),
            "remaining_quantity": 3,
            "service_price": 50.0,
            "status": "available"
        }
        
        mock_purchase = {
            "_id": ObjectId(purchase_id),
            "tenant_id": "test_tenant",
            "client_id": client_id,
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        # Setup find_one to return different values on different calls
        mock_db.service_credits.find_one.side_effect = [mock_credit, None]  # None for remaining_credits check
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.redemption_transactions.insert_one.return_value = MagicMock(inserted_id=ObjectId())
        mock_db.service_credits.update_one.return_value = MagicMock()
        mock_db.package_audit_logs.insert_one.return_value = MagicMock()
        
        # Execute
        result = await service.redeem_credit(
            credit_id=credit_id,
            redeemed_by_staff_id=staff_id,
            transaction_id="txn_123",
            quantity=1
        )
        
        # Assert
        assert result["credit_id"] == credit_id
        assert result["service_value"] == 50.0
        assert mock_db.redemption_transactions.insert_one.called
        assert mock_db.service_credits.update_one.called
    
    @pytest.mark.asyncio
    async def test_redeem_credit_insufficient_quantity(self):
        """Test redemption with insufficient credits"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": str(ObjectId()),
            "remaining_quantity": 1,
            "service_price": 50.0
        }
        
        mock_db.service_credits.find_one.return_value = mock_credit
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Insufficient credits available"):
            await service.redeem_credit(
                credit_id=str(ObjectId()),
                redeemed_by_staff_id=str(ObjectId()),
                transaction_id="txn_123",
                quantity=5
            )
    
    @pytest.mark.asyncio
    async def test_redeem_credit_expired_package(self):
        """Test redemption of expired package"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": str(ObjectId()),
            "remaining_quantity": 3,
            "service_price": 50.0
        }
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Package has expired"):
            await service.redeem_credit(
                credit_id=str(ObjectId()),
                redeemed_by_staff_id=str(ObjectId()),
                transaction_id="txn_123",
                quantity=1
            )
    
    @pytest.mark.asyncio
    async def test_redeem_credit_cancelled_package(self):
        """Test redemption of cancelled package"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        mock_credit = {
            "_id": ObjectId(),
            "purchase_id": str(ObjectId()),
            "remaining_quantity": 3,
            "service_price": 50.0
        }
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "cancelled"
        }
        
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Package has been cancelled"):
            await service.redeem_credit(
                credit_id=str(ObjectId()),
                redeemed_by_staff_id=str(ObjectId()),
                transaction_id="txn_123",
                quantity=1
            )


class TestGetCreditBalance:
    """Tests for get_credit_balance method"""
    
    @pytest.mark.asyncio
    async def test_get_credit_balance_success(self):
        """Test retrieving credit balance"""
        # Setup
        mock_db = MagicMock()
        service = ServiceCreditService(mock_db)
        
        purchase_id = str(ObjectId())
        service_id_1 = str(ObjectId())
        service_id_2 = str(ObjectId())
        
        mock_credits = [
            {
                "_id": ObjectId(),
                "service_id": service_id_1,
                "service_name": "Haircut",
                "remaining_quantity": 2,
                "reserved_quantity": 1,
                "initial_quantity": 3
            },
            {
                "_id": ObjectId(),
                "service_id": service_id_2,
                "service_name": "Color",
                "remaining_quantity": 1,
                "reserved_quantity": 0,
                "initial_quantity": 2
            }
        ]
        
        mock_db.service_credits.find.return_value = mock_credits
        
        # Execute
        result = await service.get_credit_balance(purchase_id)
        
        # Assert
        assert result["purchase_id"] == purchase_id
        assert result["total_remaining"] == 3
        assert result["total_reserved"] == 1
        assert service_id_1 in result["credits"]
        assert service_id_2 in result["credits"]
        assert result["credits"][service_id_1]["remaining"] == 2
        assert result["credits"][service_id_2]["remaining"] == 1
