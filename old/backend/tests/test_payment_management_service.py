"""
Unit tests for Payment Management Service
Tests payment detail retrieval and refund processing
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.payment_management_service import PaymentManagementService
from app.api.exceptions import NotFoundException, BadRequestException


class TestPaymentDetailRetrieval:
    """Tests for get_payment_detail method"""
    
    @patch('app.services.payment_management_service.Database')
    def test_get_payment_detail_success(self, mock_db):
        """Test successful payment detail retrieval"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "booking_id": str(ObjectId()),
            "client_id": str(ObjectId()),
            "amount": 50000.0,
            "gateway": "paystack",
            "reference": "PAY-001",
            "status": "completed",
            "payment_type": "full",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_booking = {
            "_id": ObjectId(mock_payment["booking_id"]),
            "reference": "BK-001",
            "service": "Hair Cut",
            "client_id": mock_payment["client_id"],
            "status": "completed"
        }
        
        mock_client = {
            "_id": ObjectId(mock_payment["client_id"]),
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "08012345678"
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db_instance.bookings.find_one.return_value = mock_booking
        mock_db_instance.clients.find_one.return_value = mock_client
        mock_db_instance.payment_refunds.find.return_value = []
        
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.get_payment_detail(tenant_id, payment_id)
        
        # Assert
        assert result["id"] == payment_id
        assert result["amount"] == 50000.0
        assert result["status"] == "completed"
        assert result["booking_data"] is not None
        assert result["client_data"] is not None
        assert result["booking_data"]["reference"] == "BK-001"
        assert result["client_data"]["name"] == "John Doe"
    
    @patch('app.services.payment_management_service.Database')
    def test_get_payment_detail_not_found(self, mock_db):
        """Test payment detail retrieval when payment not found"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = None
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(NotFoundException):
            PaymentManagementService.get_payment_detail(tenant_id, payment_id)
    
    @patch('app.services.payment_management_service.Database')
    def test_get_payment_detail_invalid_id_format(self, mock_db):
        """Test payment detail retrieval with invalid ID format"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = "invalid_id"
        
        mock_db.get_db.return_value = MagicMock()
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentManagementService.get_payment_detail(tenant_id, payment_id)
    
    @patch('app.services.payment_management_service.Database')
    def test_get_payment_detail_with_refund_history(self, mock_db):
        """Test payment detail retrieval includes refund history"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "partially_refunded",
            "refund_amount": 10000.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        mock_refund = {
            "_id": ObjectId(),
            "payment_id": payment_id,
            "refund_amount": 10000.0,
            "refund_type": "partial",
            "reason": "Customer requested partial refund",
            "status": "completed",
            "created_at": datetime.utcnow()
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db_instance.bookings.find_one.return_value = None
        mock_db_instance.clients.find_one.return_value = None
        
        # Mock the find().sort() chain
        mock_find = MagicMock()
        mock_find.sort.return_value = [mock_refund]
        mock_db_instance.payment_refunds.find.return_value = mock_find
        
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.get_payment_detail(tenant_id, payment_id)
        
        # Assert
        assert result["status"] == "partially_refunded"
        assert result["refund_history"] is not None
        assert len(result["refund_history"]) == 1
        assert result["refund_history"][0]["refund_amount"] == 10000.0


class TestRefundValidation:
    """Tests for validate_refund_amount method"""
    
    @patch('app.services.payment_management_service.Database')
    def test_validate_refund_amount_success(self, mock_db):
        """Test successful refund amount validation"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 10000.0
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "completed",
            "refund_amount": 0
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.validate_refund_amount(
            payment_id, tenant_id, refund_amount
        )
        
        # Assert
        assert result["valid"] is True
        assert result["original_amount"] == 50000.0
        assert result["available_for_refund"] == 50000.0
        assert result["requested_refund"] == 10000.0
        assert result["will_be_fully_refunded"] is False
    
    @patch('app.services.payment_management_service.Database')
    def test_validate_refund_amount_full_refund(self, mock_db):
        """Test validation for full refund"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 50000.0
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "completed",
            "refund_amount": 0
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.validate_refund_amount(
            payment_id, tenant_id, refund_amount
        )
        
        # Assert
        assert result["valid"] is True
        assert result["will_be_fully_refunded"] is True
    
    @patch('app.services.payment_management_service.Database')
    def test_validate_refund_amount_exceeds_available(self, mock_db):
        """Test validation fails when refund exceeds available amount"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 60000.0
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "completed",
            "refund_amount": 0
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentManagementService.validate_refund_amount(
                payment_id, tenant_id, refund_amount
            )
    
    @patch('app.services.payment_management_service.Database')
    def test_validate_refund_already_refunded(self, mock_db):
        """Test validation fails for already refunded payment"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 10000.0
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "refunded",
            "refund_amount": 50000.0
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentManagementService.validate_refund_amount(
                payment_id, tenant_id, refund_amount
            )
    
    @patch('app.services.payment_management_service.Database')
    def test_validate_refund_invalid_status(self, mock_db):
        """Test validation fails for invalid payment status"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 10000.0
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "pending",
            "refund_amount": 0
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentManagementService.validate_refund_amount(
                payment_id, tenant_id, refund_amount
            )


class TestRefundProcessing:
    """Tests for process_refund method"""
    
    @patch('app.services.payment_management_service.Database')
    def test_process_refund_success(self, mock_db):
        """Test successful refund processing"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 10000.0
        reason = "Customer requested refund due to service issue"
        refund_type = "partial"
        processed_by = "user_123"
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "completed",
            "refund_amount": 0,
            "booking_id": None
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db_instance.payment_refunds.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.process_refund(
            tenant_id=tenant_id,
            payment_id=payment_id,
            refund_amount=refund_amount,
            reason=reason,
            refund_type=refund_type,
            processed_by=processed_by
        )
        
        # Assert
        assert result["payment_id"] == payment_id
        assert result["refund_amount"] == refund_amount
        assert result["refund_type"] == refund_type
        assert result["status"] == "completed"
        assert "refund_id" in result
        
        # Verify payment was updated
        mock_db_instance.payments.update_one.assert_called_once()
    
    @patch('app.services.payment_management_service.Database')
    def test_process_refund_full_refund(self, mock_db):
        """Test processing full refund updates status to refunded"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 50000.0
        reason = "Full refund requested by customer"
        refund_type = "full"
        processed_by = "user_123"
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "completed",
            "refund_amount": 0,
            "booking_id": None
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db_instance.payment_refunds.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.process_refund(
            tenant_id=tenant_id,
            payment_id=payment_id,
            refund_amount=refund_amount,
            reason=reason,
            refund_type=refund_type,
            processed_by=processed_by
        )
        
        # Assert
        assert result["refund_type"] == "full"
        
        # Verify payment status was updated to "refunded"
        call_args = mock_db_instance.payments.update_one.call_args
        update_dict = call_args[0][1]["$set"]
        assert update_dict["status"] == "refunded"
    
    @patch('app.services.payment_management_service.Database')
    def test_process_refund_partial_refund(self, mock_db):
        """Test processing partial refund updates status to partially_refunded"""
        # Setup
        tenant_id = "test_tenant"
        payment_id = str(ObjectId())
        refund_amount = 20000.0
        reason = "Partial refund for service adjustment"
        refund_type = "partial"
        processed_by = "user_123"
        
        mock_payment = {
            "_id": ObjectId(payment_id),
            "tenant_id": tenant_id,
            "amount": 50000.0,
            "status": "completed",
            "refund_amount": 0,
            "booking_id": None
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.payments.find_one.return_value = mock_payment
        mock_db_instance.payment_refunds.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.process_refund(
            tenant_id=tenant_id,
            payment_id=payment_id,
            refund_amount=refund_amount,
            reason=reason,
            refund_type=refund_type,
            processed_by=processed_by
        )
        
        # Assert
        assert result["refund_type"] == "partial"
        
        # Verify payment status was updated to "partially_refunded"
        call_args = mock_db_instance.payments.update_one.call_args
        update_dict = call_args[0][1]["$set"]
        assert update_dict["status"] == "partially_refunded"



class TestManualPaymentRecording:
    """Tests for record_manual_payment method"""
    
    @patch('app.services.payment_management_service.Database')
    def test_record_manual_payment_success(self, mock_db):
        """Test successful manual payment recording"""
        # Setup
        tenant_id = "test_tenant"
        booking_id = str(ObjectId())
        client_id = str(ObjectId())
        amount = 50000.0
        payment_method = "cash"
        recorded_by = "user_123"
        
        mock_booking = {
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "client_id": client_id,
            "reference": "BK-001"
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.bookings.find_one.return_value = mock_booking
        mock_db_instance.payments.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.record_manual_payment(
            tenant_id=tenant_id,
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            recorded_by=recorded_by
        )
        
        # Assert
        assert result["id"] is not None
        assert result["booking_id"] == booking_id
        assert result["amount"] == amount
        assert result["gateway"] == "manual"
        assert result["status"] == "completed"
        assert result["is_manual"] is True
        assert result["recorded_by"] == recorded_by
        assert result["payment_method"] == payment_method
        
        # Verify booking was updated
        mock_db_instance.bookings.update_one.assert_called_once()
    
    @patch('app.services.payment_management_service.Database')
    def test_record_manual_payment_booking_not_found(self, mock_db):
        """Test manual payment recording fails when booking not found"""
        # Setup
        tenant_id = "test_tenant"
        booking_id = str(ObjectId())
        amount = 50000.0
        payment_method = "cash"
        recorded_by = "user_123"
        
        mock_db_instance = MagicMock()
        mock_db_instance.bookings.find_one.return_value = None
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(NotFoundException):
            PaymentManagementService.record_manual_payment(
                tenant_id=tenant_id,
                booking_id=booking_id,
                amount=amount,
                payment_method=payment_method,
                recorded_by=recorded_by
            )
    
    @patch('app.services.payment_management_service.Database')
    def test_record_manual_payment_invalid_amount(self, mock_db):
        """Test manual payment recording fails with invalid amount"""
        # Setup
        tenant_id = "test_tenant"
        booking_id = str(ObjectId())
        amount = -1000.0
        payment_method = "cash"
        recorded_by = "user_123"
        
        mock_booking = {
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "client_id": str(ObjectId())
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.bookings.find_one.return_value = mock_booking
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentManagementService.record_manual_payment(
                tenant_id=tenant_id,
                booking_id=booking_id,
                amount=amount,
                payment_method=payment_method,
                recorded_by=recorded_by
            )
    
    @patch('app.services.payment_management_service.Database')
    def test_record_manual_payment_invalid_method(self, mock_db):
        """Test manual payment recording fails with invalid payment method"""
        # Setup
        tenant_id = "test_tenant"
        booking_id = str(ObjectId())
        amount = 50000.0
        payment_method = "invalid_method"
        recorded_by = "user_123"
        
        mock_booking = {
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "client_id": str(ObjectId())
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.bookings.find_one.return_value = mock_booking
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute & Assert
        with pytest.raises(BadRequestException):
            PaymentManagementService.record_manual_payment(
                tenant_id=tenant_id,
                booking_id=booking_id,
                amount=amount,
                payment_method=payment_method,
                recorded_by=recorded_by
            )
    
    @patch('app.services.payment_management_service.Database')
    def test_record_manual_payment_with_reference_and_notes(self, mock_db):
        """Test manual payment recording with optional reference and notes"""
        # Setup
        tenant_id = "test_tenant"
        booking_id = str(ObjectId())
        client_id = str(ObjectId())
        amount = 50000.0
        payment_method = "bank_transfer"
        recorded_by = "user_123"
        reference = "TRANSFER-12345"
        notes = "Customer transferred via bank"
        
        mock_booking = {
            "_id": ObjectId(booking_id),
            "tenant_id": tenant_id,
            "client_id": client_id
        }
        
        mock_db_instance = MagicMock()
        mock_db_instance.bookings.find_one.return_value = mock_booking
        mock_db_instance.payments.insert_one.return_value = MagicMock(
            inserted_id=ObjectId()
        )
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        result = PaymentManagementService.record_manual_payment(
            tenant_id=tenant_id,
            booking_id=booking_id,
            amount=amount,
            payment_method=payment_method,
            recorded_by=recorded_by,
            reference=reference,
            notes=notes
        )
        
        # Assert
        assert result["reference"] == reference
        assert result["notes"] == notes
