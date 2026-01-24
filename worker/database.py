"""
Database models and connection management for Phishly Celery worker.

This module provides SQLAlchemy models and query functions for interacting
with the PostgreSQL database during email campaign processing.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict
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
    text,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

# SQLAlchemy Base
Base = declarative_base()


# ============================================
# Database Models
# ============================================


class AdminUser(Base):
    """Admin users who create campaigns."""

    __tablename__ = "admin_users"

    id = Column(BigInteger, primary_key=True)
    # Add other fields as needed


class Department(Base):
    """Employee departments for organizing targets."""

    __tablename__ = "departments"

    id = Column(BigInteger, primary_key=True)
    # Add other fields as needed


class Target(Base):
    """Target employees who receive phishing emails."""

    __tablename__ = "targets"

    id = Column(BigInteger, primary_key=True)
    department_id = Column(BigInteger, ForeignKey("departments.id"))
    email = Column(String(255))
    salutation = Column(String(20))  # Mr., Ms., Mrs., Dr., Prof., Mx.
    first_name = Column(String(100))
    last_name = Column(String(100))
    position = Column(String(100))

    department = relationship("Department")


class TargetList(Base):
    """Grouped lists of targets."""

    __tablename__ = "target_lists"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    name = Column(String(255))
    description = Column(Text)

    created_by = relationship("AdminUser")


class TargetListMember(Base):
    """Many-to-many relationship: target lists to targets."""

    __tablename__ = "target_list_members"

    id = Column(BigInteger, primary_key=True)
    target_list_id = Column(BigInteger, ForeignKey("target_lists.id"))
    target_id = Column(BigInteger, ForeignKey("targets.id"))

    target_list = relationship("TargetList")
    target = relationship("Target")


class EmailTemplate(Base):
    """Email templates for phishing campaigns."""

    __tablename__ = "email_templates"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    default_landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))
    name = Column(String(255))
    subject = Column(String(500))
    body_html = Column(Text)  # Database column name
    body_text = Column(Text)  # Database column name
    from_name = Column(String(255))  # Database column name
    from_email = Column(String(255))  # Database column name
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    created_by = relationship("AdminUser")
    default_landing_page = relationship("LandingPage")


class LandingPage(Base):
    """Landing pages shown after clicking phishing link."""

    __tablename__ = "landing_pages"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    name = Column(String(255))
    url_path = Column(String(255))  # e.g., /login-portal
    # Domain for email links (e.g., phishing.example.com)
    domain = Column(String(255), nullable=False)
    html_content = Column(Text)
    css_content = Column(Text)
    js_content = Column(Text)
    redirect_url = Column(String(500))  # Where to redirect after submission
    capture_credentials = Column(Integer, default=0)  # Boolean as int
    capture_form_data = Column(Integer, default=1)  # Boolean as int

    created_by = relationship("AdminUser")


class Campaign(Base):
    """Phishing campaigns."""

    __tablename__ = "campaigns"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    email_template_id = Column(BigInteger, ForeignKey("email_templates.id"))
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))
    name = Column(String(255))
    description = Column(Text)
    status = Column(String(50))  # draft, scheduled, active, completed, paused
    min_email_delay = Column(Integer)  # Minimum delay in seconds between emails
    max_email_delay = Column(Integer)  # Maximum delay in seconds between emails
    scheduled_launch = Column(DateTime)  # When to automatically launch the campaign
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    completed_date = Column(DateTime)  # When campaign was marked as completed
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

    created_by = relationship("AdminUser")
    email_template = relationship("EmailTemplate")
    landing_page = relationship("LandingPage")


class CampaignTargetList(Base):
    """Many-to-many relationship: campaigns to target lists."""

    __tablename__ = "campaign_target_lists"

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id"))
    target_list_id = Column(BigInteger, ForeignKey("target_lists.id"))

    campaign = relationship("Campaign")
    target_list = relationship("TargetList")


class CampaignTarget(Base):
    """Individual campaign-target assignments with tracking."""

    __tablename__ = "campaign_targets"

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id"))
    target_id = Column(BigInteger, ForeignKey("targets.id"))
    # email_template_id and landing_page_id removed - now inherited from campaign
    tracking_token = Column(String(255), unique=True)  # Unique token for tracking
    status = Column(String(50))  # pending, sent, opened, clicked, submitted
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    campaign = relationship("Campaign")
    target = relationship("Target")


class EmailJob(Base):
    """Email sending jobs with status tracking."""

    __tablename__ = "email_jobs"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    celery_task_id = Column(String(255))  # Celery task ID for revocation
    status = Column(String(50))  # pending, queued, sending, sent, failed, bounced, revoked
    scheduled_at = Column(DateTime)
    sent_at = Column(DateTime)
    delay_seconds = Column(Integer)  # Random delay assigned for this email
    error_message = Column(Text)
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign_target = relationship("CampaignTarget")


class EventType(Base):
    """Types of tracking events."""

    __tablename__ = "event_types"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(100))  # email_sent, email_opened, link_clicked, form_submitted
    description = Column(Text)


class Event(Base):
    """Tracking events for campaign interactions."""

    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    event_type_id = Column(BigInteger, ForeignKey("event_types.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Database column name
    ip_address = Column(String(45))
    user_agent = Column(Text)
    browser = Column(String(100))
    os = Column(String(100))
    device_type = Column(String(50))
    location = Column(String(255))

    campaign_target = relationship("CampaignTarget")
    event_type = relationship("EventType")


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

        # Create connection string
        self.connection_string = (
            f"postgresql://{self.user}:{self.password}@" f"{self.host}:{self.port}/{self.database}"
        )

        # Create engine with connection pooling
        self.engine = create_engine(
            self.connection_string,
            poolclass=QueuePool,
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True,  # Verify connections before using
            pool_recycle=3600,  # Recycle connections after 1 hour
            echo=False,  # Set to True for SQL logging
        )

        # Create session factory
        self.SessionLocal = sessionmaker(bind=self.engine, expire_on_commit=False)

        logger.info(f"Database connection initialized: {self.host}:{self.port}/{self.database}")

    @contextmanager
    def get_session(self):
        """
        Context manager for database sessions.

        Usage:
            with db_manager.get_session() as session:
                user = session.query(Target).get(1)
        """
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
        """
        Test database connection.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test: SUCCESS")
            return True
        except Exception as e:
            logger.error(f"Database connection test: FAILED - {e}")
            return False


