"""add_active_configuration_table

Revision ID: 2d7079e0cbf5
Revises: 6d2919baffcc
Create Date: 2026-01-20 12:37:16.144540

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d7079e0cbf5'
down_revision: Union[str, Sequence[str], None] = '6d2919baffcc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create active_configuration table
    op.create_table(
        'active_configuration',
        sa.Column('id', sa.BigInteger(), primary_key=True),
        sa.Column('active_landing_page_id', sa.BigInteger(),
                  sa.ForeignKey('landing_pages.id'), nullable=True),
        sa.Column('activated_at', sa.DateTime(), nullable=True),
        sa.Column('activated_by_id', sa.BigInteger(),
                  sa.ForeignKey('admin_users.id'), nullable=True),
        sa.Column('dns_zone_file_path', sa.String(500), nullable=True),
        sa.Column('phishing_domain', sa.String(255), nullable=True),
        sa.Column('public_ip', sa.String(45), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), onupdate=sa.func.now()),
    )

    # Insert singleton row with default phishing domain from environment
    op.execute("""
        INSERT INTO active_configuration (id, phishing_domain)
        VALUES (1, 'phishing.example.com')
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('active_configuration')
