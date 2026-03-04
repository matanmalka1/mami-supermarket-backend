"""Global system settings model."""

from __future__ import annotations

from datetime import datetime, timezone
from sqlalchemy import Numeric, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class GlobalSettings(Base):
    """
    Stores system-wide configuration settings.
    Should only have one active row at a time.
    """

    __tablename__ = "global_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Delivery settings
    delivery_min: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=50.0)
    delivery_fee: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=15.0)
    free_threshold: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False, default=200.0)
    
    # Audit fields
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_by: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    
    # Relationship
    updater: Mapped["User"] = relationship("User", foreign_keys=[updated_by])

    def to_dict(self) -> dict:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "delivery_min": float(self.delivery_min),
            "delivery_fee": float(self.delivery_fee),
            "free_threshold": float(self.free_threshold),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "updated_by": self.updated_by,
        }
