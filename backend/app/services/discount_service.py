"""Service for managing POS discounts."""

from datetime import datetime
from typing import List, Optional, Dict, Any
from decimal import Decimal
from bson import ObjectId
from mongoengine import Q
from app.models.discount import Discount


class DiscountService:
    """Service for discount management."""

    @staticmethod
    def create_discount(
        tenant_id: ObjectId,
        discount_code: str,
        discount_type: str,
        discount_value: Decimal,
        applicable_to: str = "transaction",
        conditions: Optional[Dict[str, Any]] = None,
        max_discount: Optional[Decimal] = None,
        valid_from: Optional[datetime] = None,
        valid_until: Optional[datetime] = None,
        usage_limit: Optional[int] = None,
    ) -> Discount:
        """
        Create a new discount.

        Args:
            tenant_id: Tenant ID
            discount_code: Discount code
            discount_type: Discount type (percentage, fixed, loyalty, bulk)
            discount_value: Discount value
            applicable_to: Applicable to (transaction, item, service, product)
            conditions: Optional conditions dictionary
            max_discount: Optional maximum discount amount
            valid_from: Optional valid from date
            valid_until: Optional valid until date
            usage_limit: Optional usage limit

        Returns:
            Created Discount document

        Raises:
            ValueError: If discount code already exists
        """
        # Check if discount code already exists
        existing = Discount.objects(
            tenant_id=tenant_id,
            discount_code=discount_code
        ).first()

        if existing:
            raise ValueError(f"Discount code {discount_code} already exists")

        discount = Discount(
            tenant_id=tenant_id,
            discount_code=discount_code,
            discount_type=discount_type,
            discount_value=Decimal(str(discount_value)),
            applicable_to=applicable_to,
            conditions=conditions or {},
            max_discount=Decimal(str(max_discount)) if max_discount else None,
            valid_from=valid_from,
            valid_until=valid_until,
            usage_limit=usage_limit,
            active=True,
        )
        discount.save()
        return discount

    @staticmethod
    def get_discount(
        tenant_id: ObjectId,
        discount_id: ObjectId,
    ) -> Optional[Discount]:
        """
        Get a discount by ID.

        Args:
            tenant_id: Tenant ID
            discount_id: Discount ID

        Returns:
            Discount document or None if not found
        """
        return Discount.objects(
            tenant_id=tenant_id,
            id=discount_id
        ).first()

    @staticmethod
    def list_discounts(
        tenant_id: ObjectId,
        active_only: bool = False,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[List[Discount], int]:
        """
        List discounts with optional filtering.

        Args:
            tenant_id: Tenant ID
            active_only: Filter to active discounts only
            page: Page number (1-indexed)
            page_size: Number of items per page

        Returns:
            Tuple of (discounts list, total count)
        """
        query = Q(tenant_id=tenant_id)

        if active_only:
            query &= Q(active=True)

        total = Discount.objects(query).count()

        skip = (page - 1) * page_size
        discounts = Discount.objects(query).skip(skip).limit(page_size).order_by("-created_at")

        return list(discounts), total

    @staticmethod
    def validate_discount_code(
        tenant_id: ObjectId,
        discount_code: str,
        subtotal: Decimal = Decimal("0"),
    ) -> tuple[bool, Decimal, str]:
        """
        Validate a discount code.

        Args:
            tenant_id: Tenant ID
            discount_code: Discount code to validate
            subtotal: Transaction subtotal for validation

        Returns:
            Tuple of (is_valid, discount_amount, message)
        """
        discount = Discount.objects(
            tenant_id=tenant_id,
            discount_code=discount_code
        ).first()

        if not discount:
            return False, Decimal("0"), "Discount code not found"

        if not discount.active:
            return False, Decimal("0"), "Discount code is not active"

        # Check validity dates
        now = datetime.utcnow()
        if discount.valid_from and now < discount.valid_from:
            return False, Decimal("0"), "Discount code is not yet valid"

        if discount.valid_until and now > discount.valid_until:
            return False, Decimal("0"), "Discount code has expired"

        # Check usage limit
        if discount.usage_limit and discount.usage_count >= discount.usage_limit:
            return False, Decimal("0"), "Discount code usage limit exceeded"

        # Calculate discount amount
        discount_amount = DiscountService.calculate_discount_amount(discount, subtotal)

        return True, discount_amount, "Discount code is valid"

    @staticmethod
    def calculate_discount_amount(
        discount: Discount,
        subtotal: Decimal,
    ) -> Decimal:
        """
        Calculate discount amount based on discount type.

        Args:
            discount: Discount document
            subtotal: Transaction subtotal

        Returns:
            Calculated discount amount
        """
        if discount.discount_type == "percentage":
            discount_amount = (subtotal * discount.discount_value) / Decimal("100")
        elif discount.discount_type == "fixed":
            discount_amount = discount.discount_value
        else:
            # For loyalty and bulk, use fixed amount
            discount_amount = discount.discount_value

        # Apply maximum discount limit if set
        if discount.max_discount and discount_amount > discount.max_discount:
            discount_amount = discount.max_discount

        # Ensure discount doesn't exceed subtotal
        if discount_amount > subtotal:
            discount_amount = subtotal

        return discount_amount

    @staticmethod
    def apply_discount(
        tenant_id: ObjectId,
        discount_code: str,
        subtotal: Decimal,
    ) -> tuple[bool, Decimal, str]:
        """
        Apply a discount code to a transaction.

        Args:
            tenant_id: Tenant ID
            discount_code: Discount code
            subtotal: Transaction subtotal

        Returns:
            Tuple of (success, discount_amount, message)
        """
        is_valid, discount_amount, message = DiscountService.validate_discount_code(
            tenant_id, discount_code, subtotal
        )

        if not is_valid:
            return False, Decimal("0"), message

        # Increment usage count
        discount = Discount.objects(
            tenant_id=tenant_id,
            discount_code=discount_code
        ).first()

        if discount:
            discount.usage_count += 1
            discount.save()

        return True, discount_amount, "Discount applied successfully"

    @staticmethod
    def update_discount(
        tenant_id: ObjectId,
        discount_id: ObjectId,
        discount_value: Optional[Decimal] = None,
        active: Optional[bool] = None,
        valid_until: Optional[datetime] = None,
        usage_limit: Optional[int] = None,
    ) -> Optional[Discount]:
        """
        Update a discount.

        Args:
            tenant_id: Tenant ID
            discount_id: Discount ID
            discount_value: Optional new discount value
            active: Optional active status
            valid_until: Optional new valid until date
            usage_limit: Optional new usage limit

        Returns:
            Updated Discount document or None if not found
        """
        discount = Discount.objects(
            tenant_id=tenant_id,
            id=discount_id
        ).first()

        if not discount:
            return None

        if discount_value is not None:
            discount.discount_value = Decimal(str(discount_value))

        if active is not None:
            discount.active = active

        if valid_until is not None:
            discount.valid_until = valid_until

        if usage_limit is not None:
            discount.usage_limit = usage_limit

        discount.save()
        return discount

    @staticmethod
    def check_discount_conditions(
        discount: Discount,
        transaction_data: dict,
    ) -> bool:
        """
        Check if discount conditions are met.

        Args:
            discount: Discount document
            transaction_data: Transaction data dictionary

        Returns:
            True if conditions are met, False otherwise
        """
        if not discount.conditions:
            return True

        # Check minimum amount condition
        if "min_amount" in discount.conditions:
            min_amount = Decimal(str(discount.conditions["min_amount"]))
            if transaction_data.get("subtotal", Decimal("0")) < min_amount:
                return False

        # Check applicable items condition
        if "applicable_items" in discount.conditions:
            applicable_items = discount.conditions["applicable_items"]
            transaction_items = transaction_data.get("items", [])
            item_ids = [item.get("item_id") for item in transaction_items]
            if not any(item_id in applicable_items for item_id in item_ids):
                return False

        return True
