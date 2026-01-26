from __future__ import annotations

from sqlalchemy import Column, ForeignKey, String, Enum as SQLEnum, Integer
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .enums import Role

class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    phone = Column(String(32), nullable=True)
    password_hash = Column(String(256), nullable=False)
    role = Column(
        SQLEnum(Role, name="role_enum"),
        nullable=False,
        server_default=Role.CUSTOMER.value,
    )
    membership_tier = Column(String(32), nullable=False, server_default="FREE")
    default_branch_id = Column(Integer, ForeignKey("branches.id"))

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    payment_tokens = relationship(
        "PaymentToken",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    wishlist_items = relationship(
        "WishlistItem",
        back_populates="user",
        cascade="all, delete-orphan",
    )
