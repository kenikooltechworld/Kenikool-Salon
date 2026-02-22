"""Unit tests for service management."""

import pytest
from decimal import Decimal
from bson import ObjectId
from app.models.service import Service
from app.models.tenant import Tenant
from app.context import set_tenant_id, clear_context


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
    return tenant


@pytest.fixture
def test_service(test_tenant):
    """Create a test service."""
    set_tenant_id(test_tenant.id)
    service = Service(
        tenant_id=test_tenant.id,
        name="Haircut",
        description="Professional haircut service",
        duration_minutes=30,
        price=Decimal("25.00"),
        category="Hair",
        is_active=True,
        is_published=True,
        tags=["haircut", "styling"],
    )
    service.save()
    clear_context()
    return service


class TestServiceCreation:
    """Tests for service creation."""

    def test_create_service_with_valid_data(self, test_tenant):
        """Test creating a service with valid data."""
        set_tenant_id(test_tenant.id)
        service = Service(
            tenant_id=test_tenant.id,
            name="Massage",
            description="Relaxing massage",
            duration_minutes=60,
            price=Decimal("50.00"),
            category="Spa",
            is_active=True,
            is_published=False,
        )
        service.save()
        clear_context()

        assert service.id is not None
        assert service.name == "Massage"
        assert service.duration_minutes == 60
        assert service.price == Decimal("50.00")
        assert service.category == "Spa"
        assert service.is_active is True
        assert service.is_published is False

    def test_create_service_with_tags(self, test_tenant):
        """Test creating a service with tags."""
        set_tenant_id(test_tenant.id)
        service = Service(
            tenant_id=test_tenant.id,
            name="Facial",
            duration_minutes=45,
            price=Decimal("40.00"),
            category="Spa",
            tags=["facial", "skincare", "relaxation"],
        )
        service.save()
        clear_context()

        assert service.tags == ["facial", "skincare", "relaxation"]

    def test_create_service_with_public_booking_fields(self, test_tenant):
        """Test creating a service with public booking fields."""
        set_tenant_id(test_tenant.id)
        service = Service(
            tenant_id=test_tenant.id,
            name="Personal Training",
            duration_minutes=60,
            price=Decimal("75.00"),
            category="Gym",
            is_published=True,
            public_description="One-on-one personal training session",
            public_image_url="https://example.com/image.jpg",
            allow_public_booking=True,
        )
        service.save()
        clear_context()

        assert service.is_published is True
        assert service.public_description == "One-on-one personal training session"
        assert service.public_image_url == "https://example.com/image.jpg"
        assert service.allow_public_booking is True


class TestServiceRetrieval:
    """Tests for service retrieval."""

    def test_get_service_by_id(self, test_tenant, test_service):
        """Test retrieving a service by ID."""
        set_tenant_id(test_tenant.id)
        retrieved = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert retrieved is not None
        assert retrieved.id == test_service.id
        assert retrieved.name == "Haircut"

    def test_get_nonexistent_service(self, test_tenant):
        """Test retrieving a nonexistent service."""
        set_tenant_id(test_tenant.id)
        retrieved = Service.objects(id=ObjectId(), tenant_id=test_tenant.id).first()
        clear_context()

        assert retrieved is None

    def test_list_services_for_tenant(self, test_tenant):
        """Test listing all services for a tenant."""
        set_tenant_id(test_tenant.id)
        
        # Create multiple services
        for i in range(3):
            Service(
                tenant_id=test_tenant.id,
                name=f"Service {i}",
                duration_minutes=30 + i * 10,
                price=Decimal("25.00") + i,
                category="Hair" if i % 2 == 0 else "Spa",
            ).save()
        
        services = Service.objects(tenant_id=test_tenant.id)
        clear_context()

        assert services.count() == 3

    def test_list_services_filters_by_tenant(self, test_tenant):
        """Test that service listing filters by tenant."""
        set_tenant_id(test_tenant.id)
        
        # Create another tenant
        other_tenant = Tenant(
            name="Other Salon",
            subdomain="other-salon",
            subscription_tier="starter",
        )
        other_tenant.save()
        
        # Create service for other tenant
        Service(
            tenant_id=other_tenant.id,
            name="Other Service",
            duration_minutes=30,
            price=Decimal("20.00"),
            category="Hair",
        ).save()
        
        # Create service for test tenant
        Service(
            tenant_id=test_tenant.id,
            name="Test Service",
            duration_minutes=30,
            price=Decimal("25.00"),
            category="Hair",
        ).save()
        
        services = Service.objects(tenant_id=test_tenant.id)
        clear_context()

        assert services.count() == 1
        assert services.first().name == "Test Service"


