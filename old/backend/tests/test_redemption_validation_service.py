"""
Unit tests for Redemption Validation Service
Tests redemption validation, expiration checks, credit availability, and restriction enforcement
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock, AsyncMock

from app.services.redemption_validation_service import RedemptionValidationService


class TestValidateRedemption:
    """Tests for validate_redemption method"""
    
    @pytest.mark.asyncio
    async def test_validate_redemption_success(self):
        """Test successful redemption validation"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
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
        
        # Setup mocks
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find_one.return_value = mock_credit
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.validate_redemption(
            purchase_id=purchase_id,
            service_id=service_id,
            client_id=client_id
        )
        
        # Assert
        assert result["valid"] is True
        assert result["error"] is None
    
    @pytest.mark.asyncio
    async def test_validate_redemption_expired_package(self):
        """Test validation of expired package"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute
        result = await service.validate_redemption(
            purchase_id=str(ObjectId()),
            service_id=str(ObjectId()),
            client_id=str(ObjectId())
        )
        
        # Assert
        assert result["valid"] is False
        assert result["error_code"] == "PACKAGE_EXPIRED"
    
    @pytest.mark.asyncio
    async def test_validate_redemption_insufficient_credits(self):
        """Test validation with insufficient credits"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find_one.return_value = None
        
        # Execute
        result = await service.validate_redemption(
            purchase_id=str(ObjectId()),
            service_id=str(ObjectId()),
            client_id=str(ObjectId())
        )
        
        # Assert
        assert result["valid"] is False
        assert result["error_code"] == "INSUFFICIENT_CREDITS"
    
    @pytest.mark.asyncio
    async def test_validate_redemption_ownership_mismatch(self):
        """Test validation with ownership mismatch"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "client_id": str(ObjectId()),
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_credit = {
            "_id": ObjectId(),
            "remaining_quantity": 2,
            "status": "available"
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find_one.return_value = mock_credit
        
        # Execute
        result = await service.validate_redemption(
            purchase_id=str(ObjectId()),
            service_id=str(ObjectId()),
            client_id=str(ObjectId())  # Different client
        )
        
        # Assert
        assert result["valid"] is False
        assert result["error_code"] == "OWNERSHIP_MISMATCH"
    
    @pytest.mark.asyncio
    async def test_validate_redemption_cancelled_package(self):
        """Test validation of cancelled package"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        client_id = str(ObjectId())
        mock_purchase = {
            "_id": ObjectId(),
            "client_id": client_id,
            "status": "cancelled",
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_credit = {
            "_id": ObjectId(),
            "remaining_quantity": 2,
            "status": "available"
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.service_credits.find_one.return_value = mock_credit
        
        # Execute
        result = await service.validate_redemption(
            purchase_id=str(ObjectId()),
            service_id=str(ObjectId()),
            client_id=client_id
        )
        
        # Assert
        assert result["valid"] is False
        assert result["error_code"] == "PACKAGE_CANCELLED"


class TestCheckExpiration:
    """Tests for check_expiration method"""
    
    @pytest.mark.asyncio
    async def test_check_expiration_not_expired(self):
        """Test expiration check for active package"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() + timedelta(days=30)
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute
        result = await service.check_expiration(str(ObjectId()))
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_expiration_expired(self):
        """Test expiration check for expired package"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "active",
            "expiration_date": datetime.utcnow() - timedelta(days=1)
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute
        result = await service.check_expiration(str(ObjectId()))
        
        # Assert
        assert result is False
    
    @pytest.mark.asyncio
    async def test_check_expiration_status_expired(self):
        """Test expiration check for package with expired status"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "status": "expired"
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        
        # Execute
        result = await service.check_expiration(str(ObjectId()))
        
        # Assert
        assert result is False


class TestCheckCreditAvailability:
    """Tests for check_credit_availability method"""
    
    @pytest.mark.asyncio
    async def test_check_credit_available(self):
        """Test credit availability check with available credits"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_credit = {
            "_id": ObjectId(),
            "remaining_quantity": 2,
            "status": "available"
        }
        
        mock_db.service_credits.find_one.return_value = mock_credit
        
        # Execute
        result = await service.check_credit_availability(
            str(ObjectId()),
            str(ObjectId())
        )
        
        # Assert
        assert result is True
    
    @pytest.mark.asyncio
    async def test_check_credit_not_available(self):
        """Test credit availability check with no credits"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_db.service_credits.find_one.return_value = None
        
        # Execute
        result = await service.check_credit_availability(
            str(ObjectId()),
            str(ObjectId())
        )
        
        # Assert
        assert result is False


class TestCheckRestrictions:
    """Tests for check_restrictions method"""
    
    @pytest.mark.asyncio
    async def test_check_restrictions_no_violations(self):
        """Test restriction check with no violations"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        mock_purchase = {
            "_id": ObjectId(),
            "package_definition_id": str(ObjectId())
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {}
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.check_restrictions(
            purchase_id=str(ObjectId())
        )
        
        # Assert
        assert len(result) == 0
    
    @pytest.mark.asyncio
    async def test_check_stylist_restriction_violation(self):
        """Test stylist restriction violation"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        allowed_stylist_id = str(ObjectId())
        other_stylist_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(),
            "package_definition_id": str(ObjectId())
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {
                "stylist_ids": [allowed_stylist_id]
            }
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.check_restrictions(
            purchase_id=str(ObjectId()),
            stylist_id=other_stylist_id
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "stylist_restriction"
    
    @pytest.mark.asyncio
    async def test_check_location_restriction_violation(self):
        """Test location restriction violation"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        allowed_location_id = str(ObjectId())
        other_location_id = str(ObjectId())
        
        mock_purchase = {
            "_id": ObjectId(),
            "package_definition_id": str(ObjectId())
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {
                "location_ids": [allowed_location_id]
            }
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.check_restrictions(
            purchase_id=str(ObjectId()),
            location_id=other_location_id
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "location_restriction"
    
    @pytest.mark.asyncio
    async def test_check_blackout_date_violation(self):
        """Test blackout date restriction violation"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        blackout_date = datetime.utcnow()
        
        mock_purchase = {
            "_id": ObjectId(),
            "package_definition_id": str(ObjectId())
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {
                "blackout_dates": [blackout_date]
            }
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.check_restrictions(
            purchase_id=str(ObjectId()),
            redemption_date=blackout_date
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "blackout_date"
    
    @pytest.mark.asyncio
    async def test_check_time_restriction_day_violation(self):
        """Test time restriction day of week violation"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        # Create a date that is a Monday (0)
        monday = datetime(2024, 1, 1)  # This is a Monday
        
        mock_purchase = {
            "_id": ObjectId(),
            "package_definition_id": str(ObjectId())
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {
                "time_restrictions": {
                    "days_of_week": [1, 2, 3, 4, 5]  # Tuesday to Saturday
                }
            }
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.check_restrictions(
            purchase_id=str(ObjectId()),
            redemption_date=monday
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "time_restriction_day"
    
    @pytest.mark.asyncio
    async def test_check_time_restriction_time_violation(self):
        """Test time restriction time of day violation"""
        # Setup
        mock_db = MagicMock()
        service = RedemptionValidationService(mock_db)
        
        # Create a date at 8:00 AM
        early_morning = datetime(2024, 1, 1, 8, 0)
        
        mock_purchase = {
            "_id": ObjectId(),
            "package_definition_id": str(ObjectId())
        }
        
        mock_package_def = {
            "_id": ObjectId(),
            "restrictions": {
                "time_restrictions": {
                    "start_time": "09:00",
                    "end_time": "17:00"
                }
            }
        }
        
        mock_db.package_purchases.find_one.return_value = mock_purchase
        mock_db.packages.find_one.return_value = mock_package_def
        
        # Execute
        result = await service.check_restrictions(
            purchase_id=str(ObjectId()),
            redemption_date=early_morning
        )
        
        # Assert
        assert len(result) == 1
        assert result[0]["type"] == "time_restriction_before"
