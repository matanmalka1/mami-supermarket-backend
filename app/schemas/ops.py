from __future__ import annotations
from datetime import datetime

from pydantic import Field
from typing import Optional
from .common import DefaultModel
from ..models.enums import OrderStatus, PickedStatus

class OpsOrdersQuery(DefaultModel):
    status: OrderStatus | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)

class OpsOrderResponse(DefaultModel):
    order_id: int
    order_number: str
    status: OrderStatus
    urgency_rank: int
    created_at: datetime
    items_pending: int
    customer_name: str | None = None
    items_summary: str | None = None

class UpdatePickStatusRequest(DefaultModel):
    picked_status: PickedStatus

class UpdateOrderStatusRequest(DefaultModel):
    status: OrderStatus


class DamageReportRequest(DefaultModel):
    reason: str = Field(min_length=1, max_length=256)
    notes: str | None = Field(None, max_length=512)

class OpsStockRequestsQuery(DefaultModel):
    branch_id: Optional[int] = None
    status: Optional[str] = None
    limit: int = Field(default=50, ge=1, le=200)
    offset: int = Field(default=0, ge=0)
