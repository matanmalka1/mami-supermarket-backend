from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import Column, DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, JSON, String, UniqueConstraint

from .base import Base, TimestampMixin
from .enums import IdempotencyStatus


class IdempotencyKey(Base, TimestampMixin):
    __tablename__ = "idempotency_keys"
    __table_args__ = (
        UniqueConstraint("user_id", "key", name="uq_user_idempotency_key"),
        Index("ix_idempotency_key", "key"),
        Index("ix_idempotency_expires_at", "expires_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    key = Column(String(128), nullable=False)
    request_hash = Column(String(256), nullable=False)
    status = Column(
        SQLEnum(IdempotencyStatus, name="idempotency_status"),
        nullable=False,
        default=IdempotencyStatus.IN_PROGRESS,
    )
    response_payload = Column(JSON, nullable=True)
    status_code = Column(Integer, nullable=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    expires_at = Column(DateTime, nullable=False)

    def __init__(self, **kwargs):
        if "expires_at" not in kwargs:
            kwargs["expires_at"] = datetime.utcnow() + timedelta(hours=24)
        super().__init__(**kwargs)
