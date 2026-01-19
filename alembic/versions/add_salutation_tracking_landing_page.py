"""Add salutation, tracking_token, and default_landing_page_id

Revision ID: add_salutation_tracking
Revises: 999f0b6bef98
Create Date: 2026-01-19

This migration adds:
1. salutation column to targets table
2. tracking_token column to campaign_targets table
3. default_landing_page_id column to email_templates table
4. anonymous_visit event type
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_salutation_tracking'
down_revision = '999f0b6bef98'
branch_labels = None
depends_on = None


def upgrade():
    # Add salutation to targets table
    op.add_column(
        'targets',
        sa.Column('salutation', sa.String(20), nullable=True)
    )

    # Add tracking_token to campaign_targets table
    op.add_column(
        'campaign_targets',
        sa.Column('tracking_token', sa.String(255), nullable=True)
    )
    # Create unique index for tracking_token
    op.create_index(
        'ix_campaign_targets_tracking_token',
        'campaign_targets',
        ['tracking_token'],
        unique=True
    )

    # Add default_landing_page_id to email_templates table
    op.add_column(
        'email_templates',
        sa.Column(
            'default_landing_page_id',
            sa.BigInteger(),
            sa.ForeignKey('landing_pages.id'),
            nullable=True
        )
    )

    # Add anonymous_visit event type
    op.execute("""
        INSERT INTO event_types (name, description, created_at)
        VALUES (
            'anonymous_visit',
            'Landing page accessed without valid tracking token',
            NOW()
        )
        ON CONFLICT (name) DO NOTHING
    """)

    # Add anonymous_submission event type
    op.execute("""
        INSERT INTO event_types (name, description, created_at)
        VALUES (
            'anonymous_submission',
            'Form submitted without valid tracking token',
            NOW()
        )
        ON CONFLICT (name) DO NOTHING
    """)


def downgrade():
    # Remove anonymous_submission event type
    op.execute("""
        DELETE FROM event_types WHERE name = 'anonymous_submission'
    """)

    # Remove anonymous_visit event type
    op.execute("""
        DELETE FROM event_types WHERE name = 'anonymous_visit'
    """)

    # Remove default_landing_page_id from email_templates
    op.drop_column('email_templates', 'default_landing_page_id')

    # Remove tracking_token index and column from campaign_targets
    op.drop_index('ix_campaign_targets_tracking_token', 'campaign_targets')
    op.drop_column('campaign_targets', 'tracking_token')

    # Remove salutation from targets
    op.drop_column('targets', 'salutation')
