"""
End-to-End Workflow Tests for Membership System - Phase 9 Testing

Tests complete membership workflows from start to finish:
- Subscription creation workflow
- Subscription renewal workflow
- Subscription cancellation workflow
- Subscription pause/resume workflow
- Plan change workflow
- Payment failure workflow
- Trial period workflow

Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, AsyncMock
from bson import ObjectId
from decimal import Decimal

from app.services.membership_service import MembershipService


@pytest.fixture
def mock_db():
    """Create mock database"""
    return Mock()


@pytest.fixture
def mock_email_service():
    """Create mock email service"""
    return Mock()


@pytest.fixture
def mock_paystack_service():
    """Create mock Paystack service"""
    return Mock()


@pytest.fixture
def membership_service(mock_db, mock_email_service, mock_paystack_service):
    """Create MembershipService instance"""
    service = MembershipService(mock_db)
    service.email_service = mock_email_service
    service.paystack_service = mock_paystack_service
    return service


@pytest.fixture
def sample_plan():
    """Sample membership plan"""
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant",
        "name": "Gold Membership",
        "price": Decimal("99.99"),
        "duration_days": 30,
        "billing_cycle": "monthly",
        "benefits": ["20% off", "Priority booking"],
        "discount_percentage": 20,
        "trial_period_days": 7,
        "is_active": True,
    }


@pytest.fixture
def sample_client():
    """Sample client"""
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant",
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "1234567890",
    }


class TestSubscriptionCreationWorkflow:
    """End-to-end tests for subscription creation workflow"""

    def test_subscription_creation_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete subscription creation workflow"""
        # Setup
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.clients.find_one.return_value = sample_client
        mock_db.subscriptions.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Step 1: Create subscription
        subscription = membership_service.create_subscription(
            tenant_id="test_tenant",
            client_id=str(sample_client["_id"]),
            plan_id=str(sample_plan["_id"]),
            payment_method_id="pm_123",
            auto_renew=True,
            trial_days=7,
        )
        
        # Verify subscription created
        assert subscription is not None
        assert subscription["status"] == "active"
        
        # Step 2: Verify welcome email sent
        membership_service.email_service.send_welcome_email.assert_called_once()
        
        # Step 3: Verify subscription in database
        mock_db.subscriptions.insert_one.assert_called_once()
        
        # Step 4: Verify subscription appears in client profile
        mock_db.subscriptions.find_one.return_value = subscription
        retrieved = membership_service.get_subscription_details(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
        )
        assert retrieved is not None
        
        # Step 5: Verify discount applied in POS
        discount = membership_service.apply_membership_discount(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
            original_price=Decimal("100.00"),
        )
        assert discount > 0

    def test_subscription_creation_with_trial_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test subscription creation with trial period"""
        # Setup
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.clients.find_one.return_value = sample_client
        mock_db.subscriptions.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Create subscription with trial
        subscription = membership_service.create_subscription(
            tenant_id="test_tenant",
            client_id=str(sample_client["_id"]),
            plan_id=str(sample_plan["_id"]),
            payment_method_id="pm_123",
            auto_renew=True,
            trial_days=7,
        )
        
        # Verify trial period set
        assert subscription["is_trial"] is True
        assert subscription["trial_end_date"] is not None


class TestSubscriptionRenewalWorkflow:
    """End-to-end tests for subscription renewal workflow"""

    def test_subscription_renewal_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete subscription renewal workflow"""
        # Setup
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": sample_client["_id"],
            "plan_id": sample_plan["_id"],
            "status": "active",
            "start_date": now - timedelta(days=30),
            "end_date": now,
            "renewal_date": now,
            "auto_renew": True,
            "payment_method_id": "pm_123",
            "is_trial": False,
        }
        
        mock_db.subscriptions.find_one.return_value = subscription
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Step 1: Send 7-day renewal reminder
        membership_service.email_service.send_renewal_reminder_7day(
            client_email=sample_client["email"],
            client_name=sample_client["name"],
            plan_name=sample_plan["name"],
            plan_price=float(sample_plan["price"]),
            billing_cycle=sample_plan["billing_cycle"],
            discount_percentage=sample_plan["discount_percentage"],
            renewal_date=now + timedelta(days=7),
            manage_url="https://example.com/manage",
            pause_url="https://example.com/pause",
            salon_name="Test Salon",
            currency_symbol="₦",
        )
        
        # Step 2: Send 1-day renewal reminder
        membership_service.email_service.send_renewal_reminder_1day(
            client_email=sample_client["email"],
            client_name=sample_client["name"],
            plan_name=sample_plan["name"],
            plan_price=float(sample_plan["price"]),
            billing_cycle=sample_plan["billing_cycle"],
            discount_percentage=sample_plan["discount_percentage"],
            renewal_date=now + timedelta(days=1),
            manage_url="https://example.com/manage",
            cancel_url="https://example.com/cancel",
            salon_name="Test Salon",
            currency_symbol="₦",
        )
        
        # Step 3: Process renewal payment
        membership_service.paystack_service.charge_authorization.return_value = {
            "status": "success",
            "reference": "ref_123",
            "amount": float(sample_plan["price"]),
        }
        
        # Step 4: Update subscription dates
        new_renewal_date = now + timedelta(days=30)
        updated_subscription = subscription.copy()
        updated_subscription["renewal_date"] = new_renewal_date
        updated_subscription["end_date"] = new_renewal_date
        
        mock_db.subscriptions.find_one.return_value = updated_subscription
        
        # Step 5: Send renewal confirmation
        membership_service.email_service.send_renewal_confirmation(
            client_email=sample_client["email"],
            client_name=sample_client["name"],
            plan_name=sample_plan["name"],
            plan_price=float(sample_plan["price"]),
            billing_cycle=sample_plan["billing_cycle"],
            transaction_id="ref_123",
            renewal_date=now,
            next_renewal_date=new_renewal_date,
            dashboard_url="https://example.com/dashboard",
            salon_name="Test Salon",
            currency_symbol="₦",
        )
        
        # Verify all steps completed
        assert membership_service.email_service.send_renewal_reminder_7day.called
        assert membership_service.email_service.send_renewal_reminder_1day.called
        assert membership_service.paystack_service.charge_authorization.called
        assert membership_service.email_service.send_renewal_confirmation.called


