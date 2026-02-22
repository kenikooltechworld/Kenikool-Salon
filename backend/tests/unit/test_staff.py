"""Unit tests for Staff model and endpoints."""

import pytest
from datetime import date, datetime
from decimal import Decimal
from bson import ObjectId
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.context import set_tenant_id, clear_context


@pytest.fixture
def test_tenant():
    """Create a test tenant."""
    tenant = Tenant(
        name="Test Salon",
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


class TestStaffCreation:
    """Test staff creation."""

    def test_create_staff_with_valid_data(self, test_tenant, test_user):
        """Test creating a staff member with valid data."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            specialties=["haircut", "coloring"],
            certifications=["Cosmetology License"],
            hourly_rate=Decimal("25.00"),
            hire_date=date(2023, 1, 15),
            bio="Experienced stylist",
            status="active",
        )
        staff.save()
        clear_context()

        assert staff.id is not None
        assert staff.user_id == test_user.id
        assert staff.specialties == ["haircut", "coloring"]
        assert staff.certifications == ["Cosmetology License"]
        assert staff.hourly_rate == Decimal("25.00")
        assert staff.hire_date == date(2023, 1, 15)
        assert staff.bio == "Experienced stylist"
        assert staff.status == "active"

        staff.delete()

    def test_create_staff_with_minimal_data(self, test_tenant, test_user):
        """Test creating a staff member with minimal required data."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("20.00"),
        )
        staff.save()
        clear_context()

        assert staff.id is not None
        assert staff.user_id == test_user.id
        assert staff.hourly_rate == Decimal("20.00")
        assert staff.specialties == []
        assert staff.certifications == []
        assert staff.status == "active"

        staff.delete()

    def test_create_staff_with_multiple_specialties(self, test_tenant, test_user):
        """Test creating a staff member with multiple specialties."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            specialties=["massage", "facial", "body_treatment"],
            hourly_rate=Decimal("30.00"),
        )
        staff.save()
        clear_context()

        assert len(staff.specialties) == 3
        assert "massage" in staff.specialties
        assert "facial" in staff.specialties
        assert "body_treatment" in staff.specialties

        staff.delete()

    def test_create_staff_with_multiple_certifications(self, test_tenant, test_user):
        """Test creating a staff member with multiple certifications."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            certifications=["Massage Therapy License", "CPR Certified", "First Aid"],
            hourly_rate=Decimal("35.00"),
        )
        staff.save()
        clear_context()

        assert len(staff.certifications) == 3
        assert "Massage Therapy License" in staff.certifications
        assert "CPR Certified" in staff.certifications

        staff.delete()

    def test_create_staff_with_profile_image(self, test_tenant, test_user):
        """Test creating a staff member with profile image URL."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("25.00"),
            profile_image_url="https://example.com/staff/john.jpg",
        )
        staff.save()
        clear_context()

        assert staff.profile_image_url == "https://example.com/staff/john.jpg"

        staff.delete()


class TestStaffUpdate:
    """Test staff updates."""

    def test_update_staff_specialties(self, test_tenant, test_user):
        """Test updating staff specialties."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            specialties=["haircut"],
            hourly_rate=Decimal("25.00"),
        )
        staff.save()
        clear_context()

        # Update specialties
        set_tenant_id(test_tenant.id)
        staff.specialties = ["haircut", "coloring", "styling"]
        staff.save()
        clear_context()

        # Verify update
        set_tenant_id(test_tenant.id)
        updated_staff = Staff.objects(id=staff.id).first()
        assert len(updated_staff.specialties) == 3
        assert "styling" in updated_staff.specialties
        clear_context()

        staff.delete()

    def test_update_staff_hourly_rate(self, test_tenant, test_user):
        """Test updating staff hourly rate."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("20.00"),
        )
        staff.save()
        clear_context()

        # Update hourly rate
        set_tenant_id(test_tenant.id)
        staff.hourly_rate = Decimal("30.00")
        staff.save()
        clear_context()

        # Verify update
        set_tenant_id(test_tenant.id)
        updated_staff = Staff.objects(id=staff.id).first()
        assert updated_staff.hourly_rate == Decimal("30.00")
        clear_context()

        staff.delete()

    def test_update_staff_status(self, test_tenant, test_user):
        """Test updating staff status."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("25.00"),
            status="active",
        )
        staff.save()
        clear_context()

        # Update status
        set_tenant_id(test_tenant.id)
        staff.status = "on_leave"
        staff.save()
        clear_context()

        # Verify update
        set_tenant_id(test_tenant.id)
        updated_staff = Staff.objects(id=staff.id).first()
        assert updated_staff.status == "on_leave"
        clear_context()

        staff.delete()


