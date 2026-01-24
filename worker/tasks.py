"""
Celery tasks for Phishly phishing simulation platform.

This module defines asynchronous tasks for sending phishing emails,
tracking campaign status, and processing results.
"""

import os
import logging
from datetime import datetime
from celery import Celery

# Import worker modules
from database import (
    db_manager,
    get_campaign_details,
    get_target_details,
    get_campaign_target,
    create_email_job,
    update_email_job_status,
    update_campaign_target_status,
    log_event,
    get_email_template_variables,
)
from email_renderer import EmailRenderer
from email_sender import get_email_sender

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery("phishly")

# Configure Celery
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

app.conf.update(
    broker_url=f"redis://{REDIS_HOST}:{REDIS_PORT}/1",  # DB 1 for broker queue
    result_backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/2",  # DB 2 for results
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=270,  # Soft limit at 4.5 minutes
    worker_prefetch_multiplier=1,  # Only fetch one task at a time
    result_expires=3600,  # Results expire after 1 hour
    task_acks_late=True,  # Acknowledge tasks after completion
    task_reject_on_worker_lost=True,  # Reject tasks if worker dies
)

# Phishing domain configuration
PHISHING_DOMAIN = os.getenv("PHISHING_DOMAIN", "phishing.example.com")

# Initialize email renderer and sender
email_renderer = EmailRenderer(phishing_domain=PHISHING_DOMAIN)
email_sender = get_email_sender(mock=os.getenv("SMTP_MOCK", "false").lower() == "true")


@app.task(
    name="tasks.send_phishing_email",
    bind=True,
    autoretry_for=(Exception,),
    retry_kwargs={"max_retries": 3, "countdown": 60},
)
def send_phishing_email(self, campaign_id: int, target_id: int) -> dict:
    """
    Send a phishing email to a target as part of a campaign.

    This task will:
    1. Query PostgreSQL for campaign and target details
    2. Render the email template with personalization
    3. Send the email via SMTP
    4. Update the email_jobs table with status
    5. Log events to the events table

    Args:
        campaign_id: ID of the phishing campaign
        target_id: ID of the target employee

    Returns:
        dict: Result containing status and metadata

    Raises:
        Exception: Re-raised after updating database with failure status
    """
    task_id = self.request.id
    logger.info(
        f"Task {task_id} started: send_phishing_email("
        f"campaign_id={campaign_id}, target_id={target_id})"
    )

    email_job_id = None

    try:
        # Step 1: Query database for campaign and target details
        with db_manager.get_session() as session:
            # Get campaign details
            campaign = get_campaign_details(session, campaign_id)
            if not campaign:
                raise ValueError(f"Campaign not found: {campaign_id}")

            # Get target details
            target = get_target_details(session, target_id)
            if not target:
                raise ValueError(f"Target not found: {target_id}")

            # Get campaign-target assignment
            campaign_target = get_campaign_target(session, campaign_id, target_id)
            if not campaign_target:
                raise ValueError(
                    f"Campaign-target assignment not found: {campaign_id}, {target_id}"
                )

            # Get email template from campaign
            email_template = campaign.email_template
            if not email_template:
                raise ValueError(f"No email template found for campaign {campaign_id}")

            # Get landing page from campaign (or template default as fallback)
            landing_page = campaign.landing_page or getattr(
                email_template, "default_landing_page", None
            )
            if not landing_page:
                raise ValueError(f"No landing page found for campaign {campaign_id}")

            # Create email job record
            email_job = create_email_job(
                session,
                campaign_target_id=campaign_target.id,
                celery_task_id=task_id,
                scheduled_at=datetime.utcnow(),
            )
            email_job_id = email_job.id

            logger.info(
                f"Created email job {email_job_id} for campaign_target {campaign_target.id}"
            )

            # Get tracking token (or generate if not exists)
            tracking_token = campaign_target.tracking_token
            if not tracking_token:
                # Generate deterministic HMAC-based token for this campaign-target pair
                tracking_token = email_renderer.generate_tracking_token(
                    campaign_id=campaign_id, target_id=target_id
                )
                campaign_target.tracking_token = tracking_token
                session.flush()

            # Build template variables
            template_vars = get_email_template_variables(email_template, target, campaign)

            # Step 2: Render email template with landing page's domain
            html_content, text_content = email_renderer.render_email(
                html_template=email_template.body_html,
                text_template=email_template.body_text,
                variables=template_vars,
                tracking_token=tracking_token,
                landing_page_url=landing_page.url_path,
                phishing_domain=landing_page.domain,  # Use landing page's domain for links
            )

            # Render subject line
            subject = email_renderer.render_subject(
                subject_template=email_template.subject, variables=template_vars
            )

            logger.info(f"Email rendered for {target.email}: subject='{subject}'")

            # Step 3: Update email job status to 'sending'
            update_email_job_status(session, email_job_id, status="sending")

        # Step 4: Send email via SMTP (outside database transaction)
        email_sent = email_sender.send_email(
            to_email=target.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content,
            from_email=email_template.from_email,
            from_name=email_template.from_name,
            reply_to=email_template.from_email,
            custom_headers={
                "X-Campaign-ID": str(campaign_id),
                "X-Target-ID": str(target_id),
                "X-Tracking-Token": tracking_token,
                "X-Template-ID": str(email_template.id),
                "X-Template-Name": (email_template.name or "")[:50],
                "X-Phishly-Version": "1.0",
            },
        )

        if not email_sent:
            raise Exception("Email sending failed (returned False)")

        # Step 5: Update database with success status
        with db_manager.get_session() as session:
            # Update email job status
            update_email_job_status(session, email_job_id, status="sent", sent_at=datetime.utcnow())

            # Update campaign target status
            campaign_target = get_campaign_target(session, campaign_id, target_id)
            update_campaign_target_status(session, campaign_target.id, status="sent")

            # Log email_sent event
            log_event(
                session,
                campaign_target_id=campaign_target.id,
                event_type_name="email_sent",
                metadata=f'{{"task_id": "{task_id}"}}',
            )

        # Build success result
        result = {
            "status": "sent",
            "campaign_id": campaign_id,
            "target_id": target_id,
            "campaign_target_id": campaign_target.id,
            "email_job_id": email_job_id,
            "task_id": task_id,
            "to_email": target.email,
            "subject": subject,
            "tracking_token": tracking_token,
            "sent_at": datetime.utcnow().isoformat(),
            "message": "Email sent successfully",
        }

        logger.info(f"Task {task_id} completed successfully: {target.email}")
        return result

    except Exception as e:
        logger.error(f"Task {task_id} failed: {str(e)}", exc_info=True)

        # Update database with failure status
        if email_job_id:
            try:
                with db_manager.get_session() as session:
                    update_email_job_status(
                        session, email_job_id, status="failed", error_message=str(e)
                    )
            except Exception as db_error:
                logger.error(f"Failed to update email job status: {db_error}")

        # Re-raise exception for Celery retry mechanism
        raise


