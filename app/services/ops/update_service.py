from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Order
from app.models.enums import OrderStatus, PickedStatus, Role
from app.schemas.orders import OrderResponse
from app.services.audit_service import AuditService
from .mappers import to_detail
from .transitions import can_transition


class OpsOrderUpdateService:
    @staticmethod
    def update_item_status(
        order_id: int,
        item_id: int,
        picked_status: str,
        actor_id: int,
    ) -> OrderResponse:
        session = db.session
        order = session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .with_for_update()
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        item = next((i for i in order.items if i.id == item_id), None)
        if not item:
            raise DomainError("NOT_FOUND", "Order item not found", status_code=404)
        try:
            new_status = PickedStatus(picked_status)
        except ValueError:
            raise DomainError("BAD_REQUEST", "Invalid picked status", status_code=400)
        old_value = {"picked_status": item.picked_status.value}
        item.picked_status = new_status
        session.add(item)
        AuditService.log_event(
            entity_type="order_item",
            action="UPDATE_PICK_STATUS",
            actor_user_id=actor_id,
            entity_id=item.id,
            old_value=old_value,
            new_value={"picked_status": new_status.value},
        )
        session.commit()
        return to_detail(order)

    @staticmethod
    def update_order_status(
        order_id: int,
        status_value: str,
        actor_id: int,
        actor_role: Role,
    ) -> OrderResponse:
        session = db.session
        order = session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.items))
            .with_for_update()
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        try:
            new_status = OrderStatus(status_value)
        except ValueError:
            raise DomainError("BAD_REQUEST", "Invalid status", status_code=400)
        if not can_transition(order, new_status, actor_role):
            raise DomainError("INVALID_STATUS_TRANSITION", "Status transition not allowed", status_code=409)
        old_value = {"status": order.status.value}
        order.status = new_status
        session.add(order)
        AuditService.log_event(
            entity_type="order",
            action="UPDATE_STATUS",
            actor_user_id=actor_id,
            entity_id=order.id,
            old_value=old_value,
            new_value={"status": order.status.value},
        )
        session.commit()
        return to_detail(order)
