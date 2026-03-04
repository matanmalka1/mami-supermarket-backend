"""Customer order retrieval and cancellation logic."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import select ,func
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Inventory, Order
from app.models.enums import OrderStatus
from app.schemas.orders import CancelOrderResponse, OrderItemResponse, OrderResponse
from app.services.audit_service import AuditService

class OrderService:
    @staticmethod
    def list_orders(user_id: int, limit: int, offset: int) -> tuple[list[OrderResponse], int]:
        stmt = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        orders = db.session.execute(stmt).scalars().all()
        total = db.session.scalar(
            select(func.count()).select_from(Order).where(Order.user_id == user_id)
        )
        return [OrderService._to_response(order) for order in orders], total or 0

    @staticmethod
    def get_order(order_id: int, user_id: int) -> OrderResponse:
        order = OrderService._load_order(order_id)
        if order.user_id != user_id:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        return OrderService._to_response(order)

    @staticmethod
    def cancel_order(order_id: int, user_id: int) -> CancelOrderResponse:
        session = db.session
        order = session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .with_for_update()
        ).scalar_one_or_none()
        if not order or order.user_id != user_id:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        if order.status != OrderStatus.CREATED:
            raise DomainError(
                "INVALID_STATUS",
                "Order cannot be canceled in its current status",
                status_code=409,
            )
        canceled_at = datetime.now(timezone.utc)
        old_value = {"status": order.status.value}
        order.status = OrderStatus.CANCELED

        # Restore inventory for each item if we know the fulfillment branch.
        if order.branch_id:
            product_ids = [item.product_id for item in order.items]
            inv_rows = session.execute(
                select(Inventory)
                .where(
                    Inventory.branch_id == order.branch_id,
                    Inventory.product_id.in_(product_ids),
                )
                .with_for_update()
            ).scalars().all()
            inv_map = {row.product_id: row for row in inv_rows}
            for item in order.items:
                inv = inv_map.get(item.product_id)
                if inv is not None:
                    inv.available_quantity += item.quantity

        AuditService.log_event(
            entity_type="order",
            action="CANCEL",
            actor_user_id=user_id,
            entity_id=order.id,
            old_value=old_value,
            new_value={"status": order.status.value},
            context={"canceled_at": canceled_at.isoformat()},
        )
        session.add(order)
        session.commit()
        return CancelOrderResponse(order_id=order.id, canceled_at=canceled_at)

    @staticmethod
    def _load_order(order_id: int) -> Order:
        order = db.session.execute(
            select(Order).where(Order.id == order_id).options(selectinload(Order.items))
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        return order

    @staticmethod
    def _to_response(order: Order) -> OrderResponse:
        items = [
            OrderItemResponse(
                id=item.id,
                product_id=item.product_id,
                name=item.name,
                sku=item.sku,
                unit_price=item.unit_price,
                quantity=item.quantity,
                picked_status=item.picked_status,
            )
            for item in order.items
        ]
        return OrderResponse(
            id=order.id,
            order_number=order.order_number,
            total_amount=order.total_amount,
            status=order.status,
            fulfillment_type=order.fulfillment_type,
            created_at=order.created_at,
            items=items,
        )
