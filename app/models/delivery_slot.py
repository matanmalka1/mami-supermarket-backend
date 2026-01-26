from __future__ import annotations

from sqlalchemy import Column, ForeignKey, Integer, Time
from sqlalchemy.orm import relationship
from .base import Base, SoftDeleteMixin, TimestampMixin

class DeliverySlot(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "delivery_slots"

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    day_of_week = Column(Integer, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    branch = relationship("Branch", back_populates="delivery_slots")
