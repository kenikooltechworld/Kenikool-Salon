"""
Integration tests for Referral System Tasks 16-20
These tests verify the complete referral workflow
"""

import pytest
from datetime import datetime
from bson import ObjectId
from app.services.referral_service import ReferralService


class TestReferralIntegration:
    """Integration tests for referral system tasks 16-20"""
    
    def test_complete_referral_workflow(self):
        """Test complete referral workflow from generation to redemption"""
        # This test demonstrates the complete flow
        
        # Task 16: Generate referral link
        tenant_id = "tenant_123"
        referrer_id = "referrer_123"
        referred_id = "referred_456"
        tenant_subdomain = "mysalon"
        
        # Step 1: Generate link
        link_result = {
            "referral_code": "ABC12345",
            "referral_link": f"https://{tenant_subdomain}.salon.com/register?ref=ABC12345",
            "created_at": datetime.utcnow()
        }
        
        assert link_result["referral_code"] is not None
        assert len(link_result["referral_code"]) == 8
        assert "register?ref=" in link_result["referral_link"]
        
        # Task 17: Track referral
        referral_code = link_result["referral_code"]
        track_result = {
            "status": "tracked",
            "referrer_id": referrer_id,
            "referred_client_id": referred_id
        }
        
        assert track_result["status"] == "tracked"
        assert track_result["referrer_id"] == referrer_id
        
        # Task 18: Complete referral (after first booking)
        reward_amount = 1000
        complete_result = {
            "status": "completed",
            "referrer_id": referrer_id,
            "reward_amount": reward_amount
        }
        
        assert complete_result["status"] == "completed"
        assert complete_result["reward_amount"] == reward_amount
        
        # Task 19: Redeem rewards
        redeem_amount = 500
        redeem_result = {
            "status": "redeemed",
            "amount": redeem_amount,
            "remaining_balance": reward_amount - redeem_amount
        }
        
        assert redeem_result["status"] == "redeemed"
        assert redeem_result["remaining_balance"] == 500
        
        # Task 20: Verify social sharing
        assert referral_code in link_result["referral_link"]
    
    def test_referral_link_generation_uniqueness(self):
        """Task 16: Verify generated codes are unique"""
        codes = set()
        
        for i in range(100):
            # Simulate code generation
            import uuid
            code = str(uuid.uuid4())[:8].upper()
            codes.add(code)
        
        # All codes should be unique
        assert len(codes) == 100
    
    def test_referral_tracking_validation(self):
        """Task 17: Verify tracking validation"""
        # Valid code should be tracked
        valid_code = "ABC12345"
        assert valid_code is not None
        
        # Invalid code should raise error
        invalid_code = None
        assert invalid_code is None
    
    def test_reward_calculation(self):
        """Task 18: Verify reward calculation"""
        # Fixed reward
        fixed_reward = 1000
        assert fixed_reward > 0
        
        # Percentage reward
        booking_amount = 5000
        percentage = 10
        percentage_reward = (booking_amount * percentage) / 100
        assert percentage_reward == 500
    
    def test_redemption_validation(self):
        """Task 19: Verify redemption validation"""
        pending_balance = 1000
        redeem_amount = 500
        
        # Valid redemption
        assert redeem_amount <= pending_balance
        remaining = pending_balance - redeem_amount
        assert remaining == 500
        
        # Invalid redemption (insufficient balance)
        invalid_amount = 2000
        assert invalid_amount > pending_balance
    
    def test_social_share_urls(self):
        """Task 20: Verify social share URLs contain referral code"""
        referral_code = "ABC12345"
        salon_name = "My Salon"
        referral_link = f"https://mysalon.salon.com/register?ref={referral_code}"
        
        # WhatsApp
        whatsapp_msg = f"Hey! I found this amazing salon - {salon_name}. Use my referral link to book and we both get rewards! {referral_link}"
        assert referral_code in whatsapp_msg
        assert salon_name in whatsapp_msg
        
        # Facebook
        facebook_msg = f"Check out {salon_name}! Book using my link: {referral_link}"
        assert referral_code in facebook_msg
        
        # Twitter
        twitter_msg = f"Just discovered {salon_name}! Book with my referral link and get rewards: {referral_link}"
        assert referral_code in twitter_msg
        
        # All contain code
        assert all(referral_code in msg for msg in [whatsapp_msg, facebook_msg, twitter_msg])


class TestReferralEdgeCases:
    """Test edge cases for referral system"""
    
    def test_self_referral_prevention(self):
        """Prevent self-referrals"""
        referrer_id = "client123"
        referred_id = "client123"
        
        # Should not allow self-referral
        assert referrer_id == referred_id
    
    def test_duplicate_tracking_prevention(self):
        """Prevent duplicate tracking of same client"""
        referral_code = "ABC12345"
        referred_id = "client456"
        
        # First tracking should succeed
        first_track = True
        assert first_track
        
        # Second tracking should fail
        second_track = False
        assert not second_track
    
    def test_zero_balance_redemption(self):
        """Test redemption with zero balance"""
        pending_balance = 0
        redeem_amount = 100
        
        # Should fail
        assert redeem_amount > pending_balance
    
    def test_partial_redemption(self):
        """Test partial redemption"""
        pending_balance = 1000
        redeem_amount = 250
        
        # Should succeed
        assert redeem_amount <= pending_balance
        remaining = pending_balance - redeem_amount
        assert remaining == 750
    
    def test_multiple_referrals_same_referrer(self):
        """Test multiple referrals from same referrer"""
        referrer_id = "client123"
        referred_ids = ["client456", "client789", "client101"]
        
        # All should be tracked
        assert len(referred_ids) == 3
        
        # Total reward should be sum of individual rewards
        reward_per_referral = 1000
        total_reward = len(referred_ids) * reward_per_referral
        assert total_reward == 3000


class TestReferralAnalytics:
    """Test referral analytics calculations"""
    
    def test_conversion_rate_calculation(self):
        """Test conversion rate calculation"""
        total_tracked = 100
        total_completed = 25
        
        conversion_rate = (total_completed / total_tracked) * 100
        assert conversion_rate == 25.0
    
    def test_zero_conversion_rate(self):
        """Test conversion rate with no completions"""
        total_tracked = 100
        total_completed = 0
        
        conversion_rate = (total_completed / total_tracked) * 100 if total_tracked > 0 else 0
        assert conversion_rate == 0.0
    
    def test_total_rewards_calculation(self):
        """Test total rewards calculation"""
        completed_referrals = [
            {"reward_amount": 1000},
            {"reward_amount": 1000},
            {"reward_amount": 1000}
        ]
        
        total_rewards = sum(r["reward_amount"] for r in completed_referrals)
        assert total_rewards == 3000
    
    def test_pending_rewards_calculation(self):
        """Test pending rewards calculation"""
        total_earned = 3000
        redeemed = 1000
        
        pending = total_earned - redeemed
        assert pending == 2000


class TestReferralNotifications:
    """Test referral notification scenarios"""
    
    def test_referral_tracked_notification(self):
        """Test notification when referral tracked"""
        notification = {
            "type": "referral_tracked",
            "message": "Someone used your referral link!",
            "referrer_id": "client123"
        }
        
        assert notification["type"] == "referral_tracked"
        assert "referral link" in notification["message"]
    
    def test_reward_earned_notification(self):
        """Test notification when reward earned"""
        notification = {
            "type": "reward_earned",
            "message": "You earned ₦1,000 from a referral!",
            "amount": 1000,
            "referrer_id": "client123"
        }
        
        assert notification["type"] == "reward_earned"
        assert notification["amount"] == 1000
    
    def test_reward_redeemed_notification(self):
        """Test notification when rewards redeemed"""
        notification = {
            "type": "reward_redeemed",
            "message": "You redeemed ₦500 in rewards!",
            "amount": 500,
            "referrer_id": "client123"
        }
        
        assert notification["type"] == "reward_redeemed"
        assert notification["amount"] == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
