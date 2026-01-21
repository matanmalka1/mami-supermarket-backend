from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy import TIMESTAMP, Column, Boolean
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class TimestampMixin:
    """Shared timestamps for most entities."""

    created_at = Column(TIMESTAMP, nullable=False, server_default=sa.func.now())
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=sa.func.now(),
        onupdate=sa.func.now(),
    )


class SoftDeleteMixin:
    """Flagged entities for soft deletion."""

    is_active = Column(Boolean, nullable=False, server_default="true")
