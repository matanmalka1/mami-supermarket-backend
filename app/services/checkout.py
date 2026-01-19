"""Checkout preview and confirm logic with pessimistic locking."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID, uuid4

from flask import current_app
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import Cart, CartItem, Inventory, Order, OrderDeliveryDetails, OrderItem, OrderPickupDetails
from ..models.enums import FulfillmentType, OrderStatus
from ..schemas.checkout import (
    CheckoutConfirmRequest,
    CheckoutConfirmResponse,
    CheckoutPreviewRequest,
    CheckoutPreviewResponse,
    MissingItem,
)
from ..services.audit import AuditService
from ..services.branches import BranchService
from ..services.payment import PaymentService


class CheckoutService:
    @staticmethod
    def preview(payload: CheckoutPreviewRequest) -> CheckoutPreviewResponse:
        branch_id = CheckoutService._resolve_branch(payload.fulfillment_type, payload.branch_id)
        cart = CheckoutService._load_cart(payload.cart_id)
        missing = CheckoutService._missing_items(cart.items, branch_id)
        delivery_fee = CheckoutService._delivery_fee(cart)
        return CheckoutPreviewResponse(
            cart_total=delivery_fee["cart_total"],
            delivery_fee=delivery_fee["delivery_fee"] if payload.fulfillment_type == FulfillmentType.DELIVERY else None,
            missing_items=missing,
            fulfillment_type=payload.fulfillment_type,
        )

    @staticmethod
    def confirm(payload: CheckoutConfirmRequest) -> CheckoutConfirmResponse:
        branch_id = CheckoutService._resolve_branch(payload.fulfillment_type, payload.branch_id)
        cart = CheckoutService._load_cart(payload.cart_id, for_update=True, branch_id=branch_id)

        # Lock inventory rows
        inv_ids = [item.product_id for item in cart.items]
        inventory_rows = db.session.execute(
            select(Inventory).where(Inventory.product_id.in_(inv_ids)).where(Inventory.branch_id == branch_id).with_for_update()
        ).scalars().all()
        inv_map = {(inv.product_id, inv.branch_id): inv for inv in inventory_rows}

        # Verify quantities
        missing = CheckoutService._missing_items(cart.items, branch_id, inv_map)
        if missing:
            raise DomainError("INSUFFICIENT_STOCK", "Insufficient stock for items", status_code=409, details={"missing": [m.model_dump() for m in missing]})

        # Charge payment (stub)
        cart_total = sum(item.unit_price * item.quantity for item in cart.items)
        delivery_fee = CheckoutService._delivery_fee(cart)["delivery_fee"]
        total_amount = float(cart_total + (delivery_fee or 0))
        payment_ref = PaymentService.charge(payload.payment_token_id, total_amount)

        # Create order + snapshots and decrement inventory
        order = Order(
            id=uuid4(),
            order_number=CheckoutService._order_number(),
            user_id=cart.user_id,
            total_amount=total_amount,
            fulfillment_type=payload.fulfillment_type or FulfillmentType.DELIVERY,
            status=OrderStatus.CREATED,
            branch_id=branch_id,
        )
        db.session.add(order)
        for item in cart.items:
            OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                name=item.product.name,
                sku=item.product.sku,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            db.session.add(
                OrderItem(
                    id=uuid4(),
                    order_id=order.id,
                    product_id=item.product_id,
                    name=item.product.name,
                    sku=item.product.sku,
                    unit_price=item.unit_price,
                    quantity=item.quantity,
                )
            )
            key = (item.product_id, branch_id)
            inv_row = inv_map.get(key)
            if inv_row:
                inv_row.available_quantity -= item.quantity
                db.session.add(inv_row)

        if payload.fulfillment_type == FulfillmentType.DELIVERY:
            delivery = OrderDeliveryDetails(
                id=uuid4(),
                order_id=order.id,
                delivery_slot_id=payload.delivery_slot_id,
                address=payload.address or "",
                slot_start=None,
                slot_end=None,
            )
            db.session.add(delivery)
        else:
            pickup = OrderPickupDetails(
                id=uuid4(),
                order_id=order.id,
                branch_id=branch_id,
                pickup_window_start=datetime.utcnow(),
                pickup_window_end=datetime.utcnow(),
            )
            db.session.add(pickup)

        AuditService.log_event(
            entity_type="order",
            action="CREATE",
            entity_id=order.id,
            actor_user_id=order.user_id,
            new_value={"order_number": order.order_number, "total_amount": total_amount},
        )
        db.session.commit()

        return CheckoutConfirmResponse(
            order_id=order.id,
            order_number=order.order_number,
            total_paid=total_amount,
            payment_reference=payment_ref,
        )

    @staticmethod
    def _order_number() -> str:
        return f"ORD-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:6].upper()}"

    @staticmethod
    def _resolve_branch(fulfillment_type: FulfillmentType | None, branch_id: UUID | None) -> UUID:
        if fulfillment_type == FulfillmentType.DELIVERY:
            source_id = current_app.config.get("DELIVERY_SOURCE_BRANCH_ID", "")
            branch = BranchService.ensure_delivery_source_branch_exists(source_id)
            return branch.id
        if branch_id:
            branch = db.session.get(Branch, branch_id)
            if not branch or not branch.is_active:
                raise DomainError("NOT_FOUND", "Branch not found", status_code=404)
            return branch.id
        raise DomainError("BAD_REQUEST", "Branch is required for pickup", status_code=400)

    @staticmethod
    def _load_cart(cart_id: UUID, for_update: bool = False, branch_id: UUID | None = None) -> Cart:
        stmt = select(Cart).where(Cart.id == cart_id).options(joinedload(Cart.items).joinedload(CartItem.product))
        if for_update:
            stmt = stmt.with_for_update()
        cart = db.session.execute(stmt).scalar_one_or_none()
        if not cart:
            raise DomainError("NOT_FOUND", "Cart not found", status_code=404)
        return cart

    @staticmethod
    def _missing_items(cart_items, branch_id: UUID, inv_map=None) -> list[MissingItem]:
        missing: list[MissingItem] = []
        for item in cart_items:
            if inv_map is None:
                inv_row = db.session.execute(
                    select(Inventory).where(Inventory.product_id == item.product_id, Inventory.branch_id == branch_id)
                ).scalar_one_or_none()
            else:
                inv_row = inv_map.get((item.product_id, branch_id))
            available = inv_row.available_quantity if inv_row else 0
            if available < item.quantity:
                missing.append(
                    MissingItem(
                        product_id=item.product_id,
                        requested_quantity=item.quantity,
                        available_quantity=available,
                    )
                )
        return missing

    @staticmethod
    def _delivery_fee(cart: Cart) -> dict[str, float]:
        cart_total = sum(item.unit_price * item.quantity for item in cart.items)
        min_total = float(current_app.config.get("DELIVERY_MIN_TOTAL", 150))
        under_min_fee = float(current_app.config.get("DELIVERY_FEE_UNDER_MIN", 30))
        delivery_fee = 0.0 if cart_total >= min_total else under_min_fee
        return {"cart_total": cart_total, "delivery_fee": delivery_fee}
