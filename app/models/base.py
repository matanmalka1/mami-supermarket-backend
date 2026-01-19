"""SQLAlchemy base and mixins for shared columns."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import TIMESTAMP, Column, Boolean, func
from sqlalchemy.orm import declarative_base


Base = declarative_base()


class TimestampMixin:
    """Shared timestamps for most entities."""

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=func.now(), onupdate=func.now())


class SoftDeleteMixin:
    """Flagged entities for soft deletion."""

    is_active = Column(Boolean, nullable=False, server_default="true")
