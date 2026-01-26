from __future__ import annotations

from sqlalchemy import Column, Enum as SQLEnum, ForeignKey, Index, Integer
from sqlalchemy.orm import relationship

from .base import Base, TimestampMixin
from .enums import StockRequestStatus, StockRequestType

class StockRequest(Base, TimestampMixin):
    __tablename__ = "stock_requests"
    __table_args__ = (
        Index("ix_stock_requests_status", "status"),
        Index("ix_stock_requests_branch_id", "branch_id"),
        Index("ix_stock_requests_created_at", "created_at"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    branch_id = Column(Integer, ForeignKey("branches.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    request_type = Column(SQLEnum(StockRequestType, name="stock_request_type"), nullable=False)
    status = Column(
        SQLEnum(StockRequestStatus, name="stock_request_status"),
        nullable=False,
        server_default=StockRequestStatus.PENDING.value,
    )
    actor_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    branch = relationship("Branch")
    product = relationship("Product")
    actor = relationship("User")
