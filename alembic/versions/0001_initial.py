"""Initial schema creation.

Uses explicit op.create_table() calls so Alembic can track every column,
index, and constraint in its migration history.
"""

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None

import sqlalchemy as sa
from alembic import op


def upgrade() -> None:
    # ── Enum types (PostgreSQL) ──────────────────────────────────────────────
    op.execute("CREATE TYPE IF NOT EXISTS role AS ENUM ('CUSTOMER','EMPLOYEE','MANAGER','ADMIN')")
    op.execute("CREATE TYPE IF NOT EXISTS order_status AS ENUM ('CREATED','IN_PROGRESS','READY','OUT_FOR_DELIVERY','DELIVERED','CANCELED','DELAYED','MISSING')")
    op.execute("CREATE TYPE IF NOT EXISTS fulfillment_type AS ENUM ('DELIVERY','PICKUP')")
    op.execute("CREATE TYPE IF NOT EXISTS picked_status AS ENUM ('PENDING','PICKED','MISSING')")
    op.execute("CREATE TYPE IF NOT EXISTS stock_request_type AS ENUM ('SET_QUANTITY','ADD_QUANTITY')")
    op.execute("CREATE TYPE IF NOT EXISTS stock_request_status AS ENUM ('PENDING','APPROVED','REJECTED')")
    op.execute("CREATE TYPE IF NOT EXISTS cart_status AS ENUM ('ACTIVE','CHECKED_OUT','ABANDONED')")
    op.execute("CREATE TYPE IF NOT EXISTS idempotency_status AS ENUM ('IN_PROGRESS','SUCCEEDED','FAILED')")

    # ── users ────────────────────────────────────────────────────────────────
    op.create_table(
        "users",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(120), nullable=False, unique=True),
        sa.Column("full_name", sa.String(100), nullable=False),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("password_hash", sa.String(256), nullable=False),
        sa.Column("role", sa.Enum("CUSTOMER", "EMPLOYEE", "MANAGER", "ADMIN", name="role"), nullable=False, server_default="CUSTOMER"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # ── branches ─────────────────────────────────────────────────────────────
    op.create_table(
        "branches",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("city", sa.String(100), nullable=True),
        sa.Column("address", sa.String(255), nullable=True),
        sa.Column("phone", sa.String(20), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_delivery_source", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("source_branch_id", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── categories ───────────────────────────────────────────────────────────
    op.create_table(
        "categories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(100), nullable=False, unique=True),
        sa.Column("slug", sa.String(100), nullable=False, unique=True),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── products ─────────────────────────────────────────────────────────────
    op.create_table(
        "products",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("sku", sa.String(64), nullable=False, unique=True),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("price", sa.Numeric(10, 2), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column("category_id", sa.Integer, sa.ForeignKey("categories.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("is_organic", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("is_featured", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_products_category_id", "products", ["category_id"])
    op.create_index("ix_products_sku", "products", ["sku"], unique=True)

    # ── inventory ────────────────────────────────────────────────────────────
    op.create_table(
        "inventory",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("available_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reserved_quantity", sa.Integer, nullable=False, server_default="0"),
        sa.Column("reorder_point", sa.Integer, nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("product_id", "branch_id", name="uq_inventory_product_branch"),
    )

    # ── delivery_slots ───────────────────────────────────────────────────────
    op.create_table(
        "delivery_slots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("slot_start", sa.DateTime, nullable=False),
        sa.Column("slot_end", sa.DateTime, nullable=False),
        sa.Column("max_orders", sa.Integer, nullable=False, server_default="10"),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── addresses ────────────────────────────────────────────────────────────
    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("label", sa.String(50), nullable=True),
        sa.Column("street", sa.String(200), nullable=False),
        sa.Column("city", sa.String(100), nullable=False),
        sa.Column("zip_code", sa.String(20), nullable=True),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_addresses_user_id", "addresses", ["user_id"])

    # ── payment_tokens ───────────────────────────────────────────────────────
    op.create_table(
        "payment_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", sa.String(32), nullable=False),
        sa.Column("provider_token", sa.String(128), nullable=False),
        sa.Column("brand", sa.String(32), nullable=True),
        sa.Column("last4", sa.String(4), nullable=True),
        sa.Column("exp_month", sa.Integer, nullable=True),
        sa.Column("exp_year", sa.Integer, nullable=True),
        sa.Column("is_default", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── orders ───────────────────────────────────────────────────────────────
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_number", sa.String(32), nullable=False, unique=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("fulfillment_type", sa.Enum("DELIVERY", "PICKUP", name="fulfillment_type"), nullable=False),
        sa.Column("status", sa.Enum("CREATED", "IN_PROGRESS", "READY", "OUT_FOR_DELIVERY", "DELIVERED", "CANCELED", "DELAYED", "MISSING", name="order_status"), nullable=False, server_default="CREATED"),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_orders_user_id", "orders", ["user_id"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_created_at", "orders", ["created_at"])

    # ── order_items ──────────────────────────────────────────────────────────
    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False),
        sa.Column("product_id", sa.Integer, nullable=False),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("sku", sa.String(64), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("picked_status", sa.Enum("PENDING", "PICKED", "MISSING", name="picked_status"), nullable=False, server_default="PENDING"),
    )

    # ── order_delivery_details ───────────────────────────────────────────────
    op.create_table(
        "order_delivery_details",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False, unique=True),
        sa.Column("delivery_slot_id", sa.Integer, sa.ForeignKey("delivery_slots.id"), nullable=True),
        sa.Column("address", sa.String(256), nullable=False),
        sa.Column("slot_start", sa.DateTime, nullable=True),
        sa.Column("slot_end", sa.DateTime, nullable=True),
    )

    # ── order_pickup_details ─────────────────────────────────────────────────
    op.create_table(
        "order_pickup_details",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=False, unique=True),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("pickup_window_start", sa.DateTime, nullable=False),
        sa.Column("pickup_window_end", sa.DateTime, nullable=False),
    )

    # ── carts ────────────────────────────────────────────────────────────────
    op.create_table(
        "carts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("status", sa.Enum("ACTIVE", "CHECKED_OUT", "ABANDONED", name="cart_status"), nullable=False, server_default="ACTIVE"),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── cart_items ───────────────────────────────────────────────────────────
    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("cart_id", sa.Integer, sa.ForeignKey("carts.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.UniqueConstraint("cart_id", "product_id", name="uq_cart_product"),
    )

    # ── idempotency_keys ─────────────────────────────────────────────────────
    op.create_table(
        "idempotency_keys",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("key", sa.String(128), nullable=False),
        sa.Column("request_hash", sa.String(256), nullable=False),
        sa.Column("status", sa.Enum("IN_PROGRESS", "SUCCEEDED", "FAILED", name="idempotency_status"), nullable=False, server_default="IN_PROGRESS"),
        sa.Column("response_payload", sa.JSON, nullable=True),
        sa.Column("status_code", sa.Integer, nullable=True),
        sa.Column("order_id", sa.Integer, sa.ForeignKey("orders.id"), nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "key", name="uq_user_idempotency_key"),
    )
    op.create_index("ix_idempotency_key", "idempotency_keys", ["key"])
    op.create_index("ix_idempotency_expires_at", "idempotency_keys", ["expires_at"])

    # ── stock_requests ───────────────────────────────────────────────────────
    op.create_table(
        "stock_requests",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("branch_id", sa.Integer, sa.ForeignKey("branches.id"), nullable=False),
        sa.Column("requested_by", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("reviewed_by", sa.Integer, sa.ForeignKey("users.id"), nullable=True),
        sa.Column("request_type", sa.Enum("SET_QUANTITY", "ADD_QUANTITY", name="stock_request_type"), nullable=False),
        sa.Column("quantity", sa.Integer, nullable=False),
        sa.Column("status", sa.Enum("PENDING", "APPROVED", "REJECTED", name="stock_request_status"), nullable=False, server_default="PENDING"),
        sa.Column("note", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── audit ────────────────────────────────────────────────────────────────
    op.create_table(
        "audit",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("entity_type", sa.String(64), nullable=False),
        sa.Column("entity_id", sa.Integer, nullable=False),
        sa.Column("action", sa.String(64), nullable=False),
        sa.Column("actor_user_id", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("old_value", sa.JSON, nullable=True),
        sa.Column("new_value", sa.JSON, nullable=True),
        sa.Column("context", sa.JSON, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_audit_entity_type", "audit", ["entity_type"])
    op.create_index("ix_audit_actor_user_id", "audit", ["actor_user_id"])

    # ── registration_otp ─────────────────────────────────────────────────────
    op.create_table(
        "registration_otp",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("email", sa.String(120), nullable=False),
        sa.Column("code_hash", sa.String(256), nullable=False),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("is_used", sa.Boolean, nullable=False, server_default=sa.text("false")),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )
    op.create_index("ix_registration_otp_email", "registration_otp", ["email"])

    # ── password_reset_tokens ────────────────────────────────────────────────
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("token_hash", sa.String(256), nullable=False, index=True),
        sa.Column("expires_at", sa.DateTime, nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
    )

    # ── global_settings ──────────────────────────────────────────────────────
    op.create_table(
        "global_settings",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("delivery_min", sa.Numeric(10, 2), nullable=False, server_default="50.0"),
        sa.Column("delivery_fee", sa.Numeric(10, 2), nullable=False, server_default="15.0"),
        sa.Column("free_threshold", sa.Numeric(10, 2), nullable=False, server_default="200.0"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("NOW()")),
        sa.Column("updated_by", sa.Integer, sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )

    # ── wishlist_items ───────────────────────────────────────────────────────
    op.create_table(
        "wishlist_items",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer, sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer, sa.ForeignKey("products.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, server_default=sa.text("NOW()")),
        sa.UniqueConstraint("user_id", "product_id", name="uq_wishlist_user_product"),
    )

    # ── token_blocklist ──────────────────────────────────────────────────────
    op.create_table(
        "token_blocklist",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("jti", sa.String(36), nullable=False),
        sa.Column("revoked_at", sa.DateTime, nullable=False),
    )
    op.create_index("ix_token_blocklist_jti", "token_blocklist", ["jti"], unique=True)


def downgrade() -> None:
    op.drop_table("token_blocklist")
    op.drop_table("wishlist_items")
    op.drop_table("global_settings")
    op.drop_table("password_reset_tokens")
    op.drop_table("registration_otp")
    op.drop_table("audit")
    op.drop_table("stock_requests")
    op.drop_table("idempotency_keys")
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("order_pickup_details")
    op.drop_table("order_delivery_details")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("payment_tokens")
    op.drop_table("addresses")
    op.drop_table("delivery_slots")
    op.drop_table("inventory")
    op.drop_table("products")
    op.drop_table("categories")
    op.drop_table("branches")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS idempotency_status")
    op.execute("DROP TYPE IF EXISTS cart_status")
    op.execute("DROP TYPE IF EXISTS stock_request_status")
    op.execute("DROP TYPE IF EXISTS stock_request_type")
    op.execute("DROP TYPE IF EXISTS picked_status")
    op.execute("DROP TYPE IF EXISTS fulfillment_type")
    op.execute("DROP TYPE IF EXISTS order_status")
    op.execute("DROP TYPE IF EXISTS role")
