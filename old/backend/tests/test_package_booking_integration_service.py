"""
Tests for Package Booking Integration Service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.package_booking_integration_service import PackageBookingIntegrationService
from app.api.exceptions import NotFoundException, BadRequestException


@pytest.fixture
def mock_db():
    """Create a mock database"""
    db = Mock()
    db.package_purchases = Mock()
    db.service_credits = Mock()
    db.credit_reservations = Mock()
    db.bookings = Mock()
    db.package_definitions = Mock()
    db.redemption_transactions = Mock()
    return db


class TestCheckAvailableCredits:
    """Tests for check_available_credits method"""
    
    def test_check_available_credits_returns_empty_list_when_no_packages(self, mock_db):
        """Should return empty list when client has no active packages"""
        mock_db.package_purchases.find.return_value = []
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.check_available_credits(
                client_id="client123",
                service_id="service123",
                tenant_id="tenant123"
            )
        
        assert result == []
    
    def test_check_available_credits_returns_credits_for_active_packages(self, mock_db):
        """Should return available credits for active packages"""
        package_id = ObjectId()
        credit_id = ObjectId()
        
        mock_db.package_purchases.find.return_value = [
            {
                "_id": package_id,
                "client_id": "client123",
                "status": "active",
                "expiration_date": datetime.utcnow() + timedelta(days=30)
            }
        ]
        
        mock_db.service_credits.find.return_value = [
            {
                "_id": credit_id,
                "purchase_id": package_id,
                "service_id": "service123",
                "service_name": "Haircut",
                "service_price": 50.0,
                "initial_quantity": 3,
                "remaining_quantity": 2,
                "reserved_quantity": 0,
                "status": "available"
            }
        ]
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.check_available_credits(
                client_id="client123",
                service_id="service123",
                tenant_id="tenant123"
            )
        
        assert len(result) == 1
        assert result[0]["service_id"] == "service123"
        assert result[0]["remaining_quantity"] == 2


class TestReserveCredit:
    """Tests for reserve_credit method"""
    
    def test_reserve_credit_creates_reservation(self, mock_db):
        """Should create a reservation for a credit"""
        credit_id = ObjectId()
        purchase_id = ObjectId()
        
        # Setup the mock to return credit
        mock_db.service_credits.find_one.return_value = {
            "_id": credit_id,
            "purchase_id": purchase_id,
            "service_id": "service123",
            "service_name": "Haircut",
            "service_price": 50.0,
            "initial_quantity": 3,
            "remaining_quantity": 2,
            "reserved_quantity": 0,
            "status": "available",
            "tenant_id": "tenant123"
        }
        
        mock_db.service_credits.update_one.return_value = Mock()
        mock_db.credit_reservations.insert_one.return_value = Mock()
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.reserve_credit(
                credit_id=str(credit_id),
                booking_id="booking123",
                tenant_id="tenant123"
            )
        
        # Verify the result has the expected structure
        assert "_id" in result
        assert "service_id" in result
        # Verify the reservation was created
        assert mock_db.credit_reservations.insert_one.called
    
    def test_reserve_credit_raises_error_when_no_credits(self, mock_db):
        """Should raise error when credit has no remaining quantity"""
        credit_id = ObjectId()
        
        mock_db.service_credits.find_one.return_value = {
            "_id": credit_id,
            "remaining_quantity": 0,
            "status": "redeemed"
        }
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            with pytest.raises(BadRequestException):
                PackageBookingIntegrationService.reserve_credit(
                    credit_id=str(credit_id),
                    booking_id="booking123",
                    tenant_id="tenant123"
                )


class TestReleaseCredit:
    """Tests for release_credit method"""
    
    def test_release_credit_marks_reservation_as_released(self, mock_db):
        """Should mark reservation as released and set credit to available"""
        credit_id = ObjectId()
        reservation_id = ObjectId()
        
        # Setup mocks for the sequence of calls
        mock_db.service_credits.find_one.return_value = {
            "_id": credit_id,
            "purchase_id": ObjectId(),
            "service_id": "service123",
            "service_name": "Haircut",
            "service_price": 50.0,
            "initial_quantity": 3,
            "remaining_quantity": 2,
            "reserved_quantity": 0,
            "status": "reserved",
            "tenant_id": "tenant123"
        }
        
        mock_db.credit_reservations.find_one.side_effect = [
            {
                "_id": reservation_id,
                "credit_id": credit_id,
                "booking_id": "booking123",
                "status": "active"
            },
            None  # No other active reservations
        ]
        
        mock_db.credit_reservations.update_one.return_value = Mock()
        mock_db.service_credits.update_one.return_value = Mock()
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.release_credit(
                credit_id=str(credit_id),
                booking_id="booking123",
                tenant_id="tenant123"
            )
        
        # Verify the result has the expected structure
        assert "_id" in result
        assert "service_id" in result
        # Verify the reservation was updated
        assert mock_db.credit_reservations.update_one.called


class TestRedeemCreditForBooking:
    """Tests for redeem_credit_for_booking method"""
    
    def test_redeem_credit_decrements_quantity(self, mock_db):
        """Should decrement credit quantity and create redemption transaction"""
        credit_id = ObjectId()
        purchase_id = ObjectId()
        booking_id = ObjectId()
        
        mock_db.service_credits.find_one.side_effect = [
            {
                "_id": credit_id,
                "purchase_id": purchase_id,
                "service_id": "service123",
                "service_price": 50.0,
                "remaining_quantity": 2,
                "status": "available"
            },
            {
                "_id": credit_id,
                "remaining_quantity": 1,
                "status": "available"
            }
        ]
        
        mock_db.bookings.find_one.return_value = {
            "_id": booking_id,
            "client_id": "client123",
            "service_id": "service123"
        }
        
        mock_db.service_credits.update_one.return_value = Mock()
        mock_db.credit_reservations.update_one.return_value = Mock()
        mock_db.redemption_transactions.insert_one.return_value = Mock()
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.redeem_credit_for_booking(
                credit_id=str(credit_id),
                booking_id=str(booking_id),
                tenant_id="tenant123",
                staff_id="staff123"
            )
        
        assert result["service_value"] == 50.0
        mock_db.service_credits.update_one.assert_called_once()
        mock_db.redemption_transactions.insert_one.assert_called_once()
    
    def test_redeem_credit_raises_error_when_no_credits(self, mock_db):
        """Should raise error when credit has no remaining quantity"""
        credit_id = ObjectId()
        
        mock_db.service_credits.find_one.return_value = {
            "_id": credit_id,
            "remaining_quantity": 0,
            "status": "redeemed"
        }
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            with pytest.raises(BadRequestException):
                PackageBookingIntegrationService.redeem_credit_for_booking(
                    credit_id=str(credit_id),
                    booking_id="booking123",
                    tenant_id="tenant123",
                    staff_id="staff123"
                )


class TestGetBookingPackageInfo:
    """Tests for get_booking_package_info method"""
    
    def test_get_booking_package_info_returns_package_details(self, mock_db):
        """Should return package info for a booking paid via package"""
        booking_id = "booking123"
        purchase_id = ObjectId()
        credit_id = ObjectId()
        
        mock_db.redemption_transactions.find_one.return_value = {
            "_id": ObjectId(),
            "purchase_id": purchase_id,
            "credit_id": credit_id,
            "service_id": "service123",
            "service_value": 50.0,
            "redemption_date": datetime.utcnow()
        }
        
        mock_db.package_purchases.find_one.return_value = {
            "_id": purchase_id,
            "package_definition_id": ObjectId()
        }
        
        mock_db.package_definitions.find_one.return_value = {
            "_id": ObjectId(),
            "name": "3 Haircuts"
        }
        
        mock_db.service_credits.find_one.return_value = {
            "_id": credit_id,
            "remaining_quantity": 1
        }
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.get_booking_package_info(
                booking_id=booking_id,
                tenant_id="tenant123"
            )
        
        assert result is not None
        assert result["package_name"] == "3 Haircuts"
        assert result["service_value"] == 50.0
        assert result["remaining_credits"] == 1
    
    def test_get_booking_package_info_returns_none_when_not_paid_via_package(self, mock_db):
        """Should return None when booking was not paid via package"""
        mock_db.redemption_transactions.find_one.return_value = None
        
        with patch('app.services.package_booking_integration_service.Database.get_db', return_value=mock_db):
            result = PackageBookingIntegrationService.get_booking_package_info(
                booking_id="booking123",
                tenant_id="tenant123"
            )
        
        assert result is None