# ============================================
# Query Functions
# ============================================


def get_campaign_details(session: Session, campaign_id: int) -> Optional[Campaign]:
    """
    Get campaign details with related data.

    Args:
        session: SQLAlchemy session
        campaign_id: Campaign ID

    Returns:
        Campaign object or None if not found
    """
    return session.query(Campaign).filter(Campaign.id == campaign_id).first()


def get_target_details(session: Session, target_id: int) -> Optional[Target]:
    """
    Get target details.

    Args:
        session: SQLAlchemy session
        target_id: Target ID

    Returns:
        Target object or None if not found
    """
    return session.query(Target).filter(Target.id == target_id).first()


def get_campaign_target(
    session: Session, campaign_id: int, target_id: int
) -> Optional[CampaignTarget]:
    """
    Get campaign-target assignment.

    Args:
        session: SQLAlchemy session
        campaign_id: Campaign ID
        target_id: Target ID

    Returns:
        CampaignTarget object or None if not found
    """
    return (
        session.query(CampaignTarget)
        .filter(CampaignTarget.campaign_id == campaign_id, CampaignTarget.target_id == target_id)
        .first()
    )


def create_email_job(
    session: Session,
    campaign_target_id: int,
    celery_task_id: str,
    scheduled_at: Optional[datetime] = None,
) -> EmailJob:
    """
    Create a new email job record.

    Args:
        session: SQLAlchemy session
        campaign_target_id: CampaignTarget ID
        celery_task_id: Celery task ID
        scheduled_at: Scheduled send time (optional)

    Returns:
        Created EmailJob object
    """
    job = EmailJob(
        campaign_target_id=campaign_target_id,
        status="queued",
        scheduled_at=scheduled_at or datetime.utcnow(),
        celery_task_id=celery_task_id,
        retry_count=0,
    )
    session.add(job)
    session.flush()
    return job


