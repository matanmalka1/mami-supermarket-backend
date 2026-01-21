from __future__ import annotations
from datetime import datetime
from uuid import UUID
from .common import DefaultModel

class AuditQuery(DefaultModel):
    entity_type: str | None = None
    action: str | None = None
    actor_user_id: UUID | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    limit: int = 50
    offset: int = 0

class AuditResponse(DefaultModel):
    id: UUID
    entity_type: str
    entity_id: UUID
    action: str
    old_value: dict[str, object] | None
    new_value: dict[str, object] | None
    context: dict[str, object] | None
    actor_user_id: UUID | None
    created_at: datetime
