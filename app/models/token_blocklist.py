from __future__ import annotations

from sqlalchemy import Column, DateTime, Index, Integer, String

from .base import Base


class TokenBlocklist(Base):
    """Stores JTI (JWT ID) of revoked tokens."""

    __tablename__ = "token_blocklist"
    __table_args__ = (Index("ix_token_blocklist_jti", "jti", unique=True),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    jti = Column(String(36), nullable=False)
    revoked_at = Column(DateTime, nullable=False)
