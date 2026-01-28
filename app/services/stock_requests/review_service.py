from __future__ import annotations
from sqlalchemy import select ,func
from sqlalchemy.orm import selectinload
from flask import current_app
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import StockRequest
from app.models.enums import StockRequestStatus
from app.schemas.stock_requests import BulkReviewRequest, StockRequestResponse
from app.services.audit_service import AuditService
from .apply import apply_inventory_change
from .mappers import to_response


class StockRequestReviewService:
    @staticmethod
    def list_admin(status: StockRequestStatus | None, limit: int, offset: int) -> tuple[list[StockRequestResponse], int]:
        stmt = select(StockRequest).order_by(StockRequest.created_at.desc())
        if status:
            stmt = stmt.where(StockRequest.status == status)
        total = db.session.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return [to_response(row) for row in rows], total or 0

    @staticmethod
    def get_request(request_id: int) -> StockRequestResponse:
        """Get detailed stock request information."""
        stock_request = db.session.execute(
            select(StockRequest)
            .where(StockRequest.id == request_id)
            .options(selectinload(StockRequest.branch), selectinload(StockRequest.product))
        ).scalar_one_or_none()
        
        if not stock_request:
            raise DomainError("STOCK_REQUEST_NOT_FOUND", "Stock request not found", status_code=404)
        
        return to_response(stock_request)

    @staticmethod
    def review(
        request_id: int,
        status: StockRequestStatus,
        approved_quantity: int | None,
        rejection_reason: str | None,
        actor_id: int,
    ) -> StockRequestResponse:
        session = db.session
        stock_request = session.execute(
            select(StockRequest)
            .where(StockRequest.id == request_id)
            .options(selectinload(StockRequest.branch), selectinload(StockRequest.product))
            .with_for_update()
        ).scalar_one_or_none()
        if not stock_request:
            raise DomainError("NOT_FOUND", "Stock request not found", status_code=404)
        if stock_request.status != StockRequestStatus.PENDING:
            raise DomainError("INVALID_STATUS", "Stock request already reviewed", status_code=409)

        if status == StockRequestStatus.APPROVED:
            if approved_quantity is None or approved_quantity <= 0:
                raise DomainError("INVALID_QUANTITY", "Approved quantity must be positive", status_code=400)
            apply_inventory_change(
                stock_request.branch_id,
                stock_request.product_id,
                stock_request.request_type,
                approved_quantity,
                actor_id,
            )
            stock_request.quantity = approved_quantity
        elif status == StockRequestStatus.REJECTED:
            if not rejection_reason:
                raise DomainError("INVALID_REJECTION", "Rejection reason is required", status_code=400)
        stock_request.status = status
        session.add(stock_request)
        session.commit()
        AuditService.log_event(
            entity_type="stock_request",
            action="REVIEW",
            actor_user_id=actor_id,
            entity_id=stock_request.id,
            old_value={"status": StockRequestStatus.PENDING.value},
            new_value={"status": status.value, "approved_quantity": stock_request.quantity, "rejection_reason": rejection_reason},
        )
        return to_response(stock_request)

    @staticmethod
    def bulk_review(payload: BulkReviewRequest, actor_id: int) -> list[dict]:
        results: list[dict] = []
        for item in payload.items:
            try:
                res = StockRequestReviewService.review(
                    item.request_id,
                    item.status,
                    item.approved_quantity,
                    item.rejection_reason,
                    actor_id,
                )
                results.append({"request_id": item.request_id, "status": res.status, "result": "ok"})
            except DomainError as exc:
                db.session.rollback()
                results.append(
                    {
                        "request_id": item.request_id,
                        "status": None,
                        "result": "error",
                        "error_code": exc.code,
                        "message": exc.message,
                    }
                )
            except Exception as exc:
                db.session.rollback()
                current_app.logger.exception(
                    "Unexpected failure reviewing stock request %s", item.request_id
                )
                results.append(
                    {
                        "request_id": item.request_id,
                        "status": None,
                        "result": "error",
                        "error_code": "INTERNAL_ERROR",
                        "message": str(exc),
                    }
                )
        return results
