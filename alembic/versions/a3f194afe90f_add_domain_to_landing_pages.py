"""add_domain_to_landing_pages

Revision ID: a3f194afe90f
Revises: 2d7079e0cbf5
Create Date: 2026-01-20 20:56:43.776061

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3f194afe90f'
down_revision: Union[str, Sequence[str], None] = '2d7079e0cbf5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add domain column to landing_pages table
    op.add_column('landing_pages', sa.Column('domain', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove domain column from landing_pages table
    op.drop_column('landing_pages', 'domain')
