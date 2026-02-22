"""
Unit tests for Receipt Service
Tests receipt generation and email delivery
"""
import pytest
from datetime import datetime
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.receipt_service import ReceiptService
from app.api.exceptions import NotFoundException, BadRequestException


class TestReceiptNumberGeneration:
    """Tests for receipt number generation"""
    
    @patch('app.services.receipt_service.Database')
    def test_generate_receipt_number_success(self, mock_db):
        """Test successful receipt number generation"""
        # Setup
        tenant_id = str(ObjectId())
        
        mock_db_instance = MagicMock()
        mock_db_instance.payment_receipts.count_documents.return_value = 5
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        receipt_number = ReceiptService.generate_receipt_number(tenant_id)
        
        # Assert
        assert receipt_number is not None
        assert receipt_number.startswith("RCP-")
        assert "000006" in receipt_number  # count + 1
    
    @patch('app.services.receipt_service.Database')
    def test_generate_receipt_number_first_receipt(self, mock_db):
        """Test receipt number generation for first receipt"""
        # Setup
        tenant_id = str(ObjectId())
        
        mock_db_instance = MagicMock()
        mock_db_instance.payment_receipts.count_documents.return_value = 0
        mock_db.get_db.return_value = mock_db_instance
        
        # Execute
        receipt_number = ReceiptService.generate_receipt_number(tenant_id)
        
        # Assert
        assert receipt_number is not None
        assert "000001" in receipt_number


class TestReceiptDataFormatting:
    """Tests for receipt data formatting"""
    
    def test_format_receipt_data_complete(self):
        """Test receipt data formatting with all data"""
        # Setup
        payment = {
            "reference": "PAY-001",
            "amount": 50000.0,
            "payment_method": "card",
            "gateway": "paystack",
            "created_at": datetime.utcnow(),
            "status": "completed",
            "is_manual": False
        }
        
        booking = {
            "reference": "BK-001",
            "service": "Hair Cut",
            "start_time": datetime.utcnow()
        }
        
        client = {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "08012345678"
        }
        
        salon_info = {
            "name": "Test Salon",
            "address": "123 Main St",
            "phone": "08012345678",
            "email": "salon@example.com"
        }
        
        # Execute
        result = ReceiptService.format_receipt_data(payment, booking, client, salon_info)
        
        # Assert
        assert result["payment_reference"] == "PAY-001"
        assert result["payment_amount"] == 50000.0
        assert result["client_name"] == "John Doe"
        assert result["booking_reference"] == "BK-001"
        assert result["salon_name"] == "Test Salon"
    
    def test_format_receipt_data_minimal(self):
        """Test receipt data formatting with minimal data"""
        # Setup
        payment = {
            "reference": "PAY-001",
            "amount": 50000.0,
            "gateway": "paystack",
            "created_at": datetime.utcnow(),
            "status": "completed"
        }
        
        # Execute
        result = ReceiptService.format_receipt_data(payment)
        
        # Assert
        assert result["payment_reference"] == "PAY-001"
        assert result["payment_amount"] == 50000.0
        assert result["booking_reference"] is None
        assert result["client_name"] is None


class TestPDFGeneration:
    """Tests for PDF generation"""
    
    def test_generate_pdf_receipt_success(self):
        """Test successful PDF receipt generation"""
        # Setup
        receipt_data = {
            "payment_reference": "PAY-001",
            "payment_amount": 50000.0,
            "payment_method": "card",
            "payment_date": datetime.utcnow(),
            "payment_status": "completed",
            "is_manual": False,
            "booking_reference": "BK-001",
            "booking_service": "Hair Cut",
            "booking_date": datetime.utcnow(),
            "client_name": "John Doe",
            "client_email": "john@example.com",
            "client_phone": "08012345678",
            "salon_name": "Test Salon",
            "salon_address": "123 Main St",
            "salon_phone": "08012345678",
            "salon_email": "salon@example.com"
        }
        
        receipt_number = "RCP-TEST-000001"
        
        # Execute
        pdf_bytes = ReceiptService.generate_pdf_receipt(receipt_data, receipt_number)
        
        # Assert
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert isinstance(pdf_bytes, bytes)
        # PDF files start with %PDF
        assert pdf_bytes.startswith(b"%PDF")
    
    def test_generate_pdf_receipt_minimal_data(self):
        """Test PDF generation with minimal data"""
        # Setup
        receipt_data = {
            "payment_reference": "PAY-001",
            "payment_amount": 50000.0,
            "payment_method": "cash",
            "payment_date": datetime.utcnow(),
            "payment_status": "completed",
            "is_manual": True,
            "salon_name": "Salon"
        }
        
        receipt_number = "RCP-TEST-000001"
        
        # Execute
        pdf_bytes = ReceiptService.generate_pdf_receipt(receipt_data, receipt_number)
        
        # Assert
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")
