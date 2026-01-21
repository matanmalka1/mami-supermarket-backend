from __future__ import annotations
import uuid
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, SoftDeleteMixin, TimestampMixin

class Branch(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "branches"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(128), nullable=False, unique=True)
    address = Column(String(256), nullable=False)

    inventory = relationship("Inventory", back_populates="branch", cascade="all, delete-orphan")
    delivery_slots = relationship(
        "DeliverySlot",
        back_populates="branch",
        cascade="all, delete-orphan",
    )