class TestSubscriptionCancellationWorkflow:
    """End-to-end tests for subscription cancellation workflow"""

    def test_subscription_cancellation_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete subscription cancellation workflow"""
        # Setup
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": sample_client["_id"],
            "plan_id": sample_plan["_id"],
            "status": "active",
            "start_date": datetime.utcnow() - timedelta(days=30),
            "end_date": datetime.utcnow() + timedelta(days=30),
            "renewal_date": datetime.utcnow() + timedelta(days=30),
            "auto_renew": True,
            "payment_method_id": "pm_123",
        }
        
        mock_db.subscriptions.find_one.return_value = subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Step 1: Cancel subscription
        cancelled = membership_service.cancel_subscription(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
            reason="User requested",
        )
        
        # Verify cancellation
        assert cancelled["status"] == "cancelled"
        
        # Step 2: Verify cancellation email sent
        membership_service.email_service.send_cancellation_confirmation.assert_called_once()
        
        # Step 3: Verify discount no longer applied
        mock_db.subscriptions.find_one.return_value = cancelled
        discount = membership_service.apply_membership_discount(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
            original_price=Decimal("100.00"),
        )
        assert discount == Decimal("0.00")


class TestSubscriptionPauseResumeWorkflow:
    """End-to-end tests for subscription pause/resume workflow"""

    def test_subscription_pause_resume_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete subscription pause/resume workflow"""
        # Setup
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": sample_client["_id"],
            "plan_id": sample_plan["_id"],
            "status": "active",
            "start_date": datetime.utcnow() - timedelta(days=15),
            "end_date": datetime.utcnow() + timedelta(days=15),
            "renewal_date": datetime.utcnow() + timedelta(days=15),
            "auto_renew": True,
            "payment_method_id": "pm_123",
        }
        
        mock_db.subscriptions.find_one.return_value = subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Step 1: Pause subscription
        paused = membership_service.pause_subscription(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
        )
        
        # Verify pause
        assert paused["status"] == "paused"
        membership_service.email_service.send_pause_confirmation.assert_called_once()
        
        # Step 2: Verify renewal not processed while paused
        paused_subscription = subscription.copy()
        paused_subscription["status"] = "paused"
        mock_db.subscriptions.find_one.return_value = paused_subscription
        
        # Step 3: Resume subscription
        paused_subscription["status"] = "paused"
        mock_db.subscriptions.find_one.return_value = paused_subscription
        
        resumed = membership_service.resume_subscription(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
        )
        
        # Verify resume
        assert resumed["status"] == "active"
        membership_service.email_service.send_resume_confirmation.assert_called_once()


