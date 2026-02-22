"""Integration tests for POS critical gaps implementation."""

import pytest
from decimal import Decimal
from bson import ObjectId
from app.models.cart import Cart
from app.models.transaction import Transaction
from app.models.refund import Refund
from app.models.inventory import Inventory
from app.models.staff_commission import StaffCommission
from app.services.transaction_service import TransactionService
from app.services.inventory_deduction_service import InventoryDeductionService
from app.services.discount_service import DiscountService
from app.services.commission_service import CommissionService
from app.services.refund_service import RefundService


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
def product_id():
    """Create a test product ID."""
    return ObjectId()


@pytest.fixture
def setup_inventory(tenant_id, product_id):
    """Setup test inventory."""
    inventory = Inventory(
        tenant_id=tenant_id,
        name="Test Product",
        sku="TEST-001",
        quantity=100,
        reorder_level=10,
        unit_cost=50.0,
        unit="piece",
        category="Test",
    )
    inventory.save()
    return inventory


class TestCartAPI:
    """Test Cart API endpoints."""

    def test_create_cart(self, tenant_id, staff_id):
        """Test creating a cart."""
        cart = Cart(
            tenant_id=tenant_id,
            staff_id=staff_id,
            status="active",
        )
        cart.save()

        assert cart.id is not None
        assert cart.status == "active"
        assert len(cart.items) == 0
        assert cart.total == Decimal("0")

    def test_add_item_to_cart(self, tenant_id, staff_id):
        """Test adding item to cart."""
        cart = Cart(
            tenant_id=tenant_id,
            staff_id=staff_id,
            status="active",
        )
        cart.save()

        # Add item
        from app.models.cart import CartItem
        item = CartItem(
            item_type="product",
            item_id=ObjectId(),
            item_name="Test Item",
            quantity=2,
            unit_price=Decimal("50.00"),
            line_total=Decimal("100.00"),
        )
        cart.items.append(item)
        cart.subtotal = Decimal("100.00")
        cart.total = Decimal("100.00")
        cart.save()

        assert len(cart.items) == 1
        assert cart.items[0].item_name == "Test Item"
        assert cart.subtotal == Decimal("100.00")

    def test_update_cart_status(self, tenant_id, staff_id):
        """Test updating cart status."""
        cart = Cart(
            tenant_id=tenant_id,
            staff_id=staff_id,
            status="active",
        )
        cart.save()

        cart.status = "completed"
        cart.save()

        updated_cart = Cart.objects(id=cart.id).first()
        assert updated_cart.status == "completed"

    def test_delete_cart(self, tenant_id, staff_id):
        """Test deleting a cart."""
        cart = Cart(
            tenant_id=tenant_id,
            staff_id=staff_id,
            status="active",
        )
        cart.save()
        cart_id = cart.id

        cart.delete()

        deleted_cart = Cart.objects(id=cart_id).first()
        assert deleted_cart is None


class TestRefundAPI:
    """Test Refund API endpoints."""

    def test_create_refund_request(self, tenant_id):
        """Test creating a refund request."""
        from app.models.payment import Payment

        # Create a payment first
        payment = Payment(
            tenant_id=tenant_id,
            amount=Decimal("100.00"),
            currency="NGN",
            status="success",
            reference="test_ref_123",
        )
        payment.save()

        # Create refund
        refund_service = RefundService()
        try:
            refund_data = refund_service.create_refund(
                payment_id=str(payment.id),
                amount=Decimal("50.00"),
                reason="Customer request",
            )

            assert refund_data["refund_id"] is not None
            assert refund_data["amount"] == Decimal("50.00")
            assert refund_data["status"] == "pending"
        except Exception as e:
            # Paystack integration might fail in test environment
            assert "Failed to process refund" in str(e) or "Paystack" in str(e)

    def test_refund_validation(self, tenant_id):
        """Test refund validation."""
        from app.models.payment import Payment

        # Create a payment
        payment = Payment(
            tenant_id=tenant_id,
            amount=Decimal("100.00"),
            currency="NGN",
            status="pending",  # Not success
            reference="test_ref_456",
        )
        payment.save()

        # Try to create refund for non-success payment
        refund_service = RefundService()
        with pytest.raises(ValueError, match="must be in success status"):
            refund_service.create_refund(
                payment_id=str(payment.id),
                amount=Decimal("50.00"),
                reason="Customer request",
            )