class TestStaffQuerying:
    """Test staff querying."""

    def test_query_staff_by_specialty(self, test_tenant, test_user):
        """Test querying staff by specialty."""
        set_tenant_id(test_tenant.id)
        
        # Create multiple staff members
        staff1 = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            specialties=["haircut"],
            hourly_rate=Decimal("25.00"),
        )
        staff1.save()

        # Create another user for second staff
        user2 = User(
            tenant_id=test_tenant.id,
            email="staff2@example.com",
            password_hash="hashed_password",
            first_name="Jane",
            last_name="Smith",
            phone="+234987654321",
            status="active",
        )
        user2.save()

        staff2 = Staff(
            tenant_id=test_tenant.id,
            user_id=user2.id,
            specialties=["massage", "facial"],
            hourly_rate=Decimal("30.00"),
        )
        staff2.save()
        clear_context()

        # Query by specialty
        set_tenant_id(test_tenant.id)
        haircut_staff = Staff.objects(tenant_id=test_tenant.id, specialties="haircut")
        massage_staff = Staff.objects(tenant_id=test_tenant.id, specialties="massage")
        clear_context()

        assert haircut_staff.count() == 1
        assert massage_staff.count() == 1

        staff1.delete()
        staff2.delete()
        user2.delete()

    def test_query_staff_by_status(self, test_tenant, test_user):
        """Test querying staff by status."""
        set_tenant_id(test_tenant.id)
        
        # Create staff with different statuses
        staff1 = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("25.00"),
            status="active",
        )
        staff1.save()

        user2 = User(
            tenant_id=test_tenant.id,
            email="staff_inactive@example.com",
            password_hash="hashed_password",
            first_name="Bob",
            last_name="Johnson",
            phone="+234555555555",
            status="active",
        )
        user2.save()

        staff2 = Staff(
            tenant_id=test_tenant.id,
            user_id=user2.id,
            hourly_rate=Decimal("30.00"),
            status="inactive",
        )
        staff2.save()
        clear_context()

        # Query by status
        set_tenant_id(test_tenant.id)
        active_staff = Staff.objects(tenant_id=test_tenant.id, status="active")
        inactive_staff = Staff.objects(tenant_id=test_tenant.id, status="inactive")
        clear_context()

        assert active_staff.count() == 1
        assert inactive_staff.count() == 1

        staff1.delete()
        staff2.delete()
        user2.delete()

    def test_query_staff_by_multiple_criteria(self, test_tenant, test_user):
        """Test querying staff by multiple criteria."""
        set_tenant_id(test_tenant.id)
        
        # Create staff with specific criteria
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            specialties=["haircut", "coloring"],
            hourly_rate=Decimal("25.00"),
            status="active",
        )
        staff.save()
        clear_context()

        # Query by multiple criteria
        set_tenant_id(test_tenant.id)
        result = Staff.objects(
            tenant_id=test_tenant.id,
            specialties="haircut",
            status="active",
        )
        clear_context()

        assert result.count() == 1
        assert result.first().hourly_rate == Decimal("25.00")

        staff.delete()


class TestStaffDeletion:
    """Test staff deletion."""

    def test_delete_staff(self, test_tenant, test_user):
        """Test deleting a staff member."""
        set_tenant_id(test_tenant.id)
        staff = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("25.00"),
        )
        staff.save()
        staff_id = staff.id
        clear_context()

        # Delete staff
        set_tenant_id(test_tenant.id)
        staff.delete()
        clear_context()

        # Verify deletion
        set_tenant_id(test_tenant.id)
        deleted_staff = Staff.objects(id=staff_id).first()
        assert deleted_staff is None
        clear_context()


class TestStaffValidation:
    """Test staff validation."""

    def test_staff_hourly_rate_cannot_be_negative(self, test_tenant, test_user):
        """Test that hourly rate cannot be negative."""
        set_tenant_id(test_tenant.id)
        
        # This should raise a validation error
        with pytest.raises(Exception):
            staff = Staff(
                tenant_id=test_tenant.id,
                user_id=test_user.id,
                hourly_rate=Decimal("-10.00"),
            )
            staff.save()
        
        clear_context()

    def test_staff_requires_hourly_rate(self, test_tenant, test_user):
        """Test that hourly rate is required."""
        set_tenant_id(test_tenant.id)
        
        # This should raise a validation error
        with pytest.raises(Exception):
            staff = Staff(
                tenant_id=test_tenant.id,
                user_id=test_user.id,
            )
            staff.save()
        
        clear_context()

    def test_staff_status_must_be_valid(self, test_tenant, test_user):
        """Test that status must be one of the valid choices."""
        set_tenant_id(test_tenant.id)
        
        # This should raise a validation error
        with pytest.raises(Exception):
            staff = Staff(
                tenant_id=test_tenant.id,
                user_id=test_user.id,
                hourly_rate=Decimal("25.00"),
                status="invalid_status",
            )
            staff.save()
        
        clear_context()
