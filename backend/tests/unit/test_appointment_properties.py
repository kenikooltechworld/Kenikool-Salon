"""Property-based tests for appointments.

This module tests the core properties of appointment functionality:
- Property 2: Appointment Status Transitions - Verify marking as completed updates status persistently
- Property 9: Appointment Filtering by Status - Verify filtered results only include selected status
- Property 17: Appointment Detail Completeness - Verify all required information displays

Validates: Requirements 2.4, 2.5, 2.6
"""

import pytest
from hypothesis import given, strategies as st, assume, settings, HealthCheck
from datetime import datetime, timedelta
from decimal import Decimal
from bson import ObjectId
from unittest.mock import Mock, MagicMock, patch

from app.models.appointment import Appointment
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.models.service import Service
from app.models.customer import Customer
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
def appointment_status_strategy(draw):
    """Generate valid appointment statuses."""
    return draw(st.sampled_from(["scheduled", "confirmed", "in_progress"]))


@st.composite
def appointment_data_strategy(draw, test_tenant, test_staff_member, test_customer, test_service):
    """Generate appointment data with various initial statuses."""
    now = datetime.utcnow()
    start_time = draw(st.datetimes(
        min_value=now,
        max_value=now + timedelta(days=30)
    ))
    
    status = draw(appointment_status_strategy())
    
    return {
        "tenant_id": test_tenant.id,
        "customer_id": test_customer.id,
        "staff_id": test_staff_member.id,
        "service_id": test_service.id,
        "start_time": start_time,
        "end_time": start_time + timedelta(hours=1),
        "status": status,
        "price": Decimal("50.00"),
        "notes": draw(st.text(min_size=0, max_size=100)),
        "idempotency_key": f"test-appt-{ObjectId()}",
    }


@st.composite
def multiple_appointments_strategy(draw, test_tenant, test_staff_member, test_customer, test_service):
    """Generate multiple appointments with different statuses."""
    now = datetime.utcnow()
    num_appointments = draw(st.integers(min_value=2, max_value=5))
    
    appointments = []
    statuses = ["scheduled", "confirmed", "in_progress", "completed", "cancelled"]
    
    for i in range(num_appointments):
        start_time = now + timedelta(hours=i)
        status = draw(st.sampled_from(statuses))
        
        appointments.append({
            "tenant_id": test_tenant.id,
            "customer_id": test_customer.id,
            "staff_id": test_staff_member.id,
            "service_id": test_service.id,
            "start_time": start_time,
            "end_time": start_time + timedelta(hours=1),
            "status": status,
            "price": Decimal("50.00"),
            "notes": f"Appointment {i}",
            "idempotency_key": f"test-appt-{i}-{ObjectId()}",
        })
    
    return appointments


