"""Internal helpers for address operations."""

from __future__ import annotations
from typing import Any

from sqlalchemy.exc import IntegrityError

from ....extensions import db
from ....middleware.error_handler import DomainError
from ....models import Address
from ...audit_service import AuditService

ENTITY_TYPE = "address"

def fetch_address(user_id: int, address_id: int) -> Address:
    address = db.session.query(Address).filter_by(id=address_id, user_id=user_id).first()
    if not address:
        raise DomainError("ADDRESS_NOT_FOUND", "Address not found", status_code=404)
    return address

def commit_with_audit(
    user_id: int,
    entity_id: int,
    action: str,
    error_message: str,
    **log_kwargs: Any,
) -> None:
    try:
        db.session.commit()
        AuditService.log_event(
            entity_type=ENTITY_TYPE,
            action=action,
            actor_user_id=user_id,
            entity_id=entity_id,
            **log_kwargs,
        )
    except IntegrityError as exc:
        db.session.rollback()
        raise DomainError("DATABASE_ERROR", error_message, details={"error": str(exc)})


def update_field(
    address: Address,
    payload: Any,
    field: str,
    old_values: dict[str, Any],
    new_values: dict[str, Any],
) -> None:
    value = getattr(payload, field)
    if value is None:
        return
    old_values[field] = getattr(address, field)
    setattr(address, field, value)
    new_values[field] = value
