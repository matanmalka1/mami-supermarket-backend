import sqlalchemy as sa
from app.extensions import db
from app.models import StockRequest
from app.schemas.stock_requests import StockRequestResponse
from .mappers import to_response

def list_ops(branch_id: int | None, status: str | None, limit: int, offset: int) -> tuple[list[StockRequestResponse], int]:
    stmt = sa.select(StockRequest).order_by(StockRequest.created_at.desc())
    if branch_id:
        stmt = stmt.where(StockRequest.branch_id == branch_id)
    if status:
        stmt = stmt.where(StockRequest.status == status)
    total = db.session.scalar(sa.select(sa.func.count()).select_from(stmt.subquery()))
    rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
    return [to_response(row) for row in rows], total or 0
