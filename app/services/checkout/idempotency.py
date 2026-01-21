from __future__ import annotations
import hashlib
import json
from uuid import UUID, uuid4
from sqlalchemy import select
from app.extensions import db
from app.middleware.error_handler import DomainError
from app.models import IdempotencyKey
from app.schemas.checkout import CheckoutConfirmRequest, CheckoutConfirmResponse


class CheckoutIdempotencyManager:
    @staticmethod
    def hash_request(payload: CheckoutConfirmRequest) -> str:
        data = payload.model_dump()
        data.pop("idempotency_key", None)
        return hashlib.sha256(json.dumps(data, sort_keys=True, default=str).encode("utf-8")).hexdigest()

    @staticmethod
    def get_existing(user_id: UUID, key: str, request_hash: str) -> IdempotencyKey | None:
        existing = db.session.execute(
            select(IdempotencyKey).where(
                IdempotencyKey.user_id == user_id,
                IdempotencyKey.key == key,
            )
        ).scalar_one_or_none()
        if not existing:
            return None
        if existing.request_hash != request_hash:
            raise DomainError("IDEMPOTENCY_CONFLICT", "Request payload differs for same Idempotency-Key", status_code=409)
        return existing

    @staticmethod
    def store_response(user_id: UUID, key: str, request_hash: str, response: CheckoutConfirmResponse) -> None:
        record = IdempotencyKey(
            id=uuid4(),
            user_id=user_id,
            key=key,
            request_hash=request_hash,
            response_payload=response.model_dump(),
            status_code=201,
        )
        db.session.add(record)
        db.session.commit()
