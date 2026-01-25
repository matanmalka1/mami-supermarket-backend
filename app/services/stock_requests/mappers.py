from __future__ import annotations
from app.models import StockRequest
from app.schemas.stock_requests import StockRequestResponse


def to_response(row: StockRequest) -> StockRequestResponse:
    return StockRequestResponse(
        id=row.id,
        branch_id=row.branch_id,
        branch_name=getattr(row.branch, "name", None),
        product_id=row.product_id,
        product_name=getattr(row.product, "name", None),
        product_sku=getattr(row.product, "sku", None),
        quantity=row.quantity,
        request_type=row.request_type,
        status=row.status,
        actor_user_id=row.actor_user_id,
        created_at=row.created_at,
    )
