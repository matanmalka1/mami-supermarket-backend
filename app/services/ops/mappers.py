from __future__ import annotations
from app.models import Order
from app.models.enums import OrderStatus, PickedStatus
from app.schemas.ops import OpsOrderResponse
from app.schemas.orders import OrderItemResponse, OrderResponse


def to_ops_response(order: Order) -> OpsOrderResponse:
    pending_count = sum(1 for item in order.items if item.picked_status != PickedStatus.PICKED)
    urgency_rank = urgency_rank_for_order(order)
    return OpsOrderResponse(
        order_id=order.id,
        order_number=order.order_number,
        status=order.status,
        urgency_rank=urgency_rank,
        created_at=order.created_at,
        items_pending=pending_count,
    )


def to_detail(order: Order) -> OrderResponse:
    items = [
        OrderItemResponse(
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


def urgency_rank_for_order(order: Order) -> int:
    if order.delivery and order.delivery.delivery_slot:
        start = order.delivery.delivery_slot.start_time
        return (start.hour * 60 + start.minute) if start else 24 * 60
    return 24 * 60
