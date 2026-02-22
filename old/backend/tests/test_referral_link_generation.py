"""
Tests for referral link generation (Task 16)
"""
import pytest
from datetime import datetime
from bson import ObjectId
from app.services.referral_service import ReferralService
from app.database import Database


@pytest.fixture
def db():
    """Get database instance"""
    return Database.get_db()


@pytest.fixture
def tenant_id():
    """Test tenant ID"""
    return "test-tenant-link-gen"


@pytest.fixture
def client_id():
    """Test client ID"""
    return str(ObjectId())


@pytest.fixture
def tenant_subdomain():
    """Test tenant subdomain"""
    return "test-salon"


@pytest.fixture
def cleanup_referrals(db, tenant_id):
    """Cleanup referrals after test"""
    yield
    db.referrals.delete_many({"tenant_id": tenant_id})


class TestReferralLinkGeneration:
    """Test referral link generation functionality"""
    
    def test_generate_link_for_new_client(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Test generating referral link for new client"""
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        assert result is not None
        assert "referral_code" in result
        assert "referral_link" in result
        assert result["referral_code"] is not None
        assert len(result["referral_code"]) > 0
        assert tenant_subdomain in result["referral_link"]
        assert result["referral_code"] in result["referral_link"]
    
    def test_referral_code_is_unique(self, db, tenant_id, tenant_subdomain, cleanup_referrals):
        """Test that generated referral codes are unique"""
        client_id_1 = str(ObjectId())
        client_id_2 = str(ObjectId())
        
        result_1 = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id_1,
            tenant_subdomain=tenant_subdomain
        )
        
        result_2 = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id_2,
            tenant_subdomain=tenant_subdomain
        )
        
        assert result_1["referral_code"] != result_2["referral_code"]
    
    def test_existing_client_returns_same_link(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Test that existing client returns same referral link"""
        # Generate link first time
        result_1 = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        # Generate link second time
        result_2 = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        assert result_1["referral_code"] == result_2["referral_code"]
        assert result_1["referral_link"] == result_2["referral_link"]
    
    def test_referral_link_format(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Test that referral link has correct format"""
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        # Link should contain ref parameter
        assert "ref=" in result["referral_link"]
        assert result["referral_code"] in result["referral_link"]
    
    def test_referral_code_stored_in_database(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Test that referral code is stored in database"""
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        # Verify in database
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "code": result["referral_code"]
        })
        
        assert referral is not None
        assert referral["status"] == "active"
    
    def test_referral_link_has_created_timestamp(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Test that referral link has created_at timestamp"""
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        assert "created_at" in result
        assert isinstance(result["created_at"], datetime)
    
    def test_multiple_tenants_have_unique_codes(self, db, client_id, tenant_subdomain, cleanup_referrals):
        """Test that different tenants can have unique codes for same client"""
        tenant_id_1 = "tenant-1"
        tenant_id_2 = "tenant-2"
        
        result_1 = ReferralService.generate_referral_link(
            tenant_id=tenant_id_1,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        result_2 = ReferralService.generate_referral_link(
            tenant_id=tenant_id_2,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        assert result_1["referral_code"] != result_2["referral_code"]
        
        # Cleanup
        db.referrals.delete_many({"tenant_id": {"$in": [tenant_id_1, tenant_id_2]}})
    
    def test_referral_link_contains_subdomain(self, db, tenant_id, client_id, cleanup_referrals):
        """Test that referral link contains tenant subdomain"""
        subdomain = "my-salon"
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=subdomain
        )
        
        assert subdomain in result["referral_link"]
    
    def test_referral_code_is_alphanumeric(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Test that referral code is alphanumeric"""
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=client_id,
            tenant_subdomain=tenant_subdomain
        )
        
        code = result["referral_code"]
        assert code.isalnum() or "-" in code  # Allow alphanumeric and hyphens
        assert len(code) > 0


class TestReferralLinkGenerationProperties:
    """Property-based tests for referral link generation"""
    
    def test_generated_link_always_has_code(self, db, tenant_id, tenant_subdomain, cleanup_referrals):
        """Property: Generated link should always have a referral code"""
        for i in range(5):
            client_id = str(ObjectId())
            result = ReferralService.generate_referral_link(
                tenant_id=tenant_id,
                client_id=client_id,
                tenant_subdomain=tenant_subdomain
            )
            
            assert result["referral_code"] is not None
            assert len(result["referral_code"]) > 0
    
    def test_same_client_always_returns_same_code(self, db, tenant_id, client_id, tenant_subdomain, cleanup_referrals):
        """Property: Same client should always return same referral code"""
        codes = []
        for _ in range(3):
            result = ReferralService.generate_referral_link(
                tenant_id=tenant_id,
                client_id=client_id,
                tenant_subdomain=tenant_subdomain
            )
            codes.append(result["referral_code"])
        
        # All codes should be identical
        assert len(set(codes)) == 1
    
    def test_different_clients_get_different_codes(self, db, tenant_id, tenant_subdomain, cleanup_referrals):
        """Property: Different clients should get different codes"""
        codes = []
        for _ in range(5):
            client_id = str(ObjectId())
            result = ReferralService.generate_referral_link(
                tenant_id=tenant_id,
                client_id=client_id,
                tenant_subdomain=tenant_subdomain
            )
            codes.append(result["referral_code"])
        
        # All codes should be unique
        assert len(set(codes)) == len(codes)
    
    def test_referral_link_always_contains_code(self, db, tenant_id, tenant_subdomain, cleanup_referrals):
        """Property: Referral link should always contain the referral code"""
        for i in range(5):
            client_id = str(ObjectId())
            result = ReferralService.generate_referral_link(
                tenant_id=tenant_id,
                client_id=client_id,
                tenant_subdomain=tenant_subdomain
            )
            
            assert result["referral_code"] in result["referral_link"]
