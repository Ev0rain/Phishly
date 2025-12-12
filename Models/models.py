from sqlalchemy import BigInteger, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(BigInteger, primary_key=True)

    # Relationships
    target_lists = relationship("TargetList", back_populates="created_by")
    email_templates = relationship("EmailTemplate", back_populates="created_by")
    landing_pages = relationship("LandingPage", back_populates="created_by")
    campaigns = relationship("Campaign", back_populates="created_by")
    form_templates = relationship("FormTemplate", back_populates="created_by")


class Department(Base):
    __tablename__ = "departments"

    id = Column(BigInteger, primary_key=True)

    # Relationships
    targets = relationship("Target", back_populates="department")


class Target(Base):
    __tablename__ = "targets"

    id = Column(BigInteger, primary_key=True)
    department_id = Column(BigInteger, ForeignKey("departments.id"))

    # Relationships
    department = relationship("Department", back_populates="targets")
    target_list_members = relationship("TargetListMember", back_populates="target")
    campaign_targets = relationship("CampaignTarget", back_populates="target")


class TargetList(Base):
    __tablename__ = "target_lists"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))

    # Relationships
    created_by = relationship("AdminUser", back_populates="target_lists")
    target_list_members = relationship("TargetListMember", back_populates="target_list")
    campaign_target_lists = relationship("CampaignTargetList", back_populates="target_list")


class TargetListMember(Base):
    __tablename__ = "target_list_members"
    __table_args__ = (
        UniqueConstraint("target_list_id", "target_id", name="target_list_members_target_list_id_target_id_key"),
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

    # Relationships
    created_by = relationship("AdminUser", back_populates="email_templates")
    campaigns = relationship("Campaign", back_populates="email_template")
    campaign_targets = relationship("CampaignTarget", back_populates="email_template")


class LandingPage(Base):
    __tablename__ = "landing_pages"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))

    # Relationships
    created_by = relationship("AdminUser", back_populates="landing_pages")
    campaigns = relationship("Campaign", back_populates="landing_page")
    campaign_targets = relationship("CampaignTarget", back_populates="landing_page")
    form_templates = relationship("FormTemplate", back_populates="landing_page")


class Campaign(Base):
    __tablename__ = "campaigns"

    id = Column(BigInteger, primary_key=True)
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))
    email_template_id = Column(BigInteger, ForeignKey("email_templates.id"))
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))

    # Relationships
    created_by = relationship("AdminUser", back_populates="campaigns")
    email_template = relationship("EmailTemplate", back_populates="campaigns")
    landing_page = relationship("LandingPage", back_populates="campaigns")
    campaign_target_lists = relationship("CampaignTargetList", back_populates="campaign")
    campaign_targets = relationship("CampaignTarget", back_populates="campaign")


class CampaignTargetList(Base):
    __tablename__ = "campaign_target_lists"
    __table_args__ = (
        UniqueConstraint("campaign_id", "target_list_id", name="campaign_target_lists_campaign_id_target_list_id_key"),
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
        UniqueConstraint("campaign_id", "target_id", name="campaign_targets_campaign_id_target_id_key"),
    )

    id = Column(BigInteger, primary_key=True)
    campaign_id = Column(BigInteger, ForeignKey("campaigns.id"))
    target_id = Column(BigInteger, ForeignKey("targets.id"))
    email_template_id = Column(BigInteger, ForeignKey("email_templates.id"))
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))

    # Relationships
    campaign = relationship("Campaign", back_populates="campaign_targets")
    target = relationship("Target", back_populates="campaign_targets")
    email_template = relationship("EmailTemplate", back_populates="campaign_targets")
    landing_page = relationship("LandingPage", back_populates="campaign_targets")
    email_jobs = relationship("EmailJob", back_populates="campaign_target")
    events = relationship("Event", back_populates="campaign_target")
    form_submissions = relationship("FormSubmission", back_populates="campaign_target")


class EmailJob(Base):
    __tablename__ = "email_jobs"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))

    # Relationships
    campaign_target = relationship("CampaignTarget", back_populates="email_jobs")


class EventType(Base):
    __tablename__ = "event_types"

    id = Column(BigInteger, primary_key=True)

    # Relationships
    events = relationship("Event", back_populates="event_type")


class Event(Base):
    __tablename__ = "events"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    event_type_id = Column(BigInteger, ForeignKey("event_types.id"))

    # Relationships
    campaign_target = relationship("CampaignTarget", back_populates="events")
    event_type = relationship("EventType", back_populates="events")


class FormTemplate(Base):
    __tablename__ = "form_templates"

    id = Column(BigInteger, primary_key=True)
    landing_page_id = Column(BigInteger, ForeignKey("landing_pages.id"))
    created_by_id = Column(BigInteger, ForeignKey("admin_users.id"))

    # Relationships
    landing_page = relationship("LandingPage", back_populates="form_templates")
    created_by = relationship("AdminUser", back_populates="form_templates")
    form_questions = relationship("FormQuestion", back_populates="form_template")
    form_submissions = relationship("FormSubmission", back_populates="form_template")


class FormQuestion(Base):
    __tablename__ = "form_questions"

    id = Column(BigInteger, primary_key=True)
    form_template_id = Column(BigInteger, ForeignKey("form_templates.id"))

    # Relationships
    form_template = relationship("FormTemplate", back_populates="form_questions")
    form_answers = relationship("FormAnswer", back_populates="form_question")


class FormSubmission(Base):
    __tablename__ = "form_submissions"

    id = Column(BigInteger, primary_key=True)
    campaign_target_id = Column(BigInteger, ForeignKey("campaign_targets.id"))
    form_template_id = Column(BigInteger, ForeignKey("form_templates.id"))

    # Relationships
    campaign_target = relationship("CampaignTarget", back_populates="form_submissions")
    form_template = relationship("FormTemplate", back_populates="form_submissions")
    form_answers = relationship("FormAnswer", back_populates="form_submission")


class FormAnswer(Base):
    __tablename__ = "form_answers"

    id = Column(BigInteger, primary_key=True)
    form_submission_id = Column(BigInteger, ForeignKey("form_submissions.id"))
    form_question_id = Column(BigInteger, ForeignKey("form_questions.id"))

    # Relationships
    form_submission = relationship("FormSubmission", back_populates="form_answers")
    form_question = relationship("FormQuestion", back_populates="form_answers")
