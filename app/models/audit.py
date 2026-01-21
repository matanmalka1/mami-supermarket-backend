from __future__ import annotations

import uuid

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, ForeignKey, JSON, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base

class Audit(Base):
    __tablename__ = "audit"
    __table_args__ = (UniqueConstraint("id", name="pk_audit"),)

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, nullable=False, server_default=sa.func.now())

    actor = relationship("User")