class TestAppointmentStatusTransitions:
    """Property-based tests for appointment status transitions.
    
    **Property 2: Appointment Status Transitions**
    Verify marking as completed updates status persistently
    
    Validates: Requirements 2.6
    """

    @given(
        initial_status=appointment_status_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_mark_appointment_completed_updates_status(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        initial_status,
    ):
        """
        **Property 2: Appointment Status Transitions**
        
        For any appointment with initial status (scheduled, confirmed, in_progress),
        when marking it as completed, the system SHALL update the appointment status
        to "completed" and persist the change such that subsequent queries return
        the updated status.
        
        Validates: Requirements 2.6
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        
        # Create appointment with initial status
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=test_customer.id,
            staff_id=test_staff_member.id,
            service_id=test_service.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            status=initial_status,
            price=Decimal("50.00"),
            notes="Test appointment",
            idempotency_key=f"test-appt-{ObjectId()}",
        )
        appointment.save()
        
        # Verify initial status
        assert appointment.status == initial_status
        
        # Mark as completed
        appointment.status = "completed"
        appointment.save()
        
        # Verify status is updated in memory
        assert appointment.status == "completed"
        
        # Query the appointment again to verify persistence
        retrieved_appointment = Appointment.objects(
            tenant_id=test_tenant.id,
            id=appointment.id
        ).first()
        
        # Verify status persists in database
        assert retrieved_appointment is not None
        assert retrieved_appointment.status == "completed"
        
        # Verify other fields remain unchanged
        assert retrieved_appointment.customer_id == test_customer.id
        assert retrieved_appointment.staff_id == test_staff_member.id
        assert retrieved_appointment.service_id == test_service.id
        assert retrieved_appointment.price == Decimal("50.00")
        
        # Cleanup
        appointment.delete()
        clear_context()

    @given(
        initial_status=appointment_status_strategy(),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_mark_completed_multiple_queries_consistency(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        initial_status,
    ):
        """
        **Property 2: Appointment Status Transitions - Consistency**
        
        For any appointment marked as completed, multiple subsequent queries
        SHALL consistently return the "completed" status without variation.
        
        Validates: Requirements 2.6
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=2)
        
        # Create appointment
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=test_customer.id,
            staff_id=test_staff_member.id,
            service_id=test_service.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            status=initial_status,
            price=Decimal("50.00"),
            idempotency_key=f"test-appt-{ObjectId()}",
        )
        appointment.save()
        
        # Mark as completed
        appointment.status = "completed"
        appointment.save()
        
        # Query multiple times and verify consistency
        for _ in range(5):
            retrieved = Appointment.objects(
                tenant_id=test_tenant.id,
                id=appointment.id
            ).first()
            assert retrieved.status == "completed"
        
        # Cleanup
        appointment.delete()
        clear_context()


class TestAppointmentFilteringByStatus:
    """Property-based tests for appointment filtering by status.
    
    **Property 9: Appointment Filtering by Status**
    Verify filtered results only include selected status
    
    Validates: Requirements 2.4
    """

    @given(
        filter_status=st.sampled_from(["scheduled", "confirmed", "in_progress", "completed", "cancelled"]),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_filter_appointments_by_status_includes_only_matching(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        filter_status,
    ):
        """
        **Property 9: Appointment Filtering by Status**
        
        For any status filter applied to the appointments list, all returned
        appointments SHALL have a status matching the selected filter, and no
        appointments with other statuses SHALL be included.
        
        Validates: Requirements 2.4
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        
        # Create appointments with different statuses
        created_appointments = []
        all_statuses = ["scheduled", "confirmed", "in_progress", "completed", "cancelled"]
        
        for i, status in enumerate(all_statuses):
            start_time = now + timedelta(hours=i)
            appointment = Appointment(
                tenant_id=test_tenant.id,
                customer_id=test_customer.id,
                staff_id=test_staff_member.id,
                service_id=test_service.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),
                status=status,
                price=Decimal("50.00"),
                idempotency_key=f"test-appt-{i}-{ObjectId()}",
            )
            appointment.save()
            created_appointments.append(appointment)
        
        # Filter by specific status
        filtered_appointments = Appointment.objects(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            status=filter_status,
        )
        
        # Verify all returned appointments match the filter
        assert filtered_appointments.count() >= 1
        for appointment in filtered_appointments:
            assert appointment.status == filter_status
        
        # Verify no appointments with other statuses are included
        for appointment in filtered_appointments:
            assert appointment.status != "no_show"  # Ensure no_show is not included
            for other_status in all_statuses:
                if other_status != filter_status:
                    assert appointment.status != other_status
        
        # Cleanup
        for appointment in created_appointments:
            appointment.delete()
        
        clear_context()

    @given(
        num_appointments=st.integers(min_value=2, max_value=5),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_filter_excludes_other_statuses(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        num_appointments,
    ):
        """
        **Property 9: Appointment Filtering by Status - Exclusion**
        
        For any status filter, appointments with other statuses SHALL be
        completely excluded from the filtered results.
        
        Validates: Requirements 2.4
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        
        # Create appointments with "scheduled" status
        scheduled_appointments = []
        for i in range(num_appointments):
            start_time = now + timedelta(hours=i)
            appointment = Appointment(
                tenant_id=test_tenant.id,
                customer_id=test_customer.id,
                staff_id=test_staff_member.id,
                service_id=test_service.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),
                status="scheduled",
                price=Decimal("50.00"),
                idempotency_key=f"test-scheduled-{i}-{ObjectId()}",
            )
            appointment.save()
            scheduled_appointments.append(appointment)
        
        # Create appointments with "completed" status
        completed_appointments = []
        for i in range(num_appointments):
            start_time = now + timedelta(hours=i + 100)
            appointment = Appointment(
                tenant_id=test_tenant.id,
                customer_id=test_customer.id,
                staff_id=test_staff_member.id,
                service_id=test_service.id,
                start_time=start_time,
                end_time=start_time + timedelta(hours=1),
                status="completed",
                price=Decimal("50.00"),
                idempotency_key=f"test-completed-{i}-{ObjectId()}",
            )
            appointment.save()
            completed_appointments.append(appointment)
        
        # Filter for "scheduled" status
        scheduled_filtered = Appointment.objects(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            status="scheduled",
        )
        
        # Verify no completed appointments are in scheduled results
        for appointment in scheduled_filtered:
            assert appointment.status == "scheduled"
            assert appointment not in completed_appointments
        
        # Filter for "completed" status
        completed_filtered = Appointment.objects(
            tenant_id=test_tenant.id,
            staff_id=test_staff_member.id,
            status="completed",
        )
        
        # Verify no scheduled appointments are in completed results
        for appointment in completed_filtered:
            assert appointment.status == "completed"
            assert appointment not in scheduled_appointments
        
        # Cleanup
        for appointment in scheduled_appointments + completed_appointments:
            appointment.delete()
        
        clear_context()


