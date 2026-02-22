"""
Tests for membership payment processing service.
Tests payment processing, renewal, grace period logic, and proration calculations.
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock, patch
from bson import ObjectId

from app.services.membership_service import MembershipService
from app.schemas.membership import BillingCycle, SubscriptionStatus


@pytest.fixture
def mock_db():
    """Create mock database"""
    db = MagicMock()
    db.__getitem__ = MagicMock(return_value=MagicMock())
    return db


@pytest.fixture
def membership_service(mock_db):
    """Create membership service with mock database"""
    service = MembershipService(mock_db)
    service.paystack_service = AsyncMock()
    return service


class TestProcessPayment:
    """Tests for payment processing"""

    @pytest.mark.asyncio
    async def test_process_payment_success(self, membership_service, mock_db):
        """Test successful payment processing"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "tenant_id": "tenant_1",
            "client_id": "client_1",
            "plan_id": "plan_1",
            "payment_method_id": "auth_code_123",
            "payment_history": [],
        }
        
        client = {
            "_id": ObjectId("client_1"),
            "email": "client@example.com",
        }
        
        plan = {
            "_id": ObjectId("plan_1"),
            "name": "Gold Plan",
            "price": 99.99,
            "billing_cycle": "monthly",
        }
        
        # Mock Paystack response
        paystack_response = {
            "reference": "ref_123456",
            "status": "success",
            "amount": 9999,
        }
        
        membership_service.paystack_service.charge_authorization.return_value = paystack_response
        
        # Mock database queries
        mock_db.__getitem__.return_value.find_one = AsyncMock(side_effect=[subscription, client, plan])
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=subscription)
        
        # Execute
        result = await membership_service.process_payment(
            subscription_id=subscription_id,
            amount=99.99,
            description="Test payment",
        )
        
        # Assert
        assert result["success"] is True
        assert result["transaction_id"] == "ref_123456"
        assert result["amount"] == 99.99
        
        # Verify Paystack was called with correct parameters
        membership_service.paystack_service.charge_authorization.assert_called_once()
        call_args = membership_service.paystack_service.charge_authorization.call_args
        assert call_args.kwargs["authorization_code"] == "auth_code_123"
        assert call_args.kwargs["email"] == "client@example.com"
        assert call_args.kwargs["amount"] == 99.99

    @pytest.mark.asyncio
    async def test_process_payment_failure(self, membership_service, mock_db):
        """Test payment processing failure"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "tenant_id": "tenant_1",
            "client_id": "client_1",
            "plan_id": "plan_1",
            "payment_method_id": "auth_code_123",
        }
        
        client = {
            "_id": ObjectId("client_1"),
            "email": "client@example.com",
        }
        
        plan = {
            "_id": ObjectId("plan_1"),
            "name": "Gold Plan",
            "price": 99.99,
        }
        
        # Mock Paystack failure
        membership_service.paystack_service.charge_authorization.side_effect = Exception("Payment declined")
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(side_effect=[subscription, client, plan])
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=subscription)
        
        # Execute & Assert
        with pytest.raises(Exception):
            await membership_service.process_payment(
                subscription_id=subscription_id,
                amount=99.99,
                description="Test payment",
            )


class TestCalculateProration:
    """Tests for proration calculations"""

    @pytest.mark.asyncio
    async def test_proration_upgrade(self, membership_service, mock_db):
        """Test proration for plan upgrade"""
        # Setup
        current_plan = {
            "_id": ObjectId("plan_1"),
            "name": "Silver",
            "price": 50.0,
            "billing_cycle": "monthly",
        }
        
        new_plan = {
            "_id": ObjectId("plan_2"),
            "name": "Gold",
            "price": 100.0,
            "billing_cycle": "monthly",
        }
        
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "tenant_1",
            "plan_id": str(current_plan["_id"]),
            "end_date": now + timedelta(days=15),  # 15 days remaining
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=current_plan)
        
        # Execute
        proration = await membership_service.calculate_proration(subscription, new_plan)
        
        # Assert - upgrade should be positive
        # Daily rate difference: (100/30 - 50/30) * 15 = (3.33 - 1.67) * 15 = 25
        assert proration > 0
        assert abs(proration - 25.0) < 1.0  # Allow small rounding difference

    @pytest.mark.asyncio
    async def test_proration_downgrade(self, membership_service, mock_db):
        """Test proration for plan downgrade"""
        # Setup
        current_plan = {
            "_id": ObjectId("plan_1"),
            "name": "Gold",
            "price": 100.0,
            "billing_cycle": "monthly",
        }
        
        new_plan = {
            "_id": ObjectId("plan_2"),
            "name": "Silver",
            "price": 50.0,
            "billing_cycle": "monthly",
        }
        
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "tenant_1",
            "plan_id": str(current_plan["_id"]),
            "end_date": now + timedelta(days=15),
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=current_plan)
        
        # Execute
        proration = await membership_service.calculate_proration(subscription, new_plan)
        
        # Assert - downgrade should be negative
        assert proration < 0

    @pytest.mark.asyncio
    async def test_proration_quarterly_cycle(self, membership_service, mock_db):
        """Test proration with quarterly billing cycle"""
        # Setup
        current_plan = {
            "_id": ObjectId("plan_1"),
            "name": "Silver",
            "price": 150.0,
            "billing_cycle": "quarterly",
        }
        
        new_plan = {
            "_id": ObjectId("plan_2"),
            "name": "Gold",
            "price": 300.0,
            "billing_cycle": "quarterly",
        }
        
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "tenant_1",
            "plan_id": str(current_plan["_id"]),
            "end_date": now + timedelta(days=45),  # 45 days remaining in 90-day cycle
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=current_plan)
        
        # Execute
        proration = await membership_service.calculate_proration(subscription, new_plan)
        
        # Assert
        # Daily rate difference: (300/90 - 150/90) * 45 = (3.33 - 1.67) * 45 = 75
        assert proration > 0
        assert abs(proration - 75.0) < 1.0


class TestProcessRenewal:
    """Tests for subscription renewal"""

    @pytest.mark.asyncio
    async def test_renewal_success(self, membership_service, mock_db):
        """Test successful subscription renewal"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "tenant_id": "tenant_1",
            "client_id": "client_1",
            "plan_id": "plan_1",
            "auto_renew": True,
            "payment_method_id": "auth_code_123",
            "payment_history": [],
            "renewal_history": [],
            "benefit_usage": {"limit": -1},
        }
        
        plan = {
            "_id": ObjectId("plan_1"),
            "name": "Gold",
            "price": 99.99,
            "billing_cycle": "monthly",
        }
        
        # Mock database
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=subscription)
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=subscription)
        
        # Mock payment processing
        with patch.object(membership_service, 'process_payment', new_callable=AsyncMock) as mock_payment:
            mock_payment.return_value = {
                "success": True,
                "transaction_id": "ref_123",
                "amount": 99.99,
            }
            
            # Execute
            result = await membership_service.process_renewal(subscription_id)
            
            # Assert
            assert result["success"] is True
            assert "new_end_date" in result
            mock_payment.assert_called_once()

    @pytest.mark.asyncio
    async def test_renewal_auto_renew_disabled(self, membership_service, mock_db):
        """Test renewal when auto_renew is disabled"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "auto_renew": False,
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=subscription)
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Auto-renewal is disabled"):
            await membership_service.process_renewal(subscription_id)


class TestHandleFailedPayment:
    """Tests for failed payment handling with grace period"""

    @pytest.mark.asyncio
    async def test_first_payment_failure_enters_grace_period(self, membership_service, mock_db):
        """Test that first payment failure enters grace period"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "status": "active",
            "retry_count": 0,
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=subscription)
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=subscription)
        
        # Execute
        result = await membership_service.handle_failed_payment(
            subscription_id=subscription_id,
            reason="Card declined",
        )
        
        # Assert
        assert result["status"] == "grace_period_entered"
        assert result["retry_count"] == 1
        assert result["max_retries"] == 3

    @pytest.mark.asyncio
    async def test_retry_attempt(self, membership_service, mock_db):
        """Test payment retry attempt"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "status": "grace_period",
            "retry_count": 1,
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=subscription)
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=subscription)
        
        # Execute
        result = await membership_service.handle_failed_payment(
            subscription_id=subscription_id,
            reason="Retry attempt",
        )
        
        # Assert
        assert result["status"] == "retry_scheduled"
        assert result["retry_count"] == 2

    @pytest.mark.asyncio
    async def test_max_retries_exceeded_cancels_subscription(self, membership_service, mock_db):
        """Test that subscription is cancelled after max retries"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "status": "grace_period",
            "retry_count": 3,
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=subscription)
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=subscription)
        
        # Execute
        result = await membership_service.handle_failed_payment(
            subscription_id=subscription_id,
            reason="Max retries exceeded",
        )
        
        # Assert
        assert result["status"] == "cancelled"
        assert result["reason"] == "Max retries exceeded"
        assert result["retry_count"] == 3