class TestServiceFiltering:
    """Tests for service filtering."""

    def test_filter_services_by_category(self, test_tenant):
        """Test filtering services by category."""
        set_tenant_id(test_tenant.id)
        
        # Create services in different categories
        Service(
            tenant_id=test_tenant.id,
            name="Haircut",
            duration_minutes=30,
            price=Decimal("25.00"),
            category="Hair",
        ).save()
        
        Service(
            tenant_id=test_tenant.id,
            name="Massage",
            duration_minutes=60,
            price=Decimal("50.00"),
            category="Spa",
        ).save()
        
        # Filter by category
        hair_services = Service.objects(tenant_id=test_tenant.id, category="Hair")
        spa_services = Service.objects(tenant_id=test_tenant.id, category="Spa")
        clear_context()

        assert hair_services.count() == 1
        assert hair_services.first().name == "Haircut"
        assert spa_services.count() == 1
        assert spa_services.first().name == "Massage"

    def test_filter_services_by_active_status(self, test_tenant):
        """Test filtering services by active status."""
        set_tenant_id(test_tenant.id)
        
        # Create active and inactive services
        Service(
            tenant_id=test_tenant.id,
            name="Active Service",
            duration_minutes=30,
            price=Decimal("25.00"),
            category="Hair",
            is_active=True,
        ).save()
        
        Service(
            tenant_id=test_tenant.id,
            name="Inactive Service",
            duration_minutes=30,
            price=Decimal("25.00"),
            category="Hair",
            is_active=False,
        ).save()
        
        # Filter by active status
        active_services = Service.objects(tenant_id=test_tenant.id, is_active=True)
        inactive_services = Service.objects(tenant_id=test_tenant.id, is_active=False)
        clear_context()

        assert active_services.count() == 1
        assert active_services.first().name == "Active Service"
        assert inactive_services.count() == 1
        assert inactive_services.first().name == "Inactive Service"

    def test_filter_services_by_published_status(self, test_tenant):
        """Test filtering services by published status."""
        set_tenant_id(test_tenant.id)
        
        # Create published and unpublished services
        Service(
            tenant_id=test_tenant.id,
            name="Published Service",
            duration_minutes=30,
            price=Decimal("25.00"),
            category="Hair",
            is_published=True,
        ).save()
        
        Service(
            tenant_id=test_tenant.id,
            name="Unpublished Service",
            duration_minutes=30,
            price=Decimal("25.00"),
            category="Hair",
            is_published=False,
        ).save()
        
        # Filter by published status
        published = Service.objects(tenant_id=test_tenant.id, is_published=True)
        unpublished = Service.objects(tenant_id=test_tenant.id, is_published=False)
        clear_context()

        assert published.count() == 1
        assert published.first().name == "Published Service"
        assert unpublished.count() == 1
        assert unpublished.first().name == "Unpublished Service"


