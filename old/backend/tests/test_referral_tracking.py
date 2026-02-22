"""
Tests for referral tracking (Task 17)
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
    return "test-tenant-tracking"


@pytest.fixture
def referrer_id():
    """Test referrer ID"""
    return str(ObjectId())


@pytest.fixture
def referred_client_id():
    """Test referred client ID"""
    return str(ObjectId())


@pytest.fixture
def referral_code(db, tenant_id, referrer_id):
    """Create a referral code for testing"""
    result = ReferralService.generate_referral_link(
        tenant_id=tenant_id,
        client_id=referrer_id,
        tenant_subdomain="test-salon"
    )
    return result["referral_code"]


@pytest.fixture
def cleanup_referrals(db, tenant_id):
    """Cleanup referrals after test"""
    yield
    db.referrals.delete_many({"tenant_id": tenant_id})


class TestReferralTracking:
    """Test referral tracking functionality"""
    
    def test_track_referral_with_valid_code(self, db, tenant_id, referral_code, referred_client_id, cleanup_referrals):
        """Test tracking referral with valid referral code"""
        result = ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_id
        )
        
        assert result is not None
        assert result["status"] == "tracked"
        assert result["referred_client_id"] == referred_client_id
    
    def test_tracking_record_created(self, db, tenant_id, referral_code, referred_client_id, cleanup_referrals):
        """Test that tracking record is created in database"""
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_id
        )
        
        # Verify tracking record exists
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code,
            "tracking_records.referred_client_id": ObjectId(referred_client_id)
        })
        
        assert referral is not None
        assert len(referral["tracking_records"]) > 0
        
        tracking_record = referral["tracking_records"][0]
        assert tracking_record["referred_client_id"] == ObjectId(referred_client_id)
        assert tracking_record["status"] == "pending"
    
    def test_tracking_record_has_timestamp(self, db, tenant_id, referral_code, referred_client_id, cleanup_referrals):
        """Test that tracking record has tracked_at timestamp"""
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_id
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        
        tracking_record = referral["tracking_records"][0]
        assert "tracked_at" in tracking_record
        assert isinstance(tracking_record["tracked_at"], datetime)
    
    def test_duplicate_tracking_prevention(self, db, tenant_id, referral_code, referred_client_id, cleanup_referrals):
        """Test that duplicate tracking is prevented"""
        # Track first time
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_id
        )
        
        # Try to track same client again
        with pytest.raises(ValueError) as exc_info:
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
        
        assert "already been tracked" in str(exc_info.value)
    
    def test_invalid_code_handling(self, db, tenant_id, referred_client_id, cleanup_referrals):
        """Test handling of invalid referral code"""
        with pytest.raises(ValueError) as exc_info:
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code="INVALID_CODE",
                referred_client_id=referred_client_id
            )
        
        assert "Invalid" in str(exc_info.value) or "invalid" in str(exc_info.value)
    
    def test_self_referral_prevention(self, db, tenant_id, referrer_id, cleanup_referrals):
        """Test that self-referrals are prevented"""
        # Generate referral code
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=referrer_id,
            tenant_subdomain="test-salon"
        )
        referral_code = result["referral_code"]
        
        # Try to refer self
        with pytest.raises(ValueError) as exc_info:
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referrer_id
            )
        
        assert "Cannot refer yourself" in str(exc_info.value) or "self" in str(exc_info.value).lower()
    
    def test_total_tracked_incremented(self, db, tenant_id, referral_code, cleanup_referrals):
        """Test that total_tracked count is incremented"""
        referred_client_1 = str(ObjectId())
        referred_client_2 = str(ObjectId())
        
        # Track first referral
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_1
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        assert referral["total_tracked"] == 1
        
        # Track second referral
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_2
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        assert referral["total_tracked"] == 2
    
    def test_inactive_code_not_tracked(self, db, tenant_id, referrer_id, referred_client_id, cleanup_referrals):
        """Test that inactive referral codes cannot be tracked"""
        # Generate referral code
        result = ReferralService.generate_referral_link(
            tenant_id=tenant_id,
            client_id=referrer_id,
            tenant_subdomain="test-salon"
        )
        referral_code = result["referral_code"]
        
        # Deactivate the code
        db.referrals.update_one(
            {"tenant_id": tenant_id, "code": referral_code},
            {"$set": {"status": "inactive"}}
        )
        
        # Try to track with inactive code
        with pytest.raises(ValueError):
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
    
    def test_tracking_different_tenants_isolated(self, db, referrer_id, referred_client_id, cleanup_referrals):
        """Test that tracking is isolated between tenants"""
        tenant_id_1 = "tenant-1"
        tenant_id_2 = "tenant-2"
        
        # Generate code for tenant 1
        result_1 = ReferralService.generate_referral_link(
            tenant_id=tenant_id_1,
            client_id=referrer_id,
            tenant_subdomain="salon-1"
        )
        code_1 = result_1["referral_code"]
        
        # Try to track with tenant 2 using tenant 1's code
        with pytest.raises(ValueError):
            ReferralService.track_referral(
                tenant_id=tenant_id_2,
                referral_code=code_1,
                referred_client_id=referred_client_id
            )
        
        # Cleanup
        db.referrals.delete_many({"tenant_id": {"$in": [tenant_id_1, tenant_id_2]}})


class TestReferralTrackingProperties:
    """Property-based tests for referral tracking"""
    
    def test_tracked_referral_always_has_status(self, db, tenant_id, referral_code, cleanup_referrals):
        """Property: Tracked referral should always have status"""
        for i in range(3):
            referred_client_id = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
            
            referral = db.referrals.find_one({
                "tenant_id": tenant_id,
                "code": referral_code,
                "tracking_records.referred_client_id": ObjectId(referred_client_id)
            })
            
            tracking_record = referral["tracking_records"][-1]
            assert tracking_record["status"] in ["pending", "completed", "expired"]
    
    def test_each_tracking_has_timestamp(self, db, tenant_id, referral_code, cleanup_referrals):
        """Property: Each tracking record should have a timestamp"""
        for i in range(3):
            referred_client_id = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
            
            referral = db.referrals.find_one({
                "tenant_id": tenant_id,
                "code": referral_code
            })
            
            for record in referral["tracking_records"]:
                assert "tracked_at" in record
                assert isinstance(record["tracked_at"], datetime)
    
    def test_multiple_referrals_tracked_independently(self, db, tenant_id, referral_code, cleanup_referrals):
        """Property: Multiple referrals should be tracked independently"""
        referred_clients = [str(ObjectId()) for _ in range(3)]
        
        for client_id in referred_clients:
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=client_id
            )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        
        # Should have 3 tracking records
        assert len(referral["tracking_records"]) == 3
        
        # Each should have unique referred_client_id
        tracked_ids = [str(r["referred_client_id"]) for r in referral["tracking_records"]]
        assert len(set(tracked_ids)) == 3
