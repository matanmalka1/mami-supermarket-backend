from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from pydantic import Field
from .common import DefaultModel, Pagination
from ..models.enums import OrderStatus, FulfillmentType, PickedStatus

class OrderItemResponse(DefaultModel):
    product_id: UUID
    name: str
    sku: str
    unit_price: Decimal
    quantity: int
    picked_status: PickedStatus

class OrderResponse(DefaultModel):
    id: UUID
    order_number: str
    total_amount: Decimal
    status: OrderStatus
    fulfillment_type: FulfillmentType
    created_at: datetime
    items: list[OrderItemResponse]

class OrderListResponse(DefaultModel):
    orders: list[OrderResponse]
    pagination: Pagination

class CancelOrderResponse(DefaultModel):
    order_id: UUID
    canceled_at: datetime
    status: OrderStatus = Field(default=OrderStatus.CANCELED)
