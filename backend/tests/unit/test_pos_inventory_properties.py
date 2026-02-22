"""Property-based tests for POS inventory deduction."""

import pytest
from hypothesis import given, strategies as st
from bson import ObjectId
from app.models.transaction import TransactionItem
from app.services.inventory_deduction_service import InventoryDeductionService


class TestInventoryDeductionProperties:
    """Property-based tests for inventory deduction service."""

    @given(
        quantity=st.integers(min_value=1, max_value=100),
    )
    def test_inventory_deduction_accuracy(self, quantity):
        """
        **Property 2: Inventory Deduction Accuracy**
        **Validates: Requirements 72.1**

        For any transaction with product items, the inventory quantity SHALL be
        reduced by the exact quantity sold.
        """
        from app.models.inventory import Inventory

        tenant_id = ObjectId()
        product_id = ObjectId()

        # Create inventory
        inventory = Inventory(
            tenant_id=tenant_id,
            product_id=product_id,
            quantity_on_hand=1000,
            quantity_reserved=0,
            quantity_available=1000,
            reorder_point=50,
            reorder_quantity=100,
        )
        inventory.save()

        # Create transaction item
        item = TransactionItem(
            item_type="product",
            item_id=product_id,
            item_name="Test Product",
            quantity=quantity,
            unit_price=100,
            line_total=quantity * 100,
        )

        # Deduct inventory
        try:
            InventoryDeductionService.deduct_inventory(
                tenant_id=tenant_id,
                transaction_id=ObjectId(),
                items=[item],
            )

            # Verify inventory was deducted
            updated_inventory = Inventory.objects(
                tenant_id=tenant_id,
                product_id=product_id
            ).first()

            assert updated_inventory is not None
            assert updated_inventory.quantity_on_hand == 1000 - quantity
        finally:
            # Cleanup
            inventory.delete()

    @given(
        quantity=st.integers(min_value=1, max_value=100),
    )
    def test_refund_inventory_restoration(self, quantity):
        """
        **Property 5: Refund Inventory Restoration**
        **Validates: Requirements 78.3**

        For any refunded transaction, the inventory quantities SHALL be restored
        to pre-transaction levels.
        """
        from app.models.inventory import Inventory, InventoryMovement

        tenant_id = ObjectId()
        product_id = ObjectId()
        transaction_id = ObjectId()

        # Create inventory
        inventory = Inventory(
            tenant_id=tenant_id,
            product_id=product_id,
            quantity_on_hand=1000,
            quantity_reserved=0,
            quantity_available=1000,
            reorder_point=50,
            reorder_quantity=100,
        )
        inventory.save()

        # Create inventory movement (sale)
        movement = InventoryMovement(
            tenant_id=tenant_id,
            product_id=product_id,
            movement_type="sale",
            quantity=-quantity,
            reference_id=str(transaction_id),
        )
        movement.save()

        # Manually deduct inventory
        inventory.quantity_on_hand -= quantity
        inventory.save()

        # Restore inventory
        try:
            InventoryDeductionService.restore_inventory(
                tenant_id=tenant_id,
                transaction_id=transaction_id,
            )

            # Verify inventory was restored
            updated_inventory = Inventory.objects(
                tenant_id=tenant_id,
                product_id=product_id
            ).first()

            assert updated_inventory is not None
            assert updated_inventory.quantity_on_hand == 1000
        finally:
            # Cleanup
            inventory.delete()
            movement.delete()