class TestServiceUpdate:
    """Tests for service updates."""

    def test_update_service_name(self, test_tenant, test_service):
        """Test updating a service name."""
        set_tenant_id(test_tenant.id)
        test_service.name = "Premium Haircut"
        test_service.save()
        
        updated = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert updated.name == "Premium Haircut"

    def test_update_service_price(self, test_tenant, test_service):
        """Test updating a service price."""
        set_tenant_id(test_tenant.id)
        test_service.price = Decimal("35.00")
        test_service.save()
        
        updated = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert updated.price == Decimal("35.00")

    def test_update_service_duration(self, test_tenant, test_service):
        """Test updating a service duration."""
        set_tenant_id(test_tenant.id)
        test_service.duration_minutes = 45
        test_service.save()
        
        updated = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert updated.duration_minutes == 45

    def test_update_service_category(self, test_tenant, test_service):
        """Test updating a service category."""
        set_tenant_id(test_tenant.id)
        test_service.category = "Premium Hair"
        test_service.save()
        
        updated = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert updated.category == "Premium Hair"

    def test_update_service_status(self, test_tenant, test_service):
        """Test updating a service active status."""
        set_tenant_id(test_tenant.id)
        test_service.is_active = False
        test_service.save()
        
        updated = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert updated.is_active is False

    def test_update_service_published_status(self, test_tenant, test_service):
        """Test updating a service published status."""
        set_tenant_id(test_tenant.id)
        test_service.is_published = False
        test_service.save()
        
        updated = Service.objects(id=test_service.id, tenant_id=test_tenant.id).first()
        clear_context()

        assert updated.is_published is False


class TestServiceDeletion:
    """Tests for service deletion."""

    def test_delete_service(self, test_tenant, test_service):
        """Test deleting a service."""
        set_tenant_id(test_tenant.id)
        service_id = test_service.id
        test_service.delete()
        
        deleted = Service.objects(id=service_id, tenant_id=test_tenant.id).first()
        clear_context()

        assert deleted is None

    def test_delete_nonexistent_service(self, test_tenant):
        """Test deleting a nonexistent service."""
        set_tenant_id(test_tenant.id)
        nonexistent_id = ObjectId()
        
        # Should not raise an error
        Service.objects(id=nonexistent_id, tenant_id=test_tenant.id).delete()
        clear_context()

        # Verify nothing was deleted
        assert Service.objects(id=nonexistent_id, tenant_id=test_tenant.id).count() == 0


class TestServiceValidation:
    """Tests for service validation."""

    def test_service_requires_tenant_id(self):
        """Test that service requires tenant_id."""
        with pytest.raises(Exception):
            Service(
                name="Test Service",
                duration_minutes=30,
                price=Decimal("25.00"),
                category="Hair",
            ).save()

    def test_service_requires_name(self, test_tenant):
        """Test that service requires name."""
        set_tenant_id(test_tenant.id)
        with pytest.raises(Exception):
            Service(
                tenant_id=test_tenant.id,
                duration_minutes=30,
                price=Decimal("25.00"),
                category="Hair",
            ).save()
        clear_context()

    def test_service_requires_duration(self, test_tenant):
        """Test that service requires duration."""
        set_tenant_id(test_tenant.id)
        with pytest.raises(Exception):
            Service(
                tenant_id=test_tenant.id,
                name="Test Service",
                price=Decimal("25.00"),
                category="Hair",
            ).save()
        clear_context()

    def test_service_requires_price(self, test_tenant):
        """Test that service requires price."""
        set_tenant_id(test_tenant.id)
        with pytest.raises(Exception):
            Service(
                tenant_id=test_tenant.id,
                name="Test Service",
                duration_minutes=30,
                category="Hair",
            ).save()
        clear_context()

    def test_service_requires_category(self, test_tenant):
        """Test that service requires category."""
        set_tenant_id(test_tenant.id)
        with pytest.raises(Exception):
            Service(
                tenant_id=test_tenant.id,
                name="Test Service",
                duration_minutes=30,
                price=Decimal("25.00"),
            ).save()
        clear_context()

    def test_service_price_cannot_be_negative(self, test_tenant):
        """Test that service price cannot be negative."""
        set_tenant_id(test_tenant.id)
        with pytest.raises(Exception):
            Service(
                tenant_id=test_tenant.id,
                name="Test Service",
                duration_minutes=30,
                price=Decimal("-10.00"),
                category="Hair",
            ).save()
        clear_context()

    def test_service_duration_must_be_positive(self, test_tenant):
        """Test that service duration must be positive."""
        set_tenant_id(test_tenant.id)
        with pytest.raises(Exception):
            Service(
                tenant_id=test_tenant.id,
                name="Test Service",
                duration_minutes=0,
                price=Decimal("25.00"),
                category="Hair",
            ).save()
        clear_context()
