"""
Tests for duplicate detection service
"""
import pytest
from datetime import datetime, timedelta
from bson import ObjectId
from app.services.duplicate_detection_service import DuplicateDetectionService
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-123"


@pytest.fixture
def sample_clients(db, tenant_id):
    """Create sample clients for testing"""
    clients = [
        {
            "tenant_id": tenant_id,
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john.smith@example.com",
            "address": "123 Main St",
            "tags": ["vip"],
            "total_visits": 5,
            "total_spent": 500.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "tenant_id": tenant_id,
            "name": "John Smyth",  # Similar name
            "phone": "+1-555-0101",  # Same phone
            "email": "john.smyth@example.com",
            "address": "123 Main Street",
            "tags": ["regular"],
            "total_visits": 3,
            "total_spent": 300.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "tenant_id": tenant_id,
            "name": "Jane Doe",
            "phone": "+1-555-0102",
            "email": "jane.doe@example.com",
            "address": "456 Oak Ave",
            "tags": ["new"],
            "total_visits": 1,
            "total_spent": 100.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    result = db.clients.insert_many(clients)
    return result.inserted_ids


class TestDuplicateDetection:
    """Test duplicate detection functionality"""
    
    def test_calculate_similarity_identical_strings(self):
        """Test similarity calculation for identical strings"""
        score = DuplicateDetectionService._calculate_similarity("John Smith", "John Smith")
        assert score == 1.0
    
    def test_calculate_similarity_similar_strings(self):
        """Test similarity calculation for similar strings"""
        score = DuplicateDetectionService._calculate_similarity("John Smith", "John Smyth")
        assert score > 0.8  # Should be high similarity
    
    def test_calculate_similarity_different_strings(self):
        """Test similarity calculation for different strings"""
        score = DuplicateDetectionService._calculate_similarity("John", "Jane")
        assert score < 0.5  # Should be low similarity
    
    def test_calculate_similarity_empty_strings(self):
        """Test similarity calculation with empty strings"""
        score = DuplicateDetectionService._calculate_similarity("", "")
        assert score == 0.0
    
    def test_normalize_phone(self):
        """Test phone normalization"""
        assert DuplicateDetectionService._normalize_phone("+1-555-0101") == "15550101"
        assert DuplicateDetectionService._normalize_phone("(555) 0101") == "5550101"
        assert DuplicateDetectionService._normalize_phone("") == ""
    
    def test_calculate_duplicate_score_identical_clients(self):
        """Test duplicate score for identical clients"""
        client1 = {
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john@example.com"
        }
        client2 = {
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john@example.com"
        }
        
        score = DuplicateDetectionService._calculate_duplicate_score(client1, client2)
        assert score == 1.0
    
    def test_calculate_duplicate_score_similar_clients(self):
        """Test duplicate score for similar clients"""
        client1 = {
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john.smith@example.com"
        }
        client2 = {
            "name": "John Smyth",
            "phone": "+1-555-0101",
            "email": "john.smyth@example.com"
        }
        
        score = DuplicateDetectionService._calculate_duplicate_score(client1, client2)
        assert score > 0.8  # Should be high similarity due to matching phone
    
    def test_calculate_duplicate_score_different_clients(self):
        """Test duplicate score for different clients"""
        client1 = {
            "name": "John Smith",
            "phone": "+1-555-0101",
            "email": "john@example.com"
        }
        client2 = {
            "name": "Jane Doe",
            "phone": "+1-555-0102",
            "email": "jane@example.com"
        }
        
        score = DuplicateDetectionService._calculate_duplicate_score(client1, client2)
        assert score < 0.5  # Should be low similarity
    
    def test_find_duplicates(self, db, tenant_id, sample_clients):
        """Test finding duplicate clients"""
        duplicates = DuplicateDetectionService.find_duplicates(tenant_id)
        
        # Should find at least one duplicate pair (John Smith and John Smyth)
        assert len(duplicates) > 0
        
        # Check first duplicate pair
        dup = duplicates[0]
        assert dup["similarity_score"] > 0.8
        assert dup["phone_match"] == 1.0  # Same phone
    
    def test_merge_clients(self, db, tenant_id, sample_clients):
        """Test merging two clients"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        # Merge client 2 into client 1
        merged = DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id
        )
        
        # Check merged data
        assert merged["_id"] == ObjectId(client1_id)
        assert merged["merged_from"] == client2_id
        assert "merge_date" in merged
        
        # Check that secondary client is marked as merged
        secondary = db.clients.find_one({"_id": ObjectId(client2_id)})
        assert secondary["is_merged"] is True
        assert secondary["merged_into"] == client1_id
    
    def test_merge_clients_with_field_selections(self, db, tenant_id, sample_clients):
        """Test merging clients with field selections"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        # Merge with field selections (keep secondary email)
        merged = DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id,
            field_selections={"email": "secondary"}
        )
        
        # Check that secondary email was used
        assert merged["email"] == "john.smyth@example.com"
    
    def test_merge_clients_combines_tags(self, db, tenant_id, sample_clients):
        """Test that merge combines tags from both clients"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        merged = DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id
        )
        
        # Check that tags are combined
        assert "vip" in merged["tags"]
        assert "regular" in merged["tags"]
    
    def test_merge_updates_related_records(self, db, tenant_id, sample_clients):
        """Test that merge updates all related records"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        # Create related records for secondary client
        db.bookings.insert_one({
            "tenant_id": tenant_id,
            "client_id": client2_id,
            "service_id": "service-1",
            "created_at": datetime.utcnow()
        })
        
        db.payments.insert_one({
            "tenant_id": tenant_id,
            "client_id": client2_id,
            "amount": 100.0,
            "created_at": datetime.utcnow()
        })
        
        # Merge clients
        DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id
        )
        
        # Check that related records were updated
        booking = db.bookings.find_one({"service_id": "service-1"})
        assert booking["client_id"] == client1_id
        
        payment = db.payments.find_one({"amount": 100.0})
        assert payment["client_id"] == client1_id
    
    def test_undo_merge(self, db, tenant_id, sample_clients):
        """Test undoing a merge"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        # Merge clients
        merged = DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id
        )
        
        # Get merge record
        merge_record = db.client_merges.find_one({
            "primary_client_id": client1_id,
            "secondary_client_id": client2_id,
            "tenant_id": tenant_id
        })
        
        # Undo merge
        restored = DuplicateDetectionService.undo_merge(
            merge_id=str(merge_record["_id"]),
            tenant_id=tenant_id
        )
        
        # Check that secondary client is restored
        secondary = db.clients.find_one({"_id": ObjectId(client2_id)})
        assert secondary["is_merged"] is False
        assert secondary["merged_into"] is None
    
    def test_undo_merge_reverts_related_records(self, db, tenant_id, sample_clients):
        """Test that undo merge reverts related records"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        # Create related record for secondary client
        db.bookings.insert_one({
            "tenant_id": tenant_id,
            "client_id": client2_id,
            "service_id": "service-1",
            "created_at": datetime.utcnow()
        })
        
        # Merge clients
        merged = DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id
        )
        
        # Get merge record
        merge_record = db.client_merges.find_one({
            "primary_client_id": client1_id,
            "secondary_client_id": client2_id,
            "tenant_id": tenant_id
        })
        
        # Undo merge
        DuplicateDetectionService.undo_merge(
            merge_id=str(merge_record["_id"]),
            tenant_id=tenant_id
        )
        
        # Check that related records were reverted
        booking = db.bookings.find_one({"service_id": "service-1"})
        assert booking["client_id"] == client2_id
    
    def test_undo_merge_expires_after_24_hours(self, db, tenant_id, sample_clients):
        """Test that merge cannot be undone after 24 hours"""
        client1_id = str(sample_clients[0])
        client2_id = str(sample_clients[1])
        
        # Merge clients
        DuplicateDetectionService.merge_clients(
            primary_client_id=client1_id,
            secondary_client_id=client2_id,
            tenant_id=tenant_id
        )
        
        # Get merge record and manually expire it
        merge_record = db.client_merges.find_one({
            "primary_client_id": client1_id,
            "secondary_client_id": client2_id,
            "tenant_id": tenant_id
        })
        
        # Update expires_at to past
        db.client_merges.update_one(
            {"_id": merge_record["_id"]},
            {"$set": {"expires_at": datetime.utcnow() - timedelta(hours=1)}}
        )
        
        # Try to undo - should fail
        with pytest.raises(Exception):
            DuplicateDetectionService.undo_merge(
                merge_id=str(merge_record["_id"]),
                tenant_id=tenant_id
            )