@app.task(name="tasks.test_task")
def test_task(message: str) -> dict:
    """
    Simple test task to verify Celery is working.

    Args:
        message: Test message string

    Returns:
        dict: Echo of the message with metadata
    """
    logger.info(f"Test task received: {message}")
    return {"status": "success", "message": message, "worker": "celery-worker"}


@app.task(name="tasks.send_campaign_batch")
def send_campaign_batch(campaign_id: int, target_ids: list) -> dict:
    """
    Send phishing emails to multiple targets in a campaign (batch processing).

    This task enqueues individual send_phishing_email tasks for each target.

    Args:
        campaign_id: ID of the phishing campaign
        target_ids: List of target IDs to send emails to

    Returns:
        dict: Result with task IDs and statistics
    """
    logger.info(f"Batch send started: campaign {campaign_id}, {len(target_ids)} targets")

    task_ids = []
    for target_id in target_ids:
        # Enqueue individual send task
        result = send_phishing_email.delay(campaign_id, target_id)
        task_ids.append({"target_id": target_id, "task_id": result.id})

    result = {
        "status": "queued",
        "campaign_id": campaign_id,
        "total_targets": len(target_ids),
        "tasks": task_ids,
        "message": f"Queued {len(target_ids)} email tasks for campaign {campaign_id}",
    }

    logger.info(f"Batch send completed: {result}")
    return result


@app.task(name="tasks.test_smtp_connection")
def test_smtp_connection() -> dict:
    """
    Test SMTP connection and configuration.

    Returns:
        dict: Connection test result
    """
    logger.info("Testing SMTP connection...")

    try:
        is_connected = email_sender.test_connection()

        result = {
            "status": "success" if is_connected else "failed",
            "smtp_host": email_sender.smtp_host,
            "smtp_port": email_sender.smtp_port,
            "smtp_use_tls": email_sender.smtp_use_tls,
            "smtp_use_ssl": email_sender.smtp_use_ssl,
            "message": "SMTP connection successful" if is_connected else "SMTP connection failed",
        }

        logger.info(f"SMTP test result: {result}")
        return result

    except Exception as e:
        logger.error(f"SMTP test failed: {e}")
        return {"status": "error", "message": str(e)}


@app.task(name="tasks.test_database_connection")
def test_database_connection() -> dict:
    """
    Test PostgreSQL database connection.

    Returns:
        dict: Connection test result
    """
    logger.info("Testing database connection...")

    try:
        is_connected = db_manager.test_connection()

        result = {
            "status": "success" if is_connected else "failed",
            "postgres_host": db_manager.host,
            "postgres_port": db_manager.port,
            "postgres_db": db_manager.database,
            "postgres_user": db_manager.user,
            "message": "Database connection successful"
            if is_connected
            else "Database connection failed",
        }

        logger.info(f"Database test result: {result}")
        return result

    except Exception as e:
        logger.error(f"Database test failed: {e}")
        return {"status": "error", "message": str(e)}


# Celery beat schedule (for periodic tasks - future use)
app.conf.beat_schedule = {
    # Example: Clean up old results every hour
    # 'cleanup-results': {
    #     'task': 'tasks.cleanup_old_results',
    #     'schedule': 3600.0,  # Run every hour
    # },
}


if __name__ == "__main__":
    # For testing tasks directly
    print("=" * 80)
    print("Phishly Celery Worker Configuration")
    print("=" * 80)
    print(f"Broker:     {app.conf.broker_url}")
    print(f"Backend:    {app.conf.result_backend}")
    print(
        f"PostgreSQL: postgresql://{db_manager.user}:***@"
        f"{db_manager.host}:{db_manager.port}/{db_manager.database}"
    )
    print(
        f"SMTP:       {email_sender.smtp_host}:{email_sender.smtp_port} "
        f"(TLS: {email_sender.smtp_use_tls})"
    )
    print(f"Phishing:   {PHISHING_DOMAIN}")
    print("=" * 80)
    print("\nRegistered tasks:")
    for task_name in sorted(app.tasks.keys()):
        if task_name.startswith("tasks."):
            print(f"  - {task_name}")
    print("=" * 80)
