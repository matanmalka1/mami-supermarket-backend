from __future__ import annotations
from uuid import UUID, uuid4
import sqlalchemy as sa
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import Inventory, StockRequest
from app.models.enums import StockRequestStatus
from app.schemas.stock_requests import StockRequestCreateRequest, StockRequestResponse
from app.services.audit_service import AuditService
from .mappers import to_response


class StockRequestEmployeeService:
    @staticmethod
    def create_request(user_id: UUID, payload: StockRequestCreateRequest) -> StockRequestResponse:
        inventory = db.session.execute(
            sa.select(Inventory)
            .where(Inventory.branch_id == payload.branch_id)
            .where(Inventory.product_id == payload.product_id)
        ).scalar_one_or_none()
        if not inventory:
            raise DomainError("NOT_FOUND", "Inventory row not found for branch/product", status_code=404)
        request = StockRequest(
            id=uuid4(),
            branch_id=payload.branch_id,
            product_id=payload.product_id,
            quantity=payload.quantity,
            request_type=payload.request_type,
            status=StockRequestStatus.PENDING,
            actor_user_id=user_id,
        )
        db.session.add(request)
        db.session.commit()
        AuditService.log_event(
            entity_type="stock_request",
            action="CREATE",
            actor_user_id=user_id,
            entity_id=request.id,
            new_value={
                "branch_id": str(payload.branch_id),
                "product_id": str(payload.product_id),
                "quantity": payload.quantity,
                "request_type": payload.request_type.value,
            },
        )
        return to_response(request)

    @staticmethod
    def list_my(user_id: UUID, limit: int, offset: int) -> tuple[list[StockRequestResponse], int]:
        stmt = (
            sa.select(StockRequest)
            .where(StockRequest.actor_user_id == user_id)
            .order_by(StockRequest.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        total = db.session.scalar(
            sa.select(sa.func.count()).select_from(StockRequest).where(StockRequest.actor_user_id == user_id)
        )
        rows = db.session.execute(stmt).scalars().all()
        return [to_response(row) for row in rows], total or 0
