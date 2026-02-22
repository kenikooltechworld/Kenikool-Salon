"""
Tests for gift card schema enhancement migration
"""

import pytest
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from app.config import settings
from migrations.enhance_gift_cards import GiftCardMigration


@pytest.fixture
def test_db():
    """Create test database connection"""
    client = MongoClient(settings.MONGODB_URL)
    db = client[f"{settings.MONGODB_DB_NAME}_test"]
    yield db
    # Cleanup
    client.drop_database(f"{settings.MONGODB_DB_NAME}_test")
    client.close()


@pytest.fixture
def migration(test_db):
    """Create migration instance with test database"""
    migration = GiftCardMigration(settings.MONGODB_URL, f"{settings.MONGODB_DB_NAME}_test")
    yield migration
    migration.close()


class TestGiftCardMigration:
    """Test gift card schema enhancement migration"""
    
    def test_migration_adds_new_fields_to_existing_cards(self, test_db, migration):
        """Test that migration adds new fields to existing gift cards"""
        # Create existing gift card without new fields
        existing_card = {
            "tenant_id": "test_tenant",
            "card_number": "GC-TEST001",
            "amount": 10000,
            "balance": 10000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        }
        
        test_db.gift_cards.insert_one(existing_card)
        
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify new fields were added
        updated_card = test_db.gift_cards.find_one({"card_number": "GC-TEST001"})
        assert updated_card is not None
        assert "delivery_status" in updated_card
        assert updated_card["delivery_status"] == "pending"
        assert "pin" in updated_card
        assert updated_card["pin"] is None
        assert "activation_required" in updated_card
        assert updated_card["activation_required"] is False
        assert "audit_log" in updated_card
        assert isinstance(updated_card["audit_log"], list)
        assert "security_flags" in updated_card
        assert isinstance(updated_card["security_flags"], list)
        assert "terms_version" in updated_card
        assert updated_card["terms_version"] == "1.0"
        assert "design_theme" in updated_card
        assert updated_card["design_theme"] == "default"
    
    def test_migration_creates_terms_collection(self, test_db, migration):
        """Test that migration creates gift_card_terms collection"""
        # Verify collection doesn't exist yet
        assert "gift_card_terms" not in test_db.list_collection_names()
        
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify collection was created
        assert "gift_card_terms" in test_db.list_collection_names()
        
        # Verify default terms exist
        terms = test_db.gift_card_terms.find_one({"version": "1.0"})
        assert terms is not None
        assert terms["is_active"] is True
        assert "GIFT CARD TERMS" in terms["content"]
        assert "VALIDITY" in terms["content"]
        assert "REDEMPTION" in terms["content"]
    
    def test_migration_creates_designs_collection(self, test_db, migration):
        """Test that migration creates gift_card_designs collection"""
        # Verify collection doesn't exist yet
        assert "gift_card_designs" not in test_db.list_collection_names()
        
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify collection was created
        assert "gift_card_designs" in test_db.list_collection_names()
        
        # Verify default designs exist
        designs = list(test_db.gift_card_designs.find({"is_active": True}))
        assert len(designs) >= 5
        
        # Verify specific themes
        themes = [d["theme"] for d in designs]
        assert "default" in themes
        assert "christmas" in themes
        assert "birthday" in themes
        assert "valentine" in themes
        assert "elegant" in themes
    
    def test_migration_creates_indexes(self, test_db, migration):
        """Test that migration creates required indexes"""
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify gift_cards indexes
        gift_cards_indexes = test_db.gift_cards.list_indexes()
        index_names = [idx["name"] for idx in gift_cards_indexes]
        
        assert "card_number_1" in index_names
        assert "tenant_id_1_status_1" in index_names
        assert "tenant_id_1_created_at_-1" in index_names
        assert "tenant_id_1_expires_at_1" in index_names
        assert "recipient_email_1" in index_names
        
        # Verify gift_card_terms indexes
        terms_indexes = test_db.gift_card_terms.list_indexes()
        terms_index_names = [idx["name"] for idx in terms_indexes]
        assert "version_1" in terms_index_names
        assert "is_active_1" in terms_index_names
        
        # Verify gift_card_designs indexes
        designs_indexes = test_db.gift_card_designs.list_indexes()
        designs_index_names = [idx["name"] for idx in designs_indexes]
        assert "theme_1" in designs_index_names
        assert "is_active_1" in designs_index_names
    
    def test_migration_is_idempotent(self, test_db, migration):
        """Test that migration can be run multiple times safely"""
        # Run migration first time
        result1 = migration.run()
        assert result1["success"] is True
        
        # Count documents after first run
        terms_count_1 = test_db.gift_card_terms.count_documents({})
        designs_count_1 = test_db.gift_card_designs.count_documents({})
        
        # Run migration second time
        result2 = migration.run()
        assert result2["success"] is True
        
        # Verify counts haven't changed (idempotent)
        terms_count_2 = test_db.gift_card_terms.count_documents({})
        designs_count_2 = test_db.gift_card_designs.count_documents({})
        
        assert terms_count_1 == terms_count_2
        assert designs_count_1 == designs_count_2
    
    def test_migration_preserves_existing_data(self, test_db, migration):
        """Test that migration preserves existing gift card data"""
        # Create multiple existing cards with different data
        cards = [
            {
                "tenant_id": "tenant1",
                "card_number": "GC-PRESERVE001",
                "amount": 5000,
                "balance": 2500,
                "card_type": "physical",
                "status": "active",
                "recipient_name": "John Doe",
                "recipient_email": "john@example.com",
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc)
            },
            {
                "tenant_id": "tenant2",
                "card_number": "GC-PRESERVE002",
                "amount": 10000,
                "balance": 10000,
                "card_type": "digital",
                "status": "inactive",
                "recipient_name": "Jane Smith",
                "recipient_email": "jane@example.com",
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc)
            }
        ]
        
        test_db.gift_cards.insert_many(cards)
        
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify all original data is preserved
        card1 = test_db.gift_cards.find_one({"card_number": "GC-PRESERVE001"})
        assert card1["amount"] == 5000
        assert card1["balance"] == 2500
        assert card1["card_type"] == "physical"
        assert card1["status"] == "active"
        assert card1["recipient_name"] == "John Doe"
        assert card1["recipient_email"] == "john@example.com"
        
        card2 = test_db.gift_cards.find_one({"card_number": "GC-PRESERVE002"})
        assert card2["amount"] == 10000
        assert card2["balance"] == 10000
        assert card2["card_type"] == "digital"
        assert card2["status"] == "inactive"
        assert card2["recipient_name"] == "Jane Smith"
    
    def test_migration_handles_empty_collection(self, test_db, migration):
        """Test that migration works with empty gift_cards collection"""
        # Verify collection is empty
        assert test_db.gift_cards.count_documents({}) == 0
        
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify collections were created
        assert "gift_card_terms" in test_db.list_collection_names()
        assert "gift_card_designs" in test_db.list_collection_names()
    
    def test_card_number_unique_index(self, test_db, migration):
        """Test that card_number unique index is enforced"""
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Insert first card
        test_db.gift_cards.insert_one({
            "tenant_id": "test_tenant",
            "card_number": "GC-UNIQUE001",
            "amount": 5000,
            "balance": 5000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        })
        
        # Try to insert duplicate card_number
        with pytest.raises(DuplicateKeyError):
            test_db.gift_cards.insert_one({
                "tenant_id": "test_tenant",
                "card_number": "GC-UNIQUE001",
                "amount": 5000,
                "balance": 5000,
                "card_type": "digital",
                "status": "active",
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc)
            })
    
    def test_terms_version_unique_index(self, test_db, migration):
        """Test that terms version unique index is enforced"""
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Try to insert duplicate version
        with pytest.raises(DuplicateKeyError):
            test_db.gift_card_terms.insert_one({
                "version": "1.0",
                "content": "Different content",
                "effective_date": datetime.now(timezone.utc),
                "created_at": datetime.now(timezone.utc),
                "created_by": "test",
                "is_active": False
            })
    
    def test_design_theme_unique_index(self, test_db, migration):
        """Test that design theme unique index is enforced"""
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Try to insert duplicate theme
        with pytest.raises(DuplicateKeyError):
            test_db.gift_card_designs.insert_one({
                "name": "Duplicate Default",
                "theme": "default",
                "template_html": "<div>Different</div>",
                "template_css": ".different {}",
                "preview_url": None,
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            })
    
    def test_rollback_removes_new_fields(self, test_db, migration):
        """Test that rollback removes new fields from gift cards"""
        # Create card and run migration
        test_db.gift_cards.insert_one({
            "tenant_id": "test_tenant",
            "card_number": "GC-ROLLBACK001",
            "amount": 5000,
            "balance": 5000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        })
        
        migration.run()
        
        # Verify new fields exist
        card = test_db.gift_cards.find_one({"card_number": "GC-ROLLBACK001"})
        assert "delivery_status" in card
        assert "audit_log" in card
        
        # Rollback
        result = migration.rollback()
        assert result["success"] is True
        
        # Verify new fields are removed
        card = test_db.gift_cards.find_one({"card_number": "GC-ROLLBACK001"})
        assert "delivery_status" not in card
        assert "audit_log" not in card
        assert "security_flags" not in card
    
    def test_rollback_drops_new_collections(self, test_db, migration):
        """Test that rollback drops new collections"""
        # Run migration
        migration.run()
        
        # Verify collections exist
        assert "gift_card_terms" in test_db.list_collection_names()
        assert "gift_card_designs" in test_db.list_collection_names()
        
        # Rollback
        result = migration.rollback()
        assert result["success"] is True
        
        # Verify collections are dropped
        assert "gift_card_terms" not in test_db.list_collection_names()
        assert "gift_card_designs" not in test_db.list_collection_names()


class TestMigrationIntegration:
    """Integration tests for migration with real database"""
    
    @pytest.mark.integration
    def test_migration_with_real_database(self):
        """Test migration with real database (requires MongoDB running)"""
        migration = GiftCardMigration(settings.MONGODB_URL, settings.MONGODB_DB_NAME)
        try:
            # Run migration
            result = migration.run()
            assert result["success"] is True
            
            # Verify collections exist
            db = migration.db
            assert "gift_card_terms" in db.list_collection_names()
            assert "gift_card_designs" in db.list_collection_names()
            
            # Verify indexes exist
            gift_cards_indexes = db.gift_cards.list_indexes()
            index_names = [idx["name"] for idx in gift_cards_indexes]
            assert "card_number_1" in index_names
            
        finally:
            migration.close()
