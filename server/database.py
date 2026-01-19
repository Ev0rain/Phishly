"""
Database models and connection management for Phishly Phishing Server.

This module provides SQLAlchemy models and query functions for:
- Looking up campaign targets by tracking token
- Fetching landing page content
- Logging tracking events (link clicks, form submissions)
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from contextlib import contextmanager

from sqlalchemy import (
    create_engine,
    Column,
    BigInteger,
    String,
    Text,
    DateTime,
    ForeignKey,
    Integer,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

Base = declarative_base()


# ============================================
# Database Models (subset needed for phishing server)
# ============================================


class Target(Base):
    """Target employees who receive phishing emails."""

    __tablename__ = "targets"

    id = Column(BigInteger, primary_key=True)
    email = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))


class Campaign(Base):
    """Phishing campaigns."""

    __tablename__ = "campaigns"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))
    status = Column(String(50))

    landing_page = relationship("LandingPage")


class CampaignTarget(Base):
    """Individual campaign-target assignments with tracking."""

    __tablename__ = "campaign_targets"

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id"))
    target_id = Column(BigInteger, ForeignKey("targets.id"))
    tracking_token = Column(String(255), unique=True)
    status = Column(String(50))

    campaign = relationship("Campaign")
    target = relationship("Target")


class LandingPage(Base):
    """Landing pages shown after clicking phishing link."""

    __tablename__ = "landing_pages"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255))
    url_path = Column(String(255), unique=True)
    html_content = Column(Text)
    css_content = Column(Text)
    js_content = Column(Text)
    capture_credentials = Column(Boolean, default=False)
    capture_form_data = Column(Boolean, default=True)
    redirect_url = Column(String(500))


class EventType(Base):
    """Types of tracking events."""

    __tablename__ = "event_types"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100), unique=True)
    description = Column(Text)


class Event(Base):
    """Tracking events for campaign interactions."""

    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    event_type_id = Column(BigInteger, ForeignKey("event_types.id"))
    ip_address = Column(String(45))
    user_agent = Column(Text)
    browser = Column(String(100))
    os = Column(String(100))
    device_type = Column(String(50))
    location = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign_target = relationship("CampaignTarget")
    event_type = relationship("EventType")


class FormSubmission(Base):
    """Form submissions from landing pages."""

    __tablename__ = "form_submissions"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    form_template_id = Column(BigInteger)
    submitted_at = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    campaign_target = relationship("CampaignTarget")


# ============================================
# Database Connection
# ============================================


class DatabaseManager:
    """Manage database connections and queries."""

    def __init__(self):
        """Initialize database connection from environment variables."""
        self.host = os.getenv("POSTGRES_HOST", "postgres-db")
        self.port = os.getenv("POSTGRES_PORT", "5432")
        self.database = os.getenv("POSTGRES_DB", "phishly")
        self.user = os.getenv("POSTGRES_USER", "admin")
        self.password = os.getenv("POSTGRES_PASSWORD", "")

        self.connection_string = (
            f"postgresql://{self.user}:{self.password}@"
            f"{self.host}:{self.port}/{self.database}"
        )

        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False,
        )

        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)
        logger.info(f"Database initialized: {self.host}:{self.port}/{self.database}")

    @contextmanager
    def get_session(self):
        """Context manager for database sessions."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    def test_connection(self) -> bool:
        """Test database connection."""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False


# ============================================
# Query Functions
# ============================================


def get_campaign_target_by_token(
    session: Session, tracking_token: str
) -> Optional[CampaignTarget]:
    """
    Look up campaign target by tracking token.

    Args:
        session: SQLAlchemy session
        tracking_token: The tracking token from the URL

    Returns:
        CampaignTarget object or None if not found
    """
    return (
        session.query(CampaignTarget)
        .filter(CampaignTarget.tracking_token == tracking_token)
        .first()
    )


