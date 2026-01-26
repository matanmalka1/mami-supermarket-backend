from __future__ import annotations

from sqlalchemy import Column, String, Text, Integer
import sqlalchemy as sa
from sqlalchemy.orm import relationship

from .base import Base, SoftDeleteMixin, TimestampMixin

class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    icon_slug = Column(String(64), nullable=True)
    is_active = Column(sa.Boolean, nullable=False, server_default='true')

    products = relationship("Product", back_populates="category")
