from __future__ import annotations

import uuid

from sqlalchemy import Column, String, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID

from .base import Base, TimestampMixin

class RegistrationOTP(Base, TimestampMixin):
    __tablename__ = "registration_otps"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=False), nullable=False)
    is_used = Column(Boolean, nullable=False, server_default="false")
