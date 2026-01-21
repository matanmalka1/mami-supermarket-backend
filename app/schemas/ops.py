from __future__ import annotations
from datetime import date, datetime
from uuid import UUID
from pydantic import Field
from .common import DefaultModel
from ..models.enums import OrderStatus, PickedStatus

class OpsOrdersQuery(DefaultModel):
    status: OrderStatus | None = None
    date_from: date | None = None
    date_to: date | None = None
    limit: int = Field(default=25, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class OpsOrderResponse(DefaultModel):
    order_id: UUID
    order_number: str
    status: OrderStatus
    urgency_rank: int
    created_at: datetime
    items_pending: int

class UpdatePickStatusRequest(DefaultModel):
    picked_status: PickedStatus

class UpdateOrderStatusRequest(DefaultModel):
    status: OrderStatus
