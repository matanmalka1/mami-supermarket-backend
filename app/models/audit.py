from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String
from sqlalchemy.orm import relationship

from .base import Base

class Audit(Base):
    __tablename__ = "audit"

    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(Integer, nullable=False, index=True)

    action = Column(String(64), nullable=False, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)

    actor_user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=True)

    created_at = Column(DateTime, nullable=False, server_default=sa.func.now())

    actor = relationship("User")