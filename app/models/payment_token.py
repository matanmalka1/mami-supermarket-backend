from __future__ import annotations
import uuid
from sqlalchemy import Boolean, Column, ForeignKey, JSON, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class PaymentToken(Base, TimestampMixin):
    __tablename__ = "payment_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(64), nullable=False)
    token = Column(String(512), nullable=False)
    is_default = Column(Boolean, nullable=False, server_default="false")
    metadata_payload = Column("metadata", JSON, nullable=True)

    user = relationship("User", back_populates="payment_tokens")
