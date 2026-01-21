"""add_template_path_to_landing_pages

Revision ID: 2c0f11d5f148
Revises: a3f194afe90f
Create Date: 2026-01-20 21:48:40.430616

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c0f11d5f148'
down_revision: Union[str, Sequence[str], None] = 'a3f194afe90f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add template_path column to landing_pages table
    # This will store the filesystem path to the template directory (e.g., "phish-page", "info_page")
    op.add_column('landing_pages', sa.Column('template_path', sa.String(length=500), nullable=True))

    # Make html_content nullable (was previously required)
    # This allows new landing pages to use template_path instead of html_content
    op.alter_column('landing_pages', 'html_content', nullable=True)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove template_path column from landing_pages table
    op.drop_column('landing_pages', 'template_path')