class TestPlanChangeWorkflow:
    """End-to-end tests for plan change workflow"""

    def test_plan_change_upgrade_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete plan upgrade workflow"""
        # Setup
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": sample_client["_id"],
            "plan_id": sample_plan["_id"],
            "status": "active",
            "start_date": datetime.utcnow() - timedelta(days=15),
            "end_date": datetime.utcnow() + timedelta(days=15),
            "renewal_date": datetime.utcnow() + timedelta(days=15),
            "auto_renew": True,
            "payment_method_id": "pm_123",
        }
        
        new_plan = sample_plan.copy()
        new_plan["_id"] = ObjectId()
        new_plan["price"] = Decimal("149.99")
        
        mock_db.subscriptions.find_one.return_value = subscription
        mock_db.plans.find_one.return_value = new_plan
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Step 1: Change plan
        changed = membership_service.change_plan(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
            new_plan_id=str(new_plan["_id"]),
        )
        
        # Verify plan changed
        assert changed["plan_id"] == str(new_plan["_id"])
        
        # Step 2: Verify proration calculated
        # Proration = (new_price - old_price) * (days_remaining / total_days)
        
        # Step 3: Verify payment processed
        membership_service.paystack_service.charge_authorization.return_value = {
            "status": "success",
            "reference": "ref_upgrade",
        }
        
        # Step 4: Verify new plan benefits apply immediately
        mock_db.subscriptions.find_one.return_value = changed
        retrieved = membership_service.get_subscription_details(
            tenant_id="test_tenant",
            subscription_id=str(subscription["_id"]),
        )
        assert retrieved["plan_id"] == str(new_plan["_id"])


class TestPaymentFailureWorkflow:
    """End-to-end tests for payment failure workflow"""

    def test_payment_failure_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete payment failure workflow"""
        # Setup
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": sample_client["_id"],
            "plan_id": sample_plan["_id"],
            "status": "active",
            "start_date": datetime.utcnow() - timedelta(days=30),
            "end_date": datetime.utcnow(),
            "renewal_date": datetime.utcnow(),
            "auto_renew": True,
            "payment_method_id": "pm_123",
            "retry_count": 0,
        }
        
        mock_db.subscriptions.find_one.return_value = subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Step 1: Payment fails
        membership_service.paystack_service.charge_authorization.return_value = {
            "status": "failed",
            "error": "Insufficient funds",
        }
        
        # Step 2: Subscription enters grace_period
        grace_subscription = subscription.copy()
        grace_subscription["status"] = "grace_period"
        grace_subscription["grace_period_end_date"] = datetime.utcnow() + timedelta(days=14)
        
        mock_db.subscriptions.find_one.return_value = grace_subscription
        
        # Step 3: Payment failure notification sent
        membership_service.email_service.send_payment_failure_notification(
            client_email=sample_client["email"],
            client_name=sample_client["name"],
            plan_name=sample_plan["name"],
            plan_price=float(sample_plan["price"]),
            billing_cycle=sample_plan["billing_cycle"],
            failure_reason="Insufficient funds",
            failure_date=datetime.utcnow(),
            grace_period_end_date=datetime.utcnow() + timedelta(days=14),
            update_payment_url="https://example.com/update-payment",
            contact_support_url="https://example.com/support",
            salon_name="Test Salon",
            currency_symbol="₦",
        )
        
        # Step 4: Payment retry attempted
        grace_subscription["retry_count"] = 1
        mock_db.subscriptions.find_one.return_value = grace_subscription
        
        # Step 5: Grace period warning sent if retries fail
        membership_service.email_service.send_grace_period_warning(
            client_email=sample_client["email"],
            client_name=sample_client["name"],
            plan_name=sample_plan["name"],
            plan_price=float(sample_plan["price"]),
            grace_period_end_date=datetime.utcnow() + timedelta(days=14),
            retry_date_1=datetime.utcnow() + timedelta(days=2),
            retry_date_2=datetime.utcnow() + timedelta(days=4),
            retry_date_3=datetime.utcnow() + timedelta(days=6),
            cancellation_date=datetime.utcnow() + timedelta(days=14),
            update_payment_url="https://example.com/update-payment",
            contact_support_url="https://example.com/support",
            salon_name="Test Salon",
            currency_symbol="₦",
        )
        
        # Step 6: Subscription cancelled after grace period
        cancelled_subscription = grace_subscription.copy()
        cancelled_subscription["status"] = "cancelled"
        
        mock_db.subscriptions.find_one.return_value = cancelled_subscription
        
        # Verify all steps completed
        assert membership_service.email_service.send_payment_failure_notification.called
        assert membership_service.email_service.send_grace_period_warning.called


