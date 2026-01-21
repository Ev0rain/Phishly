from sqlalchemy import (
    BigInteger,
    Column,
    ForeignKey,
    UniqueConstraint,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(BigInteger, primary_key=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)  # Store bcrypt hash
    full_name = Column(String(255))
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_login = Column(DateTime)

    # Relationships
    target_lists = relationship("TargetList", back_populates="created_by")
    email_templates = relationship("EmailTemplate", back_populates="created_by")
    landing_pages = relationship("LandingPage", back_populates="created_by")
    campaigns = relationship("Campaign", back_populates="created_by")
    form_templates = relationship("FormTemplate", back_populates="created_by")


class Department(Base):
    __tablename__ = "departments"

    id = Column(BigInteger, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    targets = relationship("Target", back_populates="department")


class Target(Base):
    __tablename__ = "targets"

    id = Column(BigInteger, primary_key=True)
    department_id = Column(BigInteger, ForeignKey("departments.id"))
    email = Column(String(255), nullable=False, unique=True)
    salutation = Column(String(20))  # Mr., Ms., Mrs., Dr., Prof., Mx.
    first_name = Column(String(100))
    last_name = Column(String(100))
    position = Column(String(255))
    phone = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    department = relationship("Department", back_populates="targets")
    target_list_members = relationship("TargetListMember", back_populates="target")
    campaign_targets = relationship("CampaignTarget", back_populates="target")


class TargetList(Base):
    __tablename__ = "target_lists"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("AdminUser", back_populates="target_lists")
    target_list_members = relationship("TargetListMember", back_populates="target_list")
    campaign_target_lists = relationship("CampaignTargetList", back_populates="target_list")


class TargetListMember(Base):
    __tablename__ = "target_list_members"
    __table_args__ = (
        UniqueConstraint(
            "target_list_id",
            "target_id",
            name="target_list_members_target_list_id_target_id_key",
        ),
    )

    id = Column(BigInteger, primary_key=True)
    target_list_id = Column(BigInteger, ForeignKey("target_lists.id"))
    target_id = Column(BigInteger, ForeignKey("targets.id"))

    # Relationships
    target_list = relationship("TargetList", back_populates="target_list_members")
    target = relationship("Target", back_populates="target_list_members")


class EmailTemplate(Base):
    __tablename__ = "email_templates"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    default_landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"), nullable=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(500), nullable=False)
    body_html = Column(Text, nullable=False)
    body_text = Column(Text)  # Plain text fallback
    from_name = Column(String(255))
    from_email = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("AdminUser", back_populates="email_templates")
    default_landing_page = relationship("LandingPage", back_populates="email_templates")
    campaigns = relationship("Campaign", back_populates="email_template")


class LandingPage(Base):
    __tablename__ = "landing_pages"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    name = Column(String(255), nullable=False)
    url_path = Column(String(255), unique=True, nullable=False)  # e.g., /login-portal
    domain = Column(String(255))  # e.g., phishing.example.com or full URL https://phishing.example.com/login

    # DEPRECATED: Content columns - use template_path instead
    # These columns are kept for backwards compatibility during migration
    html_content = Column(Text)  # Now nullable - use template_path for new pages
    css_content = Column(Text)
    js_content = Column(Text)

    # NEW: Filesystem path to template directory (e.g., "phish-page", "info_page")
    template_path = Column(String(500))  # Path relative to /templates/landing_pages/

    capture_credentials = Column(Boolean, default=False)
    capture_form_data = Column(Boolean, default=True)
    redirect_url = Column(String(500))  # Where to redirect after submission
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("AdminUser", back_populates="landing_pages")
    campaigns = relationship("Campaign", back_populates="landing_page")
    email_templates = relationship("EmailTemplate", back_populates="default_landing_page")
    form_templates = relationship("FormTemplate", back_populates="landing_page")


class ActiveConfiguration(Base):
    """Singleton table for active landing page configuration."""
    __tablename__ = "active_configuration"

    id = Column(BigInteger, primary_key=True)  # Always 1 (singleton)
    active_landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"), nullable=True)
    activated_at = Column(DateTime)
    activated_by_id = Column(BigInteger, ForeignKey("admin_users.id"), nullable=True)
    dns_zone_file_path = Column(String(500))
    phishing_domain = Column(String(255))
    public_ip = Column(String(45))  # IPv4/IPv6 for DNS A record
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow)

    # Relationships
    active_landing_page = relationship("LandingPage")
    activated_by = relationship("AdminUser")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    email_template_id = Column(BigInteger, ForeignKey("email_templates.id"))
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(
        String(50), default="draft", nullable=False
    )  # draft, scheduled, active, paused, completed
    min_email_delay = Column(Integer, default=30)  # Minimum delay in seconds between emails
    max_email_delay = Column(Integer, default=180)  # Maximum delay in seconds between emails
    scheduled_launch = Column(DateTime)  # When to automatically launch the campaign
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    created_by = relationship("AdminUser", back_populates="campaigns")
    email_template = relationship("EmailTemplate", back_populates="campaigns")
    landing_page = relationship("LandingPage", back_populates="campaigns")
    campaign_target_lists = relationship("CampaignTargetList", back_populates="campaign")
    campaign_targets = relationship("CampaignTarget", back_populates="campaign")


class CampaignTargetList(Base):
    __tablename__ = "campaign_target_lists"
    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "target_list_id",
            name="campaign_target_lists_campaign_id_target_list_id_key",
        ),
    )

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id"))
    target_list_id = Column(BigInteger, ForeignKey("target_lists.id"))

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_target_lists")
    target_list = relationship("TargetList", back_populates="campaign_target_lists")


