"""
Verification tests for gift card schema enhancement (Task 1.1)
Tests that all new fields and indexes are properly created
"""

import pytest
from datetime import datetime, timezone
from bson import ObjectId
from pymongo import MongoClient
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from app.config import settings
from migrations.enhance_gift_cards import GiftCardMigration


class TestGiftCardSchemaVerification:
    """Verify gift card schema enhancement is complete"""
    
    @pytest.fixture
    def test_db(self):
        """Create test database connection"""
        client = MongoClient(settings.MONGODB_URL)
        db = client[f"{settings.MONGODB_DB_NAME}_schema_test"]
        yield db
        # Cleanup
        client.drop_database(f"{settings.MONGODB_DB_NAME}_schema_test")
        client.close()
    
    @pytest.fixture
    def migration(self, test_db):
        """Create migration instance with test database"""
        migration = GiftCardMigration(settings.MONGODB_URL, f"{settings.MONGODB_DB_NAME}_schema_test")
        yield migration
        migration.close()
    
    def test_all_new_fields_added_to_schema(self, test_db, migration):
        """Verify all new fields are added to gift card schema"""
        # Create a sample gift card before migration
        test_db.gift_cards.insert_one({
            "tenant_id": "test_tenant",
            "card_number": "GC-SCHEMA001",
            "amount": 5000,
            "balance": 5000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        })
        
        # Run migration
        result = migration.run()
        assert result["success"] is True
        
        # Verify all new fields exist
        card = test_db.gift_cards.find_one({"card_number": "GC-SCHEMA001"})
        
        # Delivery fields
        assert "delivery_status" in card
        assert "delivery_method" in card
        assert "delivery_attempts" in card
        assert "last_delivery_attempt" in card
        assert "scheduled_delivery" in card
        
        # Security fields
        assert "pin" in card
        assert "pin_enabled" in card
        assert "activation_required" in card
        assert "activated_at" in card
        assert "activated_by" in card
        
        # Customization fields
        assert "terms_version" in card
        assert "design_theme" in card
        assert "certificate_url" in card
        assert "qr_code_data" in card
        
        # Audit and security fields
        assert "security_flags" in card
        assert "suspicious_activity_count" in card
        assert "last_balance_check" in card
        assert "balance_check_count_today" in card
        assert "audit_log" in card
    
    def test_field_types_and_defaults(self, test_db, migration):
        """Verify field types and default values"""
        test_db.gift_cards.insert_one({
            "tenant_id": "test_tenant",
            "card_number": "GC-TYPES001",
            "amount": 5000,
            "balance": 5000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        })
        
        migration.run()
        card = test_db.gift_cards.find_one({"card_number": "GC-TYPES001"})
        
        # Verify types and defaults
        assert isinstance(card["delivery_status"], str)
        assert card["delivery_status"] == "pending"
        
        assert isinstance(card["delivery_attempts"], int)
        assert card["delivery_attempts"] == 0
        
        assert card["pin"] is None
        assert isinstance(card["pin_enabled"], bool)
        assert card["pin_enabled"] is False
        
        assert isinstance(card["activation_required"], bool)
        assert card["activation_required"] is False
        
        assert isinstance(card["security_flags"], list)
        assert len(card["security_flags"]) == 0
        
        assert isinstance(card["audit_log"], list)
        assert len(card["audit_log"]) == 0
        
        assert isinstance(card["suspicious_activity_count"], int)
        assert card["suspicious_activity_count"] == 0
        
        assert isinstance(card["balance_check_count_today"], int)
        assert card["balance_check_count_today"] == 0
    
    def test_gift_card_terms_collection_created(self, test_db, migration):
        """Verify gift_card_terms collection is created with default terms"""
        migration.run()
        
        # Verify collection exists
        assert "gift_card_terms" in test_db.list_collection_names()
        
        # Verify default terms
        terms = test_db.gift_card_terms.find_one({"version": "1.0"})
        assert terms is not None
        assert terms["is_active"] is True
        assert "GIFT CARD TERMS" in terms["content"]
        assert "VALIDITY" in terms["content"]
        assert "REDEMPTION" in terms["content"]
        assert "TRANSFER" in terms["content"]
        assert "REFUNDS" in terms["content"]
        assert "SECURITY" in terms["content"]
        assert "LIABILITY" in terms["content"]
        assert "CHANGES" in terms["content"]
    
    def test_gift_card_designs_collection_created(self, test_db, migration):
        """Verify gift_card_designs collection is created with default templates"""
        migration.run()
        
        # Verify collection exists
        assert "gift_card_designs" in test_db.list_collection_names()
        
        # Verify default designs
        designs = list(test_db.gift_card_designs.find({"is_active": True}))
        assert len(designs) >= 5
        
        # Verify specific themes
        themes = {d["theme"]: d for d in designs}
        assert "default" in themes
        assert "christmas" in themes
        assert "birthday" in themes
        assert "valentine" in themes
        assert "elegant" in themes
        
        # Verify design structure
        for design in designs:
            assert "name" in design
            assert "theme" in design
            assert "template_html" in design
            assert "template_css" in design
            assert "is_active" in design
            assert "created_at" in design
    
    def test_all_required_indexes_created(self, test_db, migration):
        """Verify all required indexes are created"""
        migration.run()
        
        # Get all indexes
        gift_cards_indexes = list(test_db.gift_cards.list_indexes())
        index_names = [idx["name"] for idx in gift_cards_indexes]
        
        # Verify required indexes exist
        required_indexes = [
            "card_number_1",
            "tenant_id_1_status_1",
            "tenant_id_1_created_at_-1",
            "tenant_id_1_expires_at_1",
            "recipient_email_1",
            "tenant_id_1_delivery_status_1",
            "tenant_id_1_balance_check_count_today_1",
            "security_flags_1"
        ]
        
        for idx in required_indexes:
            assert idx in index_names, f"Index {idx} not found"
    
    def test_card_number_unique_index(self, test_db, migration):
        """Verify card_number has unique index"""
        migration.run()
        
        # Get card_number index
        indexes = list(test_db.gift_cards.list_indexes())
        card_number_index = next((idx for idx in indexes if idx["name"] == "card_number_1"), None)
        
        assert card_number_index is not None
        assert card_number_index.get("unique") is True
    
    def test_terms_version_unique_index(self, test_db, migration):
        """Verify terms version has unique index"""
        migration.run()
        
        # Get version index
        indexes = list(test_db.gift_card_terms.list_indexes())
        version_index = next((idx for idx in indexes if idx["name"] == "version_1"), None)
        
        assert version_index is not None
        assert version_index.get("unique") is True
    
    def test_design_theme_unique_index(self, test_db, migration):
        """Verify design theme has unique index"""
        migration.run()
        
        # Get theme index
        indexes = list(test_db.gift_card_designs.list_indexes())
        theme_index = next((idx for idx in indexes if idx["name"] == "theme_1"), None)
        
        assert theme_index is not None
        assert theme_index.get("unique") is True
    
    def test_backward_compatibility(self, test_db, migration):
        """Verify migration maintains backward compatibility"""
        # Create multiple cards with different structures
        cards = [
            {
                "tenant_id": "tenant1",
                "card_number": "GC-COMPAT001",
                "amount": 5000,
                "balance": 5000,
                "card_type": "physical",
                "status": "active",
                "recipient_name": "John Doe",
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc)
            },
            {
                "tenant_id": "tenant2",
                "card_number": "GC-COMPAT002",
                "amount": 10000,
                "balance": 0,
                "card_type": "digital",
                "status": "redeemed",
                "recipient_name": "Jane Smith",
                "created_at": datetime.now(timezone.utc),
                "expires_at": datetime.now(timezone.utc)
            }
        ]
        
        test_db.gift_cards.insert_many(cards)
        
        # Run migration
        migration.run()
        
        # Verify all original fields are preserved
        card1 = test_db.gift_cards.find_one({"card_number": "GC-COMPAT001"})
        assert card1["amount"] == 5000
        assert card1["balance"] == 5000
        assert card1["card_type"] == "physical"
        assert card1["status"] == "active"
        assert card1["recipient_name"] == "John Doe"
        
        card2 = test_db.gift_cards.find_one({"card_number": "GC-COMPAT002"})
        assert card2["amount"] == 10000
        assert card2["balance"] == 0
        assert card2["card_type"] == "digital"
        assert card2["status"] == "redeemed"
        assert card2["recipient_name"] == "Jane Smith"
    
    def test_migration_idempotency(self, test_db, migration):
        """Verify migration is idempotent"""
        # Run migration first time
        result1 = migration.run()
        assert result1["success"] is True
        
        # Count documents
        terms_count_1 = test_db.gift_card_terms.count_documents({})
        designs_count_1 = test_db.gift_card_designs.count_documents({})
        
        # Run migration second time
        result2 = migration.run()
        assert result2["success"] is True
        
        # Verify counts haven't changed
        terms_count_2 = test_db.gift_card_terms.count_documents({})
        designs_count_2 = test_db.gift_card_designs.count_documents({})
        
        assert terms_count_1 == terms_count_2
        assert designs_count_1 == designs_count_2
    
    def test_audit_log_structure(self, test_db, migration):
        """Verify audit_log has correct structure"""
        test_db.gift_cards.insert_one({
            "tenant_id": "test_tenant",
            "card_number": "GC-AUDIT001",
            "amount": 5000,
            "balance": 5000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        })
        
        migration.run()
        card = test_db.gift_cards.find_one({"card_number": "GC-AUDIT001"})
        
        # Verify audit_log is a list
        assert isinstance(card["audit_log"], list)
        
        # Verify audit_log can store entries with required fields
        assert all(isinstance(entry, dict) for entry in card["audit_log"])
    
    def test_security_flags_structure(self, test_db, migration):
        """Verify security_flags has correct structure"""
        test_db.gift_cards.insert_one({
            "tenant_id": "test_tenant",
            "card_number": "GC-SECURITY001",
            "amount": 5000,
            "balance": 5000,
            "card_type": "digital",
            "status": "active",
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc)
        })
        
        migration.run()
        card = test_db.gift_cards.find_one({"card_number": "GC-SECURITY001"})
        
        # Verify security_flags is a list
        assert isinstance(card["security_flags"], list)
        
        # Verify it's empty initially
        assert len(card["security_flags"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