class TestUpdatePaymentMethod:
    """Tests for updating payment method"""

    @pytest.mark.asyncio
    async def test_update_payment_method_success(self, membership_service, mock_db):
        """Test successful payment method update"""
        # Setup
        subscription_id = str(ObjectId())
        subscription = {
            "_id": ObjectId(subscription_id),
            "tenant_id": "tenant_1",
            "payment_method_id": "old_auth_code",
        }
        
        updated_subscription = {
            **subscription,
            "payment_method_id": "new_auth_code",
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=subscription)
        mock_db.__getitem__.return_value.find_one_and_update = AsyncMock(return_value=updated_subscription)
        
        # Execute
        result = await membership_service.update_payment_method(
            tenant_id="tenant_1",
            subscription_id=subscription_id,
            payment_method_id="new_auth_code",
        )
        
        # Assert
        assert result["payment_method_id"] == "new_auth_code"

    @pytest.mark.asyncio
    async def test_update_payment_method_not_found(self, membership_service, mock_db):
        """Test updating payment method for non-existent subscription"""
        # Setup
        subscription_id = str(ObjectId())
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=None)
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Subscription .* not found"):
            await membership_service.update_payment_method(
                tenant_id="tenant_1",
                subscription_id=subscription_id,
                payment_method_id="new_auth_code",
            )


