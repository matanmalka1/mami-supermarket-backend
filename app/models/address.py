from __future__ import annotations

from sqlalchemy import Boolean, Column, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin

class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    address_line = Column(String(256), nullable=False)
    city = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    postal_code = Column(String(16), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    is_default = Column(Boolean, nullable=False, server_default="false")

    user = relationship("User", back_populates="addresses")