"""API routes for POS carts."""

from fastapi import APIRouter, Depends, HTTPException, Query
from bson import ObjectId
from decimal import Decimal
from app.context import get_tenant_id, get_user_id
from app.schemas.cart import (
    CartCreateRequest,
    CartUpdateRequest,
    CartAddItemRequest,
    CartResponse,
    CartListResponse,
)
from app.models.cart import Cart, CartItem
from app.services.pos_audit_service import POSAuditService

router = APIRouter(prefix="/pos/carts", tags=["pos_carts"])


@router.post("", response_model=CartResponse)
async def create_cart(
    request: CartCreateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Create a new cart."""
    try:
        cart = Cart(
            tenant_id=tenant_id,
            customer_id=ObjectId(request.customer_id) if request.customer_id else None,
            staff_id=ObjectId(request.staff_id),
            status="active",
        )
        cart.save()

        # Log cart creation
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="cart_created",
            resource_type="cart",
            resource_id=str(cart.id),
            details={"staff_id": request.staff_id},
        )

        return CartResponse(
            id=str(cart.id),
            customer_id=str(cart.customer_id) if cart.customer_id else None,
            staff_id=str(cart.staff_id),
            items=[],
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            discount_amount=cart.discount_amount,
            total=cart.total,
            status=cart.status,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{cart_id}", response_model=CartResponse)
async def get_cart(
    cart_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
):
    """Get cart details."""
    try:
        cart = Cart.objects(
            tenant_id=tenant_id,
            id=ObjectId(cart_id),
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        return CartResponse(
            id=str(cart.id),
            customer_id=str(cart.customer_id) if cart.customer_id else None,
            staff_id=str(cart.staff_id),
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in cart.items
            ],
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            discount_amount=cart.discount_amount,
            total=cart.total,
            status=cart.status,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{cart_id}", response_model=CartResponse)
async def update_cart(
    cart_id: str,
    request: CartUpdateRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Update cart."""
    try:
        cart = Cart.objects(
            tenant_id=tenant_id,
            id=ObjectId(cart_id),
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        old_values = {
            "customer_id": str(cart.customer_id) if cart.customer_id else None,
            "status": cart.status,
        }

        if request.customer_id:
            cart.customer_id = ObjectId(request.customer_id)

        if request.status:
            cart.status = request.status

        cart.save()

        # Log cart modification
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="cart_updated",
            resource_type="cart",
            resource_id=str(cart.id),
            details={"old_values": old_values, "new_values": request.dict()},
        )

        return CartResponse(
            id=str(cart.id),
            customer_id=str(cart.customer_id) if cart.customer_id else None,
            staff_id=str(cart.staff_id),
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in cart.items
            ],
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            discount_amount=cart.discount_amount,
            total=cart.total,
            status=cart.status,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cart_id}")
async def delete_cart(
    cart_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Delete cart."""
    try:
        cart = Cart.objects(
            tenant_id=tenant_id,
            id=ObjectId(cart_id),
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        cart.delete()

        # Log cart deletion
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="cart_deleted",
            resource_type="cart",
            resource_id=str(cart.id),
        )

        return {"message": "Cart deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{cart_id}/items", response_model=CartResponse)
async def add_item_to_cart(
    cart_id: str,
    request: CartAddItemRequest,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Add item to cart."""
    try:
        cart = Cart.objects(
            tenant_id=tenant_id,
            id=ObjectId(cart_id),
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Calculate line total
        line_total = request.quantity * request.unit_price

        # Create cart item
        cart_item = CartItem(
            item_type=request.item_type,
            item_id=ObjectId(request.item_id),
            item_name=request.item_name,
            quantity=request.quantity,
            unit_price=request.unit_price,
            line_total=line_total,
        )

        # Add item to cart
        cart.items.append(cart_item)

        # Recalculate totals
        cart.subtotal = sum(item.line_total for item in cart.items)
        cart.total = cart.subtotal - cart.discount_amount + cart.tax_amount

        cart.save()

        # Log item addition
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="cart_item_added",
            resource_type="cart",
            resource_id=str(cart.id),
            details={"item": request.dict()},
        )

        return CartResponse(
            id=str(cart.id),
            customer_id=str(cart.customer_id) if cart.customer_id else None,
            staff_id=str(cart.staff_id),
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in cart.items
            ],
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            discount_amount=cart.discount_amount,
            total=cart.total,
            status=cart.status,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{cart_id}/items/{item_id}")
async def remove_item_from_cart(
    cart_id: str,
    item_id: str,
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Remove item from cart."""
    try:
        cart = Cart.objects(
            tenant_id=tenant_id,
            id=ObjectId(cart_id),
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Find and remove item
        item_to_remove = None
        for item in cart.items:
            if str(item.item_id) == item_id:
                item_to_remove = item
                break

        if not item_to_remove:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        cart.items.remove(item_to_remove)

        # Recalculate totals
        cart.subtotal = sum(item.line_total for item in cart.items)
        cart.total = cart.subtotal - cart.discount_amount + cart.tax_amount

        cart.save()

        # Log item removal
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="cart_item_removed",
            resource_type="cart",
            resource_id=str(cart.id),
            details={"item_id": item_id},
        )

        return {"message": "Item removed from cart successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{cart_id}/items/{item_id}", response_model=CartResponse)
async def update_item_quantity(
    cart_id: str,
    item_id: str,
    quantity: int = Query(..., ge=1),
    tenant_id: ObjectId = Depends(get_tenant_id),
    user_id: ObjectId = Depends(get_user_id),
):
    """Update item quantity in cart."""
    try:
        cart = Cart.objects(
            tenant_id=tenant_id,
            id=ObjectId(cart_id),
        ).first()

        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Find and update item
        item_found = False
        for item in cart.items:
            if str(item.item_id) == item_id:
                item.quantity = quantity
                item.line_total = quantity * item.unit_price
                item_found = True
                break

        if not item_found:
            raise HTTPException(status_code=404, detail="Item not found in cart")

        # Recalculate totals
        cart.subtotal = sum(item.line_total for item in cart.items)
        cart.total = cart.subtotal - cart.discount_amount + cart.tax_amount

        cart.save()

        # Log item update
        POSAuditService.log_action(
            tenant_id=tenant_id,
            user_id=user_id,
            action="cart_item_updated",
            resource_type="cart",
            resource_id=str(cart.id),
            details={"item_id": item_id, "quantity": quantity},
        )

        return CartResponse(
            id=str(cart.id),
            customer_id=str(cart.customer_id) if cart.customer_id else None,
            staff_id=str(cart.staff_id),
            items=[
                {
                    "item_type": item.item_type,
                    "item_id": str(item.item_id),
                    "item_name": item.item_name,
                    "quantity": item.quantity,
                    "unit_price": item.unit_price,
                    "line_total": item.line_total,
                }
                for item in cart.items
            ],
            subtotal=cart.subtotal,
            tax_amount=cart.tax_amount,
            discount_amount=cart.discount_amount,
            total=cart.total,
            status=cart.status,
            created_at=cart.created_at.isoformat(),
            updated_at=cart.updated_at.isoformat(),
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
