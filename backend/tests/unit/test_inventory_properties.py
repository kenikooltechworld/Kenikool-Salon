"""Property-based tests for inventory management"""
from hypothesis import given, strategies as st, assume
from datetime import datetime
from app.models.inventory import Inventory, InventoryTransaction, StockAlert
from app.services.inventory_service import InventoryService
import pytest


class TestInventoryDeductionAccuracy:
    """Property 41: Inventory Deduction Accuracy - Validates Requirements 27.1"""

    @given(
        initial_quantity=st.integers(min_value=10, max_value=1000),
        deduction_quantity=st.integers(min_value=1, max_value=100),
    )
    def test_inventory_deduction_reduces_quantity(self, initial_quantity, deduction_quantity):
        """Inventory deduction should reduce quantity by exact amount"""
        assume(deduction_quantity <= initial_quantity)
        
        # Create inventory
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST001",
            quantity=initial_quantity,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        # Deduct inventory
        transaction = InventoryService.deduct_inventory(
            inventory_id=str(inventory.id),
            quantity=deduction_quantity,
            reason="test",
        )
        
        # Verify
        inventory.reload()
        assert inventory.quantity == initial_quantity - deduction_quantity
        assert transaction.quantity_change == -deduction_quantity
        assert transaction.transaction_type == "out"

    @given(
        quantity=st.integers(min_value=1, max_value=100),
    )
    def test_inventory_deduction_creates_transaction(self, quantity):
        """Each deduction should create a transaction record"""
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST002",
            quantity=quantity + 10,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        transaction = InventoryService.deduct_inventory(
            inventory_id=str(inventory.id),
            quantity=quantity,
            reason="test",
        )
        
        assert transaction is not None
        assert transaction.quantity_change == -quantity
        assert InventoryTransaction.objects(id=transaction.id).count() == 1

    @given(
        quantity=st.integers(min_value=1, max_value=100),
    )
    def test_inventory_deduction_prevents_negative(self, quantity):
        """Deduction should not allow negative inventory"""
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST003",
            quantity=5,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        with pytest.raises(ValueError):
            InventoryService.deduct_inventory(
                inventory_id=str(inventory.id),
                quantity=quantity,
                reason="test",
            )


class TestStockAlertTriggering:
    """Property 42: Stock Alert Triggering - Validates Requirements 28.1"""

    @given(
        initial_quantity=st.integers(min_value=1, max_value=100),
        reorder_level=st.integers(min_value=1, max_value=50),
    )
    def test_low_stock_alert_created(self, initial_quantity, reorder_level):
        """Alert should be created when stock falls below reorder level"""
        assume(initial_quantity > reorder_level)
        
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST004",
            quantity=initial_quantity,
            reorder_level=reorder_level,
            unit_cost=10.0,
        )
        inventory.save()
        
        # Deduct to trigger alert
        deduction = initial_quantity - reorder_level + 1
        InventoryService.deduct_inventory(
            inventory_id=str(inventory.id),
            quantity=deduction,
            reason="test",
        )
        
        # Check alert was created
        alerts = StockAlert.objects(
            tenant_id="test_tenant",
            inventory_id=inventory.id,
            alert_type="low_stock",
        )
        assert alerts.count() > 0

    @given(
        quantity=st.integers(min_value=1, max_value=50),
    )
    def test_out_of_stock_alert_created(self, quantity):
        """Out of stock alert should be created when quantity reaches zero"""
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST005",
            quantity=quantity,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        # Deduct all
        InventoryService.deduct_inventory(
            inventory_id=str(inventory.id),
            quantity=quantity,
            reason="test",
        )
        
        # Check alert
        alerts = StockAlert.objects(
            tenant_id="test_tenant",
            inventory_id=inventory.id,
            alert_type="out_of_stock",
        )
        assert alerts.count() > 0


class TestInventoryReconciliationAccuracy:
    """Property 43: Inventory Reconciliation Accuracy - Validates Requirements 30.1"""

    @given(
        system_count=st.integers(min_value=0, max_value=100),
        physical_count=st.integers(min_value=0, max_value=100),
    )
    def test_reconciliation_calculates_discrepancy(self, system_count, physical_count):
        """Reconciliation should correctly calculate discrepancy"""
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST006",
            quantity=system_count,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        result = InventoryService.reconcile_inventory(
            inventory_id=str(inventory.id),
            physical_count=physical_count,
            notes="test",
        )
        
        assert result["system_count"] == system_count
        assert result["physical_count"] == physical_count
        assert result["discrepancy"] == physical_count - system_count

    @given(
        system_count=st.integers(min_value=0, max_value=100),
        physical_count=st.integers(min_value=0, max_value=100),
    )
    def test_reconciliation_creates_adjustment(self, system_count, physical_count):
        """Reconciliation should create adjustment transaction if discrepancy exists"""
        assume(system_count != physical_count)
        
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST007",
            quantity=system_count,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        InventoryService.reconcile_inventory(
            inventory_id=str(inventory.id),
            physical_count=physical_count,
            notes="test",
        )
        
        # Check transaction was created
        transactions = InventoryTransaction.objects(
            tenant_id="test_tenant",
            inventory_id=inventory.id,
            transaction_type="reconciliation",
        )
        assert transactions.count() > 0

    @given(
        system_count=st.integers(min_value=0, max_value=100),
        physical_count=st.integers(min_value=0, max_value=100),
    )
    def test_reconciliation_updates_quantity(self, system_count, physical_count):
        """Reconciliation should update inventory quantity to physical count"""
        inventory = Inventory(
            tenant_id="test_tenant",
            name="Test Item",
            sku="TEST008",
            quantity=system_count,
            reorder_level=5,
            unit_cost=10.0,
        )
        inventory.save()
        
        InventoryService.reconcile_inventory(
            inventory_id=str(inventory.id),
            physical_count=physical_count,
            notes="test",
        )
        
        inventory.reload()
        assert inventory.quantity == physical_count
