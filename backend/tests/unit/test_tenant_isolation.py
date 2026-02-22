"""Property-based tests for tenant isolation."""

import pytest
from hypothesis import given, strategies as st
from bson import ObjectId
from app.context import set_tenant_id, get_tenant_id, set_user_id, get_user_id, clear_context


class TestTenantIsolation:
    """Test tenant isolation and context management."""

    def test_tenant_id_context_set_and_get(self):
        """Test that tenant_id can be set and retrieved from context."""
        tenant_id = ObjectId()
        set_tenant_id(tenant_id)

        assert get_tenant_id() == tenant_id

        clear_context()

    def test_user_id_context_set_and_get(self):
        """Test that user_id can be set and retrieved from context."""
        user_id = ObjectId()
        set_user_id(user_id)

        assert get_user_id() == user_id

        clear_context()

    @given(
        tenant_ids=st.lists(
            st.just(ObjectId()),
            min_size=1,
            max_size=5,
        )
    )
    def test_multiple_tenant_contexts(self, tenant_ids):
        """Test that multiple tenant contexts can be managed."""
        for tenant_id in tenant_ids:
            set_tenant_id(tenant_id)
            assert get_tenant_id() == tenant_id
            clear_context()

    def test_context_isolation_between_requests(self):
        """Test that context is isolated between requests."""
        tenant_id_1 = ObjectId()
        tenant_id_2 = ObjectId()

        # Set first tenant
        set_tenant_id(tenant_id_1)
        assert get_tenant_id() == tenant_id_1

        # Clear and set second tenant
        clear_context()
        set_tenant_id(tenant_id_2)
        assert get_tenant_id() == tenant_id_2

        # Verify first tenant is not accessible
        assert get_tenant_id() != tenant_id_1

        clear_context()

    def test_context_clear_removes_all_values(self):
        """Test that clear_context removes all context values."""
        tenant_id = ObjectId()
        user_id = ObjectId()

        set_tenant_id(tenant_id)
        set_user_id(user_id)

        assert get_tenant_id() is not None
        assert get_user_id() is not None

        clear_context()

        assert get_tenant_id() is None
        assert get_user_id() is None

    def test_default_context_values_are_none(self):
        """Test that default context values are None."""
        clear_context()

        assert get_tenant_id() is None
        assert get_user_id() is None

    @given(
        tenant_id=st.just(ObjectId()),
        user_id=st.just(ObjectId()),
    )
    def test_both_contexts_can_be_set(self, tenant_id, user_id):
        """Test that both tenant_id and user_id can be set simultaneously."""
        set_tenant_id(tenant_id)
        set_user_id(user_id)

        assert get_tenant_id() == tenant_id
        assert get_user_id() == user_id

        clear_context()

    def test_tenant_id_string_conversion(self):
        """Test that tenant_id can be set from string."""
        tenant_id = ObjectId()
        tenant_id_str = str(tenant_id)

        set_tenant_id(ObjectId(tenant_id_str))

        assert get_tenant_id() == tenant_id

        clear_context()

    def test_context_with_none_values(self):
        """Test that context handles None values correctly."""
        set_tenant_id(None)
        set_user_id(None)

        assert get_tenant_id() is None
        assert get_user_id() is None

    def test_context_overwrite(self):
        """Test that context values can be overwritten."""
        tenant_id_1 = ObjectId()
        tenant_id_2 = ObjectId()

        set_tenant_id(tenant_id_1)
        assert get_tenant_id() == tenant_id_1

        set_tenant_id(tenant_id_2)
        assert get_tenant_id() == tenant_id_2

        clear_context()
