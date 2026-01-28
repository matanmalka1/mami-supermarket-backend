from __future__ import annotations
import sqlalchemy as sa
from sqlalchemy import Boolean, Column, ForeignKey, JSON, String, Integer
from sqlalchemy.orm import relationship
from .base import Base, TimestampMixin

class PaymentToken(Base, TimestampMixin):
    __tablename__ = "payment_tokens"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    provider = Column(String(32), nullable=False)          # stripe / tranzila
    provider_token = Column(String(128), nullable=False)   # token 

    brand = Column(String(32), nullable=True)
    last4 = Column(String(4), nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)

    is_default = Column(Boolean, nullable=False, server_default=sa.text("false"))
    is_active = Column(Boolean, nullable=False, server_default=sa.text("true"))

    user = relationship("User", back_populates="payment_tokens")
