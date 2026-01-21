from __future__ import annotations

import uuid

from sqlalchemy import Column, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin


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
