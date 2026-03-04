from __future__ import annotations

from sqlalchemy import select , func 
from datetime import datetime, timezone
from sqlalchemy.orm import selectinload
from sqlalchemy.orm import Session

from ..extensions import db
from ..models import Audit

from app.services.shared_queries import SharedOperations

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

        resolved_entity_id = entity_id or actor_user_id or 0
        session: Session = db.session
        entry = Audit(
            entity_type=entity_type,
            action=action,
            actor_user_id=actor_user_id,
            entity_id=resolved_entity_id,
            old_value=AuditService._serialize_for_json(old_value) if old_value else None,
            new_value=AuditService._serialize_for_json(new_value) if new_value else None,
            context=AuditService._serialize_for_json(context) if context else None,
            created_at=datetime.now(timezone.utc),
        )
        session.add(entry)
        session.flush()  # Flush but let caller commit
        return entry

class AuditQueryService:
    @staticmethod
    def list_logs(filters: dict, limit: int, offset: int) -> tuple[list[dict], int]:
        from app.services.shared_queries import SharedOperations
        
        stmt = select(Audit).options(selectinload(Audit.actor)).order_by(Audit.created_at.desc())
        
        # Build conditions for filtering
        conditions = {
            "entity_type": (
                lambda: bool(filters.get("entity_type")),
                Audit.entity_type == filters["entity_type"] if filters.get("entity_type") else None,
            ),
            "action": (
                lambda: bool(filters.get("action")),
                Audit.action == filters["action"] if filters.get("action") else None,
            ),
            "actor_user_id": (
                lambda: filters.get("actor_user_id") is not None,
                Audit.actor_user_id == filters["actor_user_id"] if filters.get("actor_user_id") is not None else None,
            ),
            "date_from": (
                lambda: filters.get("date_from") is not None,
                Audit.created_at >= filters["date_from"] if filters.get("date_from") is not None else None,
            ),
            "date_to": (
                lambda: filters.get("date_to") is not None,
                Audit.created_at <= filters["date_to"] if filters.get("date_to") is not None else None,
            ),
        }
        
        stmt = SharedOperations.build_filtered_query(stmt, conditions)
        
        def transform(row):
            return AuditQueryService._to_dict(row)
        
        rows, total = SharedOperations.paginate_query(
            base_query=stmt,
            model_class=Audit,
            limit=limit,
            offset=offset,
            transform_fn=transform,
        )
        return rows, total

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
