"""make_landing_page_domain_required

Revision ID: 34f83be6345c
Revises: 2c0f11d5f148
Create Date: 2026-01-23 11:43:09.516328

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34f83be6345c'
down_revision: Union[str, Sequence[str], None] = '2c0f11d5f148'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Make landing_pages.domain column NOT NULL
    op.alter_column('landing_pages', 'domain',
               existing_type=sa.String(length=255),
               nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Make landing_pages.domain column nullable again
    op.alter_column('landing_pages', 'domain',
               existing_type=sa.String(length=255),
               nullable=True)
