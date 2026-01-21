from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, JSON
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin

class IdempotencyKey(Base, TimestampMixin):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "key", "request_hash", name="uq_idempotency_key_hash"),
        Index("ix_idempotency_key", "key"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key = Column(String(128), nullable=False)
    request_hash = Column(String(256), nullable=False)
    response_payload = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=sa.func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )
