from __future__ import annotations
from datetime import datetime
from uuid import UUID, uuid4
import sqlalchemy as sa
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session
from ..extensions import db
from ..models import Audit

class AuditService:
    @staticmethod
    def log_event(
        *,
        entity_type: str,
        action: str,
        actor_user_id: UUID | None = None,
        entity_id: UUID | None = None,
        old_value: dict[str, object] | None = None,
        new_value: dict[str, object] | None = None,
        context: dict[str, object] | None = None,
    ) -> Audit:
        session: Session = db.session
        entry = Audit(
            id=uuid4(),
            entity_type=entity_type,
            action=action,
            actor_user_id=actor_user_id,
            entity_id=entity_id,
            old_value=old_value,
            new_value=new_value,
            context=context,
            created_at=datetime.utcnow(),
        )
        session.add(entry)
        session.flush()
        return entry

class AuditQueryService:
    @staticmethod
    def list_logs(filters: dict, limit: int, offset: int) -> tuple[list[dict], int]:
        stmt = sa.select(Audit).options(selectinload(Audit.actor)).order_by(Audit.created_at.desc())
        if filters.get("entity_type"):
            stmt = stmt.where(Audit.entity_type == filters["entity_type"])
        if filters.get("action"):
            stmt = stmt.where(Audit.action == filters["action"])
        if filters.get("actor_user_id"):
            stmt = stmt.where(Audit.actor_user_id == filters["actor_user_id"])
        if filters.get("date_from"):
            stmt = stmt.where(Audit.created_at >= filters["date_from"])
        if filters.get("date_to"):
            stmt = stmt.where(Audit.created_at <= filters["date_to"])
        total = db.session.scalar(sa.select(sa.func.count()).select_from(stmt.subquery()))
        rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return [AuditQueryService._to_dict(row) for row in rows], total or 0

    @staticmethod
    def _to_dict(row: Audit) -> dict:
        return {
            "id": row.id,
            "entity_type": row.entity_type,
            "entity_id": str(row.entity_id),
            "action": row.action,
            "old_value": row.old_value,
            "new_value": row.new_value,
            "context": row.context,
            "actor_user_id": str(row.actor_user_id) if row.actor_user_id else None,
            "actor_email": row.actor.email if row.actor else None,
            "created_at": row.created_at,
        }
