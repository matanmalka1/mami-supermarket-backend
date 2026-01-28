from __future__ import annotations

from sqlalchemy import select , func 
from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from ..extensions import db
from ..middleware.error_handler import DomainError
from ..models import Audit

class AuditService:
    @staticmethod
    def _serialize_for_json(value):
        from datetime import time, date, datetime
        if isinstance(value, (time, date, datetime)):
            return value.isoformat()
        if isinstance(value, dict):
            return {k: AuditService._serialize_for_json(v) for k, v in value.items()}
        if isinstance(value, list):
            return [AuditService._serialize_for_json(v) for v in value]
        return value

    @staticmethod
    def log_event(
        *,
        entity_type: str,
        action: str,
        actor_user_id: int | None = None,
        entity_id: int | None = None,
        old_value: dict[str, object] | None = None,
        new_value: dict[str, object] | None = None,
        context: dict[str, object] | None = None,
    ) -> Audit:
        if entity_id is None:
            raise DomainError(
                "MISSING_ENTITY_ID",
                "Entity ID is required for audit records",
                status_code=500,
            )
        resolved_entity_id = entity_id
        session: Session = db.session
        entry = Audit(
            entity_type=entity_type,
            action=action,
            actor_user_id=actor_user_id,
            entity_id=resolved_entity_id,
            old_value=AuditService._serialize_for_json(old_value) if old_value else None,
            new_value=AuditService._serialize_for_json(new_value) if new_value else None,
            context=AuditService._serialize_for_json(context) if context else None,
            created_at=datetime.utcnow(),
        )
        session.add(entry)
        session.flush()
        return entry

class AuditQueryService:
    @staticmethod
    def list_logs(filters: dict, limit: int, offset: int) -> tuple[list[dict], int]:
        stmt = select(Audit).options(selectinload(Audit.actor)).order_by(Audit.created_at.desc())
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
        total = db.session.scalar(select(func.count()).select_from(stmt.subquery()))
        rows = db.session.execute(stmt.offset(offset).limit(limit)).scalars().all()
        return [AuditQueryService._to_dict(row) for row in rows], total or 0

    @staticmethod
    def _to_dict(row: Audit) -> dict:
        return {
            "id": row.id,
            "entity_type": row.entity_type,
            "entity_id": row.entity_id,
            "action": row.action,
            "old_value": row.old_value,
            "new_value": row.new_value,
            "context": row.context,
            "actor_user_id": row.actor_user_id,
            "actor_email": row.actor.email if row.actor else None,
            "created_at": row.created_at,
        }
