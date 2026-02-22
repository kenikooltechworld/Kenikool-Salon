"""
Tests for package system database indexes
"""
import pytest
from app.database import Database


@pytest.fixture(scope="module")
def db():
    """Get database instance"""
    if not Database._initialized:
        Database.connect_db()
    return Database.get_db()


class TestPackageIndexes:
    """Test package system indexes"""
    
    def test_package_purchases_indexes_exist(self, db):
        """Test that package_purchases collection has required indexes"""
        indexes = db.package_purchases.index_information()
        index_names = list(indexes.keys())
        
        # Check for required indexes
        assert any("client_id" in str(idx) and "status" in str(idx) for idx in index_names), \
            "Missing index on (client_id, status)"
        assert any("expiration_date" in str(idx) and "status" in str(idx) for idx in index_names), \
            "Missing index on (expiration_date, status)"
        assert any("tenant_id" in str(idx) and "purchase_date" in str(idx) for idx in index_names), \
            "Missing index on (tenant_id, purchase_date)"
    
    def test_service_credits_indexes_exist(self, db):
        """Test that service_credits collection has required indexes"""
        indexes = db.service_credits.index_information()
        index_names = list(indexes.keys())
        
        # Check for required indexes
        assert any("purchase_id" in str(idx) and "service_id" in str(idx) for idx in index_names), \
            "Missing index on (purchase_id, service_id)"
        assert any("purchase_id" in str(idx) and "status" in str(idx) for idx in index_names), \
            "Missing index on (purchase_id, status)"
    
    def test_redemption_transactions_indexes_exist(self, db):
        """Test that redemption_transactions collection has required indexes"""
        indexes = db.redemption_transactions.index_information()
        index_names = list(indexes.keys())
        
        # Check for required indexes
        assert any("purchase_id" in str(idx) and "redemption_date" in str(idx) for idx in index_names), \
            "Missing index on (purchase_id, redemption_date)"
        assert any("client_id" in str(idx) and "redemption_date" in str(idx) for idx in index_names), \
            "Missing index on (client_id, redemption_date)"
    
    def test_package_audit_logs_indexes_exist(self, db):
        """Test that package_audit_logs collection has required indexes"""
        indexes = db.package_audit_logs.index_information()
        index_names = list(indexes.keys())
        
        # Check for required indexes
        assert any("entity_id" in str(idx) and "timestamp" in str(idx) for idx in index_names), \
            "Missing index on (entity_id, timestamp)"
        assert any("tenant_id" in str(idx) and "timestamp" in str(idx) for idx in index_names), \
            "Missing index on (tenant_id, timestamp)"
    
    def test_all_package_collections_have_indexes(self, db):
        """Test that all package collections have at least one index besides _id"""
        collections = [
            "package_purchases",
            "service_credits",
            "redemption_transactions",
            "package_audit_logs"
        ]
        
        for collection_name in collections:
            collection = db[collection_name]
            indexes = collection.index_information()
            
            # Should have at least _id index and one more
            assert len(indexes) > 1, f"{collection_name} has no indexes besides _id"
    
    def test_package_purchases_compound_indexes(self, db):
        """Test that package_purchases has compound indexes for common queries"""
        indexes = db.package_purchases.index_information()
        
        # Convert indexes to string for easier checking
        index_str = str(indexes)
        
        # Check for compound indexes
        assert "tenant_id" in index_str, "Missing tenant_id in indexes"
        assert "client_id" in index_str, "Missing client_id in indexes"
        assert "status" in index_str, "Missing status in indexes"
    
    def test_service_credits_compound_indexes(self, db):
        """Test that service_credits has compound indexes for common queries"""
        indexes = db.service_credits.index_information()
        
        # Convert indexes to string for easier checking
        index_str = str(indexes)
        
        # Check for compound indexes
        assert "purchase_id" in index_str, "Missing purchase_id in indexes"
        assert "service_id" in index_str, "Missing service_id in indexes"
        assert "status" in index_str, "Missing status in indexes"
    
    def test_redemption_transactions_compound_indexes(self, db):
        """Test that redemption_transactions has compound indexes for common queries"""
        indexes = db.redemption_transactions.index_information()
        
        # Convert indexes to string for easier checking
        index_str = str(indexes)
        
        # Check for compound indexes
        assert "purchase_id" in index_str, "Missing purchase_id in indexes"
        assert "client_id" in index_str, "Missing client_id in indexes"
        assert "redemption_date" in index_str, "Missing redemption_date in indexes"
    
    def test_package_audit_logs_compound_indexes(self, db):
        """Test that package_audit_logs has compound indexes for common queries"""
        indexes = db.package_audit_logs.index_information()
        
        # Convert indexes to string for easier checking
        index_str = str(indexes)
        
        # Check for compound indexes
        assert "entity_id" in index_str, "Missing entity_id in indexes"
        assert "tenant_id" in index_str, "Missing tenant_id in indexes"
        assert "timestamp" in index_str, "Missing timestamp in indexes"
        assert "action_type" in index_str, "Missing action_type in indexes"