class TestAnalyticsCalculations:
    """Tests for analytics calculations"""

    @pytest.mark.asyncio
    async def test_calculate_mrr(self, membership_service, mock_db):
        """Test MRR calculation"""
        # Setup
        subscriptions = [
            {
                "_id": ObjectId(),
                "plan_id": "plan_1",
                "status": "active",
            },
            {
                "_id": ObjectId(),
                "plan_id": "plan_2",
                "status": "active",
            },
        ]
        
        plans = [
            {
                "_id": ObjectId("plan_1"),
                "price": 50.0,
                "billing_cycle": "monthly",
            },
            {
                "_id": ObjectId("plan_2"),
                "price": 100.0,
                "billing_cycle": "monthly",
            },
        ]
        
        mock_db.__getitem__.return_value.find = AsyncMock(return_value=AsyncMock(to_list=AsyncMock(return_value=subscriptions)))
        mock_db.__getitem__.return_value.find_one = AsyncMock(side_effect=plans)
        
        # Execute
        mrr = await membership_service.calculate_mrr("tenant_1")
        
        # Assert
        assert mrr == 150.0  # 50 + 100

    @pytest.mark.asyncio
    async def test_calculate_churn_rate(self, membership_service, mock_db):
        """Test churn rate calculation"""
        # Setup
        mock_db.__getitem__.return_value.count_documents = AsyncMock(side_effect=[5, 100])  # 5 cancelled, 100 active
        
        # Execute
        churn_rate = await membership_service.calculate_churn_rate("tenant_1", period_days=30)
        
        # Assert
        assert churn_rate == 5.0  # 5/100 * 100


class TestProrationEdgeCases:
    """Tests for proration edge cases"""

    @pytest.mark.asyncio
    async def test_proration_no_days_remaining(self, membership_service, mock_db):
        """Test proration when subscription has expired"""
        # Setup
        current_plan = {
            "_id": ObjectId("plan_1"),
            "price": 50.0,
            "billing_cycle": "monthly",
        }
        
        new_plan = {
            "_id": ObjectId("plan_2"),
            "price": 100.0,
            "billing_cycle": "monthly",
        }
        
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "tenant_1",
            "plan_id": str(current_plan["_id"]),
            "end_date": now - timedelta(days=5),  # Already expired
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=current_plan)
        
        # Execute
        proration = await membership_service.calculate_proration(subscription, new_plan)
        
        # Assert - should be 0 since no days remaining
        assert proration == 0.0

    @pytest.mark.asyncio
    async def test_proration_yearly_cycle(self, membership_service, mock_db):
        """Test proration with yearly billing cycle"""
        # Setup
        current_plan = {
            "_id": ObjectId("plan_1"),
            "price": 1200.0,
            "billing_cycle": "yearly",
        }
        
        new_plan = {
            "_id": ObjectId("plan_2"),
            "price": 2400.0,
            "billing_cycle": "yearly",
        }
        
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "tenant_1",
            "plan_id": str(current_plan["_id"]),
            "end_date": now + timedelta(days=182),  # ~6 months remaining
        }
        
        mock_db.__getitem__.return_value.find_one = AsyncMock(return_value=current_plan)
        
        # Execute
        proration = await membership_service.calculate_proration(subscription, new_plan)
        
        # Assert
        # Daily rate difference: (2400/365 - 1200/365) * 182 = (6.58 - 3.29) * 182 ≈ 600
        assert proration > 0
        assert abs(proration - 600.0) < 50.0  # Allow reasonable rounding