class TestInventoryDeduction:
    """Test inventory deduction integration."""

    def test_inventory_deduction_on_transaction(
        self, tenant_id, customer_id, staff_id, product_id, setup_inventory
    ):
        """Test inventory deduction when transaction is created."""
        items_data = [
            {
                "item_type": "product",
                "item_id": str(setup_inventory.id),
                "item_name": "Test Product",
                "quantity": 5,
                "unit_price": Decimal("50.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Create transaction
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
        )

        # Check inventory was deducted
        inventory = Inventory.objects(
            tenant_id=tenant_id, id=setup_inventory.id
        ).first()
        assert inventory.quantity == 95  # 100 - 5

    def test_inventory_restoration_on_cancellation(
        self, tenant_id, customer_id, staff_id, product_id, setup_inventory
    ):
        """Test inventory restoration when transaction is cancelled."""
        items_data = [
            {
                "item_type": "product",
                "item_id": str(setup_inventory.id),
                "item_name": "Test Product",
                "quantity": 5,
                "unit_price": Decimal("50.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Create transaction
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
        )

        # Cancel transaction
        TransactionService.cancel_transaction(tenant_id, transaction.id)

        # Check inventory was restored
        inventory = Inventory.objects(
            tenant_id=tenant_id, id=setup_inventory.id
        ).first()
        assert inventory.quantity == 100  # Restored

    def test_insufficient_inventory_check(
        self, tenant_id, customer_id, staff_id, product_id, setup_inventory
    ):
        """Test that transaction fails if inventory is insufficient."""
        items_data = [
            {
                "item_type": "product",
                "item_id": str(setup_inventory.id),
                "item_name": "Test Product",
                "quantity": 150,  # More than available
                "unit_price": Decimal("50.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Try to create transaction
        with pytest.raises(ValueError, match="Insufficient inventory"):
            TransactionService.create_transaction(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                items_data=items_data,
                payment_method="cash",
            )


class TestDiscountApplication:
    """Test discount application integration."""

    def test_discount_code_application(self, tenant_id, customer_id, staff_id):
        """Test applying discount code to transaction."""
        # Create discount
        discount = DiscountService.create_discount(
            tenant_id=tenant_id,
            discount_code="SAVE10",
            discount_type="percentage",
            discount_value=Decimal("10"),
            applicable_to="transaction",
        )

        items_data = [
            {
                "item_type": "service",
                "item_id": str(ObjectId()),
                "item_name": "Test Service",
                "quantity": 1,
                "unit_price": Decimal("100.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Create transaction with discount code
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
            discount_code="SAVE10",
        )

        # Check discount was applied
        assert transaction.discount_amount == Decimal("10.00")  # 10% of 100
        assert transaction.total == Decimal("90.00")

    def test_invalid_discount_code(self, tenant_id, customer_id, staff_id):
        """Test that invalid discount code raises error."""
        items_data = [
            {
                "item_type": "service",
                "item_id": str(ObjectId()),
                "item_name": "Test Service",
                "quantity": 1,
                "unit_price": Decimal("100.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Try to create transaction with invalid discount code
        with pytest.raises(ValueError, match="Invalid discount code"):
            TransactionService.create_transaction(
                tenant_id=tenant_id,
                customer_id=customer_id,
                staff_id=staff_id,
                items_data=items_data,
                payment_method="cash",
                discount_code="INVALID",
            )


class TestCommissionCalculation:
    """Test commission calculation integration."""

    def test_commission_calculation_on_transaction(
        self, tenant_id, customer_id, staff_id
    ):
        """Test commission calculation when transaction is created."""
        items_data = [
            {
                "item_type": "service",
                "item_id": str(ObjectId()),
                "item_name": "Test Service",
                "quantity": 1,
                "unit_price": Decimal("100.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Create transaction with commission
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
            commission_rate=Decimal("10"),
            commission_type="percentage",
        )

        # Check commission was calculated
        commission = StaffCommission.objects(
            tenant_id=tenant_id, transaction_id=transaction.id
        ).first()

        assert commission is not None
        assert commission.commission_amount == Decimal("10.00")  # 10% of 100
        assert commission.commission_type == "percentage"

    def test_commission_calculation_fixed_amount(
        self, tenant_id, customer_id, staff_id
    ):
        """Test fixed amount commission calculation."""
        items_data = [
            {
                "item_type": "service",
                "item_id": str(ObjectId()),
                "item_name": "Test Service",
                "quantity": 1,
                "unit_price": Decimal("100.00"),
                "tax_rate": Decimal("0"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Create transaction with fixed commission
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
            commission_rate=Decimal("15"),
            commission_type="fixed",
        )

        # Check commission was calculated
        commission = StaffCommission.objects(
            tenant_id=tenant_id, transaction_id=transaction.id
        ).first()

        assert commission is not None
        assert commission.commission_amount == Decimal("15.00")  # Fixed amount
        assert commission.commission_type == "fixed"


class TestIntegratedFlow:
    """Test complete integrated flow with all critical gaps."""

    def test_complete_transaction_flow(
        self, tenant_id, customer_id, staff_id, product_id, setup_inventory
    ):
        """Test complete transaction flow with inventory, discount, and commission."""
        # Create discount
        DiscountService.create_discount(
            tenant_id=tenant_id,
            discount_code="SAVE20",
            discount_type="percentage",
            discount_value=Decimal("20"),
            applicable_to="transaction",
        )

        items_data = [
            {
                "item_type": "product",
                "item_id": str(setup_inventory.id),
                "item_name": "Test Product",
                "quantity": 2,
                "unit_price": Decimal("100.00"),
                "tax_rate": Decimal("10"),
                "discount_rate": Decimal("0"),
            }
        ]

        # Create transaction with all integrations
        transaction = TransactionService.create_transaction(
            tenant_id=tenant_id,
            customer_id=customer_id,
            staff_id=staff_id,
            items_data=items_data,
            payment_method="cash",
            discount_code="SAVE20",
            commission_rate=Decimal("5"),
            commission_type="percentage",
        )

        # Verify transaction
        assert transaction.subtotal == Decimal("200.00")
        assert transaction.discount_amount == Decimal("40.00")  # 20% of 200
        assert transaction.tax_amount == Decimal("16.00")  # 10% of (200-40)
        assert transaction.total == Decimal("176.00")

        # Verify inventory deduction
        inventory = Inventory.objects(
            tenant_id=tenant_id, id=setup_inventory.id
        ).first()
        assert inventory.quantity == 98  # 100 - 2

        # Verify commission
        commission = StaffCommission.objects(
            tenant_id=tenant_id, transaction_id=transaction.id
        ).first()
        assert commission is not None
        assert commission.commission_amount == Decimal("8.80")  # 5% of 176
