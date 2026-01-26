from __future__ import annotations
from decimal import Decimal
from datetime import datetime
from pydantic import Field
from .common import DefaultModel, Pagination
from ..models.enums import OrderStatus, FulfillmentType, PickedStatus

class OrderItemResponse(DefaultModel):
    id: int
    product_id: int
    name: str
    sku: str
    unit_price: Decimal
    quantity: int
    picked_status: PickedStatus

class OrderResponse(DefaultModel):
    id: int
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
    order_id: int
    canceled_at: datetime
    status: OrderStatus = Field(default=OrderStatus.CANCELED)
