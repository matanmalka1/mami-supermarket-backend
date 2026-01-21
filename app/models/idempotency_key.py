from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String, UniqueConstraint, JSON, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin
from .enums import IdempotencyStatus

class IdempotencyKey(Base, TimestampMixin):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_user_idempotency_key"),
        Index("ix_idempotency_key", "key"),
        Index("ix_idempotency_expires_at", "expires_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    key = Column(String(128), nullable=False)
    request_hash = Column(String(256), nullable=False)
    status = Column(SQLEnum(IdempotencyStatus), nullable=False, default=IdempotencyStatus.IN_PROGRESS)
    response_payload = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, nullable=False, server_default=sa.func.now())
    updated_at = Column(
        DateTime,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )

    def __init__(self, **kwargs):
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.utcnow() + timedelta(hours=24)
        super().__init__(**kwargs)
