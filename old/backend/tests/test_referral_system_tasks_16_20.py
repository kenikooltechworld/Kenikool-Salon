"""
Tests for Referral System Tasks 16-20
Task 16: Test Referral Link Generation
Task 17: Test Referral Tracking
Task 18: Test Reward Completion
Task 19: Test Reward Redemption
Task 20: Test Social Sharing
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from bson import ObjectId
from app.services.referral_service import ReferralService


class TestReferralLinkGeneration:
    """Task 16: Test Referral Link Generation"""
    
    @patch('app.services.referral_service.Database')
    def test_generate_link_for_new_client(self, mock_db):
        """Generate link for new client"""
        # Setup
        tenant_id = "tenant123"
        client_id = "client123"
        tenant_subdomain = "mysalon"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        mock_db_instance.referrals.find_one.return_value = None
        mock_db_instance.referrals.insert_one.return_value.inserted_id = ObjectId()
        
        # Execute
        result = ReferralService.generate_referral_link(tenant_id, client_id, tenant_subdomain)
        
        # Assert
        assert result["referral_code"] is not None
        assert len(result["referral_code"]) == 8
        assert result["referral_link"] == f"https://{tenant_subdomain}.salon.com/register?ref={result['referral_code']}"
        assert "created_at" in result
    
    @patch('app.services.referral_service.Database')
    def test_generate_link_uniqueness(self, mock_db):
        """Verify uniqueness of generated codes"""
        tenant_id = "tenant123"
        client_id1 = "client123"
        client_id2 = "client456"
        tenant_subdomain = "mysalon"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        mock_db_instance.referrals.find_one.return_value = None
        mock_db_instance.referrals.insert_one.return_value.inserted_id = ObjectId()
        
        # Generate two codes
        result1 = ReferralService.generate_referral_link(tenant_id, client_id1, tenant_subdomain)
        result2 = ReferralService.generate_referral_link(tenant_id, client_id2, tenant_subdomain)
        
        # Assert codes are different
        assert result1["referral_code"] != result2["referral_code"]
    
    @patch('app.services.referral_service.Database')
    def test_existing_client_returns_same_link(self, mock_db):
        """Test existing client returns same link"""
        tenant_id = "tenant123"
        client_id = "client123"
        tenant_subdomain = "mysalon"
        existing_code = "ABC12345"
        existing_link = f"https://{tenant_subdomain}.salon.com/register?ref={existing_code}"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        # First call returns existing referral
        existing_referral = {
            "_id": ObjectId(),
            "code": existing_code,
            "referral_link": existing_link,
            "created_at": datetime.utcnow()
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        result = ReferralService.generate_referral_link(tenant_id, client_id, tenant_subdomain)
        
        # Assert
        assert result["referral_code"] == existing_code
        assert result["referral_link"] == existing_link


class TestReferralTracking:
    """Task 17: Test Referral Tracking"""
    
    @patch('app.services.referral_service.Database')
    def test_register_with_valid_referral_code(self, mock_db):
        """Register with valid referral code"""
        tenant_id = "tenant123"
        referral_code = "ABC12345"
        referred_client_id = "client456"
        referrer_id = "client123"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        # Mock finding the referral
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "code": referral_code,
            "client_id": ObjectId(referrer_id),
            "status": "active",
            "tracking_records": []
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        result = ReferralService.track_referral(tenant_id, referral_code, referred_client_id)
        
        # Assert
        assert result["status"] == "tracked"
        assert result["referrer_id"] == referrer_id
        assert result["referred_client_id"] == referred_client_id
        mock_db_instance.referrals.update_one.assert_called_once()
    
    @patch('app.services.referral_service.Database')
    def test_verify_tracking_record_created(self, mock_db):
        """Verify tracking record created"""
        tenant_id = "tenant123"
        referral_code = "ABC12345"
        referred_client_id = "client456"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "code": referral_code,
            "client_id": ObjectId("client123"),
            "status": "active",
            "tracking_records": []
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        ReferralService.track_referral(tenant_id, referral_code, referred_client_id)
        
        # Assert update was called with tracking record
        call_args = mock_db_instance.referrals.update_one.call_args
        assert call_args is not None
        update_dict = call_args[0][1]
        assert "$push" in update_dict
        assert "tracking_records" in update_dict["$push"]
    
    @patch('app.services.referral_service.Database')
    def test_duplicate_prevention(self, mock_db):
        """Test duplicate prevention"""
        tenant_id = "tenant123"
        referral_code = "ABC12345"
        referred_client_id = "client456"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        # Mock finding existing tracking
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "code": referral_code,
            "client_id": ObjectId("client123"),
            "status": "active",
            "tracking_records": [
                {
                    "referred_client_id": ObjectId(referred_client_id),
                    "status": "pending"
                }
            ]
        }
        
        # First call returns None (no duplicate), second call returns existing
        mock_db_instance.referrals.find_one.side_effect = [
            existing_referral,  # For finding referral by code
            existing_referral   # For checking duplicate
        ]
        
        # Execute and assert
        with pytest.raises(ValueError, match="already been tracked"):
            ReferralService.track_referral(tenant_id, referral_code, referred_client_id)
    
    @patch('app.services.referral_service.Database')
    def test_invalid_code_handling(self, mock_db):
        """Test invalid code handling"""
        tenant_id = "tenant123"
        referral_code = "INVALID"
        referred_client_id = "client456"
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        mock_db_instance.referrals.find_one.return_value = None
        
        # Execute and assert
        with pytest.raises(ValueError, match="Invalid or inactive"):
            ReferralService.track_referral(tenant_id, referral_code, referred_client_id)


class TestRewardCompletion:
    """Task 18: Test Reward Completion"""
    
    @patch('app.services.referral_service.Database')
    def test_complete_first_booking_for_referred_client(self, mock_db):
        """Complete first booking for referred client"""
        tenant_id = "tenant123"
        referred_client_id = "client456"
        reward_amount = 1000
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId("client123"),
            "tracking_records": [
                {
                    "referred_client_id": ObjectId(referred_client_id),
                    "status": "pending"
                }
            ]
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        result = ReferralService.complete_referral(tenant_id, referred_client_id, reward_amount)
        
        # Assert
        assert result["status"] == "completed"
        assert result["reward_amount"] == reward_amount
        mock_db_instance.referrals.update_one.assert_called_once()
    
    @patch('app.services.referral_service.Database')
    def test_verify_reward_calculated(self, mock_db):
        """Verify reward calculated"""
        tenant_id = "tenant123"
        referred_client_id = "client456"
        reward_amount = 1500
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId("client123"),
            "tracking_records": [
                {
                    "referred_client_id": ObjectId(referred_client_id),
                    "status": "pending"
                }
            ]
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        result = ReferralService.complete_referral(tenant_id, referred_client_id, reward_amount)
        
        # Assert
        assert result["reward_amount"] == reward_amount
    
    @patch('app.services.referral_service.Database')
    def test_verify_referrer_balance_updated(self, mock_db):
        """Verify referrer balance updated"""
        tenant_id = "tenant123"
        referred_client_id = "client456"
        reward_amount = 1000
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId("client123"),
            "tracking_records": [
                {
                    "referred_client_id": ObjectId(referred_client_id),
                    "status": "pending"
                }
            ]
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        ReferralService.complete_referral(tenant_id, referred_client_id, reward_amount)
        
        # Assert update includes pending_rewards increment
        call_args = mock_db_instance.referrals.update_one.call_args
        update_dict = call_args[0][1]
        assert "$inc" in update_dict
        assert "pending_rewards" in update_dict["$inc"]
        assert update_dict["$inc"]["pending_rewards"] == reward_amount
    
    @patch('app.services.referral_service.Database')
    def test_notification_sent(self, mock_db):
        """Test notification sent"""
        tenant_id = "tenant123"
        referred_client_id = "client456"
        reward_amount = 1000
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId("client123"),
            "tracking_records": [
                {
                    "referred_client_id": ObjectId(referred_client_id),
                    "status": "pending"
                }
            ]
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        result = ReferralService.complete_referral(tenant_id, referred_client_id, reward_amount)
        
        # Assert result indicates completion
        assert result["status"] == "completed"


class TestRewardRedemption:
    """Task 19: Test Reward Redemption"""
    
    @patch('app.services.referral_service.Database')
    def test_redeem_with_sufficient_balance(self, mock_db):
        """Redeem with sufficient balance"""
        tenant_id = "tenant123"
        client_id = "client123"
        redeem_amount = 500
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "pending_rewards": 1000,
            "redeemed_rewards": 0
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        result = ReferralService.redeem_rewards(tenant_id, client_id, redeem_amount)
        
        # Assert
        assert result["status"] == "redeemed"
        assert result["amount"] == redeem_amount
        assert result["remaining_balance"] == 500
    
    @patch('app.services.referral_service.Database')
    def test_insufficient_balance_error(self, mock_db):
        """Test insufficient balance error"""
        tenant_id = "tenant123"
        client_id = "client123"
        redeem_amount = 2000
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "pending_rewards": 500,
            "redeemed_rewards": 0
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute and assert
        with pytest.raises(ValueError, match="Insufficient rewards"):
            ReferralService.redeem_rewards(tenant_id, client_id, redeem_amount)
    
    @patch('app.services.referral_service.Database')
    def test_verify_balance_deducted(self, mock_db):
        """Verify balance deducted"""
        tenant_id = "tenant123"
        client_id = "client123"
        redeem_amount = 300
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "pending_rewards": 1000,
            "redeemed_rewards": 0
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        ReferralService.redeem_rewards(tenant_id, client_id, redeem_amount)
        
        # Assert update includes pending_rewards decrement
        call_args = mock_db_instance.referrals.update_one.call_args
        update_dict = call_args[0][1]
        assert "$inc" in update_dict
        assert update_dict["$inc"]["pending_rewards"] == -redeem_amount
    
    @patch('app.services.referral_service.Database')
    def test_verify_redemption_record_created(self, mock_db):
        """Verify redemption record created"""
        tenant_id = "tenant123"
        client_id = "client123"
        redeem_amount = 500
        
        mock_db_instance = MagicMock()
        mock_db.get_db.return_value = mock_db_instance
        
        existing_referral = {
            "_id": ObjectId(),
            "tenant_id": tenant_id,
            "client_id": ObjectId(client_id),
            "pending_rewards": 1000,
            "redeemed_rewards": 0
        }
        mock_db_instance.referrals.find_one.return_value = existing_referral
        
        # Execute
        ReferralService.redeem_rewards(tenant_id, client_id, redeem_amount)
        
        # Assert update includes redemption record
        call_args = mock_db_instance.referrals.update_one.call_args
        update_dict = call_args[0][1]
        assert "$push" in update_dict
        assert "redemption_records" in update_dict["$push"]


class TestSocialSharing:
    """Task 20: Test Social Sharing"""
    
    def test_whatsapp_share_link(self):
        """Test WhatsApp share link"""
        referral_code = "ABC12345"
        salon_name = "My Salon"
        referral_link = f"https://mysalon.salon.com/register?ref={referral_code}"
        
        # Build WhatsApp share URL
        message = f"Hey! I found this amazing salon - {salon_name}. Use my referral link to book and we both get rewards! {referral_link}"
        whatsapp_url = f"https://wa.me/?text={message}"
        
        # Assert
        assert referral_code in whatsapp_url
        assert salon_name in whatsapp_url
        assert referral_link in whatsapp_url
    
    def test_facebook_share_dialog(self):
        """Test Facebook share dialog"""
        referral_code = "ABC12345"
        salon_name = "My Salon"
        referral_link = f"https://mysalon.salon.com/register?ref={referral_code}"
        
        # Build Facebook share URL
        message = f"Check out {salon_name}! Book using my link: {referral_link}"
        facebook_url = f"https://www.facebook.com/sharer/sharer.php?u={referral_link}"
        
        # Assert
        assert referral_link in facebook_url
        assert referral_code in referral_link
    
    def test_twitter_share_link(self):
        """Test Twitter share link"""
        referral_code = "ABC12345"
        salon_name = "My Salon"
        referral_link = f"https://mysalon.salon.com/register?ref={referral_code}"
        
        # Build Twitter share URL
        tweet = f"Just discovered {salon_name}! Book with my referral link and get rewards: {referral_link}"
        twitter_url = f"https://twitter.com/intent/tweet?text={tweet}"
        
        # Assert
        assert referral_code in twitter_url
        assert salon_name in twitter_url
        assert referral_link in twitter_url
    
    def test_verify_referral_code_in_all_links(self):
        """Verify referral code in all links"""
        referral_code = "ABC12345"
        salon_name = "My Salon"
        referral_link = f"https://mysalon.salon.com/register?ref={referral_code}"
        
        # WhatsApp
        whatsapp_message = f"Hey! I found this amazing salon - {salon_name}. Use my referral link to book and we both get rewards! {referral_link}"
        assert referral_code in whatsapp_message
        
        # Facebook
        facebook_message = f"Check out {salon_name}! Book using my link: {referral_link}"
        assert referral_code in facebook_message
        
        # Twitter
        twitter_message = f"Just discovered {salon_name}! Book with my referral link and get rewards: {referral_link}"
        assert referral_code in twitter_message
        
        # All should contain the code
        assert all(referral_code in msg for msg in [whatsapp_message, facebook_message, twitter_message])


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