class CampaignTarget(Base):
    __tablename__ = "campaign_targets"
    __table_args__ = (
        UniqueConstraint(
            "campaign_id",
            "target_id",
            name="campaign_targets_campaign_id_target_id_key",
        ),
    )

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id"))
    target_id = Column(BigInteger, ForeignKey("targets.id"))
    tracking_token = Column(String(255), unique=True)  # Unique token for tracking
    # Removed email_template_id and landing_page_id - now inherited from campaign
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, sent, opened, clicked, submitted
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_targets")
    target = relationship("Target", back_populates="campaign_targets")
    email_jobs = relationship("EmailJob", back_populates="campaign_target")
    events = relationship("Event", back_populates="campaign_target")
    form_submissions = relationship("FormSubmission", back_populates="campaign_target")


class EmailJob(Base):
    __tablename__ = "email_jobs"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    celery_task_id = Column(String(255))  # Celery task ID for revocation
    status = Column(
        String(50), default="pending", nullable=False
    )  # pending, queued, sending, sent, failed, bounced, revoked
    scheduled_at = Column(DateTime)  # When the email is scheduled to be sent
    sent_at = Column(DateTime)  # Actual send time
    delay_seconds = Column(Integer)  # Random delay assigned for this email
    error_message = Column(Text)  # Error details if failed
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign_target = relationship("CampaignTarget", back_populates="email_jobs")


class EventType(Base):
    __tablename__ = "event_types"

    id = Column(BigInteger, primary_key=True)
    name = Column(
        String(100), unique=True, nullable=False
    )  # e.g., "email_sent", "email_opened", "link_clicked", "form_submitted"
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    events = relationship("Event", back_populates="event_type")


class Event(Base):
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    event_type_id = Column(BigInteger, ForeignKey("event_types.id"))
    ip_address = Column(String(45))  # IPv4 or IPv6
    user_agent = Column(Text)
    browser = Column(String(100))
    os = Column(String(100))
    device_type = Column(String(50))  # mobile, desktop, tablet
    location = Column(String(255))  # Geolocation if available
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    campaign_target = relationship("CampaignTarget", back_populates="events")
    event_type = relationship("EventType", back_populates="events")


class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(BigInteger, primary_key=True)
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    landing_page = relationship("LandingPage", back_populates="form_templates")
    created_by = relationship("AdminUser", back_populates="form_templates")
    form_questions = relationship("FormQuestion", back_populates="form_template")
    form_submissions = relationship("FormSubmission", back_populates="form_template")


class FormQuestion(Base):
    __tablename__ = "form_questions"

    id = Column(BigInteger, primary_key=True)
    form_template_id = Column(BigInteger, ForeignKey("form_templates.id"))
    question_text = Column(Text, nullable=False)
    question_type = Column(
        String(50), nullable=False
    )  # text, email, select, radio, checkbox, textarea
    is_required = Column(Boolean, default=False)
    options = Column(Text)  # JSON string for select/radio/checkbox options
    order = Column(Integer, default=0)  # Display order
    placeholder = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    form_template = relationship("FormTemplate", back_populates="form_questions")
    form_answers = relationship("FormAnswer", back_populates="form_question")


class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    form_template_id = Column(BigInteger, ForeignKey("form_templates.id"))
    submitted_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String(45))
    user_agent = Column(Text)

    # Relationships
    campaign_target = relationship("CampaignTarget", back_populates="form_submissions")
    form_template = relationship("FormTemplate", back_populates="form_submissions")
    form_answers = relationship("FormAnswer", back_populates="form_submission")


class FormAnswer(Base):
    __tablename__ = "form_answers"

    id = Column(BigInteger, primary_key=True)
    form_submission_id = Column(BigInteger, ForeignKey("form_submissions.id"))
    form_question_id = Column(BigInteger, ForeignKey("form_questions.id"))
    answer_text = Column(Text)  # Store all answer types as text (JSON if needed)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    form_submission = relationship("FormSubmission", back_populates="form_answers")
    form_question = relationship("FormQuestion", back_populates="form_answers")
