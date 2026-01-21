from __future__ import annotations

import uuid

from sqlalchemy import Column, ForeignKey, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .enums import Role

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(
        SQLEnum(Role, name="role_enum"),
        nullable=False,
        server_default=Role.CUSTOMER.value,
    )
    default_branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"))

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    payment_tokens = relationship(
        "PaymentToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
