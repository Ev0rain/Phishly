"""
Celery tasks for Phishly phishing simulation platform.

This module defines asynchronous tasks for sending phishing emails,
tracking campaign status, and processing results.
"""

import os
import logging
from celery import Celery

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Celery app
app = Celery('phishly')

# Configure Celery
REDIS_HOST = os.getenv('REDIS_HOST', 'redis')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')

app.conf.update(
    broker_url=f'redis://{REDIS_HOST}:{REDIS_PORT}/1',  # DB 1 for broker queue
    result_backend=f'redis://{REDIS_HOST}:{REDIS_PORT}/2',  # DB 2 for results
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes max per task
    task_soft_time_limit=270,  # Soft limit at 4.5 minutes
    worker_prefetch_multiplier=1,  # Only fetch one task at a time
    result_expires=3600,  # Results expire after 1 hour
)

# Database connection settings (for future use)
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'postgres-db')
POSTGRES_PORT = os.getenv('POSTGRES_PORT', '5432')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'phishly')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'admin')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')


@app.task(name='tasks.send_phishing_email', bind=True)
def send_phishing_email(self, campaign_id: int, target_id: int) -> dict:
    """
    Send a phishing email to a target as part of a campaign.

    This task will:
    1. Query PostgreSQL for campaign and target details
    2. Render the email template
    3. Send the email via SMTP (future implementation)
    4. Update the email_jobs table with status
    5. Log events to the events table

    Args:
        campaign_id: ID of the phishing campaign
        target_id: ID of the target employee

    Returns:
        dict: Result containing status and metadata
    """
    logger.info(f"Task started: send_phishing_email(campaign_id={campaign_id}, target_id={target_id})")

    try:
        # TODO: Connect to PostgreSQL and query campaign details
        # Example:
        # from sqlalchemy import create_engine
        # engine = create_engine(f'postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}')
        # campaign = query_campaign(engine, campaign_id)
        # target = query_target(engine, target_id)

        # TODO: Render email template with campaign data
        # email_body = render_template(campaign.email_template, target)

        # TODO: Send email via SMTP
        # send_email(
        #     to=target.email,
        #     subject=campaign.subject,
        #     body=email_body,
        #     from_addr=campaign.sender_email
        # )

        # TODO: Update email_jobs status in PostgreSQL
        # update_email_job_status(engine, campaign_id, target_id, status='sent')

        # TODO: Log event to events table
        # log_event(engine, campaign_target_id, event_type='email_sent')

        # For now, just return a success message
        result = {
            'status': 'sent',
            'campaign_id': campaign_id,
            'target_id': target_id,
            'task_id': self.request.id,
            'message': 'Email would be sent here (SMTP not yet implemented)'
        }

        logger.info(f"Task completed: {result}")
        return result

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        # TODO: Update email_jobs status to 'failed' in PostgreSQL
        raise


@app.task(name='tasks.test_task')
def test_task(message: str) -> dict:
    """
    Simple test task to verify Celery is working.

    Args:
        message: Test message string

    Returns:
        dict: Echo of the message with metadata
    """
    logger.info(f"Test task received: {message}")
    return {
        'status': 'success',
        'message': message,
        'worker': 'celery-worker'
    }


# Celery beat schedule (for periodic tasks - future use)
app.conf.beat_schedule = {
    # Example: Clean up old results every hour
    # 'cleanup-results': {
    #     'task': 'tasks.cleanup_old_results',
    #     'schedule': 3600.0,  # Run every hour
    # },
}


if __name__ == '__main__':
    # For testing tasks directly
    print("Celery app configuration:")
    print(f"  Broker: {app.conf.broker_url}")
    print(f"  Backend: {app.conf.result_backend}")
    print(f"  PostgreSQL: postgresql://{POSTGRES_USER}:***@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}")
