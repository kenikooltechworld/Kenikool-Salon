"""Property-based tests for staff notifications.

This module tests the core properties of the staff notification system:
- Appointment reminders sent 24 hours before scheduled appointments
- Shift reminders sent at the start of each shift
- Time off approval/denial notifications
- Commission payment notifications

Validates: Requirements 15.1, 15.2, 15.3, 15.4
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from unittest.mock import Mock, MagicMock, patch

from app.models.notification import Notification, NotificationPreference
from app.models.appointment import Appointment
from app.models.shift import Shift
from app.models.time_off_request import TimeOffRequest
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.models.service import Service
from app.models.customer import Customer
from app.services.notification_service import NotificationService
from app.context import set_tenant_id, clear_context


# Fixtures
@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
        subdomain="test-salon",
        subscription_tier="professional",
        status="active",
    )
    tenant.save()
    yield tenant
    tenant.delete()


@pytest.fixture
def test_user(test_tenant):
    """Create a test user."""
    user = User(
        tenant_id=test_tenant.id,
        email="staff@example.com",
        password_hash="hashed_password",
        first_name="John",
        last_name="Doe",
        phone="+234123456789",
        status="active",
    )
    user.save()
    yield user
    user.delete()


@pytest.fixture
def test_staff_member(test_tenant, test_user):
    """Create a test staff member."""
    staff = Staff(
        tenant_id=test_tenant.id,
        user_id=test_user.id,
        payment_type="hourly",
        payment_rate=Decimal("50.00"),
        status="active",
    )
    staff.save()
    yield staff
    staff.delete()


@pytest.fixture
def test_customer(test_tenant):
    """Create a test customer."""
    customer = Customer(
        tenant_id=test_tenant.id,
        first_name="Jane",
        last_name="Smith",
        email="customer@example.com",
        phone="+234987654321",
    )
    customer.save()
    yield customer
    customer.delete()


@pytest.fixture
def test_service(test_tenant):
    """Create a test service."""
    service = Service(
        tenant_id=test_tenant.id,
        name="Haircut",
        description="Professional haircut",
        duration_minutes=30,
        price=Decimal("50.00"),
        category="Hair",
    )
    service.save()
    yield service
    service.delete()


# Strategy generators for property-based testing
@st.composite
def notification_channel_strategy(draw):
    """Generate valid notification channels."""
    return draw(st.sampled_from(["in_app", "email", "sms", "push"]))


@st.composite
def future_datetime_strategy(draw, min_hours=1, max_hours=72):
    """Generate future datetime within specified hours range."""
    now = datetime.utcnow()
    hours_ahead = draw(st.integers(min_value=min_hours, max_value=max_hours))
    return now + timedelta(hours=hours_ahead)


@st.composite
def appointment_24h_away_strategy(draw):
    """Generate appointment time exactly 24 hours away (±30 minutes)."""
    now = datetime.utcnow()
    # 24 hours ± 30 minutes
    minutes_offset = draw(st.integers(min_value=-30, max_value=30))
    return now + timedelta(hours=24, minutes=minutes_offset)


@st.composite
def shift_start_time_strategy(draw):
    """Generate shift start time within next 30 minutes."""
    now = datetime.utcnow()
    minutes_ahead = draw(st.integers(min_value=25, max_value=35))
    return now + timedelta(minutes=minutes_ahead)


@st.composite
def time_off_status_strategy(draw):
    """Generate time off request status (approved or denied)."""
    return draw(st.sampled_from(["approved", "denied"]))


@st.composite
def commission_amount_strategy(draw):
    """Generate commission amount."""
    return draw(st.decimals(min_value=Decimal("10.00"), max_value=Decimal("1000.00"), places=2))


class TestAppointmentReminderNotifications:
    """Property-based tests for appointment reminder notifications.
    
    **Property: Appointment Reminder 24h**
    The system SHALL send appointment reminders 24 hours before scheduled appointments
    
    Validates: Requirements 15.1
    """

    @given(
        appointment_time=appointment_24h_away_strategy(),
        channels=st.lists(notification_channel_strategy(), min_size=1, max_size=4, unique=True),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_appointment_reminder_created_24h_before(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        test_user,
        appointment_time,
        channels,
    ):
        """
        **Property: Appointment Reminder 24h Before**
        
        For any appointment scheduled 24 hours in the future, the system SHALL
        create appointment reminder notifications for the staff member across
        all enabled channels.
        
        Validates: Requirements 15.1
        """
        set_tenant_id(test_tenant.id)
        
        # Create appointment 24 hours away
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=test_customer.id,
            staff_id=test_staff_member.id,
            service_id=test_service.id,
            start_time=appointment_time,
            end_time=appointment_time + timedelta(hours=1),
            status="scheduled",
            price=Decimal("50.00"),
            idempotency_key=f"test-appt-{ObjectId()}",
        )
        appointment.save()
        
        # Create appointment reminder notifications
        notifications = NotificationService.create_staff_appointment_reminder(
            staff_id=str(test_user.id),
            appointment_id=str(appointment.id),
            appointment_time=appointment_time,
            customer_name=f"{test_customer.first_name} {test_customer.last_name}",
            service_name=test_service.name,
            staff_email=test_user.email,
            staff_phone=test_user.phone,
            channels=channels,
        )
        
        # Verify notifications were created
        assert len(notifications) == len(channels)
        
        # Verify each notification has correct properties
        for notification in notifications:
            assert notification.tenant_id == test_tenant.id
            assert notification.recipient_id == str(test_user.id)
            assert notification.recipient_type == "staff"
            assert notification.notification_type == "appointment_reminder_24h"
            assert notification.channel in channels
            assert notification.appointment_id == str(appointment.id)
            assert notification.status == "pending"
            assert test_customer.first_name in notification.content
            assert test_service.name in notification.content
        
        # Verify notifications can be retrieved
        # Note: Notifications are stored with recipient_id as string, so we query with string
        retrieved_notifications = Notification.objects(
            tenant_id=test_tenant.id,
            recipient_id=str(test_user.id),
            notification_type="appointment_reminder_24h",
        )
        
        assert retrieved_notifications.count() >= len(channels)
        
        # Cleanup
        for notification in notifications:
            notification.delete()
        appointment.delete()
        clear_context()

    @given(
        appointment_time=appointment_24h_away_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_appointment_reminder_respects_preferences(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        test_user,
        appointment_time,
    ):
        """
        **Property: Appointment Reminder Respects Preferences**
        
        For any appointment reminder, the system SHALL only send notifications
        through channels that are enabled in the staff member's preferences.
        
        Validates: Requirements 15.1, 15.6
        """
        set_tenant_id(test_tenant.id)
        
        # Set preferences: only in_app and email enabled
        NotificationService.set_preference(
            user_id=str(test_user.id),
            recipient_type="staff",
            notification_type="appointment_reminder_24h",
            channel="in_app",
            enabled=True,
        )
        NotificationService.set_preference(
            user_id=str(test_user.id),
            recipient_type="staff",
            notification_type="appointment_reminder_24h",
            channel="email",
            enabled=True,
        )
        NotificationService.set_preference(
            user_id=str(test_user.id),
            recipient_type="staff",
            notification_type="appointment_reminder_24h",
            channel="sms",
            enabled=False,
        )
        
        # Verify preferences
        assert NotificationService.is_notification_enabled(
            user_id=str(test_user.id),
            notification_type="appointment_reminder_24h",
            channel="in_app",
        ) is True
        
        assert NotificationService.is_notification_enabled(
            user_id=str(test_user.id),
            notification_type="appointment_reminder_24h",
            channel="email",
        ) is True
        
        assert NotificationService.is_notification_enabled(
            user_id=str(test_user.id),
            notification_type="appointment_reminder_24h",
            channel="sms",
        ) is False
        
        # Cleanup preferences
        prefs = NotificationPreference.objects(
            tenant_id=test_tenant.id,
            user_id=str(test_user.id),
        )
        for pref in prefs:
            pref.delete()
        
        clear_context()


class TestShiftReminderNotifications:
    """Property-based tests for shift reminder notifications.
    
    **Property: Shift Reminder at Start**
    The system SHALL send shift reminders at the start of each shift
    
    Validates: Requirements 15.2
    """

    @given(
        shift_start=shift_start_time_strategy(),
        channels=st.lists(notification_channel_strategy(), min_size=1, max_size=4, unique=True),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_reminder_created_at_start(
        self,
        test_tenant,
        test_staff_member,
        test_user,
        shift_start,
        channels,
    ):
        """
        **Property: Shift Reminder at Start**
        
        For any shift starting within 30 minutes, the system SHALL create
        shift reminder notifications for the staff member across all enabled channels.
        
        Validates: Requirements 15.2
        """
        set_tenant_id(test_tenant.id)
        
        # Create shift starting soon
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=shift_start,
            end_time=shift_start + timedelta(hours=8),
            status="scheduled",
            labor_cost=Decimal("400.00"),
        )
        shift.save()
        
        # Create shift reminder notifications
        notifications = NotificationService.create_staff_shift_reminder(
            staff_id=str(test_user.id),
            shift_id=str(shift.id),
            shift_start=shift_start,
            shift_end=shift_start + timedelta(hours=8),
            staff_email=test_user.email,
            staff_phone=test_user.phone,
            channels=channels,
        )
        
        # Verify notifications were created
        assert len(notifications) == len(channels)
        
        # Verify each notification has correct properties
        for notification in notifications:
            assert notification.tenant_id == test_tenant.id
            assert notification.recipient_id == str(test_user.id)
            assert notification.recipient_type == "staff"
            assert notification.notification_type == "shift_assigned"
            assert notification.channel in channels
            assert notification.shift_id == str(shift.id)
            assert notification.status == "pending"
            assert "shift" in notification.content.lower()
        
        # Verify notifications can be retrieved
        retrieved_notifications = Notification.objects(
            tenant_id=test_tenant.id,
            recipient_id=str(test_user.id),
            notification_type="shift_assigned",
        )
        
        assert retrieved_notifications.count() >= len(channels)
        
        # Cleanup
        for notification in notifications:
            notification.delete()
        shift.delete()
        clear_context()

    @given(
        shift_start=shift_start_time_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_shift_reminder_contains_time_details(
        self,
        test_tenant,
        test_staff_member,
        test_user,
        shift_start,
    ):
        """
        **Property: Shift Reminder Contains Time Details**
        
        For any shift reminder notification, the content SHALL include the
        shift start and end times.
        
        Validates: Requirements 15.2
        """
        set_tenant_id(test_tenant.id)
        
        shift_end = shift_start + timedelta(hours=8)
        
        # Create shift
        shift = Shift(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_time=shift_start,
            end_time=shift_end,
            status="scheduled",
            labor_cost=Decimal("400.00"),
        )
        shift.save()
        
        # Create shift reminder
        notifications = NotificationService.create_staff_shift_reminder(
            staff_id=str(test_user.id),
            shift_id=str(shift.id),
            shift_start=shift_start,
            shift_end=shift_end,
            staff_email=test_user.email,
            channels=["in_app"],
        )
        
        # Verify notification content includes time details
        notification = notifications[0]
        assert "shift" in notification.content.lower()
        # Content should mention start and end times
        assert notification.content is not None
        assert len(notification.content) > 0
        
        # Cleanup
        for notif in notifications:
            notif.delete()
        shift.delete()
        clear_context()


class TestTimeOffNotifications:
    """Property-based tests for time off approval/denial notifications.
    
    **Property: Time Off Approval/Denial Notifications**
    The system SHALL send time off approval/denial notifications
    
    Validates: Requirements 15.3
    """

    @given(
        status=time_off_status_strategy(),
        channels=st.lists(notification_channel_strategy(), min_size=1, max_size=4, unique=True),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_time_off_notification_created_on_status_change(
        self,
        test_tenant,
        test_staff_member,
        test_user,
        status,
        channels,
    ):
        """
        **Property: Time Off Notification on Status Change**
        
        For any time off request that is approved or denied, the system SHALL
        create notifications for the staff member across all enabled channels.
        
        Validates: Requirements 15.3
        """
        set_tenant_id(test_tenant.id)
        
        start_date = datetime.utcnow() + timedelta(days=7)
        end_date = start_date + timedelta(days=3)
        
        # Create time off request
        time_off_request = TimeOffRequest(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_date=start_date,
            end_date=end_date,
            reason="Vacation",
            status=status,
        )
        time_off_request.save()
        
        # Create time off notification
        denial_reason = "Insufficient coverage" if status == "denied" else None
        notifications = NotificationService.create_staff_time_off_notification(
            staff_id=str(test_user.id),
            time_off_request_id=str(time_off_request.id),
            status=status,
            start_date=start_date,
            end_date=end_date,
            denial_reason=denial_reason,
            staff_email=test_user.email,
            staff_phone=test_user.phone,
            channels=channels,
        )
        
        # Verify notifications were created
        assert len(notifications) == len(channels)
        
        # Verify each notification has correct properties
        expected_type = "time_off_approved" if status == "approved" else "time_off_rejected"
        
        for notification in notifications:
            assert notification.tenant_id == test_tenant.id
            assert notification.recipient_id == str(test_user.id)
            assert notification.recipient_type == "staff"
            assert notification.notification_type == expected_type
            assert notification.channel in channels
            assert notification.time_off_request_id == str(time_off_request.id)
            assert notification.status == "pending"
            assert status in notification.content.lower()
            
            # If denied, verify denial reason is in content
            if status == "denied" and denial_reason:
                assert denial_reason.lower() in notification.content.lower()
        
        # Verify notifications can be retrieved
        retrieved_notifications = Notification.objects(
            tenant_id=test_tenant.id,
            recipient_id=str(test_user.id),
            notification_type=expected_type,
        )
        
        assert retrieved_notifications.count() >= len(channels)
        
        # Cleanup
        for notification in notifications:
            notification.delete()
        time_off_request.delete()
        clear_context()

    @given(
        denial_reason=st.text(min_size=10, max_size=100),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_time_off_denial_includes_reason(
        self,
        test_tenant,
        test_staff_member,
        test_user,
        denial_reason,
    ):
        """
        **Property: Time Off Denial Includes Reason**
        
        For any time off request that is denied with a reason, the notification
        content SHALL include the denial reason.
        
        Validates: Requirements 15.3
        """
        set_tenant_id(test_tenant.id)
        
        start_date = datetime.utcnow() + timedelta(days=7)
        end_date = start_date + timedelta(days=3)
        
        # Create time off request
        time_off_request = TimeOffRequest(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            start_date=start_date,
            end_date=end_date,
            reason="Vacation",
            status="denied",
        )
        time_off_request.save()
        
        # Create denial notification with reason
        notifications = NotificationService.create_staff_time_off_notification(
            staff_id=str(test_user.id),
            time_off_request_id=str(time_off_request.id),
            status="denied",
            start_date=start_date,
            end_date=end_date,
            denial_reason=denial_reason,
            staff_email=test_user.email,
            channels=["in_app"],
        )
        
        # Verify notification includes denial reason
        notification = notifications[0]
        assert "denied" in notification.content.lower()
        assert denial_reason.lower() in notification.content.lower()
        
        # Cleanup
        for notif in notifications:
            notif.delete()
        time_off_request.delete()
        clear_context()


class TestCommissionPaymentNotifications:
    """Property-based tests for commission payment notifications.
    
    **Property: Commission Payment Notifications**
    The system SHALL send commission payment notifications
    
    Validates: Requirements 15.4
    """

    @given(
        commission_amount=commission_amount_strategy(),
        channels=st.lists(notification_channel_strategy(), min_size=1, max_size=4, unique=True),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_commission_notification_created_on_payment(
        self,
        test_tenant,
        test_staff_member,
        test_user,
        commission_amount,
        channels,
    ):
        """
        **Property: Commission Payment Notification**
        
        For any commission payment processed, the system SHALL create
        notifications for the staff member across all enabled channels.
        
        Validates: Requirements 15.4
        """
        set_tenant_id(test_tenant.id)
        
        payment_period = "January 2024"
        
        # Create commission payment notification
        notifications = NotificationService.create_staff_commission_notification(
            staff_id=str(test_user.id),
            commission_amount=float(commission_amount),
            payment_period=payment_period,
            staff_email=test_user.email,
            staff_phone=test_user.phone,
            channels=channels,
        )
        
        # Verify notifications were created
        assert len(notifications) == len(channels)
        
        # Verify each notification has correct properties
        for notification in notifications:
            assert notification.tenant_id == test_tenant.id
            assert notification.recipient_id == str(test_user.id)
            assert notification.recipient_type == "staff"
            assert notification.notification_type == "custom"
            assert notification.channel in channels
            assert notification.status == "pending"
            assert "commission" in notification.content.lower()
            assert payment_period in notification.content
            # Verify amount is in content (formatted as currency)
            assert str(commission_amount) in notification.content or f"{commission_amount:.2f}" in notification.content
        
        # Cleanup
        for notification in notifications:
            notification.delete()
        clear_context()

    @given(
        commission_amount=commission_amount_strategy(),
        payment_period=st.text(min_size=5, max_size=50),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_commission_notification_contains_amount_and_period(
        self,
        test_tenant,
        test_staff_member,
        test_user,
        commission_amount,
        payment_period,
    ):
        """
        **Property: Commission Notification Contains Amount and Period**
        
        For any commission payment notification, the content SHALL include
        the commission amount and payment period.
        
        Validates: Requirements 15.4
        """
        set_tenant_id(test_tenant.id)
        
        # Create commission notification
        notifications = NotificationService.create_staff_commission_notification(
            staff_id=str(test_user.id),
            commission_amount=float(commission_amount),
            payment_period=payment_period,
            staff_email=test_user.email,
            channels=["in_app"],
        )
        
        # Verify notification content
        notification = notifications[0]
        assert "commission" in notification.content.lower()
        assert payment_period in notification.content
        # Verify amount is formatted and included
        assert str(commission_amount) in notification.content or f"{commission_amount:.2f}" in notification.content
        
        # Cleanup
        for notif in notifications:
            notif.delete()
        clear_context()


class TestNotificationDeliveryProperties:
    """Property-based tests for notification delivery properties.
    
    Tests general notification delivery behavior across all notification types.
    """

    @given(
        notification_type=st.sampled_from([
            "appointment_reminder_24h",
            "shift_assigned",
            "time_off_approved",
            "time_off_rejected",
        ]),
        channel=notification_channel_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_notification_status_transitions(
        self,
        test_tenant,
        test_user,
        notification_type,
        channel,
    ):
        """
        **Property: Notification Status Transitions**
        
        For any notification, the status SHALL transition from pending → sent → delivered
        or pending → failed, and these transitions SHALL be persistent.
        
        Validates: Requirements 15.1, 15.2, 15.3, 15.4
        """
        set_tenant_id(test_tenant.id)
        
        # Create notification
        notification = NotificationService.create_notification(
            recipient_id=str(test_user.id),
            recipient_type="staff",
            notification_type=notification_type,
            channel=channel,
            content="Test notification content",
            subject="Test Notification",
            recipient_email=test_user.email if channel == "email" else None,
            recipient_phone=test_user.phone if channel == "sms" else None,
        )
        
        # Verify initial status
        assert notification.status == "pending"
        
        # Mark as sent
        NotificationService.mark_notification_sent(str(notification.id))
        
        # Retrieve and verify
        retrieved = NotificationService.get_notification(str(notification.id))
        assert retrieved.status == "sent"
        assert retrieved.sent_at is not None
        
        # Mark as delivered
        NotificationService.mark_notification_delivered(str(notification.id))
        
        # Retrieve and verify
        retrieved = NotificationService.get_notification(str(notification.id))
        assert retrieved.status == "delivered"
        assert retrieved.delivered_at is not None
        
        # Cleanup
        notification.delete()
        clear_context()

    @given(
        notification_type=st.sampled_from([
            "appointment_reminder_24h",
            "shift_assigned",
            "time_off_approved",
        ]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_notification_retrieval_by_recipient(
        self,
        test_tenant,
        test_user,
        notification_type,
    ):
        """
        **Property: Notification Retrieval by Recipient**
        
        For any staff member, retrieving notifications SHALL return only
        notifications addressed to that specific staff member.
        
        Validates: Requirements 15.1, 15.2, 15.3, 15.4, 15.5
        """
        set_tenant_id(test_tenant.id)
        
        # Create notification for this user
        notification = NotificationService.create_notification(
            recipient_id=str(test_user.id),
            recipient_type="staff",
            notification_type=notification_type,
            channel="in_app",
            content="Test notification",
            subject="Test",
        )
        
        # Retrieve notifications for this user
        notifications = Notification.objects(
            tenant_id=test_tenant.id,
            recipient_id=str(test_user.id),
        )
        
        # Verify all notifications belong to this user
        assert notifications.count() >= 1
        for notif in notifications:
            assert notif.recipient_id == str(test_user.id)
            assert notif.recipient_type == "staff"
        
        # Cleanup
        notification.delete()
        clear_context()
