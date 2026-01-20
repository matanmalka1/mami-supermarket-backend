from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
from app.extensions import db
from app.models import Order, OrderDeliveryDetails, OrderItem, OrderPickupDetails
from app.models.enums import FulfillmentType, OrderStatus
from app.schemas.checkout import CheckoutConfirmRequest
from app.services.audit_service import AuditService


class CheckoutOrderBuilder:
    @staticmethod
    def order_number() -> str:
        return f"ORD-{int(datetime.utcnow().timestamp())}-{uuid4().hex[:6].upper()}"

    @staticmethod
    def create_order(cart, payload: CheckoutConfirmRequest, branch_id: UUID, total_amount) -> Order:
        order = Order(
            id=uuid4(),
            order_number=CheckoutOrderBuilder.order_number(),
            user_id=cart.user_id,
            total_amount=total_amount,
            fulfillment_type=payload.fulfillment_type or FulfillmentType.DELIVERY,
            status=OrderStatus.CREATED,
            branch_id=branch_id,
        )
        db.session.add(order)
        for item in cart.items:
            order_item = OrderItem(
                id=uuid4(),
                order_id=order.id,
                product_id=item.product_id,
                name=item.product.name,
                sku=item.product.sku,
                unit_price=item.unit_price,
                quantity=item.quantity,
            )
            db.session.add(order_item)
        return order

    @staticmethod
    def add_fulfillment_details(order: Order, payload: CheckoutConfirmRequest, branch_id: UUID) -> None:
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
            return
        now = datetime.utcnow()
        pickup = OrderPickupDetails(
            id=uuid4(),
            order_id=order.id,
            branch_id=branch_id,
            pickup_window_start=now,
            pickup_window_end=now,
        )
        db.session.add(pickup)

    @staticmethod
    def audit_creation(order: Order, total_amount) -> None:
        AuditService.log_event(
            entity_type="order",
            action="CREATE",
            entity_id=order.id,
            actor_user_id=order.user_id,
            new_value={"order_number": order.order_number, "total_amount": float(total_amount)},
        )
