"""
Tests for referral reward redemption (Task 19)
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
    return "test-tenant-redemption"


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
def completed_referral(db, tenant_id, referral_code, referred_client_id, referrer_id):
    """Create a completed referral with pending rewards"""
    # Track referral
    ReferralService.track_referral(
        tenant_id=tenant_id,
        referral_code=referral_code,
        referred_client_id=referred_client_id
    )
    
    # Complete referral with reward
    ReferralService.complete_referral(
        tenant_id=tenant_id,
        referred_client_id=referred_client_id,
        reward_amount=5000.0
    )
    
    return referrer_id


@pytest.fixture
def cleanup_referrals(db, tenant_id):
    """Cleanup referrals after test"""
    yield
    db.referrals.delete_many({"tenant_id": tenant_id})


class TestReferralRewardRedemption:
    """Test referral reward redemption functionality"""
    
    def test_redeem_with_sufficient_balance(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test redeeming rewards with sufficient balance"""
        redemption_amount = 2000.0
        
        result = ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=completed_referral,
            amount=redemption_amount
        )
        
        assert result is not None
        assert result["status"] == "redeemed"
        assert result["redeemed_amount"] == redemption_amount
    
    def test_insufficient_balance_error(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test error when redeeming with insufficient balance"""
        # Try to redeem more than available (5000)
        with pytest.raises(ValueError) as exc_info:
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=completed_referral,
                amount=10000.0
            )
        
        assert "insufficient" in str(exc_info.value).lower() or "balance" in str(exc_info.value).lower()
    
    def test_balance_deducted_after_redemption(self, db, tenant_id, referrer_id, referral_code, referred_client_id, cleanup_referrals):
        """Test that pending balance is deducted after redemption"""
        # Setup: Track and complete referral
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client_id
        )
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client_id,
            reward_amount=5000.0
        )
        
        # Verify initial balance
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        assert referral["pending_rewards"] == 5000.0
        
        # Redeem
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=referrer_id,
            amount=2000.0
        )
        
        # Verify balance deducted
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        assert referral["pending_rewards"] == 3000.0
    
    def test_redemption_record_created(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test that redemption record is created"""
        redemption_amount = 1500.0
        
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=completed_referral,
            amount=redemption_amount
        )
        
        # Verify redemption record exists
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(completed_referral)
        })
        
        assert "redemption_records" in referral
        assert len(referral["redemption_records"]) > 0
        
        redemption = referral["redemption_records"][0]
        assert redemption["amount"] == redemption_amount
        assert redemption["status"] == "completed"
    
    def test_redemption_record_has_timestamp(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test that redemption record has timestamp"""
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=completed_referral,
            amount=1000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(completed_referral)
        })
        
        redemption = referral["redemption_records"][0]
        assert "redeemed_at" in redemption
        assert isinstance(redemption["redeemed_at"], datetime)
    
    def test_total_redeemed_updated(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test that total_redeemed is updated"""
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=completed_referral,
            amount=1000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(completed_referral)
        })
        
        assert referral["total_redeemed"] == 1000.0
    
    def test_multiple_redemptions_accumulate(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Test that multiple redemptions accumulate"""
        # Setup: Create multiple completed referrals
        for i in range(3):
            referred_client = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client
            )
            
            ReferralService.complete_referral(
                tenant_id=tenant_id,
                referred_client_id=referred_client,
                reward_amount=2000.0
            )
        
        # Redeem multiple times
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=referrer_id,
            amount=1000.0
        )
        
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=referrer_id,
            amount=1500.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        assert referral["total_redeemed"] == 2500.0
        assert len(referral["redemption_records"]) == 2
    
    def test_redeem_exact_balance(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test redeeming exact balance amount"""
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=completed_referral,
            amount=5000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(completed_referral)
        })
        
        assert referral["pending_rewards"] == 0.0
    
    def test_zero_amount_redemption_fails(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test that zero amount redemption fails"""
        with pytest.raises(ValueError):
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=completed_referral,
                amount=0.0
            )
    
    def test_negative_amount_redemption_fails(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test that negative amount redemption fails"""
        with pytest.raises(ValueError):
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=completed_referral,
                amount=-1000.0
            )
    
    def test_redeem_nonexistent_client_fails(self, db, tenant_id, cleanup_referrals):
        """Test that redeeming for nonexistent client fails"""
        nonexistent_client = str(ObjectId())
        
        with pytest.raises(ValueError):
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=nonexistent_client,
                amount=1000.0
            )
    
    def test_redemption_creates_account_credit(self, db, tenant_id, completed_referral, cleanup_referrals):
        """Test that redemption creates account credit"""
        redemption_amount = 2000.0
        
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=completed_referral,
            amount=redemption_amount
        )
        
        # Verify account credit is created
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(completed_referral)
        })
        
        assert "account_credit" in referral
        assert referral["account_credit"] == redemption_amount


