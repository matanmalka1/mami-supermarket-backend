from __future__ import annotations

from datetime import datetime
from sqlalchemy import select ,func
from sqlalchemy.orm import selectinload

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Order, OrderDeliveryDetails
from app.schemas.ops import OpsOrderResponse
from app.schemas.orders import OrderResponse
from .mappers import to_detail, to_ops_response


class OpsOrderQueryService:
    @staticmethod
    def list_orders(
        status,
        date_from: datetime | None,
        date_to: datetime | None,
        limit: int,
        offset: int,
    ) -> tuple[list[OpsOrderResponse], int]:
        base = select(Order)
        stmt = base.options(
            selectinload(Order.items),
            selectinload(Order.user),
            selectinload(Order.delivery).selectinload(OrderDeliveryDetails.delivery_slot),
        )
        if status:
            base = base.where(Order.status == status)
            stmt = stmt.where(Order.status == status)
        if date_from:
            base = base.where(Order.created_at >= date_from)
            stmt = stmt.where(Order.created_at >= date_from)
        if date_to:
            base = base.where(Order.created_at <= date_to)
            stmt = stmt.where(Order.created_at <= date_to)
        stmt = stmt.order_by(Order.created_at.asc())
        total = db.session.scalar(select(func.count()).select_from(base.subquery()))
        rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        responses = [to_ops_response(order) for order in rows]
        responses.sort(key=lambda o: o.urgency_rank)
        return responses, total or 0

    @staticmethod
    def get_order(order_id: int) -> OrderResponse:
        order = OpsOrderQueryService._load_order(order_id)
        return to_detail(order)

    @staticmethod
    def _load_order(order_id: int) -> Order:
        order = db.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.delivery).selectinload(OrderDeliveryDetails.delivery_slot),
            )
        ).scalar_one_or_none()
        if not order:
            raise DomainError("NOT_FOUND", "Order not found", status_code=404)
        return order
