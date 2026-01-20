"""Add idempotency_keys table"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


revision = "0002_add_idempotency_keys"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Initial migration creates all models via Base.metadata.create_all, so the table
    # may already exist when this revision runs in fresh environments.
    bind = op.get_bind()
    if inspect(bind).has_table("idempotency_keys"):
        return

    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("request_hash", sa.String(length=256), nullable=False),
        sa.Column("response_payload", sa.JSON(), nullable=True),
        sa.Column("status_code", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "key", "request_hash", name="uq_idempotency_key_hash"),
    )
    op.create_index("ix_idempotency_key", "idempotency_keys", ["key"])


def downgrade() -> None:
    op.drop_index("ix_idempotency_key", table_name="idempotency_keys")
    op.drop_table("idempotency_keys")
