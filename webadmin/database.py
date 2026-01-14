"""
Phishly WebAdmin - Database Module

This module initializes Flask-SQLAlchemy and provides database access
for the webadmin application.
"""

import sys
import os
import logging

# Add parent directory to path to import db.models
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask_sqlalchemy import SQLAlchemy  # noqa: E402
from sqlalchemy.exc import SQLAlchemyError  # noqa: E402

# Initialize Flask-SQLAlchemy extension (app will be attached later)
db = SQLAlchemy()

# Import all models from db/models.py so they're registered with SQLAlchemy
# This ensures all tables are created when db.create_all() is called
from db.models import (  # noqa: E402, F401
    AdminUser,
    Department,
    Target,
    TargetList,
    TargetListMember,
    EmailTemplate,
    LandingPage,
    Campaign,
    CampaignTargetList,
    CampaignTarget,
    EmailJob,
    EventType,
    Event,
    FormTemplate,
    FormQuestion,
    FormSubmission,
    FormAnswer,
)

# Configure logging
logger = logging.getLogger(__name__)


# Helper functions for common queries
def get_or_create_event_type(name, description=None):
    """
    Get event type by name, create if doesn't exist.

    Args:
        name: Event type name (e.g., 'email_sent', 'email_opened')
        description: Optional description

    Returns:
        EventType object
    """
    event_type = db.session.query(EventType).filter_by(name=name).first()

    if not event_type:
        event_type = EventType(name=name, description=description)
        db.session.add(event_type)
        db.session.commit()
        logger.info(f"Created new event type: {name}")

    return event_type


def get_event_type_id(name):
    """
    Get event type ID by name (faster than loading full object).

    Args:
        name: Event type name

    Returns:
        Event type ID or None if not found
    """
    event_type = (
        db.session.query(EventType.id).filter_by(name=name).first()
    )
    return event_type[0] if event_type else None


def init_event_types():
    """
    Initialize standard event types if they don't exist.
    Should be called during application initialization or database setup.
    """
    standard_event_types = [
        ("email_sent", "Email successfully sent to target"),
        ("email_opened", "Target opened the email"),
        ("link_clicked", "Target clicked the phishing link"),
        ("form_submitted", "Target submitted form data"),
        ("credentials_captured", "Target submitted credentials"),
    ]

    for name, description in standard_event_types:
        get_or_create_event_type(name, description)

    logger.info("Event types initialized")


class DatabaseError(Exception):
    """Custom exception for database operations"""

    pass


def handle_db_error(func):
    """
    Decorator for consistent error handling in database operations.

    Automatically rolls back on errors and logs exceptions.
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except SQLAlchemyError as e:
            db.session.rollback()
            logger.error(f"Database error in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed: {str(e)}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise

    return wrapper


def test_connection():
    """
    Test database connectivity.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        # Simple query to test connection
        db.session.execute(db.text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
