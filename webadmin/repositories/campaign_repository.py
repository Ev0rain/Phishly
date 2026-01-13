"""
Campaign Repository - Real database implementation

Handles all campaign-related database queries for the webadmin
"""

from repositories.base_repository import BaseRepository
from database import db, get_event_type_id
from db.models import (
    Campaign, CampaignTarget, CampaignTargetList,
    EmailTemplate, TargetList, Event, EventType
)
from sqlalchemy import func
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class CampaignRepository(BaseRepository):
    """Real database repository for campaigns"""

    @staticmethod
    def get_dashboard_stats():
        """
        Return dashboard statistics from database.

        Returns:
            dict: Dashboard KPIs (total campaigns, emails sent, open/click rates, etc.)
        """
        try:
            # Total campaigns
            total_campaigns = db.session.query(func.count(Campaign.id)).scalar() or 0

            # Active campaigns
            active_campaigns = db.session.query(func.count(Campaign.id))\
                .filter(Campaign.status == 'active').scalar() or 0

            # Total unique targets across all campaigns
            total_targets = db.session.query(func.count(func.distinct(CampaignTarget.target_id))).scalar() or 0

            # Get event type IDs (cached)
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Count events by type
            emails_sent = db.session.query(func.count(Event.id))\
                .filter(Event.event_type_id == event_sent_id).scalar() if event_sent_id else 0

            emails_opened = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                .filter(Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

            links_clicked = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                .filter(Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

            credentials_submitted = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                .filter(Event.event_type_id == event_submitted_id).scalar() if event_submitted_id else 0

            # Calculate rates
            open_rate = round((emails_opened / emails_sent * 100), 1) if emails_sent > 0 else 0.0
            click_rate = round((links_clicked / emails_sent * 100), 1) if emails_sent > 0 else 0.0
            submission_rate = round((credentials_submitted / emails_sent * 100), 1) if emails_sent > 0 else 0.0

            return {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_targets": total_targets,
                "emails_sent": emails_sent or 0,
                "emails_opened": emails_opened or 0,
                "links_clicked": links_clicked or 0,
                "credentials_submitted": credentials_submitted or 0,
                "open_rate": open_rate,
                "click_rate": click_rate,
                "submission_rate": submission_rate,
            }

        except Exception as e:
            logger.error(f"Error getting dashboard stats: {e}")
            # Return zeros if query fails
            return {
                "total_campaigns": 0,
                "active_campaigns": 0,
                "total_targets": 0,
                "emails_sent": 0,
                "emails_opened": 0,
                "links_clicked": 0,
                "credentials_submitted": 0,
                "open_rate": 0.0,
                "click_rate": 0.0,
                "submission_rate": 0.0,
            }

    @staticmethod
    def get_recent_campaigns(limit=5):
        """
        Return list of recent campaigns with engagement metrics.

        Args:
            limit: Maximum number of campaigns to return

        Returns:
            list: Recent campaigns with stats
        """
        try:
            campaigns = Campaign.query.order_by(Campaign.created_at.desc()).limit(limit).all()

            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')

            result = []
            for c in campaigns:
                # Count targets for this campaign
                targets = db.session.query(func.count(CampaignTarget.id))\
                    .filter(CampaignTarget.campaign_id == c.id).scalar() or 0

                # Count opened events for this campaign
                opened = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == c.id)\
                    .filter(Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

                # Count clicked events for this campaign
                clicked = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == c.id)\
                    .filter(Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

                result.append({
                    "id": c.id,
                    "name": c.name,
                    "status": c.status,
                    "created_at": c.created_at,
                    "targets": targets,
                    "opened": opened or 0,
                    "clicked": clicked or 0,
                })

            return result

        except Exception as e:
            logger.error(f"Error getting recent campaigns: {e}")
            return []

    @staticmethod
    def get_all_campaigns():
        """
        Return all campaigns with full details.

        Returns:
            list: All campaigns with template name, group name, and metrics
        """
        try:
            campaigns = Campaign.query.all()

            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')

            result = []
            for c in campaigns:
                # Get template name
                template_name = c.email_template.name if c.email_template else "No Template"

                # Get first target list name (campaigns can have multiple)
                group_name = "No Group"
                if c.campaign_target_lists:
                    first_list = c.campaign_target_lists[0]
                    if first_list.target_list:
                        group_name = first_list.target_list.name

                # Count emails sent (campaign targets)
                emails_sent = db.session.query(func.count(CampaignTarget.id))\
                    .filter(CampaignTarget.campaign_id == c.id).scalar() or 0

                # Count opened
                opened = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == c.id)\
                    .filter(Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

                # Count clicked
                clicked = db.session.query(func.count(func.distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == c.id)\
                    .filter(Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

                result.append({
                    "id": c.id,
                    "name": c.name,
                    "template_name": template_name,
                    "group_name": group_name,
                    "emails_sent": emails_sent,
                    "status": c.status,
                    "created_at": c.created_at,
                    "opened": opened or 0,
                    "clicked": clicked or 0,
                })

            return result

        except Exception as e:
            logger.error(f"Error getting all campaigns: {e}")
            return []

    @staticmethod
    def get_email_templates():
        """
        Return available email templates.

        Returns:
            list: Email templates with id, name, subject
        """
        try:
            templates = EmailTemplate.query.all()

            return [
                {
                    "id": t.id,
                    "name": t.name,
                    "subject": t.subject,
                }
                for t in templates
            ]

        except Exception as e:
            logger.error(f"Error getting email templates: {e}")
            return []

    @staticmethod
    def get_target_groups():
        """
        Return available target groups with member counts.

        Returns:
            list: Target groups/lists with id, name, size
        """
        try:
            # Query target lists with member counts
            target_lists = db.session.query(
                TargetList.id,
                TargetList.name,
                func.count(func.distinct(CampaignTarget.target_id)).label('size')
            ).outerjoin(
                CampaignTargetList, TargetList.id == CampaignTargetList.target_list_id
            ).outerjoin(
                Campaign, CampaignTargetList.campaign_id == Campaign.id
            ).outerjoin(
                CampaignTarget, Campaign.id == CampaignTarget.campaign_id
            ).group_by(TargetList.id, TargetList.name).all()

            return [
                {
                    "id": tl.id,
                    "name": tl.name,
                    "size": tl.size or 0,
                }
                for tl in target_lists
            ]

        except Exception as e:
            logger.error(f"Error getting target groups: {e}")
            return []

    @staticmethod
    def get_campaign_by_id(campaign_id):
        """
        Get single campaign by ID.

        Args:
            campaign_id: Campaign ID

        Returns:
            dict: Campaign details or None if not found
        """
        try:
            campaign = Campaign.query.get(campaign_id)

            if not campaign:
                return None

            return {
                "id": campaign.id,
                "name": campaign.name,
                "description": campaign.description,
                "status": campaign.status,
                "created_at": campaign.created_at,
                "start_date": campaign.start_date,
                "end_date": campaign.end_date,
            }

        except Exception as e:
            logger.error(f"Error getting campaign {campaign_id}: {e}")
            return None

    @staticmethod
    def create_campaign(name, description, email_template_id, target_list_ids, start_date=None, status='draft', created_by_id=None):
        """
        Create a new campaign with target lists.

        Args:
            name: Campaign name
            description: Campaign description
            email_template_id: ID of email template to use
            target_list_ids: List of target list IDs to include
            start_date: Campaign start date (optional)
            status: Campaign status (default: 'draft')
            created_by_id: ID of admin user creating the campaign (optional)

        Returns:
            dict: Created campaign details or None if failed
        """
        try:
            # Create campaign
            new_campaign = Campaign(
                name=name,
                description=description,
                email_template_id=email_template_id,
                created_by_id=created_by_id,
                status=status,
                start_date=start_date or datetime.utcnow(),
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(new_campaign)
            db.session.flush()  # Get ID without committing

            # Link target lists to campaign
            for target_list_id in target_list_ids:
                campaign_target_list = CampaignTargetList(
                    campaign_id=new_campaign.id,
                    target_list_id=target_list_id
                )
                db.session.add(campaign_target_list)

            # Commit all changes
            db.session.commit()

            logger.info(f"Created campaign: {name} (ID: {new_campaign.id})")

            return {
                "id": new_campaign.id,
                "name": new_campaign.name,
                "description": new_campaign.description,
                "status": new_campaign.status,
                "email_template_id": new_campaign.email_template_id,
                "created_at": new_campaign.created_at,
            }

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating campaign: {e}")
            return None

    @staticmethod
    def update_campaign_status(campaign_id, status):
        """
        Update campaign status.

        Args:
            campaign_id: Campaign ID
            status: New status

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            campaign = Campaign.query.get(campaign_id)
            if not campaign:
                return False

            campaign.status = status
            campaign.updated_at = datetime.utcnow()
            db.session.commit()

            logger.info(f"Updated campaign {campaign_id} status to {status}")
            return True

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating campaign status: {e}")
            return False

