"""
Campaigns Blueprint - Campaign management and creation
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from repositories.campaign_repository import CampaignRepository
from database import db
from db.models import Campaign, CampaignTarget, EmailJob, Target
from datetime import datetime, timedelta
from celery import Celery
import os
import logging
import random

from utils.cache_manager import (
    cache_landing_page,
    clear_campaign_cache,
    generate_task_id,
)

campaigns_bp = Blueprint("campaigns", __name__)

# Initialize repository (now using real database)
campaign_repo = CampaignRepository()

# Initialize Celery client for triggering tasks
logger = logging.getLogger(__name__)
REDIS_HOST = os.getenv("REDIS_HOST", "redis-cache")
REDIS_PORT = os.getenv("REDIS_PORT", "6379")

celery_app = Celery(
    "phishly",
    broker=f"redis://{REDIS_HOST}:{REDIS_PORT}/1",
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/2",
)


@campaigns_bp.route("/campaigns")
@login_required
def index():
    """Campaigns overview page"""
    campaigns = campaign_repo.get_all_campaigns()
    templates = campaign_repo.get_email_templates()
    groups = campaign_repo.get_target_groups()

    return render_template(
        "campaigns.html", campaigns=campaigns, templates=templates, groups=groups
    )


@campaigns_bp.route("/campaigns/create", methods=["POST"])
@login_required
def create():
    """
    Create new campaign with database integration
    """
    campaign_name = request.form.get("campaign_name")
    description = request.form.get("description", "")
    template_id = request.form.get("template_id")
    group_ids = request.form.getlist("group_ids")  # Support multiple groups

    # Delay settings
    delay_type = request.form.get("delay_type", "random")
    min_delay = request.form.get("min_delay", "30")
    max_delay = request.form.get("max_delay", "180")

    # Schedule settings
    schedule_later = request.form.get("schedule_later") == "on"
    scheduled_launch = request.form.get("scheduled_launch")

    # Validate required fields
    if not campaign_name or not template_id:
        return (
            jsonify({"success": False, "message": "Campaign name and template are required"}),
            400,
        )

    # Convert IDs to integers
    try:
        template_id = int(template_id)
        group_ids = [int(gid) for gid in group_ids if gid]
    except ValueError:
        return jsonify({"success": False, "message": "Invalid template or group ID"}), 400

    if not group_ids:
        return jsonify({"success": False, "message": "At least one target group is required"}), 400

    # Process delay settings
    try:
        if delay_type == "none":
            min_delay_seconds = 0
            max_delay_seconds = 0
        elif delay_type == "fixed":
            min_delay_seconds = int(min_delay)
            max_delay_seconds = int(min_delay)  # Same value for fixed
        else:  # random
            min_delay_seconds = int(min_delay)
            max_delay_seconds = int(max_delay)
    except ValueError:
        return jsonify({"success": False, "message": "Invalid delay values"}), 400

    # Process scheduled launch
    scheduled_launch_dt = None
    if schedule_later and scheduled_launch:
        try:
            scheduled_launch_dt = datetime.fromisoformat(scheduled_launch)
        except ValueError:
            return jsonify({"success": False, "message": "Invalid scheduled launch date/time"}), 400

    # Create campaign in database
    campaign = campaign_repo.create_campaign(
        name=campaign_name,
        description=description,
        email_template_id=template_id,
        target_list_ids=group_ids,
        status="scheduled" if scheduled_launch_dt else "draft",
        created_by_id=current_user.id if hasattr(current_user, "id") else None,
        min_email_delay=min_delay_seconds,
        max_email_delay=max_delay_seconds,
        scheduled_launch=scheduled_launch_dt,
    )

    if campaign:
        status_msg = "scheduled" if scheduled_launch_dt else "created"
        return jsonify(
            {
                "success": True,
                "message": f"Campaign '{campaign_name}' {status_msg} successfully",
                "campaign": campaign,
            }
        )
    else:
        return (
            jsonify({"success": False, "message": "Failed to create campaign. Please check logs."}),
            500,
        )


@campaigns_bp.route("/campaigns/<int:campaign_id>/launch", methods=["POST"])
@login_required
def launch_campaign(campaign_id):
    """
    Launch campaign - change status to active, cache landing page, queue emails,
    and trigger Celery tasks with custom task IDs
    """
    try:
        # Get campaign with relationships
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({"success": False, "message": "Campaign not found"}), 404

        if campaign.status == "active":
            return jsonify({"success": False, "message": "Campaign is already active"}), 400

        # Get all targets for this campaign
        campaign_targets = db.session.query(CampaignTarget).filter_by(campaign_id=campaign_id).all()

        if not campaign_targets:
            return jsonify({"success": False, "message": "Campaign has no targets"}), 400

        # Cache the landing page for fast serving
        landing_page = campaign.landing_page
        if landing_page:
            cache_result = cache_landing_page(campaign_id, landing_page)
            if cache_result:
                logger.info(f"Cached landing page for campaign {campaign_id}")
            else:
                logger.warning(f"Failed to cache landing page for campaign {campaign_id}")
        else:
            logger.warning(f"Campaign {campaign_id} has no landing page to cache")

        # Update campaign status
        campaign.status = "active"
        campaign.start_date = datetime.utcnow()

        # Get delay settings from campaign
        min_delay = campaign.min_email_delay or 0
        max_delay = campaign.max_email_delay or 0

        # Create email jobs and trigger Celery tasks
        jobs_created = 0
        tasks_queued = 0
        cumulative_delay = 0  # Track total delay for sequential scheduling

        for idx, campaign_target in enumerate(campaign_targets):
            # Calculate delay for this email
            if min_delay == 0 and max_delay == 0:
                # No delay - send immediately
                delay_seconds = 0
            elif min_delay == max_delay:
                # Fixed delay
                delay_seconds = min_delay
            else:
                # Random delay between min and max
                delay_seconds = random.randint(min_delay, max_delay)

            # Calculate scheduled time (cumulative for sequential sending)
            scheduled_time = datetime.utcnow() + timedelta(seconds=cumulative_delay)
            cumulative_delay += delay_seconds

            # Create email job record
            email_job = EmailJob(
                campaign_target_id=campaign_target.id,
                status="queued",
                scheduled_at=scheduled_time,
                delay_seconds=delay_seconds,
            )
            db.session.add(email_job)
            db.session.flush()  # Get the email_job.id
            jobs_created += 1

            # Trigger Celery task to send email
            try:
                # Get target details
                target = db.session.get(Target, campaign_target.target_id)

                if target:
                    # Generate campaign-specific task ID
                    task_id = generate_task_id(campaign_id, target.id)

                    # Queue the task asynchronously with custom task_id and countdown
                    task = celery_app.send_task(
                        "tasks.send_phishing_email",
                        args=[campaign_id, target.id],
                        kwargs={},
                        task_id=task_id,
                        queue="default",
                        countdown=cumulative_delay - delay_seconds,  # Delay before executing
                    )

                    tasks_queued += 1

                    log_msg = (
                        f"Queued Celery task {task_id} for campaign "
                        f"{campaign_id}, target {target.id} (delay: {cumulative_delay - delay_seconds}s)"
                    )
                    logger.info(log_msg)
                else:
                    logger.warning(f"Target {campaign_target.target_id} not found, skipping")
                    email_job.status = "failed"
                    email_job.error_message = "Target not found"

            except Exception as task_error:
                logger.error(f"Error queuing Celery task: {task_error}")
                email_job.status = "failed"
                email_job.error_message = str(task_error)

        db.session.commit()

        success_msg = (
            f"Campaign launched! {jobs_created} email jobs created, "
            f"{tasks_queued} tasks queued for sending."
        )
        return jsonify(
            {
                "success": True,
                "message": success_msg,
                "jobs_created": jobs_created,
                "tasks_queued": tasks_queued,
            }
        )

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error launching campaign: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Error launching campaign: {str(e)}"}), 500


@campaigns_bp.route("/campaigns/<int:campaign_id>/pause", methods=["POST"])
@login_required
def pause_campaign(campaign_id):
    """
    Pause an active campaign
    """
    try:
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({"success": False, "message": "Campaign not found"}), 404

        if campaign.status != "active":
            return (
                jsonify({"success": False, "message": "Only active campaigns can be paused"}),
                400,
            )

        campaign.status = "paused"
        campaign.completed_date = datetime.utcnow()
        db.session.commit()

        return jsonify({"success": True, "message": "Campaign paused successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error pausing campaign: {str(e)}"}), 500


@campaigns_bp.route("/campaigns/<int:campaign_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_campaign(campaign_id):
    """
    Delete a campaign (only if in draft status)
    """
    try:
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({"success": False, "message": "Campaign not found"}), 404

        if campaign.status == "active":
            return (
                jsonify(
                    {"success": False, "message": "Cannot delete active campaign. Pause it first."}
                ),
                400,
            )

        campaign_name = campaign.name

        # Clear cached landing pages
        clear_campaign_cache(campaign_id)

        db.session.delete(campaign)
        db.session.commit()

        return jsonify(
            {"success": True, "message": f"Campaign '{campaign_name}' deleted successfully"}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error deleting campaign: {str(e)}"}), 500


@campaigns_bp.route("/campaigns/<int:campaign_id>/details", methods=["GET"])
@login_required
def get_campaign_details(campaign_id):
    """
    Get detailed campaign information including template and targets with email status
    """
    try:
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({"success": False, "message": "Campaign not found"}), 404

        # Get template info
        template_info = None
        if campaign.email_template:
            template_info = {
                "id": campaign.email_template.id,
                "name": campaign.email_template.name,
                "subject": campaign.email_template.subject,
                "from_name": campaign.email_template.from_name,
                "from_email": campaign.email_template.from_email,
            }

        # Get targets with their email status
        targets_list = []
        for ct in campaign.campaign_targets:
            target = ct.target
            if target:
                # Check email job status
                email_status = "pending"
                sent_at = None
                if ct.email_jobs:
                    # Get the latest email job
                    latest_job = max(ct.email_jobs, key=lambda j: j.created_at)
                    email_status = latest_job.status
                    sent_at = latest_job.sent_at.isoformat() if latest_job.sent_at else None

                targets_list.append({
                    "id": target.id,
                    "email": target.email,
                    "first_name": target.first_name,
                    "last_name": target.last_name,
                    "position": target.position,
                    "email_status": email_status,
                    "sent_at": sent_at,
                    "target_status": ct.status,
                })

        return jsonify({
            "success": True,
            "campaign": {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "status": campaign.status,
                "created_at": campaign.created_at.isoformat() if campaign.created_at else None,
                "start_date": campaign.start_date.isoformat() if campaign.start_date else None,
                "scheduled_launch": campaign.scheduled_launch.isoformat() if campaign.scheduled_launch else None,
                "min_email_delay": campaign.min_email_delay,
                "max_email_delay": campaign.max_email_delay,
            },
            "template": template_info,
            "targets": targets_list,
            "total_targets": len(targets_list),
            "emails_sent": sum(1 for t in targets_list if t["email_status"] == "sent"),
        })

    except Exception as e:
        logger.error(f"Error getting campaign details: {e}", exc_info=True)
        return jsonify({"success": False, "message": f"Error: {str(e)}"}), 500
