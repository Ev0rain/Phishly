"""
Analytics Repository - Real database implementation

Handles all analytics-related database queries with heavy aggregations
"""

from repositories.base_repository import BaseRepository
from database import db, get_event_type_id
from db.models import (
    Campaign, CampaignTarget, CampaignTargetList,
    EmailTemplate, TargetList, Target, Department,
    Event, EventType, EmailJob
)
from sqlalchemy import func, case, and_, distinct
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class AnalyticsRepository(BaseRepository):
    """Real database repository for analytics with aggregations"""

    @staticmethod
    def get_overall_stats():
        """Return overall platform statistics"""
        try:
            # Get event type IDs
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')
            event_captured_id = get_event_type_id('credentials_captured')

            # Total campaigns
            total_campaigns = db.session.query(func.count(Campaign.id)).scalar() or 0
            active_campaigns = db.session.query(func.count(Campaign.id))\
                .filter(Campaign.status == 'active').scalar() or 0

            # Total unique targets
            total_targets = db.session.query(func.count(Target.id)).scalar() or 0

            # Total emails sent
            total_emails_sent = db.session.query(func.count(Event.id))\
                .filter(Event.event_type_id == event_sent_id).scalar() if event_sent_id else 0

            # Get unique campaign_target_ids for each event type (to avoid double counting)
            emails_opened = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                .filter(Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

            links_clicked = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                .filter(Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

            credentials_submitted = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                .filter(Event.event_type_id == event_submitted_id).scalar() if event_submitted_id else 0

            total_form_submissions = credentials_submitted  # Same as submitted for now

            # Calculate rates
            avg_open_rate = round((emails_opened / total_emails_sent * 100), 1) if total_emails_sent > 0 else 0.0
            avg_click_rate = round((links_clicked / total_emails_sent * 100), 1) if total_emails_sent > 0 else 0.0
            avg_submission_rate = round((credentials_submitted / total_emails_sent * 100), 1) if total_emails_sent > 0 else 0.0

            # This month stats
            month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            campaigns_this_month = db.session.query(func.count(Campaign.id))\
                .filter(Campaign.created_at >= month_start).scalar() or 0

            emails_sent_this_month = db.session.query(func.count(Event.id))\
                .filter(Event.event_type_id == event_sent_id, Event.created_at >= month_start).scalar() if event_sent_id else 0

            # Get most/least effective templates
            most_effective_template = "N/A"
            least_effective_template = "N/A"

            template_stats = AnalyticsRepository.get_template_effectiveness()
            if template_stats:
                most_effective_template = template_stats[0]["template_name"]  # Already sorted by effectiveness
                least_effective_template = template_stats[-1]["template_name"]

            # Get riskiest/safest departments
            riskiest_department = "N/A"
            safest_department = "N/A"

            dept_stats = AnalyticsRepository.get_department_breakdown()
            if dept_stats:
                riskiest_department = dept_stats[0]["department"]  # Already sorted by risk
                safest_department = dept_stats[-1]["department"]

            return {
                "total_campaigns": total_campaigns,
                "active_campaigns": active_campaigns,
                "total_emails_sent": total_emails_sent or 0,
                "total_targets": total_targets,
                "average_open_rate": avg_open_rate,
                "average_click_rate": avg_click_rate,
                "average_submission_rate": avg_submission_rate,
                "total_form_submissions": total_form_submissions,
                "total_credentials_captured": credentials_submitted,
                "campaigns_this_month": campaigns_this_month,
                "emails_sent_this_month": emails_sent_this_month,
                "most_effective_template": most_effective_template,
                "least_effective_template": least_effective_template,
                "riskiest_department": riskiest_department,
                "safest_department": safest_department,
            }

        except Exception as e:
            logger.error(f"Error getting overall stats: {e}")
            return {
                "total_campaigns": 0,
                "active_campaigns": 0,
                "total_emails_sent": 0,
                "total_targets": 0,
                "average_open_rate": 0.0,
                "average_click_rate": 0.0,
                "average_submission_rate": 0.0,
                "total_form_submissions": 0,
                "total_credentials_captured": 0,
                "campaigns_this_month": 0,
                "emails_sent_this_month": 0,
                "most_effective_template": "N/A",
                "least_effective_template": "N/A",
                "riskiest_department": "N/A",
                "safest_department": "N/A",
            }

    @staticmethod
    def get_campaign_performance():
        """Return performance metrics for all campaigns"""
        try:
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Get all campaigns
            campaigns = db.session.query(Campaign).all()

            result = []
            for campaign in campaigns:
                # Count events for this campaign
                sent = db.session.query(func.count(Event.id))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == campaign.id,
                            Event.event_type_id == event_sent_id).scalar() if event_sent_id else 0

                opened = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == campaign.id,
                            Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

                clicked = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == campaign.id,
                            Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

                submitted = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .join(CampaignTarget, Event.campaign_target_id == CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id == campaign.id,
                            Event.event_type_id == event_submitted_id).scalar() if event_submitted_id else 0

                # Get template name
                template_name = "N/A"
                if campaign.email_template_id:
                    template = db.session.query(EmailTemplate)\
                        .filter(EmailTemplate.id == campaign.email_template_id).first()
                    if template:
                        template_name = template.name

                # Get target group (first one if multiple)
                target_group = "N/A"
                target_list_link = db.session.query(CampaignTargetList)\
                    .filter(CampaignTargetList.campaign_id == campaign.id).first()
                if target_list_link:
                    target_list = db.session.query(TargetList)\
                        .filter(TargetList.id == target_list_link.target_list_id).first()
                    if target_list:
                        target_group = target_list.name

                result.append({
                    "id": campaign.id,
                    "name": campaign.name,
                    "status": campaign.status,
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": round((opened / sent) * 100, 1) if sent > 0 else 0.0,
                    "click_rate": round((clicked / sent) * 100, 1) if sent > 0 else 0.0,
                    "submission_rate": round((submitted / sent) * 100, 1) if sent > 0 else 0.0,
                    "start_date": campaign.start_date or campaign.created_at,
                    "template_name": template_name,
                    "target_group": target_group,
                })

            return result

        except Exception as e:
            logger.error(f"Error getting campaign performance: {e}")
            return []

    @staticmethod
    def get_time_series_data(days=30):
        """Return time series data for charts (last N days)"""
        try:
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Calculate date range
            end_date = datetime.utcnow().date()
            start_date = end_date - timedelta(days=days-1)

            # Query events grouped by date
            result = []
            current_date = start_date

            while current_date <= end_date:
                date_start = datetime.combine(current_date, datetime.min.time())
                date_end = datetime.combine(current_date, datetime.max.time())

                sent = db.session.query(func.count(Event.id))\
                    .filter(Event.event_type_id == event_sent_id,
                            Event.created_at >= date_start,
                            Event.created_at <= date_end).scalar() if event_sent_id else 0

                opened = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.event_type_id == event_opened_id,
                            Event.created_at >= date_start,
                            Event.created_at <= date_end).scalar() if event_opened_id else 0

                clicked = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.event_type_id == event_clicked_id,
                            Event.created_at >= date_start,
                            Event.created_at <= date_end).scalar() if event_clicked_id else 0

                submitted = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.event_type_id == event_submitted_id,
                            Event.created_at >= date_start,
                            Event.created_at <= date_end).scalar() if event_submitted_id else 0

                result.append({
                    "date": current_date.strftime("%Y-%m-%d"),
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": round((opened / sent) * 100, 1) if sent > 0 else 0.0,
                    "click_rate": round((clicked / sent) * 100, 1) if sent > 0 else 0.0,
                    "submission_rate": round((submitted / sent) * 100, 1) if sent > 0 else 0.0,
                })

                current_date += timedelta(days=1)

            return result

        except Exception as e:
            logger.error(f"Error getting time series data: {e}")
            return []

    @staticmethod
    def get_department_breakdown():
        """Return metrics broken down by department"""
        try:
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Get all departments
            departments = db.session.query(Department).all()

            result = []
            for dept in departments:
                # Count targets in this department
                total_targets = db.session.query(func.count(Target.id))\
                    .filter(Target.department_id == dept.id).scalar() or 0

                # Get campaign targets for this department
                dept_campaign_targets = db.session.query(CampaignTarget.id)\
                    .join(Target, CampaignTarget.target_id == Target.id)\
                    .filter(Target.department_id == dept.id).subquery()

                # Count events
                sent = db.session.query(func.count(Event.id))\
                    .filter(Event.campaign_target_id.in_(dept_campaign_targets),
                            Event.event_type_id == event_sent_id).scalar() if event_sent_id else 0

                opened = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.campaign_target_id.in_(dept_campaign_targets),
                            Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

                clicked = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.campaign_target_id.in_(dept_campaign_targets),
                            Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

                submitted = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.campaign_target_id.in_(dept_campaign_targets),
                            Event.event_type_id == event_submitted_id).scalar() if event_submitted_id else 0

                open_rate = round((opened / sent) * 100, 1) if sent > 0 else 0.0
                click_rate = round((clicked / sent) * 100, 1) if sent > 0 else 0.0
                submission_rate = round((submitted / sent) * 100, 1) if sent > 0 else 0.0

                result.append({
                    "department": dept.name,
                    "total_targets": total_targets,
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": open_rate,
                    "click_rate": click_rate,
                    "submission_rate": submission_rate,
                    "risk_score": submission_rate,  # Higher = more risky
                })

            # Sort by risk score descending
            result.sort(key=lambda x: x["risk_score"], reverse=True)

            return result

        except Exception as e:
            logger.error(f"Error getting department breakdown: {e}")
            return []

    @staticmethod
    def get_template_effectiveness():
        """Return effectiveness metrics for each email template"""
        try:
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Get all templates
            templates = db.session.query(EmailTemplate).all()

            result = []
            for template in templates:
                # Count campaigns using this template
                times_used = db.session.query(func.count(Campaign.id))\
                    .filter(Campaign.email_template_id == template.id).scalar() or 0

                # Get campaign IDs for this template
                campaign_ids = db.session.query(Campaign.id)\
                    .filter(Campaign.email_template_id == template.id).subquery()

                # Get campaign targets for these campaigns
                template_campaign_targets = db.session.query(CampaignTarget.id)\
                    .filter(CampaignTarget.campaign_id.in_(campaign_ids)).subquery()

                # Count events
                sent = db.session.query(func.count(Event.id))\
                    .filter(Event.campaign_target_id.in_(template_campaign_targets),
                            Event.event_type_id == event_sent_id).scalar() if event_sent_id else 0

                opened = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.campaign_target_id.in_(template_campaign_targets),
                            Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

                clicked = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.campaign_target_id.in_(template_campaign_targets),
                            Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

                submitted = db.session.query(func.count(distinct(Event.campaign_target_id)))\
                    .filter(Event.campaign_target_id.in_(template_campaign_targets),
                            Event.event_type_id == event_submitted_id).scalar() if event_submitted_id else 0

                open_rate = round((opened / sent) * 100, 1) if sent > 0 else 0.0
                click_rate = round((clicked / sent) * 100, 1) if sent > 0 else 0.0
                submission_rate = round((submitted / sent) * 100, 1) if sent > 0 else 0.0

                # Calculate effectiveness score (weighted: open + click*2 + submit*3)
                effectiveness = round(((opened + clicked * 2 + submitted * 3) / (sent * 6)) * 100, 1) if sent > 0 else 0.0

                result.append({
                    "template_name": template.name,
                    "times_used": times_used,
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": open_rate,
                    "click_rate": click_rate,
                    "submission_rate": submission_rate,
                    "effectiveness_score": effectiveness,
                })

            # Sort by effectiveness score descending
            result.sort(key=lambda x: x["effectiveness_score"], reverse=True)

            return result

        except Exception as e:
            logger.error(f"Error getting template effectiveness: {e}")
            return []

    @staticmethod
    def get_device_breakdown():
        """Return metrics by device type"""
        # TODO: Implement device tracking in events
        return [
            {"device_type": "N/A", "count": 0, "percentage": 0.0,
             "open_rate": 0.0, "click_rate": 0.0, "submission_rate": 0.0}
        ]

    @staticmethod
    def get_browser_breakdown():
        """Return metrics by browser"""
        # TODO: Implement browser tracking in events
        return [{"browser": "N/A", "count": 0, "percentage": 0.0}]

    @staticmethod
    def get_os_breakdown():
        """Return metrics by operating system"""
        # TODO: Implement OS tracking in events
        return [{"os": "N/A", "count": 0, "percentage": 0.0}]

    @staticmethod
    def get_event_timeline(limit=50):
        """Return recent events for timeline view"""
        try:
            # Query recent events with related data
            events = db.session.query(
                Event.id,
                Event.created_at,
                Event.ip_address,
                Event.user_agent,
                EventType.name.label('event_type'),
                Campaign.name.label('campaign_name'),
                Target.email.label('target_email')
            ).join(
                EventType, Event.event_type_id == EventType.id
            ).join(
                CampaignTarget, Event.campaign_target_id == CampaignTarget.id
            ).join(
                Campaign, CampaignTarget.campaign_id == Campaign.id
            ).join(
                Target, CampaignTarget.target_id == Target.id
            ).order_by(
                Event.created_at.desc()
            ).limit(limit).all()

            result = []
            for event in events:
                result.append({
                    "id": event.id,
                    "event_type": event.event_type,
                    "campaign_name": event.campaign_name,
                    "target_email": event.target_email,
                    "timestamp": event.created_at,
                    "ip_address": event.ip_address or "N/A",
                    "device": "N/A",  # TODO: Parse from user_agent
                    "browser": "N/A",  # TODO: Parse from user_agent
                })

            return result

        except Exception as e:
            logger.error(f"Error getting event timeline: {e}")
            return []

    @staticmethod
    def get_top_vulnerable_users(limit=10):
        """Return users who are most vulnerable (clicked/submitted most)"""
        try:
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Get all targets with their event counts
            targets = db.session.query(Target).all()

            result = []
            for target in targets:
                # Get campaign targets for this target
                target_campaign_targets = db.session.query(CampaignTarget.id)\
                    .filter(CampaignTarget.target_id == target.id).subquery()

                # Count events
                received = db.session.query(func.count(Event.id))\
                    .filter(Event.campaign_target_id.in_(target_campaign_targets)).scalar() or 0

                opened = db.session.query(func.count(Event.id))\
                    .filter(Event.campaign_target_id.in_(target_campaign_targets),
                            Event.event_type_id == event_opened_id).scalar() if event_opened_id else 0

                clicked = db.session.query(func.count(Event.id))\
                    .filter(Event.campaign_target_id.in_(target_campaign_targets),
                            Event.event_type_id == event_clicked_id).scalar() if event_clicked_id else 0

                submitted = db.session.query(func.count(Event.id))\
                    .filter(Event.campaign_target_id.in_(target_campaign_targets),
                            Event.event_type_id == event_submitted_id).scalar() if event_submitted_id else 0

                # Skip if no events
                if received == 0:
                    continue

                # Get department name
                dept_name = "Unknown"
                if target.department_id:
                    dept = db.session.query(Department)\
                        .filter(Department.id == target.department_id).first()
                    if dept:
                        dept_name = dept.name

                # Calculate vulnerability score
                vulnerability = round((clicked * 2 + submitted * 5) / (received * 7) * 100, 1) if received > 0 else 0.0

                result.append({
                    "email": target.email,
                    "name": f"{target.first_name} {target.last_name}" if target.first_name else target.email,
                    "department": dept_name,
                    "emails_received": received,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "vulnerability_score": vulnerability,
                })

            # Sort by vulnerability score descending
            result.sort(key=lambda x: x["vulnerability_score"], reverse=True)

            return result[:limit]

        except Exception as e:
            logger.error(f"Error getting top vulnerable users: {e}")
            return []

    @staticmethod
    def get_filtered_data(filters):
        """
        Return analytics data filtered by criteria

        Args:
            filters: dict with keys like campaign_id, template_id, group_id, date_from, date_to

        Returns:
            dict: Filtered analytics data
        """
        try:
            event_sent_id = get_event_type_id('email_sent')
            event_opened_id = get_event_type_id('email_opened')
            event_clicked_id = get_event_type_id('link_clicked')
            event_submitted_id = get_event_type_id('form_submitted')

            # Build query with filters
            query = db.session.query(Event)

            # Filter by campaign
            if filters.get('campaign_id'):
                query = query.join(CampaignTarget)\
                    .filter(CampaignTarget.campaign_id == filters['campaign_id'])

            # Filter by date range
            if filters.get('date_from'):
                query = query.filter(Event.created_at >= filters['date_from'])
            if filters.get('date_to'):
                query = query.filter(Event.created_at <= filters['date_to'])

            # Count by event type
            sent = query.filter(Event.event_type_id == event_sent_id).count() if event_sent_id else 0
            opened = query.filter(Event.event_type_id == event_opened_id).count() if event_opened_id else 0
            clicked = query.filter(Event.event_type_id == event_clicked_id).count() if event_clicked_id else 0
            submitted = query.filter(Event.event_type_id == event_submitted_id).count() if event_submitted_id else 0

            return {
                "emails_sent": sent,
                "emails_opened": opened,
                "links_clicked": clicked,
                "credentials_submitted": submitted,
                "filters_applied": filters,
            }

        except Exception as e:
            logger.error(f"Error getting filtered data: {e}")
            return {
                "emails_sent": 0,
                "emails_opened": 0,
                "links_clicked": 0,
                "credentials_submitted": 0,
                "filters_applied": filters,
            }

