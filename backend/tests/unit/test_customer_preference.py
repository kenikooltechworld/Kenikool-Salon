"""Unit tests for customer preference model and operations."""

import pytest
from datetime import datetime
from bson import ObjectId
from app.models.customer_preference import CustomerPreference


@pytest.fixture
def tenant_id():
    """Create a test tenant ID."""
    return ObjectId()


@pytest.fixture
def customer_id():
    """Create a test customer ID."""
    return ObjectId()


@pytest.fixture
def staff_id():
    """Create a test staff ID."""
    return ObjectId()


@pytest.fixture
def service_id():
    """Create a test service ID."""
    return ObjectId()


class TestCustomerPreferenceModel:
    """Test CustomerPreference model."""

    def test_create_customer_preference_with_defaults(self, tenant_id, customer_id):
        """Test creating a customer preference with default values."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )
        preference.save()

        assert preference.id is not None
        assert preference.customer_id == customer_id
        assert preference.tenant_id == tenant_id
        assert preference.preferred_staff_ids == []
        assert preference.preferred_service_ids == []
        assert preference.communication_methods == ["email"]
        assert preference.preferred_time_slots == []
        assert preference.language == "en"
        assert preference.notes is None
        assert isinstance(preference.created_at, datetime)
        assert isinstance(preference.updated_at, datetime)

        preference.delete()

    def test_create_customer_preference_with_all_fields(
        self, tenant_id, customer_id, staff_id, service_id
    ):
        """Test creating a customer preference with all fields."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
            preferred_staff_ids=[staff_id],
            preferred_service_ids=[service_id],
            communication_methods=["email", "sms"],
            preferred_time_slots=["morning", "afternoon"],
            language="fr",
            notes="Prefers morning appointments",
        )
        preference.save()

        assert preference.preferred_staff_ids == [staff_id]
        assert preference.preferred_service_ids == [service_id]
        assert preference.communication_methods == ["email", "sms"]
        assert preference.preferred_time_slots == ["morning", "afternoon"]
        assert preference.language == "fr"
        assert preference.notes == "Prefers morning appointments"

        preference.delete()

    def test_update_customer_preference(self, tenant_id, customer_id, staff_id, service_id):
        """Test updating a customer preference."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )
        preference.save()

        # Update preferences
        preference.preferred_staff_ids = [staff_id]
        preference.preferred_service_ids = [service_id]
        preference.communication_methods = ["sms", "phone"]
        preference.language = "es"
        preference.save()

        # Verify updates
        updated = CustomerPreference.objects(id=preference.id).first()
        assert updated.preferred_staff_ids == [staff_id]
        assert updated.preferred_service_ids == [service_id]
        assert updated.communication_methods == ["sms", "phone"]
        assert updated.language == "es"

        preference.delete()

    def test_query_by_customer_id(self, tenant_id, customer_id):
        """Test querying preferences by customer ID."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )
        preference.save()

        found = CustomerPreference.objects(
            customer_id=customer_id,
            tenant_id=tenant_id
        ).first()

        assert found is not None
        assert found.id == preference.id

        preference.delete()

    def test_multiple_preferences_for_different_customers(self, tenant_id):
        """Test creating preferences for multiple customers."""
        customer_id_1 = ObjectId()
        customer_id_2 = ObjectId()

        pref1 = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id_1,
            language="en",
        )
        pref1.save()

        pref2 = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id_2,
            language="fr",
        )
        pref2.save()

        # Query each preference
        found1 = CustomerPreference.objects(
            customer_id=customer_id_1,
            tenant_id=tenant_id
        ).first()
        found2 = CustomerPreference.objects(
            customer_id=customer_id_2,
            tenant_id=tenant_id
        ).first()

        assert found1.language == "en"
        assert found2.language == "fr"

        pref1.delete()
        pref2.delete()

    def test_communication_methods_validation(self, tenant_id, customer_id):
        """Test that communication methods are validated."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
            communication_methods=["email", "sms", "phone"],
        )
        preference.save()

        found = CustomerPreference.objects(id=preference.id).first()
        assert found.communication_methods == ["email", "sms", "phone"]

        preference.delete()

    def test_preferred_time_slots(self, tenant_id, customer_id):
        """Test storing preferred time slots."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
            preferred_time_slots=["morning", "afternoon"],
        )
        preference.save()

        found = CustomerPreference.objects(id=preference.id).first()
        assert found.preferred_time_slots == ["morning", "afternoon"]

        preference.delete()

    def test_notes_field(self, tenant_id, customer_id):
        """Test storing notes in preferences."""
        notes = "Customer prefers female staff and hypoallergenic products"
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
            notes=notes,
        )
        preference.save()

        found = CustomerPreference.objects(id=preference.id).first()
        assert found.notes == notes

        preference.delete()

    def test_delete_customer_preference(self, tenant_id, customer_id):
        """Test deleting a customer preference."""
        preference = CustomerPreference(
            tenant_id=tenant_id,
            customer_id=customer_id,
        )
        preference.save()
        preference_id = preference.id

        preference.delete()

        found = CustomerPreference.objects(id=preference_id).first()
        assert found is None

    def test_tenant_isolation(self):
        """Test that preferences are isolated by tenant."""
        tenant_id_1 = ObjectId()
        tenant_id_2 = ObjectId()
        customer_id = ObjectId()

        pref1 = CustomerPreference(
            tenant_id=tenant_id_1,
            customer_id=customer_id,
            language="en",
        )
        pref1.save()

        pref2 = CustomerPreference(
            tenant_id=tenant_id_2,
            customer_id=customer_id,
            language="fr",
        )
        pref2.save()

        # Query from tenant 1 should only get tenant 1's preference
        found = CustomerPreference.objects(
            customer_id=customer_id,
            tenant_id=tenant_id_1
        ).first()

        assert found.language == "en"

        pref1.delete()
        pref2.delete()