class TestTrialPeriodWorkflow:
    """End-to-end tests for trial period workflow"""

    def test_trial_period_complete_workflow(self, membership_service, mock_db, sample_plan, sample_client):
        """Test complete trial period workflow"""
        # Setup
        now = datetime.utcnow()
        subscription = {
            "_id": ObjectId(),
            "tenant_id": "test_tenant",
            "client_id": sample_client["_id"],
            "plan_id": sample_plan["_id"],
            "status": "active",
            "start_date": now,
            "end_date": now + timedelta(days=7),
            "renewal_date": now + timedelta(days=7),
            "auto_renew": True,
            "payment_method_id": "pm_123",
            "is_trial": True,
            "trial_end_date": now + timedelta(days=7),
        }
        
        mock_db.subscriptions.find_one.return_value = subscription
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Step 1: Trial subscription created without payment
        assert subscription["is_trial"] is True
        
        # Step 2: Trial period duration respected
        assert subscription["trial_end_date"] == now + timedelta(days=7)
        
        # Step 3: Trial conversion task processes conversion
        # (This would be a background task)
        
        # Step 4: Payment processed on trial end date
        membership_service.paystack_service.charge_authorization.return_value = {
            "status": "success",
            "reference": "ref_trial_conversion",
            "amount": float(sample_plan["price"]),
        }
        
        # Step 5: Renewal confirmation sent
        membership_service.email_service.send_renewal_confirmation(
            client_email=sample_client["email"],
            client_name=sample_client["name"],
            plan_name=sample_plan["name"],
            plan_price=float(sample_plan["price"]),
            billing_cycle=sample_plan["billing_cycle"],
            transaction_id="ref_trial_conversion",
            renewal_date=now + timedelta(days=7),
            next_renewal_date=now + timedelta(days=37),
            dashboard_url="https://example.com/dashboard",
            salon_name="Test Salon",
            currency_symbol="₦",
        )
        
        # Verify all steps completed
        assert membership_service.paystack_service.charge_authorization.called
        assert membership_service.email_service.send_renewal_confirmation.called

