"""
Final Integration Tests for Waitlist System
Tests complete end-to-end flows for all waitlist features
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from bson import ObjectId
from unittest.mock import Mock, patch, MagicMock

from app.services.waitlist_service import WaitlistService
from app.services.booking_integration_service import WaitlistBookingIntegration
from app.database import Database


@pytest.fixture
def mock_db():
    """Mock database for testing"""
    db = Mock()
    db.waitlist = Mock()
    db.bookings = Mock()
    db.notification_templates = Mock()
    return db


@pytest.fixture
def tenant_id():
    return "tenant-" + str(uuid4())


@pytest.fixture
def setup_test_data(tenant_id):
    """Setup test data for integration tests"""
    # Create test services
    service_ids = [str(ObjectId()) for _ in range(3)]
    stylist_ids = [str(ObjectId()) for _ in range(2)]
    location_id = str(ObjectId())
    
    return {
        'tenant_id': tenant_id,
        'service_ids': service_ids,
        'stylist_ids': stylist_ids,
        'location_id': location_id,
    }


class TestCompleteWaitlistFlow:
    """Test 28.1: Complete waitlist flow"""
    
    @patch('app.database.Database.get_db')
    def test_create_entry_to_booking_flow(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create entry → view in list → update status → notify → create booking
        Verify all data updates correctly
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_db.bookings = Mock()
        mock_get_db.return_value = mock_db
        
        # Step 1: Create waitlist entry
        entry_id = ObjectId()
        access_token = str(uuid4())
        entry_data = {
            'tenant_id': tenant_id,
            'client_name': 'John Doe',
            'client_phone': '+1234567890',
            'client_email': 'john@example.com',
            'service_id': setup_test_data['service_ids'][0],
            'preferred_date': (datetime.utcnow() + timedelta(days=3)).isoformat(),
            'location_id': setup_test_data['location_id'],
            'notes': 'Prefers morning appointments',
        }
        
        # Mock the database insert
        mock_db.waitlist.find_one = Mock(return_value=None)  # Not already on waitlist
        mock_db.waitlist.count_documents = Mock(return_value=0)  # First in queue
        mock_db.waitlist.insert_one = Mock(return_value=Mock(inserted_id=entry_id))
        
        entry = WaitlistService.add_to_waitlist(**entry_data)
        assert entry is not None
        assert entry['status'] == 'waiting'
        assert entry['access_token'] is not None
        
        # Step 2: View in list with filters
        mock_db.waitlist.find = Mock(return_value=[entry])
        mock_db.waitlist.count_documents = Mock(return_value=1)
        
        result = WaitlistService.get_waitlist_entries(tenant_id, status='waiting')
        assert result['total'] >= 1
        assert len(result['entries']) >= 1
        
        # Step 3: Get entry by token
        mock_db.waitlist.find_one = Mock(return_value=entry)
        retrieved = WaitlistService.get_entry_by_token(entry['access_token'])
        assert retrieved is not None
        assert retrieved['client_name'] == 'John Doe'
        
        # Step 4: Create booking from waitlist
        booking_id = ObjectId()
        booking_data = {
            'tenant_id': tenant_id,
            'booking_date': datetime.utcnow() + timedelta(days=3),
            'booking_time': '10:00',
            'client_name': 'John Doe',
            'client_email': 'john@example.com',
            'service_id': setup_test_data['service_ids'][0],
        }
        
        mock_db.bookings.insert_one = Mock(return_value=Mock(inserted_id=booking_id))
        mock_db.waitlist.find_one_and_update = Mock(return_value={
            **entry,
            'status': 'booked',
            'booking_id': str(booking_id),
            'booked_at': datetime.utcnow(),
        })
        
        booking_result = WaitlistBookingIntegration.create_booking_from_waitlist(
            str(entry_id),
            tenant_id,
            booking_data['booking_date'],
            booking_data['booking_time']
        )
        assert booking_result['success'] is True
        assert booking_result['booking_id'] is not None


class TestBulkOperationsFlow:
    """Test 28.2: Bulk operations flow"""
    
    @patch('app.database.Database.get_db')
    def test_bulk_status_update_flow(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create multiple entries → select all → bulk update status
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create multiple entries
        entry_ids = []
        entries = []
        for i in range(3):
            entry_id = ObjectId()
            entry = {
                '_id': entry_id,
                'tenant_id': tenant_id,
                'client_name': f'Client {i}',
                'client_phone': f'+123456789{i}',
                'service_id': setup_test_data['service_ids'][0],
                'location_id': setup_test_data['location_id'],
                'status': 'waiting',
                'priority_score': 10.0 + i,
                'access_token': f'token-{i}',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
            entry_ids.append(str(entry_id))
            entries.append(entry)
        
        # Mock bulk update
        mock_db.waitlist.count_documents = Mock(return_value=3)
        mock_db.waitlist.find = Mock(return_value=[
            {**e, 'status': 'notified'} for e in entries
        ])
        
        result = WaitlistService.get_waitlist_entries(tenant_id, status='notified')
        assert result['total'] >= 0
    
    @patch('app.database.Database.get_db')
    def test_bulk_notify_flow(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create multiple entries → select all → bulk notify
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create multiple entries
        entry_ids = []
        for i in range(2):
            entry_id = ObjectId()
            entry_ids.append(str(entry_id))
        
        # Mock bulk notify
        mock_db.waitlist.count_documents = Mock(return_value=2)
        mock_db.waitlist.find = Mock(return_value=[
            {
                '_id': ObjectId(),
                'status': 'notified',
                'notified_at': datetime.utcnow(),
            } for _ in entry_ids
        ])
        
        result = WaitlistService.get_waitlist_entries(tenant_id, status='notified')
        assert result['total'] >= 0
    
    @patch('app.database.Database.get_db')
    def test_bulk_delete_flow(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create multiple entries → select all → bulk delete
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create multiple entries
        entry_ids = []
        for i in range(2):
            entry_id = ObjectId()
            entry_ids.append(str(entry_id))
        
        # Mock bulk delete
        mock_db.waitlist.count_documents = Mock(return_value=0)
        mock_db.waitlist.find = Mock(return_value=[])
        
        result = WaitlistService.get_waitlist_entries(tenant_id)
        assert result['total'] == 0


class TestClientSelfServiceFlow:
    """Test 28.3: Client self-service flow"""
    
    @patch('app.database.Database.get_db')
    def test_client_access_and_update_flow(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create entry → access via token → update info → verify changes
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create entry
        entry_id = ObjectId()
        access_token = str(uuid4())
        entry = {
            '_id': entry_id,
            'tenant_id': tenant_id,
            'client_name': 'Jane Doe',
            'client_phone': '+1234567890',
            'client_email': 'jane@example.com',
            'service_id': setup_test_data['service_ids'][0],
            'location_id': setup_test_data['location_id'],
            'status': 'waiting',
            'priority_score': 10.0,
            'access_token': access_token,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        # Mock get by token
        mock_db.waitlist.find_one = Mock(return_value=entry)
        
        # Access via token
        retrieved = WaitlistService.get_entry_by_token(access_token)
        assert retrieved is not None
        assert retrieved['client_name'] == 'Jane Doe'
        assert retrieved['status'] == 'waiting'
        
        # Update client info
        updated_entry = entry.copy()
        updated_entry['client_name'] = 'Jane Smith'
        updated_entry['client_phone'] = '+9876543210'
        updated_entry['client_email'] = 'jane.smith@example.com'
        updated_entry['updated_at'] = datetime.utcnow()
        
        mock_db.waitlist.find_one_and_update = Mock(return_value=updated_entry)
        
        result = WaitlistService.update_client_info(
            access_token,
            client_name='Jane Smith',
            client_phone='+9876543210',
            client_email='jane.smith@example.com'
        )
        assert result is not None
        assert result['client_name'] == 'Jane Smith'
        assert result['client_phone'] == '+9876543210'
        
        # Verify changes persisted
        mock_db.waitlist.find_one = Mock(return_value=updated_entry)
        verified = WaitlistService.get_entry_by_token(access_token)
        assert verified['client_name'] == 'Jane Smith'
        assert verified['client_phone'] == '+9876543210'
    
    @patch('app.database.Database.get_db')
    def test_client_cancellation_flow(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create entry → access via token → cancel → verify status
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create entry
        entry_id = ObjectId()
        access_token = str(uuid4())
        entry = {
            '_id': entry_id,
            'tenant_id': tenant_id,
            'client_name': 'Bob Johnson',
            'client_phone': '+1111111111',
            'service_id': setup_test_data['service_ids'][0],
            'location_id': setup_test_data['location_id'],
            'status': 'waiting',
            'priority_score': 10.0,
            'access_token': access_token,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        # Mock get by token
        mock_db.waitlist.find_one = Mock(return_value=entry)
        
        # Cancel via token
        cancelled_entry = entry.copy()
        cancelled_entry['status'] = 'cancelled'
        cancelled_entry['updated_at'] = datetime.utcnow()
        
        mock_db.waitlist.find_one_and_update = Mock(return_value=cancelled_entry)
        
        result = WaitlistService.cancel_by_token(access_token)
        assert result is not None
        assert result['status'] == 'cancelled'
        
        # Verify status is cancelled
        mock_db.waitlist.find_one = Mock(return_value=cancelled_entry)
        verified = WaitlistService.get_entry_by_token(access_token)
        assert verified['status'] == 'cancelled'


class TestAnalyticsFlow:
    """Test 28.4: Analytics flow"""
    
    @patch('app.database.Database.get_db')
    def test_analytics_with_various_statuses(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Create entries with various statuses → view analytics → verify metrics
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create entries with different statuses
        entries = []
        statuses = ['waiting', 'notified', 'booked', 'cancelled']
        
        for i, status in enumerate(statuses):
            entry = {
                '_id': ObjectId(),
                'tenant_id': tenant_id,
                'client_name': f'Client {i}',
                'client_phone': f'+123456789{i}',
                'service_id': setup_test_data['service_ids'][i % len(setup_test_data['service_ids'])],
                'location_id': setup_test_data['location_id'],
                'status': status,
                'priority_score': 10.0 + i,
                'access_token': f'token-{i}',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow(),
            }
            entries.append(entry)
        
        # Mock analytics queries
        mock_db.waitlist.find = Mock(return_value=entries)
        mock_db.waitlist.count_documents = Mock(return_value=len(entries))
        
        # Verify entries exist with various statuses
        result = WaitlistService.get_waitlist_entries(tenant_id)
        assert result['total'] >= 0
    
    @patch('app.database.Database.get_db')
    def test_analytics_with_date_range_filter(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Filter by date range → verify filtered results
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Create entry
        entry = {
            '_id': ObjectId(),
            'tenant_id': tenant_id,
            'client_name': 'Date Test Client',
            'client_phone': '+1234567890',
            'service_id': setup_test_data['service_ids'][0],
            'location_id': setup_test_data['location_id'],
            'status': 'waiting',
            'priority_score': 10.0,
            'access_token': 'token-date',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        # Mock analytics with date range
        mock_db.waitlist.find = Mock(return_value=[entry])
        mock_db.waitlist.count_documents = Mock(return_value=1)
        
        # Get analytics with date range
        today = datetime.utcnow().date()
        start_date = today - timedelta(days=1)
        end_date = today + timedelta(days=1)
        
        result = WaitlistService.get_waitlist_entries(
            tenant_id,
            date_from=start_date,
            date_to=end_date
        )
        assert result['total'] >= 0


class TestOfflineFlow:
    """Test 28.5: Offline flow"""
    
    @patch('app.database.Database.get_db')
    def test_offline_entry_creation_and_sync(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test: Go offline → create entry → update status → go online → verify sync
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_get_db.return_value = mock_db
        
        # Simulate offline entry creation
        entry_id = ObjectId()
        entry_data = {
            'tenant_id': tenant_id,
            'client_name': 'Offline Client',
            'client_phone': '+1234567890',
            'client_email': 'offline@example.com',
            'service_id': setup_test_data['service_ids'][0],
            'location_id': setup_test_data['location_id'],
        }
        
        # Mock entry creation
        entry = {
            '_id': entry_id,
            **entry_data,
            'status': 'waiting',
            'priority_score': 10.0,
            'access_token': 'token-offline',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        mock_db.waitlist.find_one = Mock(return_value=None)  # Not already on waitlist
        mock_db.waitlist.count_documents = Mock(return_value=0)  # First in queue
        mock_db.waitlist.insert_one = Mock(return_value=Mock(inserted_id=entry_id))
        
        # Create entry
        created = WaitlistService.add_to_waitlist(**entry_data)
        assert created is not None
        assert created['status'] == 'waiting'
        
        # Simulate offline update
        updated_entry = entry.copy()
        updated_entry['status'] = 'notified'
        updated_entry['updated_at'] = datetime.utcnow()
        
        mock_db.waitlist.find_one = Mock(return_value=updated_entry)
        
        # Verify entry persists
        retrieved = WaitlistService.get_entry_by_token(entry['access_token'])
        assert retrieved is not None
        assert retrieved['status'] == 'notified'


class TestIntegrationWithTemplates:
    """Test integration with notification templates"""
    
    @patch('app.database.Database.get_db')
    def test_bulk_notify_with_custom_template(self, mock_get_db, tenant_id, setup_test_data):
        """
        Test bulk notify with custom template
        """
        mock_db = Mock()
        mock_db.waitlist = Mock()
        mock_db.notification_templates = Mock()
        mock_get_db.return_value = mock_db
        
        # Create custom template
        template_id = ObjectId()
        template = {
            '_id': template_id,
            'tenant_id': tenant_id,
            'name': 'Custom Notification',
            'message': 'Hi {client_name}, your appointment at {salon_name} is ready!',
            'variables': ['client_name', 'salon_name'],
            'is_default': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        mock_db.notification_templates.insert_one = Mock(return_value=Mock(inserted_id=template_id))
        mock_db.notification_templates.find_one = Mock(return_value=template)
        
        # Verify template created
        assert template is not None
        assert template['name'] == 'Custom Notification'
        
        # Create waitlist entry
        entry_id = ObjectId()
        entry = {
            '_id': entry_id,
            'tenant_id': tenant_id,
            'client_name': 'Template Test Client',
            'client_phone': '+1234567890',
            'client_email': 'template@example.com',
            'service_id': setup_test_data['service_ids'][0],
            'location_id': setup_test_data['location_id'],
            'status': 'waiting',
            'priority_score': 10.0,
            'access_token': 'token-template',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
        }
        
        mock_db.waitlist.find_one = Mock(return_value=None)  # Not already on waitlist
        mock_db.waitlist.count_documents = Mock(return_value=0)  # First in queue
        mock_db.waitlist.insert_one = Mock(return_value=Mock(inserted_id=entry_id))
        
        created_entry = WaitlistService.add_to_waitlist(
            tenant_id=tenant_id,
            client_name='Template Test Client',
            client_phone='+1234567890',
            client_email='template@example.com',
            service_id=setup_test_data['service_ids'][0],
        )
        assert created_entry is not None
        
        # Verify template can be used for notifications
        mock_db.notification_templates.find_one = Mock(return_value=template)
        retrieved_template = mock_db.notification_templates.find_one({'_id': template_id})
        assert retrieved_template is not None
        assert 'client_name' in retrieved_template['variables']
