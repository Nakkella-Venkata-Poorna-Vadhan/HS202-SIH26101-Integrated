"""add_password_reset_tokens

Revision ID: 02_password_reset
Revises: 01dba1349855
Create Date: 2026-10-31 23:35:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '02_password_reset'
down_revision: Union[str, Sequence[str], None] = '01dba1349855'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create password_reset_tokens table and grant permissions."""
    op.create_table(
        'password_reset_tokens',
        sa.Column('id', sa.UUID(), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('token_hash', sa.String(length=64), nullable=False),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_consumed', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('consumed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name=op.f('fk_password_reset_tokens_user_id_users'), ondelete='RESTRICT'),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_password_reset_tokens')),
        sa.UniqueConstraint('token_hash', name=op.f('uq_password_reset_tokens_token_hash')),
    )
    op.create_index('idx_password_reset_user_id', 'password_reset_tokens', ['user_id'], unique=False)

    # Ensure runtime application user has table-level permissions
    op.execute("""
        DO $$
        BEGIN
            IF EXISTS (SELECT FROM pg_roles WHERE rolname = 'sih_app_user') THEN
                GRANT SELECT, INSERT, UPDATE, DELETE ON password_reset_tokens TO sih_app_user;
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    """Drop password_reset_tokens table."""
    op.drop_index('idx_password_reset_user_id', table_name='password_reset_tokens')
    op.drop_table('password_reset_tokens')

