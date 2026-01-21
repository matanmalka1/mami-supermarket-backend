from __future__ import annotations
from datetime import datetime
from uuid import UUID
from pydantic import Field
from .common import DefaultModel
from ..models.enums import StockRequestStatus, StockRequestType

class StockRequestCreateRequest(DefaultModel):
    branch_id: UUID
    product_id: UUID
    quantity: int = Field(gt=0)
    request_type: StockRequestType

class StockRequestReviewRequest(DefaultModel):
    status: StockRequestStatus
    approved_quantity: int | None = None
    rejection_reason: str | None = None

class BulkReviewItem(DefaultModel):
    request_id: UUID
    status: StockRequestStatus
    approved_quantity: int | None = None
    rejection_reason: str | None = None

class BulkReviewRequest(DefaultModel):
    items: list[BulkReviewItem]

class StockRequestResponse(DefaultModel):
    id: UUID
    branch_id: UUID
    product_id: UUID
    quantity: int
    request_type: StockRequestType
    status: StockRequestStatus
    actor_user_id: UUID
    created_at: datetime
