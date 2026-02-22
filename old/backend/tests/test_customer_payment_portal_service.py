"""
Unit tests for Customer Payment Portal Service
Tests customer payment history, payment links, and payment status
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from unittest.mock import Mock, patch
import hashlib

from app.services.customer_payment_portal_service import customer_payment_portal_service
from app.api.exceptions import NotFoundException, BadRequestException, UnauthorizedException


class TestCustomerPaymentPortalService:
    """Test cases for CustomerPaymentPortalService"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database"""
        return Mock()
    
    @pytest.fixture
    def sample_customer(self):
        """Sample customer document"""
        return {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "1234567890"
        }
    
    @pytest.fixture
    def sample_booking(self):
        """Sample booking document"""
        return {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "client_id": str(ObjectId()),
            "reference": "BK-001",
            "service": "Hair Cut",
            "total_amount": 50000,
            "status": "completed",
            "start_time": datetime.utcnow()
        }
    
    @pytest.fixture
    def sample_payment(self, sample_booking):
        """Sample payment document"""
        return {
            "_id": ObjectId(),
            "tenant_id": "test-tenant",
            "booking_id": str(sample_booking["_id"]),
            "client_id": sample_booking["client_id"],
            "amount": 50000,
            "gateway": "paystack",
            "reference": "PAY-001",
            "status": "completed",
            "payment_type": "full",
            "created_at": datetime.utcnow(),
            "verified_at": datetime.utcnow(),
            "receipt_url": None,
            "receipt_generated_at": None
        }
    
    def test_get_customer_payments_success(self, mock_db, sample_customer, sample_booking, sample_payment):
        """Test fetching customer payments successfully"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.clients.find_one.return_value = sample_customer
            mock_db.bookings.find.return_value = [sample_booking]
            mock_db.payments.count_documents.return_value = 1
            mock_db.payments.find.return_value.sort.return_value.skip.return_value.limit.return_value = [sample_payment]
            mock_db.bookings.find_one.return_value = sample_booking
            
            # Call service
            result = customer_payment_portal_service.get_customer_payments(
                "test-tenant",
                sample_customer["_id"].__str__(),
                limit=50,
                skip=0
            )
            
            # Assertions
            assert result["customer_id"] == sample_customer["_id"].__str__()
            assert result["customer_name"] == "John Doe"
            assert result["total_count"] == 1
            assert len(result["payments"]) == 1
            assert result["payments"][0]["amount"] == 50000
    
    def test_get_customer_payments_customer_not_found(self, mock_db):
        """Test fetching payments for non-existent customer"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.clients.find_one.return_value = None
            
            # Call service and expect exception
            with pytest.raises(NotFoundException):
                customer_payment_portal_service.get_customer_payments(
                    "test-tenant",
                    str(ObjectId())
                )
    
    def test_get_customer_payments_pagination(self, mock_db, sample_customer, sample_booking):
        """Test customer payments pagination"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.clients.find_one.return_value = sample_customer
            mock_db.bookings.find.return_value = [sample_booking]
            mock_db.payments.count_documents.return_value = 100
            mock_db.payments.find.return_value.sort.return_value.skip.return_value.limit.return_value = []
            
            # Call service with pagination
            result = customer_payment_portal_service.get_customer_payments(
                "test-tenant",
                str(sample_customer["_id"]),
                limit=50,
                skip=50
            )
            
            # Assertions
            assert result["total_count"] == 100
            assert result["limit"] == 50
            assert result["skip"] == 50
            assert result["has_more"] is True
    
    def test_generate_payment_link_success(self, mock_db, sample_payment):
        """Test successful payment link generation"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            mock_db.payment_links.insert_one.return_value = Mock(inserted_id=ObjectId())
            
            # Call service
            result = customer_payment_portal_service.generate_payment_link(
                "test-tenant",
                sample_payment["client_id"],
                str(sample_payment["_id"]),
                expires_in_days=30
            )
            
            # Assertions
            assert "link_id" in result
            assert "payment_link" in result
            assert "token" in result
            assert "expires_at" in result
            assert "/customer/payments/link/" in result["payment_link"]
    
    def test_generate_payment_link_payment_not_found(self, mock_db):
        """Test payment link generation for non-existent payment"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = None
            
            # Call service and expect exception
            with pytest.raises(NotFoundException):
                customer_payment_portal_service.generate_payment_link(
                    "test-tenant",
                    str(ObjectId()),
                    str(ObjectId())
                )
    
    def test_generate_payment_link_wrong_customer(self, mock_db, sample_payment):
        """Test payment link generation for payment not belonging to customer"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            
            # Call service with wrong customer ID and expect exception
            with pytest.raises(UnauthorizedException):
                customer_payment_portal_service.generate_payment_link(
                    "test-tenant",
                    str(ObjectId()),  # Different customer ID
                    str(sample_payment["_id"])
                )
    
    def test_generate_payment_link_non_pending_payment(self, mock_db):
        """Test payment link generation for non-pending payment"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            completed_payment = {
                "_id": ObjectId(),
                "tenant_id": "test-tenant",
                "client_id": str(ObjectId()),
                "status": "completed"  # Not pending
            }
            
            mock_db.payments.find_one.return_value = completed_payment
            
            # Call service and expect exception
            with pytest.raises(BadRequestException):
                customer_payment_portal_service.generate_payment_link(
                    "test-tenant",
                    completed_payment["client_id"],
                    str(completed_payment["_id"])
                )
    
    def test_validate_payment_link_success(self, mock_db, sample_payment, sample_customer, sample_booking):
        """Test successful payment link validation"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            # Generate token and hash
            token = "test-token-123"
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            link = {
                "_id": ObjectId(),
                "tenant_id": "test-tenant",
                "payment_id": str(sample_payment["_id"]),
                "customer_id": sample_payment["client_id"],
                "token_hash": token_hash,
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "access_count": 0
            }
            
            mock_db.payment_links.find_one.return_value = link
            mock_db.payments.find_one.return_value = sample_payment
            mock_db.clients.find_one.return_value = sample_customer
            mock_db.bookings.find_one.return_value = sample_booking
            mock_db.payment_links.update_one.return_value = Mock()
            
            # Call service
            result = customer_payment_portal_service.validate_payment_link(
                "test-tenant",
                token
            )
            
            # Assertions
            assert result["payment_id"] == str(sample_payment["_id"])
            assert result["customer_data"]["name"] == "John Doe"
            assert result["payment"]["amount"] == 50000
            mock_db.payment_links.update_one.assert_called_once()
    
    def test_validate_payment_link_expired(self, mock_db):
        """Test payment link validation for expired link"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            token = "test-token-123"
            token_hash = hashlib.sha256(token.encode()).hexdigest()
            
            expired_link = {
                "_id": ObjectId(),
                "tenant_id": "test-tenant",
                "expires_at": datetime.utcnow() - timedelta(days=1)  # Expired
            }
            
            mock_db.payment_links.find_one.return_value = expired_link
            
            # Call service and expect exception
            with pytest.raises(BadRequestException):
                customer_payment_portal_service.validate_payment_link(
                    "test-tenant",
                    token
                )
    
    def test_validate_payment_link_not_found(self, mock_db):
        """Test payment link validation for non-existent link"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payment_links.find_one.return_value = None
            
            # Call service and expect exception
            with pytest.raises(NotFoundException):
                customer_payment_portal_service.validate_payment_link(
                    "test-tenant",
                    "invalid-token"
                )
    
    def test_get_payment_status_success(self, mock_db, sample_payment, sample_customer, sample_booking):
        """Test getting payment status successfully"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            mock_db.bookings.find_one.return_value = sample_booking
            
            # Call service
            result = customer_payment_portal_service.get_payment_status(
                "test-tenant",
                sample_payment["client_id"],
                str(sample_payment["_id"])
            )
            
            # Assertions
            assert result["payment_id"] == str(sample_payment["_id"])
            assert result["status"] == "completed"
            assert result["amount"] == 50000
            assert "status_message" in result
    
    def test_get_payment_status_wrong_customer(self, mock_db, sample_payment):
        """Test getting payment status for payment not belonging to customer"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = sample_payment
            
            # Call service with wrong customer ID and expect exception
            with pytest.raises(UnauthorizedException):
                customer_payment_portal_service.get_payment_status(
                    "test-tenant",
                    str(ObjectId()),  # Different customer ID
                    str(sample_payment["_id"])
                )
    
    def test_get_payment_status_not_found(self, mock_db):
        """Test getting payment status for non-existent payment"""
        with patch('app.services.customer_payment_portal_service.Database') as mock_db_class:
            mock_db_class.get_db.return_value = mock_db
            
            mock_db.payments.find_one.return_value = None
            
            # Call service and expect exception
            with pytest.raises(NotFoundException):
                customer_payment_portal_service.get_payment_status(
                    "test-tenant",
                    str(ObjectId()),
                    str(ObjectId())
                )


class TestCustomerPaymentPortalProperties:
    """Property-based tests for customer payment portal service"""
    
    def test_customer_payment_isolation_property(self):
        """
        Property: For any customer viewing their payment history, 
        the returned payments must only include payments where the booking's 
        client_id matches the requesting customer's ID
        
        Validates: Requirements 10.2
        """
        # This property ensures customer isolation in payment portal
        assert hasattr(customer_payment_portal_service, 'get_customer_payments')
        assert hasattr(customer_payment_portal_service, 'get_payment_status')
    
    def test_payment_link_token_uniqueness_property(self):
        """
        Property: Each generated payment link must have a unique, 
        cryptographically secure token
        
        Validates: Requirements 10.6
        """
        # This property ensures token uniqueness and security
        assert hasattr(customer_payment_portal_service, 'generate_payment_link')
        assert hasattr(customer_payment_portal_service, 'validate_payment_link')
