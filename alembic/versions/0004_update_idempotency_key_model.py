from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '0004'
down_revision = '0003'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns
    op.add_column('idempotency_keys', sa.Column('status', sa.Enum('IN_PROGRESS', 'SUCCEEDED', 'FAILED', name='idempotencystatus'), nullable=True))
    op.add_column('idempotency_keys', sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column('idempotency_keys', sa.Column('expires_at', sa.DateTime(), nullable=True))
    
    # Set default values for existing rows
    op.execute("UPDATE idempotency_keys SET status = 'SUCCEEDED' WHERE status IS NULL")
    op.execute("UPDATE idempotency_keys SET expires_at = created_at + INTERVAL '24 hours' WHERE expires_at IS NULL")
    
    # Make columns non-nullable
    op.alter_column('idempotency_keys', 'status', nullable=False)
    op.alter_column('idempotency_keys', 'expires_at', nullable=False)
    
    # Drop old unique constraint
    op.drop_constraint('uq_idempotency_key_hash', 'idempotency_keys', type_='unique')
    
    # Add new unique constraint
    op.create_unique_constraint('uq_user_idempotency_key', 'idempotency_keys', ['user_id', 'key'])
    
    # Add foreign key for order_id
    op.create_foreign_key('fk_idempotency_keys_order_id', 'idempotency_keys', 'orders', ['order_id'], ['id'])
    
    # Add index on expires_at for cleanup queries
    op.create_index('ix_idempotency_expires_at', 'idempotency_keys', ['expires_at'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_idempotency_expires_at', table_name='idempotency_keys')
    
    # Drop foreign key
    op.drop_constraint('fk_idempotency_keys_order_id', 'idempotency_keys', type_='foreignkey')
    
    # Drop new unique constraint
    op.drop_constraint('uq_user_idempotency_key', 'idempotency_keys', type_='unique')
    
    # Recreate old unique constraint
    op.create_unique_constraint('uq_idempotency_key_hash', 'idempotency_keys', ['user_id', 'key', 'request_hash'])
    
    # Drop new columns
    op.drop_column('idempotency_keys', 'expires_at')
    op.drop_column('idempotency_keys', 'order_id')
    op.drop_column('idempotency_keys', 'status')
    
    # Drop enum type
    op.execute("DROP TYPE IF EXISTS idempotencystatus")