class TestAppointmentDetailCompleteness:
    """Property-based tests for appointment detail completeness.
    
    **Property 17: Appointment Detail Completeness**
    Verify all required information displays
    
    Validates: Requirements 2.5
    """

    @given(
        notes=st.text(min_size=0, max_size=100),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=10, deadline=None)
    def test_appointment_detail_has_all_required_fields(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        test_service,
        notes,
    ):
        """
        **Property 17: Appointment Detail Completeness**
        
        For any appointment detail view, all required information (customer name,
        contact details, service, date, time, status, notes) SHALL be displayed.
        
        Validates: Requirements 2.5
        """
        set_tenant_id(test_tenant.id)
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        
        # Create appointment with all required fields
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=test_customer.id,
            staff_id=test_staff_member.id,
            service_id=test_service.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            status="scheduled",
            price=Decimal("50.00"),
            notes=notes,
            idempotency_key=f"test-appt-{ObjectId()}",
        )
        appointment.save()
        
        # Retrieve appointment detail
        retrieved = Appointment.objects(
            tenant_id=test_tenant.id,
            id=appointment.id
        ).first()
        
        # Verify all required fields are present and accessible
        assert retrieved is not None
        
        # Customer information
        assert retrieved.customer_id is not None
        assert retrieved.customer_id == test_customer.id
        
        # Service information
        assert retrieved.service_id is not None
        assert retrieved.service_id == test_service.id
        
        # Date and time information
        assert retrieved.start_time is not None
        assert retrieved.end_time is not None
        assert retrieved.start_time < retrieved.end_time
        
        # Status information
        assert retrieved.status is not None
        assert retrieved.status in ["scheduled", "confirmed", "in_progress", "completed", "cancelled", "no_show"]
        
        # Notes (optional but should be present if provided)
        if notes:
            assert retrieved.notes == notes
        
        # Staff information
        assert retrieved.staff_id is not None
        assert retrieved.staff_id == test_staff_member.id
        
        # Price information
        assert retrieved.price is not None
        assert retrieved.price == Decimal("50.00")
        
        # Cleanup
        appointment.delete()
        clear_context()

    @given(
        customer_first_name=st.text(min_size=1, max_size=50),
        customer_last_name=st.text(min_size=1, max_size=50),
        customer_email=st.emails(),
        customer_phone=st.text(min_size=10, max_size=20),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5, deadline=None)
    def test_appointment_detail_includes_customer_contact_details(
        self,
        test_tenant,
        test_staff_member,
        test_service,
        customer_first_name,
        customer_last_name,
        customer_email,
        customer_phone,
    ):
        """
        **Property 17: Appointment Detail Completeness - Customer Contact**
        
        For any appointment, the detail view SHALL include complete customer
        contact details (name, email, phone).
        
        Validates: Requirements 2.5
        """
        set_tenant_id(test_tenant.id)
        
        # Create customer with specific details
        customer = Customer(
            tenant_id=test_tenant.id,
            first_name=customer_first_name,
            last_name=customer_last_name,
            email=customer_email,
            phone=customer_phone,
        )
        customer.save()
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        
        # Create appointment
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=customer.id,
            staff_id=test_staff_member.id,
            service_id=test_service.id,
            start_time=start_time,
            end_time=start_time + timedelta(hours=1),
            status="scheduled",
            price=Decimal("50.00"),
            idempotency_key=f"test-appt-{ObjectId()}",
        )
        appointment.save()
        
        # Retrieve appointment
        retrieved = Appointment.objects(
            tenant_id=test_tenant.id,
            id=appointment.id
        ).first()
        
        # Verify customer reference is present
        assert retrieved.customer_id == customer.id
        
        # Retrieve customer to verify contact details are available
        retrieved_customer = Customer.objects(
            tenant_id=test_tenant.id,
            id=customer.id
        ).first()
        
        assert retrieved_customer is not None
        assert retrieved_customer.first_name == customer_first_name
        assert retrieved_customer.last_name == customer_last_name
        assert retrieved_customer.email == customer_email
        assert retrieved_customer.phone == customer_phone
        
        # Cleanup
        appointment.delete()
        customer.delete()
        clear_context()

    @given(
        service_name=st.text(min_size=1, max_size=100),
        service_duration=st.integers(min_value=15, max_value=480),
        service_price=st.decimals(min_value=Decimal("1.00"), max_value=Decimal("10000.00"), places=2),
    )
    @settings(suppress_health_check=[HealthCheck.function_scoped_fixture], max_examples=5, deadline=None)
    def test_appointment_detail_includes_service_information(
        self,
        test_tenant,
        test_staff_member,
        test_customer,
        service_name,
        service_duration,
        service_price,
    ):
        """
        **Property 17: Appointment Detail Completeness - Service Info**
        
        For any appointment, the detail view SHALL include complete service
        information (name, duration, price).
        
        Validates: Requirements 2.5
        """
        set_tenant_id(test_tenant.id)
        
        # Create service with specific details
        service = Service(
            tenant_id=test_tenant.id,
            name=service_name,
            description="Test service",
            duration_minutes=service_duration,
            price=service_price,
            category="Test",
        )
        service.save()
        
        now = datetime.utcnow()
        start_time = now + timedelta(hours=1)
        
        # Create appointment
        appointment = Appointment(
            tenant_id=test_tenant.id,
            customer_id=test_customer.id,
            staff_id=test_staff_member.id,
            service_id=service.id,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=service_duration),
            status="scheduled",
            price=service_price,
            idempotency_key=f"test-appt-{ObjectId()}",
        )
        appointment.save()
        
        # Retrieve appointment
        retrieved = Appointment.objects(
            tenant_id=test_tenant.id,
            id=appointment.id
        ).first()
        
        # Verify service reference is present
        assert retrieved.service_id == service.id
        
        # Retrieve service to verify details are available
        retrieved_service = Service.objects(
            tenant_id=test_tenant.id,
            id=service.id
        ).first()
        
        assert retrieved_service is not None
        assert retrieved_service.name == service_name
        assert retrieved_service.duration_minutes == service_duration
        assert retrieved_service.price == service_price
        
        # Cleanup
        appointment.delete()
        service.delete()
        clear_context()
