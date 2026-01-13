"""
Campaigns Blueprint - Campaign management and creation
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from repositories.campaign_repository import CampaignRepository
from database import db
from db.models import Campaign, CampaignTarget, EmailJob, Target
from datetime import datetime
from celery import Celery
import os
import logging

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
    backend=f"redis://{REDIS_HOST}:{REDIS_PORT}/2"
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

    # Validate required fields
    if not campaign_name or not template_id:
        return jsonify({
            "success": False,
            "message": "Campaign name and template are required"
        }), 400

    # Convert IDs to integers
    try:
        template_id = int(template_id)
        group_ids = [int(gid) for gid in group_ids if gid]
    except ValueError:
        return jsonify({
            "success": False,
            "message": "Invalid template or group ID"
        }), 400

    if not group_ids:
        return jsonify({
            "success": False,
            "message": "At least one target group is required"
        }), 400

    # Create campaign in database
    campaign = campaign_repo.create_campaign(
        name=campaign_name,
        description=description,
        email_template_id=template_id,
        target_list_ids=group_ids,
        status='draft',
        created_by_id=current_user.id if hasattr(current_user, 'id') else None
    )

    if campaign:
        return jsonify({
            "success": True,
            "message": f"Campaign '{campaign_name}' created successfully",
            "campaign": campaign
        })
    else:
        return jsonify({
            "success": False,
            "message": "Failed to create campaign. Please check logs."
        }), 500


@campaigns_bp.route("/campaigns/<int:campaign_id>/launch", methods=["POST"])
@login_required
def launch_campaign(campaign_id):
    """
    Launch campaign - change status to active, queue emails, and trigger Celery tasks
    """
    try:
        # Get campaign
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({
                "success": False,
                "message": "Campaign not found"
            }), 404

        if campaign.status == 'active':
            return jsonify({
                "success": False,
                "message": "Campaign is already active"
            }), 400

        # Get all targets for this campaign
        campaign_targets = db.session.query(CampaignTarget)\
            .filter_by(campaign_id=campaign_id)\
            .all()

        if not campaign_targets:
            return jsonify({
                "success": False,
                "message": "Campaign has no targets"
            }), 400

        # Update campaign status
        campaign.status = 'active'
        campaign.launch_date = datetime.utcnow()

        # Create email jobs and trigger Celery tasks
        jobs_created = 0
        tasks_queued = 0

        for campaign_target in campaign_targets:
            # Create email job record
            email_job = EmailJob(
                campaign_target_id=campaign_target.id,
                status='queued',
                scheduled_time=datetime.utcnow()
            )
            db.session.add(email_job)
            db.session.flush()  # Get the email_job.id
            jobs_created += 1

            # Trigger Celery task to send email
            try:
                # Get target details
                target = db.session.get(Target, campaign_target.target_id)

                if target:
                    # Queue the task asynchronously
                    task = celery_app.send_task(
                        'tasks.send_phishing_email',
                        args=[campaign_id, target.id],
                        kwargs={},
                        queue='default'
                    )

                    # Update email job with Celery task ID
                    email_job.celery_task_id = task.id
                    tasks_queued += 1

                    logger.info(f"Queued Celery task {task.id} for campaign {campaign_id}, target {target.id}")
                else:
                    logger.warning(f"Target {campaign_target.target_id} not found, skipping")
                    email_job.status = 'failed'
                    email_job.error_message = 'Target not found'

            except Exception as task_error:
                logger.error(f"Error queuing Celery task: {task_error}")
                email_job.status = 'failed'
                email_job.error_message = str(task_error)

        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Campaign launched! {jobs_created} email jobs created, {tasks_queued} tasks queued for sending.",
            "jobs_created": jobs_created,
            "tasks_queued": tasks_queued
        })

    except Exception as e:
        db.session.rollback()
        logger.error(f"Error launching campaign: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "message": f"Error launching campaign: {str(e)}"
        }), 500


@campaigns_bp.route("/campaigns/<int:campaign_id>/pause", methods=["POST"])
@login_required
def pause_campaign(campaign_id):
    """
    Pause an active campaign
    """
    try:
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({
                "success": False,
                "message": "Campaign not found"
            }), 404

        if campaign.status != 'active':
            return jsonify({
                "success": False,
                "message": "Only active campaigns can be paused"
            }), 400

        campaign.status = 'paused'
        campaign.completed_date = datetime.utcnow()
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Campaign paused successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error pausing campaign: {str(e)}"
        }), 500


@campaigns_bp.route("/campaigns/<int:campaign_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_campaign(campaign_id):
    """
    Delete a campaign (only if in draft status)
    """
    try:
        campaign = db.session.get(Campaign, campaign_id)

        if not campaign:
            return jsonify({
                "success": False,
                "message": "Campaign not found"
            }), 404

        if campaign.status == 'active':
            return jsonify({
                "success": False,
                "message": "Cannot delete active campaign. Pause it first."
            }), 400

        campaign_name = campaign.name
        db.session.delete(campaign)
        db.session.commit()

        return jsonify({
            "success": True,
            "message": f"Campaign '{campaign_name}' deleted successfully"
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "message": f"Error deleting campaign: {str(e)}"
        }), 500

