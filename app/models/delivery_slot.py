from __future__ import annotations
import uuid
from sqlalchemy import Column, ForeignKey, Integer, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base, SoftDeleteMixin, TimestampMixin

class DeliverySlot(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "delivery_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    branch_id = Column(UUID(as_uuid=True), ForeignKey("branches.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    branch = relationship("Branch", back_populates="delivery_slots")
