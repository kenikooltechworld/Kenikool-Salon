"""
Comprehensive Unit Tests for MembershipService - Phase 9 Testing

Tests all public methods of MembershipService including:
- Subscription CRUD operations
- Subscription state transitions (pause, resume, cancel)
- Plan changes and proration
- Discount calculations
- Subscription listing with filters

Requirements: 12.1, 12.5
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from bson import ObjectId
from decimal import Decimal

from app.services.membership_service import MembershipService
from app.schemas.membership import (
    MembershipPlanCreate,
    MembershipSubscriptionCreate,
    SubscriptionStatus,
    BillingCycle,
)


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
    """Create MembershipService instance with mocked dependencies"""
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
        "created_at": datetime.utcnow(),
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


@pytest.fixture
def sample_subscription(sample_plan, sample_client):
    """Sample subscription"""
    now = datetime.utcnow()
    return {
        "_id": ObjectId(),
        "tenant_id": "test_tenant",
        "client_id": sample_client["_id"],
        "plan_id": sample_plan["_id"],
        "status": "active",
        "start_date": now,
        "end_date": now + timedelta(days=30),
        "renewal_date": now + timedelta(days=30),
        "auto_renew": True,
        "payment_method_id": "pm_123",
        "trial_end_date": now + timedelta(days=7),
        "is_trial": True,
        "created_at": now,
        "updated_at": now,
    }


class TestCreateSubscription:
    """Tests for create_subscription method"""

    def test_create_subscription_success(self, membership_service, mock_db, sample_plan, sample_client):
        """Test successful subscription creation"""
        # Setup
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.clients.find_one.return_value = sample_client
        mock_db.subscriptions.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Execute
        result = membership_service.create_subscription(
            tenant_id="test_tenant",
            client_id=str(sample_client["_id"]),
            plan_id=str(sample_plan["_id"]),
            payment_method_id="pm_123",
            auto_renew=True,
            trial_days=7,
        )
        
        # Assert
        assert result is not None
        assert result["status"] == "active"
        mock_db.subscriptions.insert_one.assert_called_once()

    def test_create_subscription_invalid_plan(self, membership_service, mock_db, sample_client):
        """Test subscription creation with invalid plan"""
        # Setup
        mock_db.plans.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Plan not found"):
            membership_service.create_subscription(
                tenant_id="test_tenant",
                client_id=str(sample_client["_id"]),
                plan_id="invalid_plan_id",
                payment_method_id="pm_123",
            )

    def test_create_subscription_invalid_client(self, membership_service, mock_db, sample_plan):
        """Test subscription creation with invalid client"""
        # Setup
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.clients.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Client not found"):
            membership_service.create_subscription(
                tenant_id="test_tenant",
                client_id="invalid_client_id",
                plan_id=str(sample_plan["_id"]),
                payment_method_id="pm_123",
            )

    def test_create_subscription_sends_welcome_email(self, membership_service, mock_db, sample_plan, sample_client):
        """Test that welcome email is sent on subscription creation"""
        # Setup
        mock_db.plans.find_one.return_value = sample_plan
        mock_db.clients.find_one.return_value = sample_client
        mock_db.subscriptions.insert_one.return_value = Mock(inserted_id=ObjectId())
        
        # Execute
        membership_service.create_subscription(
            tenant_id="test_tenant",
            client_id=str(sample_client["_id"]),
            plan_id=str(sample_plan["_id"]),
            payment_method_id="pm_123",
        )
        
        # Assert
        membership_service.email_service.send_welcome_email.assert_called_once()


class TestUpdateSubscription:
    """Tests for update_subscription method"""

    def test_update_subscription_success(self, membership_service, mock_db, sample_subscription):
        """Test successful subscription update"""
        # Setup
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Execute
        result = membership_service.update_subscription(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
            auto_renew=False,
        )
        
        # Assert
        assert result is not None
        mock_db.subscriptions.update_one.assert_called_once()

    def test_update_subscription_not_found(self, membership_service, mock_db):
        """Test updating non-existent subscription"""
        # Setup
        mock_db.subscriptions.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Subscription not found"):
            membership_service.update_subscription(
                tenant_id="test_tenant",
                subscription_id="invalid_id",
                auto_renew=False,
            )


class TestCancelSubscription:
    """Tests for cancel_subscription method"""

    def test_cancel_subscription_success(self, membership_service, mock_db, sample_subscription):
        """Test successful subscription cancellation"""
        # Setup
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Execute
        result = membership_service.cancel_subscription(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
            reason="User requested",
        )
        
        # Assert
        assert result is not None
        assert result["status"] == "cancelled"
        membership_service.email_service.send_cancellation_confirmation.assert_called_once()

    def test_cancel_subscription_already_cancelled(self, membership_service, mock_db, sample_subscription):
        """Test cancelling already cancelled subscription"""
        # Setup
        sample_subscription["status"] = "cancelled"
        mock_db.subscriptions.find_one.return_value = sample_subscription
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Subscription is already cancelled"):
            membership_service.cancel_subscription(
                tenant_id="test_tenant",
                subscription_id=str(sample_subscription["_id"]),
            )


class TestPauseSubscription:
    """Tests for pause_subscription method"""

    def test_pause_subscription_success(self, membership_service, mock_db, sample_subscription):
        """Test successful subscription pause"""
        # Setup
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Execute
        result = membership_service.pause_subscription(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
        )
        
        # Assert
        assert result is not None
        assert result["status"] == "paused"
        membership_service.email_service.send_pause_confirmation.assert_called_once()

    def test_pause_subscription_already_paused(self, membership_service, mock_db, sample_subscription):
        """Test pausing already paused subscription"""
        # Setup
        sample_subscription["status"] = "paused"
        mock_db.subscriptions.find_one.return_value = sample_subscription
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Subscription is already paused"):
            membership_service.pause_subscription(
                tenant_id="test_tenant",
                subscription_id=str(sample_subscription["_id"]),
            )


class TestResumeSubscription:
    """Tests for resume_subscription method"""

    def test_resume_subscription_success(self, membership_service, mock_db, sample_subscription):
        """Test successful subscription resume"""
        # Setup
        sample_subscription["status"] = "paused"
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Execute
        result = membership_service.resume_subscription(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
        )
        
        # Assert
        assert result is not None
        assert result["status"] == "active"
        membership_service.email_service.send_resume_confirmation.assert_called_once()

    def test_resume_subscription_not_paused(self, membership_service, mock_db, sample_subscription):
        """Test resuming non-paused subscription"""
        # Setup
        sample_subscription["status"] = "active"
        mock_db.subscriptions.find_one.return_value = sample_subscription
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Subscription is not paused"):
            membership_service.resume_subscription(
                tenant_id="test_tenant",
                subscription_id=str(sample_subscription["_id"]),
            )


class TestChangePlan:
    """Tests for change_plan method"""

    def test_change_plan_upgrade_success(self, membership_service, mock_db, sample_subscription, sample_plan):
        """Test successful plan upgrade"""
        # Setup
        new_plan = sample_plan.copy()
        new_plan["_id"] = ObjectId()
        new_plan["price"] = Decimal("149.99")
        
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.plans.find_one.return_value = new_plan
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Execute
        result = membership_service.change_plan(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
            new_plan_id=str(new_plan["_id"]),
        )
        
        # Assert
        assert result is not None
        assert result["plan_id"] == str(new_plan["_id"])

    def test_change_plan_downgrade_success(self, membership_service, mock_db, sample_subscription, sample_plan):
        """Test successful plan downgrade"""
        # Setup
        new_plan = sample_plan.copy()
        new_plan["_id"] = ObjectId()
        new_plan["price"] = Decimal("49.99")
        
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.plans.find_one.return_value = new_plan
        mock_db.subscriptions.update_one.return_value = Mock(modified_count=1)
        
        # Execute
        result = membership_service.change_plan(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
            new_plan_id=str(new_plan["_id"]),
        )
        
        # Assert
        assert result is not None
        assert result["plan_id"] == str(new_plan["_id"])


class TestGetSubscriptionDetails:
    """Tests for get_subscription_details method"""

    def test_get_subscription_details_success(self, membership_service, mock_db, sample_subscription):
        """Test retrieving subscription details"""
        # Setup
        mock_db.subscriptions.find_one.return_value = sample_subscription
        
        # Execute
        result = membership_service.get_subscription_details(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
        )
        
        # Assert
        assert result is not None
        assert result["_id"] == sample_subscription["_id"]

    def test_get_subscription_details_not_found(self, membership_service, mock_db):
        """Test retrieving non-existent subscription"""
        # Setup
        mock_db.subscriptions.find_one.return_value = None
        
        # Execute & Assert
        with pytest.raises(ValueError, match="Subscription not found"):
            membership_service.get_subscription_details(
                tenant_id="test_tenant",
                subscription_id="invalid_id",
            )


class TestListSubscriptions:
    """Tests for list_subscriptions method"""

    def test_list_subscriptions_success(self, membership_service, mock_db, sample_subscription):
        """Test listing subscriptions"""
        # Setup
        mock_db.subscriptions.find.return_value.skip.return_value.limit.return_value = [sample_subscription]
        mock_db.subscriptions.count_documents.return_value = 1
        
        # Execute
        result = membership_service.list_subscriptions(
            tenant_id="test_tenant",
            skip=0,
            limit=20,
        )
        
        # Assert
        assert result is not None
        assert len(result["subscriptions"]) == 1
        assert result["total"] == 1

    def test_list_subscriptions_with_filters(self, membership_service, mock_db, sample_subscription):
        """Test listing subscriptions with filters"""
        # Setup
        mock_db.subscriptions.find.return_value.skip.return_value.limit.return_value = [sample_subscription]
        mock_db.subscriptions.count_documents.return_value = 1
        
        # Execute
        result = membership_service.list_subscriptions(
            tenant_id="test_tenant",
            status="active",
            skip=0,
            limit=20,
        )
        
        # Assert
        assert result is not None
        assert len(result["subscriptions"]) == 1

    def test_list_subscriptions_with_sorting(self, membership_service, mock_db, sample_subscription):
        """Test listing subscriptions with sorting"""
        # Setup
        mock_db.subscriptions.find.return_value.skip.return_value.limit.return_value = [sample_subscription]
        mock_db.subscriptions.count_documents.return_value = 1
        
        # Execute
        result = membership_service.list_subscriptions(
            tenant_id="test_tenant",
            sort_by="created_at",
            sort_order=-1,
            skip=0,
            limit=20,
        )
        
        # Assert
        assert result is not None


class TestCalculateRenewalDates:
    """Tests for calculate_renewal_dates method"""

    def test_calculate_renewal_dates_monthly(self, membership_service):
        """Test renewal date calculation for monthly cycle"""
        # Setup
        start_date = datetime(2025, 1, 15)
        
        # Execute
        renewal_date, end_date = membership_service.calculate_renewal_dates(
            start_date=start_date,
            duration_days=30,
            billing_cycle="monthly",
        )
        
        # Assert
        assert renewal_date == datetime(2025, 2, 15)
        assert end_date == datetime(2025, 2, 15)

    def test_calculate_renewal_dates_quarterly(self, membership_service):
        """Test renewal date calculation for quarterly cycle"""
        # Setup
        start_date = datetime(2025, 1, 15)
        
        # Execute
        renewal_date, end_date = membership_service.calculate_renewal_dates(
            start_date=start_date,
            duration_days=90,
            billing_cycle="quarterly",
        )
        
        # Assert
        assert renewal_date == datetime(2025, 4, 15)
        assert end_date == datetime(2025, 4, 15)

    def test_calculate_renewal_dates_yearly(self, membership_service):
        """Test renewal date calculation for yearly cycle"""
        # Setup
        start_date = datetime(2025, 1, 15)
        
        # Execute
        renewal_date, end_date = membership_service.calculate_renewal_dates(
            start_date=start_date,
            duration_days=365,
            billing_cycle="yearly",
        )
        
        # Assert
        assert renewal_date == datetime(2026, 1, 15)
        assert end_date == datetime(2026, 1, 15)


class TestApplyMembershipDiscount:
    """Tests for apply_membership_discount method"""

    def test_apply_membership_discount_success(self, membership_service, mock_db, sample_subscription, sample_plan):
        """Test applying membership discount"""
        # Setup
        mock_db.subscriptions.find_one.return_value = sample_subscription
        mock_db.plans.find_one.return_value = sample_plan
        
        # Execute
        discount = membership_service.apply_membership_discount(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
            original_price=Decimal("100.00"),
        )
        
        # Assert
        assert discount is not None
        assert discount == Decimal("20.00")  # 20% of 100

    def test_apply_membership_discount_inactive_subscription(self, membership_service, mock_db, sample_subscription):
        """Test applying discount to inactive subscription"""
        # Setup
        sample_subscription["status"] = "cancelled"
        mock_db.subscriptions.find_one.return_value = sample_subscription
        
        # Execute
        discount = membership_service.apply_membership_discount(
            tenant_id="test_tenant",
            subscription_id=str(sample_subscription["_id"]),
            original_price=Decimal("100.00"),
        )
        
        # Assert
        assert discount == Decimal("0.00")

    def test_apply_membership_discount_not_found(self, membership_service, mock_db):
        """Test applying discount to non-existent subscription"""
        # Setup
        mock_db.subscriptions.find_one.return_value = None
        
        # Execute
        discount = membership_service.apply_membership_discount(
            tenant_id="test_tenant",
            subscription_id="invalid_id",
            original_price=Decimal("100.00"),
        )
        
        # Assert
        assert discount == Decimal("0.00")


class TestCalculateMetrics:
    """Tests for metric calculation methods"""

    def test_calculate_mrr(self, membership_service, mock_db, sample_subscription, sample_plan):
        """Test MRR calculation"""
        # Setup
        sample_plan["billing_cycle"] = "monthly"
        mock_db.subscriptions.find.return_value = [sample_subscription]
        mock_db.plans.find_one.return_value = sample_plan
        
        # Execute
        mrr = membership_service.calculate_mrr(tenant_id="test_tenant")
        
        # Assert
        assert mrr is not None
        assert mrr > 0

    def test_calculate_churn_rate(self, membership_service, mock_db):
        """Test churn rate calculation"""
        # Setup
        mock_db.subscriptions.count_documents.side_effect = [100, 10]  # total, cancelled
        
        # Execute
        churn_rate = membership_service.calculate_churn_rate(tenant_id="test_tenant")
        
        # Assert
        assert churn_rate is not None
        assert 0 <= churn_rate <= 100

    def test_calculate_growth_rate(self, membership_service, mock_db):
        """Test growth rate calculation"""
        # Setup
        now = datetime.utcnow()
        last_month = now - timedelta(days=30)
        
        mock_db.subscriptions.count_documents.side_effect = [100, 90]  # current, last month
        
        # Execute
        growth_rate = membership_service.calculate_growth_rate(tenant_id="test_tenant")
        
        # Assert
        assert growth_rate is not None

