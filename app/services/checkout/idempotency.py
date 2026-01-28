from __future__ import annotations

import hashlib
import json
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import IdempotencyKey
from app.models.enums import IdempotencyStatus
from app.schemas.checkout import CheckoutConfirmRequest, CheckoutConfirmResponse

class CheckoutIdempotencyManager:
    @staticmethod
    def hash_request(payload: CheckoutConfirmRequest) -> str:
        """Hash the critical request payload fields."""
        data = payload.model_dump()
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    @staticmethod
    def get_or_create_in_progress(user_id: int, key: str, request_hash: str) -> tuple[IdempotencyKey, bool]:
        existing = CheckoutIdempotencyManager._lock_existing(user_id, key)
        if existing:
            return CheckoutIdempotencyManager._handle_existing(existing, request_hash)

        record = IdempotencyKey(
            user_id=user_id,
            key=key,
            request_hash=request_hash,
            status=IdempotencyStatus.IN_PROGRESS,
        )
        db.session.add(record)
        try:
            db.session.flush()
            return record, True
        except IntegrityError:
            db.session.rollback()
            existing = CheckoutIdempotencyManager._lock_existing(user_id, key)
            if not existing:
                raise
            return CheckoutIdempotencyManager._handle_existing(existing, request_hash)

    @staticmethod
    def _lock_existing(user_id: int, key: str) -> IdempotencyKey | None:
        return db.session.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.key == key,
            ).with_for_update()
        ).scalar_one_or_none()

    @staticmethod
    def _handle_existing(existing: IdempotencyKey, request_hash: str) -> tuple[IdempotencyKey, bool]:
        if existing.request_hash != request_hash:
            raise DomainError(
                "IDEMPOTENCY_KEY_REUSE_MISMATCH",
                "Same Idempotency-Key used with different request payload",
                status_code=409,
            )
        if existing.status == IdempotencyStatus.IN_PROGRESS:
            raise DomainError(
                "IDEMPOTENCY_IN_PROGRESS",
                "This request is already being processed",
                status_code=409,
            )
        return existing, False

    @staticmethod
    def mark_succeeded(record: IdempotencyKey, response: CheckoutConfirmResponse, order_id: int) -> None:
        """Mark idempotency record as succeeded with response."""
        record.status = IdempotencyStatus.SUCCEEDED
        record.response_payload = response.model_dump()
        record.status_code = 201
        record.order_id = order_id
        db.session.flush()

    @staticmethod
    def mark_failed(record: IdempotencyKey) -> None:
        """Mark idempotency record as failed."""
        record.status = IdempotencyStatus.FAILED
        db.session.flush()
