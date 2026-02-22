"""
Tests for referral reward completion (Task 18)
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
    return "test-tenant-completion"


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
def tracked_referral(db, tenant_id, referral_code, referred_client_id):
    """Create a tracked referral for testing"""
    ReferralService.track_referral(
        tenant_id=tenant_id,
        referral_code=referral_code,
        referred_client_id=referred_client_id
    )
    return referred_client_id


@pytest.fixture
def cleanup_referrals(db, tenant_id):
    """Cleanup referrals after test"""
    yield
    db.referrals.delete_many({"tenant_id": tenant_id})


class TestReferralRewardCompletion:
    """Test referral reward completion functionality"""
    
    def test_complete_referral_with_reward(self, db, tenant_id, tracked_referral, cleanup_referrals):
        """Test completing referral and awarding reward"""
        reward_amount = 1000.0
        
        result = ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=reward_amount
        )
        
        assert result is not None
        assert result["status"] == "completed"
        assert result["reward_amount"] == reward_amount
    
    def test_tracking_record_marked_completed(self, db, tenant_id, referral_code, tracked_referral, cleanup_referrals):
        """Test that tracking record is marked as completed"""
        reward_amount = 1000.0
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=reward_amount
        )
        
        # Verify tracking record status
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code,
            "tracking_records.referred_client_id": ObjectId(tracked_referral)
        })
        
        tracking_record = referral["tracking_records"][0]
        assert tracking_record["status"] == "completed"
    
    def test_reward_amount_stored_in_tracking(self, db, tenant_id, referral_code, tracked_referral, cleanup_referrals):
        """Test that reward amount is stored in tracking record"""
        reward_amount = 1500.0
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=reward_amount
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        
        tracking_record = referral["tracking_records"][0]
        assert tracking_record["reward_amount"] == reward_amount
    
    def test_completion_timestamp_recorded(self, db, tenant_id, referral_code, tracked_referral, cleanup_referrals):
        """Test that completion timestamp is recorded"""
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=1000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        
        tracking_record = referral["tracking_records"][0]
        assert "completed_at" in tracking_record
        assert isinstance(tracking_record["completed_at"], datetime)
    
    def test_referrer_pending_rewards_updated(self, db, tenant_id, referrer_id, tracked_referral, cleanup_referrals):
        """Test that referrer's pending rewards balance is updated"""
        reward_amount = 2000.0
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=reward_amount
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        assert referral["pending_rewards"] == reward_amount
    
    def test_total_completed_incremented(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Test that total_completed count is incremented"""
        referred_client_1 = str(ObjectId())
        referred_client_2 = str(ObjectId())
        
        # Track two referrals
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_1
        )
        
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_2
        )
        
        # Complete first referral
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client_1,
            reward_amount=1000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        assert referral["total_completed"] == 1
        
        # Complete second referral
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client_2,
            reward_amount=1000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "code": referral_code
        })
        assert referral["total_completed"] == 2
    
    def test_total_rewards_earned_updated(self, db, tenant_id, referrer_id, tracked_referral, cleanup_referrals):
        """Test that total_rewards_earned is updated"""
        reward_amount = 1500.0
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=reward_amount
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        assert referral["total_rewards_earned"] == reward_amount
    
    def test_complete_nonexistent_referral_fails(self, db, tenant_id, cleanup_referrals):
        """Test that completing nonexistent referral fails"""
        nonexistent_client = str(ObjectId())
        
        with pytest.raises(ValueError):
            ReferralService.complete_referral(
                tenant_id=tenant_id,
                referred_client_id=nonexistent_client,
                reward_amount=1000.0
            )
    
    def test_complete_with_default_reward_amount(self, db, tenant_id, tracked_referral, cleanup_referrals):
        """Test completing referral with default reward amount from settings"""
        # Complete without specifying reward amount
        result = ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=tracked_referral,
            reward_amount=None
        )
        
        # Should use default from settings (1000)
        assert result["reward_amount"] == 1000
    
    def test_multiple_completions_accumulate_rewards(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Test that multiple completions accumulate rewards"""
        referred_client_1 = str(ObjectId())
        referred_client_2 = str(ObjectId())
        reward_1 = 1000.0
        reward_2 = 1500.0
        
        # Track and complete first referral
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_1
        )
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client_1,
            reward_amount=reward_1
        )
        
        # Track and complete second referral
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_2
        )
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client_2,
            reward_amount=reward_2
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        assert referral["total_rewards_earned"] == reward_1 + reward_2
        assert referral["pending_rewards"] == reward_1 + reward_2


class TestReferralRewardCompletionProperties:
    """Property-based tests for referral reward completion"""
    
    def test_completed_referral_always_has_timestamp(self, db, tenant_id, referral_code, cleanup_referrals):
        """Property: Completed referral should always have completion timestamp"""
        for i in range(3):
            referred_client_id = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
            
            ReferralService.complete_referral(
                tenant_id=tenant_id,
                referred_client_id=referred_client_id,
                reward_amount=1000.0
            )
            
            referral = db.referrals.find_one({
                "tenant_id": tenant_id,
                "code": referral_code,
                "tracking_records.referred_client_id": ObjectId(referred_client_id)
            })
            
            tracking_record = referral["tracking_records"][-1]
            assert tracking_record["completed_at"] is not None
            assert isinstance(tracking_record["completed_at"], datetime)
    
    def test_reward_amount_always_positive(self, db, tenant_id, referral_code, cleanup_referrals):
        """Property: Reward amount should always be positive"""
        for reward in [100.0, 500.0, 1000.0, 5000.0]:
            referred_client_id = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
            
            ReferralService.complete_referral(
                tenant_id=tenant_id,
                referred_client_id=referred_client_id,
                reward_amount=reward
            )
            
            referral = db.referrals.find_one({
                "tenant_id": tenant_id,
                "code": referral_code
            })
            
            tracking_record = referral["tracking_records"][-1]
            assert tracking_record["reward_amount"] > 0
    
    def test_pending_rewards_equals_sum_of_completed(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Property: Pending rewards should equal sum of all completed rewards"""
        rewards = [1000.0, 1500.0, 2000.0]
        
        for reward in rewards:
            referred_client_id = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client_id
            )
            
            ReferralService.complete_referral(
                tenant_id=tenant_id,
                referred_client_id=referred_client_id,
                reward_amount=reward
            )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        expected_total = sum(rewards)
        assert referral["pending_rewards"] == expected_total