def update_email_job_status(
    session: Session,
    job_id: int,
    status: str,
    error_message: Optional[str] = None,
    sent_at: Optional[datetime] = None,
) -> bool:
    """
    Update email job status.

    Args:
        session: SQLAlchemy session
        job_id: EmailJob ID
        status: New status (sending, sent, failed)
        error_message: Error message if failed
        sent_at: Timestamp when sent

    Returns:
        True if updated, False if not found
    """
    job = session.query(EmailJob).filter(EmailJob.id == job_id).first()
    if not job:
        return False

    job.status = status
    if error_message:
        job.error_message = error_message
    if sent_at:
        job.sent_at = sent_at

    session.flush()
    return True


def update_campaign_target_status(session: Session, campaign_target_id: int, status: str) -> bool:
    """
    Update campaign target status.

    Args:
        session: SQLAlchemy session
        campaign_target_id: CampaignTarget ID
        status: New status (pending, sent, opened, clicked, submitted)

    Returns:
        True if updated, False if not found
    """
    campaign_target = (
        session.query(CampaignTarget).filter(CampaignTarget.id == campaign_target_id).first()
    )

    if not campaign_target:
        return False

    campaign_target.status = status
    session.flush()
    return True


def log_event(
    session: Session,
    campaign_target_id: int,
    event_type_name: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[str] = None,
) -> Event:
    """
    Log a tracking event.

    Args:
        session: SQLAlchemy session
        campaign_target_id: CampaignTarget ID
        event_type_name: Event type (email_sent, email_opened, link_clicked, etc.)
        ip_address: Client IP address
        user_agent: Client user agent
        metadata: Additional metadata as JSON string

    Returns:
        Created Event object
    """
    # Get or create event type
    event_type = session.query(EventType).filter(EventType.name == event_type_name).first()

    if not event_type:
        event_type = EventType(name=event_type_name)
        session.add(event_type)
        session.flush()

    # Create event
    event = Event(
        campaign_target_id=campaign_target_id,
        event_type_id=event_type.id,
        created_at=datetime.utcnow(),
        ip_address=ip_address,
        user_agent=user_agent,
        # Note: event_metadata column was removed from model since it doesn't exist in DB
    )
    session.add(event)
    session.flush()
    return event


def get_email_template_variables(
    template: EmailTemplate, target: Target, campaign: Campaign
) -> Dict:
    """
    Build variables dictionary for email template rendering.

    Args:
        template: EmailTemplate object
        target: Target object
        campaign: Campaign object

    Returns:
        Dictionary of template variables
    """
    from datetime import datetime

    # Get department name if available
    department_name = ""
    if target.department:
        department_name = target.department.name if hasattr(target.department, "name") else ""

    return {
        # Core target variables
        "salutation": target.salutation or "",
        "first_name": target.first_name or "",
        "last_name": target.last_name or "",
        "email": target.email or "",
        "position": target.position or "",
        "department": department_name,
        # Campaign information
        "campaign_name": campaign.name or "",
        # Sender information
        "sender_name": template.from_name or "",
        "sender_email": template.from_email or "",
        # Utility variables
        "year": str(datetime.now().year),
        # Tracking (to be set by email renderer)
        "tracking_url": "",
        "landing_page_url": "",
        "unsubscribe_url": "",
    }


# Create global database manager instance
db_manager = DatabaseManager()