def get_landing_page_by_url_path(
    session: Session, url_path: str
) -> Optional[LandingPage]:
    """
    Look up landing page by URL path.

    Args:
        session: SQLAlchemy session
        url_path: The URL path (e.g., "login-portal")

    Returns:
        LandingPage object or None if not found
    """
    # Normalize path - remove leading/trailing slashes
    normalized_path = url_path.strip("/")

    # Try exact match first
    landing_page = (
        session.query(LandingPage)
        .filter(LandingPage.url_path == normalized_path)
        .first()
    )

    if not landing_page:
        # Try with leading slash
        landing_page = (
            session.query(LandingPage)
            .filter(LandingPage.url_path == f"/{normalized_path}")
            .first()
        )

    return landing_page


def get_or_create_event_type(session: Session, event_name: str) -> EventType:
    """
    Get or create an event type by name.

    Args:
        session: SQLAlchemy session
        event_name: Event type name (e.g., "link_clicked")

    Returns:
        EventType object
    """
    event_type = (
        session.query(EventType).filter(EventType.name == event_name).first()
    )

    if not event_type:
        event_type = EventType(name=event_name)
        session.add(event_type)
        session.flush()

    return event_type


def log_event(
    session: Session,
    campaign_target_id: Optional[int],
    event_type_name: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    browser: Optional[str] = None,
    os_name: Optional[str] = None,
    device_type: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Event:
    """
    Log a tracking event to the database.

    Args:
        session: SQLAlchemy session
        campaign_target_id: CampaignTarget ID (None for anonymous visits)
        event_type_name: Event type name
        ip_address: Client IP address
        user_agent: Client user agent string
        browser: Detected browser name
        os_name: Detected OS name
        device_type: Device type (mobile, desktop, tablet)
        metadata: Additional metadata as dict

    Returns:
        Created Event object
    """
    event_type = get_or_create_event_type(session, event_type_name)

    event = Event(
        campaign_target_id=campaign_target_id,
        event_type_id=event_type.id,
        ip_address=ip_address,
        user_agent=user_agent,
        browser=browser,
        os=os_name,
        device_type=device_type,
        created_at=datetime.utcnow(),
    )
    session.add(event)
    session.flush()

    logger.info(
        f"Event logged: {event_type_name} for campaign_target={campaign_target_id}"
    )
    return event


def update_campaign_target_status(
    session: Session, campaign_target_id: int, new_status: str
) -> bool:
    """
    Update campaign target status.

    Status progression: pending -> sent -> opened -> clicked -> submitted

    Args:
        session: SQLAlchemy session
        campaign_target_id: CampaignTarget ID
        new_status: New status value

    Returns:
        True if updated, False if not found
    """
    campaign_target = (
        session.query(CampaignTarget)
        .filter(CampaignTarget.id == campaign_target_id)
        .first()
    )

    if not campaign_target:
        return False

    # Status hierarchy - only update if new status is "higher"
    status_order = ["pending", "sent", "opened", "clicked", "submitted"]
    current_idx = (
        status_order.index(campaign_target.status)
        if campaign_target.status in status_order
        else 0
    )
    new_idx = status_order.index(new_status) if new_status in status_order else 0

    if new_idx > current_idx:
        campaign_target.status = new_status
        session.flush()
        logger.info(
            f"Updated campaign_target {campaign_target_id} status to {new_status}"
        )

    return True


def create_form_submission(
    session: Session,
    campaign_target_id: int,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
) -> FormSubmission:
    """
    Create a form submission record.

    Args:
        session: SQLAlchemy session
        campaign_target_id: CampaignTarget ID
        ip_address: Client IP address
        user_agent: Client user agent

    Returns:
        Created FormSubmission object
    """
    submission = FormSubmission(
        campaign_target_id=campaign_target_id,
        submitted_at=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent,
    )
    session.add(submission)
    session.flush()
    return submission


# Create global database manager instance
db_manager = DatabaseManager()
