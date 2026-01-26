from __future__ import annotations

from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Integer, Numeric
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .enums import CartStatus

class Cart(Base, TimestampMixin):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(CartStatus, name="cart_status"),nullable=False,server_default=CartStatus.ACTIVE.value,)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")
