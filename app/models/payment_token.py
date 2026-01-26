from __future__ import annotations
from sqlalchemy import Boolean, Column, ForeignKey, JSON, String, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class PaymentToken(Base, TimestampMixin):
    __tablename__ = "payment_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    provider = Column(String(64), nullable=False)
    token = Column(String(512), nullable=False)
    is_default = Column(Boolean, nullable=False, server_default="false")
    metadata_payload = Column("metadata", JSON, nullable=True)

    user = relationship("User", back_populates="payment_tokens")