class TestReferralRewardRedemptionProperties:
    """Property-based tests for referral reward redemption"""
    
    def test_redeemed_amount_always_positive(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Property: Redeemed amount should always be positive"""
        # Setup: Create completed referral with 10000 balance
        referred_client = str(ObjectId())
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client
        )
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client,
            reward_amount=10000.0
        )
        
        # Test multiple redemption amounts
        for amount in [100.0, 500.0, 1000.0, 5000.0]:
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=referrer_id,
                amount=amount
            )
            
            referral = db.referrals.find_one({
                "tenant_id": tenant_id,
                "client_id": ObjectId(referrer_id)
            })
            
            # Find the last redemption
            last_redemption = referral["redemption_records"][-1]
            assert last_redemption["amount"] > 0
    
    def test_pending_balance_never_negative(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Property: Pending balance should never go negative"""
        # Setup: Create completed referral
        referred_client = str(ObjectId())
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client
        )
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client,
            reward_amount=5000.0
        )
        
        # Redeem
        ReferralService.redeem_rewards(
            tenant_id=tenant_id,
            client_id=referrer_id,
            amount=3000.0
        )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        assert referral["pending_rewards"] >= 0
    
    def test_total_redeemed_equals_sum_of_redemptions(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Property: Total redeemed should equal sum of all redemptions"""
        # Setup: Create multiple completed referrals
        for i in range(3):
            referred_client = str(ObjectId())
            ReferralService.track_referral(
                tenant_id=tenant_id,
                referral_code=referral_code,
                referred_client_id=referred_client
            )
            
            ReferralService.complete_referral(
                tenant_id=tenant_id,
                referred_client_id=referred_client,
                reward_amount=3000.0
            )
        
        # Redeem multiple times
        redemptions = [500.0, 1000.0, 1500.0]
        for amount in redemptions:
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=referrer_id,
                amount=amount
            )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        expected_total = sum(redemptions)
        assert referral["total_redeemed"] == expected_total
    
    def test_each_redemption_has_timestamp(self, db, tenant_id, referrer_id, referral_code, cleanup_referrals):
        """Property: Each redemption should have a timestamp"""
        # Setup: Create completed referral
        referred_client = str(ObjectId())
        ReferralService.track_referral(
            tenant_id=tenant_id,
            referral_code=referral_code,
            referred_client_id=referred_client
        )
        
        ReferralService.complete_referral(
            tenant_id=tenant_id,
            referred_client_id=referred_client,
            reward_amount=5000.0
        )
        
        # Multiple redemptions
        for amount in [1000.0, 1500.0, 1000.0]:
            ReferralService.redeem_rewards(
                tenant_id=tenant_id,
                client_id=referrer_id,
                amount=amount
            )
        
        referral = db.referrals.find_one({
            "tenant_id": tenant_id,
            "client_id": ObjectId(referrer_id)
        })
        
        for redemption in referral["redemption_records"]:
            assert "redeemed_at" in redemption
            assert isinstance(redemption["redeemed_at"], datetime)
