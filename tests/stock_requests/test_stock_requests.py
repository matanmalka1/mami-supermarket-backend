import pytest
from sqlalchemy import select ,func

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Audit, StockRequest
from app.models.enums import StockRequestStatus, StockRequestType
from app.schemas.stock_requests import BulkReviewItem, BulkReviewRequest
from app.services.stock_requests import StockRequestReviewService


def test_bulk_review_partial_success(session, users, product_with_inventory):
    user, _ = users
    product, inv, _ = product_with_inventory
    req = StockRequest(
        branch_id=inv.branch_id,
        product_id=product.id,
        quantity=1,
        request_type=StockRequestType.ADD_QUANTITY,
        status=StockRequestStatus.PENDING,
        actor_user_id=user.id,
    )
    session.add(req)
    session.commit()
    payload = BulkReviewRequest(
        items=[
            BulkReviewItem(request_id=req.id, status=StockRequestStatus.APPROVED, approved_quantity=2),
            BulkReviewItem(request_id=9999, status=StockRequestStatus.APPROVED, approved_quantity=2),
        ]
    )
    results = StockRequestReviewService.bulk_review(payload, user.id)
    assert any(r["result"] == "ok" for r in results)
    assert any(r["result"] == "error" for r in results)


def test_no_audit_on_failed_review(session, users):
    user, _ = users
    with pytest.raises(DomainError):
        StockRequestReviewService.review(
            request_id=9999,
            status=StockRequestStatus.APPROVED,
            approved_quantity=1,
            rejection_reason=None,
            actor_id=user.id,
        )
    audits = db.session.execute(select(func.count()).select_from(Audit)).scalar()
    assert audits == 0
