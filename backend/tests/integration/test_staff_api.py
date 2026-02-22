"""Integration tests for Staff API endpoints."""

import pytest
from decimal import Decimal
from datetime import date
from httpx import AsyncClient
from app.main import app
from app.models.staff import Staff
from app.models.user import User
from app.models.tenant import Tenant
from app.context import set_tenant_id, clear_context


@pytest.fixture
async def client():
    """Create an async test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


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


@pytest.fixture
def test_staff(test_tenant, test_user):
    """Create a test staff member."""
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
    yield staff
    staff.delete()


class TestStaffListEndpoint:
    """Test staff list endpoint."""

    @pytest.mark.asyncio
    async def test_list_staff_empty(self, client, test_tenant):
        """Test listing staff when none exist."""
        set_tenant_id(test_tenant.id)
        response = await client.get("/staff")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0
        assert data["staff"] == []

    @pytest.mark.asyncio
    async def test_list_staff_with_pagination(self, client, test_tenant, test_user):
        """Test listing staff with pagination."""
        set_tenant_id(test_tenant.id)
        
        # Create multiple staff members
        for i in range(15):
            user = User(
                tenant_id=test_tenant.id,
                email=f"staff{i}@example.com",
                password_hash="hashed_password",
                first_name=f"Staff{i}",
                last_name="Member",
                phone=f"+234{i:09d}",
                status="active",
            )
            user.save()
            
            staff = Staff(
                tenant_id=test_tenant.id,
                user_id=user.id,
                hourly_rate=Decimal("25.00"),
            )
            staff.save()
        
        clear_context()

        # Test first page
        set_tenant_id(test_tenant.id)
        response = await client.get("/staff?page=1&page_size=10")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["staff"]) == 10
        assert data["page"] == 1
        assert data["page_size"] == 10

        # Test second page
        set_tenant_id(test_tenant.id)
        response = await client.get("/staff?page=2&page_size=10")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert len(data["staff"]) == 5

    @pytest.mark.asyncio
    async def test_list_staff_filter_by_status(self, client, test_tenant, test_user):
        """Test listing staff filtered by status."""
        set_tenant_id(test_tenant.id)
        
        # Create active staff
        staff1 = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            hourly_rate=Decimal("25.00"),
            status="active",
        )
        staff1.save()

        # Create inactive staff
        user2 = User(
            tenant_id=test_tenant.id,
            email="inactive@example.com",
            password_hash="hashed_password",
            first_name="Inactive",
            last_name="Staff",
            phone="+234987654321",
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

        # Filter by active status
        set_tenant_id(test_tenant.id)
        response = await client.get("/staff?status=active")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert data["staff"][0]["status"] == "active"

    @pytest.mark.asyncio
    async def test_list_staff_filter_by_specialty(self, client, test_tenant, test_user):
        """Test listing staff filtered by specialty."""
        set_tenant_id(test_tenant.id)
        
        # Create staff with haircut specialty
        staff1 = Staff(
            tenant_id=test_tenant.id,
            user_id=test_user.id,
            specialties=["haircut"],
            hourly_rate=Decimal("25.00"),
        )
        staff1.save()

        # Create staff with massage specialty
        user2 = User(
            tenant_id=test_tenant.id,
            email="massage@example.com",
            password_hash="hashed_password",
            first_name="Massage",
            last_name="Therapist",
            phone="+234555555555",
            status="active",
        )
        user2.save()

        staff2 = Staff(
            tenant_id=test_tenant.id,
            user_id=user2.id,
            specialties=["massage"],
            hourly_rate=Decimal("30.00"),
        )
        staff2.save()
        clear_context()

        # Filter by specialty
        set_tenant_id(test_tenant.id)
        response = await client.get("/staff?specialty=haircut")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 1
        assert "haircut" in data["staff"][0]["specialties"]


class TestStaffGetEndpoint:
    """Test staff get endpoint."""

    @pytest.mark.asyncio
    async def test_get_staff_success(self, client, test_tenant, test_staff):
        """Test getting a specific staff member."""
        set_tenant_id(test_tenant.id)
        response = await client.get(f"/staff/{test_staff.id}")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(test_staff.id)
        assert data["specialties"] == ["haircut", "coloring"]
        assert data["hourly_rate"] == 25.0

    @pytest.mark.asyncio
    async def test_get_staff_not_found(self, client, test_tenant):
        """Test getting a non-existent staff member."""
        from bson import ObjectId
        
        set_tenant_id(test_tenant.id)
        fake_id = ObjectId()
        response = await client.get(f"/staff/{fake_id}")
        clear_context()

        assert response.status_code == 404


class TestStaffCreateEndpoint:
    """Test staff create endpoint."""

    @pytest.mark.asyncio
    async def test_create_staff_success(self, client, test_tenant, test_user):
        """Test creating a staff member."""
        set_tenant_id(test_tenant.id)
        
        payload = {
            "user_id": str(test_user.id),
            "specialties": ["haircut", "coloring"],
            "certifications": ["Cosmetology License"],
            "hourly_rate": 25.0,
            "hire_date": "2023-01-15",
            "bio": "Experienced stylist",
            "status": "active",
        }
        
        response = await client.post("/staff", json=payload)
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["specialties"] == ["haircut", "coloring"]
        assert data["hourly_rate"] == 25.0
        assert data["status"] == "active"

    @pytest.mark.asyncio
    async def test_create_staff_missing_user_id(self, client, test_tenant):
        """Test creating staff without user_id."""
        set_tenant_id(test_tenant.id)
        
        payload = {
            "specialties": ["haircut"],
            "hourly_rate": 25.0,
        }
        
        response = await client.post("/staff", json=payload)
        clear_context()

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_staff_invalid_user(self, client, test_tenant):
        """Test creating staff with invalid user_id."""
        from bson import ObjectId
        
        set_tenant_id(test_tenant.id)
        
        payload = {
            "user_id": str(ObjectId()),
            "hourly_rate": 25.0,
        }
        
        response = await client.post("/staff", json=payload)
        clear_context()

        assert response.status_code == 400

    @pytest.mark.asyncio
    async def test_create_staff_duplicate_profile(self, client, test_tenant, test_user, test_staff):
        """Test creating duplicate staff profile for same user."""
        set_tenant_id(test_tenant.id)
        
        payload = {
            "user_id": str(test_user.id),
            "hourly_rate": 30.0,
        }
        
        response = await client.post("/staff", json=payload)
        clear_context()

        assert response.status_code == 400


class TestStaffUpdateEndpoint:
    """Test staff update endpoint."""

    @pytest.mark.asyncio
    async def test_update_staff_success(self, client, test_tenant, test_staff):
        """Test updating a staff member."""
        set_tenant_id(test_tenant.id)
        
        payload = {
            "specialties": ["haircut", "coloring", "styling"],
            "hourly_rate": 30.0,
        }
        
        response = await client.put(f"/staff/{test_staff.id}", json=payload)
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert len(data["specialties"]) == 3
        assert data["hourly_rate"] == 30.0

    @pytest.mark.asyncio
    async def test_update_staff_not_found(self, client, test_tenant):
        """Test updating a non-existent staff member."""
        from bson import ObjectId
        
        set_tenant_id(test_tenant.id)
        fake_id = ObjectId()
        
        payload = {"hourly_rate": 30.0}
        response = await client.put(f"/staff/{fake_id}", json=payload)
        clear_context()

        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_update_staff_status(self, client, test_tenant, test_staff):
        """Test updating staff status."""
        set_tenant_id(test_tenant.id)
        
        payload = {"status": "on_leave"}
        response = await client.put(f"/staff/{test_staff.id}", json=payload)
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "on_leave"


class TestStaffDeleteEndpoint:
    """Test staff delete endpoint."""

    @pytest.mark.asyncio
    async def test_delete_staff_success(self, client, test_tenant, test_staff):
        """Test deleting a staff member."""
        set_tenant_id(test_tenant.id)
        staff_id = test_staff.id
        
        response = await client.delete(f"/staff/{staff_id}")
        clear_context()

        assert response.status_code == 200
        data = response.json()
        assert "deleted successfully" in data["message"]

        # Verify deletion
        set_tenant_id(test_tenant.id)
        deleted_staff = Staff.objects(id=staff_id).first()
        assert deleted_staff is None
        clear_context()

    @pytest.mark.asyncio
    async def test_delete_staff_not_found(self, client, test_tenant):
        """Test deleting a non-existent staff member."""
        from bson import ObjectId
        
        set_tenant_id(test_tenant.id)
        fake_id = ObjectId()
        
        response = await client.delete(f"/staff/{fake_id}")
        clear_context()

        assert response.status_code == 404
