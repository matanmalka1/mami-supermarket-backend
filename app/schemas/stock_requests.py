from __future__ import annotations
from datetime import datetime

from pydantic import Field
from .common import DefaultModel
from ..models.enums import StockRequestStatus, StockRequestType

class StockRequestCreateRequest(DefaultModel):
    branch_id: int
    product_id: int
    quantity: int = Field(gt=0)
    request_type: StockRequestType

class StockRequestReviewRequest(DefaultModel):
    status: StockRequestStatus
    approved_quantity: int | None = None
    rejection_reason: str | None = None

class BulkReviewItem(DefaultModel):
    request_id: int
    status: StockRequestStatus
    approved_quantity: int | None = None
    rejection_reason: str | None = None

class BulkReviewRequest(DefaultModel):
    items: list[BulkReviewItem]

class StockRequestResponse(DefaultModel):
    id: int
    branch_id: int
    branch_name: str | None = None
    product_id: int
    product_name: str | None = None
    product_sku: str | None = None
    quantity: int
    request_type: StockRequestType
    status: StockRequestStatus
    actor_user_id: int
    created_at: datetime
