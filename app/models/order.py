from __future__ import annotations

from sqlalchemy import (
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Numeric,
    String,
    Integer,
)
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .enums import FulfillmentType, OrderStatus, PickedStatus

class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_number = Column(String(32), nullable=False, unique=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    fulfillment_type = Column(SQLEnum(FulfillmentType, name="fulfillment_type"), nullable=False)
    status = Column(
        SQLEnum(OrderStatus, name="order_status"),
        nullable=False,
        server_default=OrderStatus.CREATED.value,
    )
    branch_id = Column(Integer, ForeignKey("branches.id"))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship(
        "OrderDeliveryDetails",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )
    pickup = relationship(
        "OrderPickupDetails",
        back_populates="order",
        uselist=False,
        cascade="all, delete-orphan",
    )

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, nullable=False)
    name = Column(String(128), nullable=False)
    sku = Column(String(64), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    picked_status = Column(
        SQLEnum(PickedStatus, name="picked_status"),
        nullable=False,
        server_default=PickedStatus.PENDING.value,
    )

    order = relationship("Order", back_populates="items")

class OrderDeliveryDetails(Base):
    __tablename__ = "order_delivery_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    delivery_slot_id = Column(Integer, ForeignKey("delivery_slots.id"))
    address = Column(String(256), nullable=False)
    slot_start = Column(DateTime, nullable=True)
    slot_end = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="delivery")
    delivery_slot = relationship("DeliverySlot")

class OrderPickupDetails(Base):
    __tablename__ = "order_pickup_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    pickup_window_start = Column(DateTime, nullable=False)
    pickup_window_end = Column(DateTime, nullable=False)

    order = relationship("Order", back_populates="pickup")
    branch = relationship("Branch")
