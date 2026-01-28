# seed/seed_idempotency_keys.py
from __future__ import annotations

import hashlib
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.idempotency_key import IdempotencyKey 
from app.models.user import User


def _hash_payload(payload: dict) -> str:
    raw = str(sorted(payload.items())).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _ensure_idempotency_key(
    session: Session,
    *,
    user_id,
    key: str,
    request_hash: str,
    response_payload: dict | None,
    status_code: int | None,
) -> IdempotencyKey:
    existing = session.execute(
        select(IdempotencyKey).where(
            IdempotencyKey.user_id == user_id,
            IdempotencyKey.key == key,
            IdempotencyKey.request_hash == request_hash,
        )
    ).scalar_one_or_none()

    if existing:
        updated = False
        if existing.response_payload != response_payload:
            existing.response_payload = response_payload
            updated = True
        if existing.status_code != status_code:
            existing.status_code = status_code
            updated = True
        if updated:
            session.add(existing)
        return existing

    ik = IdempotencyKey(
        user_id=user_id,
        key=key,
        request_hash=request_hash,
        response_payload=response_payload,
        status_code=status_code,
    )
    session.add(ik)
    return ik


def seed_idempotency_keys(session: Session) -> list[IdempotencyKey]:
    users = session.execute(select(User)).scalars().all()
    if not users:
        raise RuntimeError("No users found. Seed users first.")

    created: list[IdempotencyKey] = []

    for u in users:
        payload1 = {"action": "create_order", "cart": "active", "currency": "ILS"}
        created.append(
            _ensure_idempotency_key(
                session,
                user_id=u.id,
                key=f"idem_{u.id}_1",
                request_hash=_hash_payload(payload1),
                response_payload={"ok": True, "orderId": None},
                status_code=201,
            )
        )

        payload2 = {"action": "add_to_cart", "sku": "PAN-RICE-1KG", "qty": 2}
        created.append(
            _ensure_idempotency_key(
                session,
                user_id=u.id,
                key=f"idem_{u.id}_2",
                request_hash=_hash_payload(payload2),
                response_payload={"ok": True},
                status_code=200,
            )
        )

    session.flush()
    return created