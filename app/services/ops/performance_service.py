from __future__ import annotations
from datetime import datetime, timedelta

import sqlalchemy as sa
from app.extensions import db
from app.models import Audit, Order, OrderItem
from app.models.enums import OrderStatus, PickedStatus


class OpsPerformanceService:
    """Aggregates live metrics for the ops dashboard."""

    RECENT_PICKER_WINDOW_MINUTES = 5

    @staticmethod
    def compute_metrics() -> dict[str, float | int]:
        session = db.session
        total_items = session.scalar(
            sa.select(sa.func.count()).select_from(OrderItem),
        ) or 0
        picked_items = session.scalar(
            sa.select(sa.func.count())
            .select_from(OrderItem)
            .where(OrderItem.picked_status == PickedStatus.PICKED),
        ) or 0
        efficiency = (
            round((picked_items / total_items) * 100, 2) if total_items > 0 else 0
        )

        active_statuses = [OrderStatus.CREATED, OrderStatus.IN_PROGRESS]
        active_orders = session.scalar(
            sa.select(sa.func.count()).select_from(Order).where(
                Order.status.in_(active_statuses),
            ),
        ) or 0
        total_orders = session.scalar(
            sa.select(sa.func.count()).select_from(Order),
        ) or 0

        window_start = datetime.utcnow() - timedelta(
            minutes=OpsPerformanceService.RECENT_PICKER_WINDOW_MINUTES,
        )
        live_picker_count = session.scalar(
            sa.select(sa.func.count(sa.distinct(Audit.actor_user_id)))
            .where(
                Audit.entity_type == "order_item",
                Audit.action == "UPDATE_PICK_STATUS",
                Audit.actor_user_id.isnot(None),
                Audit.created_at >= window_start,
            ),
        ) or 0

        return {
            "batchEfficiency": efficiency,
            "livePickers": live_picker_count,
            "activeOrders": active_orders,
            "totalOrders": total_orders,
            "pickedItems": picked_items,
            "totalItems": total_items,
            "pickerWindowMinutes": OpsPerformanceService.RECENT_PICKER_WINDOW_MINUTES,
        }
