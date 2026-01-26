from __future__ import annotations

from sqlalchemy import Column, String, TIMESTAMP, Boolean, Integer
from .base import Base, TimestampMixin

class RegistrationOTP(Base, TimestampMixin):
    __tablename__ = "registration_otps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(320), nullable=False, index=True)
    code_hash = Column(String(64), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=False), nullable=False)
    is_used = Column(Boolean, nullable=False, server_default="false")