class TestDuplicateDetectionProperties:
    """Property-based tests for duplicate detection"""
    
    def test_similarity_is_symmetric(self):
        """Property: Similarity calculation should be symmetric"""
        str1 = "John Smith"
        str2 = "John Smyth"
        
        score1 = DuplicateDetectionService._calculate_similarity(str1, str2)
        score2 = DuplicateDetectionService._calculate_similarity(str2, str1)
        
        assert score1 == score2
    
    def test_similarity_is_between_0_and_1(self):
        """Property: Similarity score should always be between 0 and 1"""
        test_pairs = [
            ("", ""),
            ("a", "b"),
            ("John", "John"),
            ("John Smith", "Jane Doe"),
            ("test", "testing")
        ]
        
        for str1, str2 in test_pairs:
            score = DuplicateDetectionService._calculate_similarity(str1, str2)
            assert 0.0 <= score <= 1.0
    
    def test_identical_strings_have_max_similarity(self):
        """Property: Identical strings should have similarity of 1.0"""
        test_strings = ["John", "test@example.com", "123-456-7890", ""]
        
        for s in test_strings:
            score = DuplicateDetectionService._calculate_similarity(s, s)
            assert score == 1.0
    
    def test_duplicate_score_is_between_0_and_1(self):
        """Property: Duplicate score should always be between 0 and 1"""
        test_pairs = [
            (
                {"name": "John", "phone": "555-0101", "email": "john@example.com"},
                {"name": "John", "phone": "555-0101", "email": "john@example.com"}
            ),
            (
                {"name": "John", "phone": "555-0101"},
                {"name": "Jane", "phone": "555-0102"}
            ),
            (
                {"name": "John"},
                {"name": "Jane"}
            )
        ]
        
        for client1, client2 in test_pairs:
            score = DuplicateDetectionService._calculate_duplicate_score(client1, client2)
            assert 0.0 <= score <= 1.0
