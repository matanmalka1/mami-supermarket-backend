"""Core database models for the backend."""

from __future__ import annotations

import uuid

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLEnum,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
    Time,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin
from .enums import (
    CartStatus,
    FulfillmentType,
    OrderStatus,
    PickedStatus,
    Role,
    StockRequestStatus,
    StockRequestType,
)


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(320), unique=True, nullable=False, index=True)
    full_name = Column(String(128), nullable=False)
    password_hash = Column(String(256), nullable=False)
    role = Column(SQLEnum(Role, name="role_enum"), nullable=False, server_default=Role.CUSTOMER.value)
    default_branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"))

    addresses = relationship("Address", back_populates="user", cascade="all, delete-orphan")
    payment_tokens = relationship("PaymentToken", back_populates="user", cascade="all, delete-orphan")
    carts = relationship("Cart", back_populates="user", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")


class Address(Base, TimestampMixin):
    __tablename__ = "addresses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    address_line = Column(String(256), nullable=False)
    city = Column(String(64), nullable=False)
    country = Column(String(64), nullable=False)
    postal_code = Column(String(16), nullable=False)

    user = relationship("User", back_populates="addresses")


class PaymentToken(Base, TimestampMixin):
    __tablename__ = "payment_tokens"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    provider = Column(String(64), nullable=False)
    token = Column(String(512), nullable=False)
    is_default = Column(Boolean, nullable=False, server_default="false")
    metadata_payload = Column("metadata", JSON, nullable=True)

    user = relationship("User", back_populates="payment_tokens")


class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text, nullable=True)

    products = relationship("Product", back_populates="category")


class Product(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "products"
    __table_args__ = (
        Index("ix_products_name", "name"),
        Index("ix_products_category_id", "category_id"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False)
    sku = Column(String(64), nullable=False, unique=True, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(Text, nullable=True)

    category = relationship("Category", back_populates="products")
    inventory = relationship("Inventory", back_populates="product", cascade="all, delete-orphan")


class Branch(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)
    address = Column(String(256), nullable=False)

    inventory = relationship("Inventory", back_populates="branch", cascade="all, delete-orphan")
    delivery_slots = relationship("DeliverySlot", back_populates="branch", cascade="all, delete-orphan")


class Inventory(Base, TimestampMixin):
    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("product_id", "branch_id", name="uq_inventory_product_branch"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    available_quantity = Column(Integer, nullable=False, default=0)
    reserved_quantity = Column(Integer, nullable=False, default=0)

    product = relationship("Product", back_populates="inventory")
    branch = relationship("Branch", back_populates="inventory")


class DeliverySlot(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "delivery_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    branch = relationship("Branch", back_populates="delivery_slots")


class Cart(Base, TimestampMixin):
    __tablename__ = "carts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    status = Column(SQLEnum(CartStatus, name="cart_status"), nullable=False, server_default=CartStatus.ACTIVE.value)

    user = relationship("User", back_populates="carts")
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base, TimestampMixin):
    __tablename__ = "cart_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cart_id = Column(UUID(as_uuid=True), ForeignKey("carts.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")


class Order(Base, TimestampMixin):
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_number = Column(String(32), nullable=False, unique=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    total_amount = Column(Numeric(12, 2), nullable=False)
    fulfillment_type = Column(SQLEnum(FulfillmentType, name="fulfillment_type"), nullable=False)
    status = Column(SQLEnum(OrderStatus, name="order_status"), nullable=False, server_default=OrderStatus.CREATED.value)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"))

    user = relationship("User", back_populates="orders")
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    delivery = relationship("OrderDeliveryDetails", back_populates="order", uselist=False, cascade="all, delete-orphan")
    pickup = relationship("OrderPickupDetails", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), nullable=False)
    name = Column(String(128), nullable=False)
    sku = Column(String(64), nullable=False)
    unit_price = Column(Numeric(10, 2), nullable=False)
    quantity = Column(Integer, nullable=False)
    picked_status = Column(SQLEnum(PickedStatus, name="picked_status"), nullable=False, server_default=PickedStatus.PENDING.value)

    order = relationship("Order", back_populates="items")


class OrderDeliveryDetails(Base):
    __tablename__ = "order_delivery_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, unique=True)
    delivery_slot_id = Column(UUID(as_uuid=True), ForeignKey("delivery_slots.id"))
    address = Column(String(256), nullable=False)
    slot_start = Column(DateTime, nullable=True)
    slot_end = Column(DateTime, nullable=True)

    order = relationship("Order", back_populates="delivery")
    delivery_slot = relationship("DeliverySlot")


class OrderPickupDetails(Base):
    __tablename__ = "order_pickup_details"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False, unique=True)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    pickup_window_start = Column(DateTime, nullable=False)
    pickup_window_end = Column(DateTime, nullable=False)

    order = relationship("Order", back_populates="pickup")
    branch = relationship("Branch")


class StockRequest(Base, TimestampMixin):
    __tablename__ = "stock_requests"
    __table_args__ = (
        Index("ix_stock_requests_status", "status"),
        Index("ix_stock_requests_branch_id", "branch_id"),
        Index("ix_stock_requests_created_at", "created_at"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    request_type = Column(SQLEnum(StockRequestType, name="stock_request_type"), nullable=False)
    status = Column(SQLEnum(StockRequestStatus, name="stock_request_status"), nullable=False, server_default=StockRequestStatus.PENDING.value)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    branch = relationship("Branch")
    product = relationship("Product")
    actor = relationship("User")


class Audit(Base):
    __tablename__ = "audit"
    __table_args__ = (
        UniqueConstraint("id", name="pk_audit"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    entity_type = Column(String(64), nullable=False, index=True)
    entity_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    action = Column(String(64), nullable=False, index=True)
    old_value = Column(JSON, nullable=True)
    new_value = Column(JSON, nullable=True)
    context = Column(JSON, nullable=True)
    actor_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    actor = relationship("User")
