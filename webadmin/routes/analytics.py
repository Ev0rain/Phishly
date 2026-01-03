"""
Analytics Routes Blueprint
Handles analytics dashboard, metrics, and data visualization
"""

from flask import Blueprint, render_template, request, jsonify
from repositories.analytics_repository import MockAnalyticsRepository
from repositories.campaign_repository import MockCampaignRepository
from repositories.templates_repository import MockTemplatesRepository
from repositories.targets_repository import MockTargetsRepository

analytics_bp = Blueprint("analytics", __name__)
analytics_repo = MockAnalyticsRepository()
campaign_repo = MockCampaignRepository()
templates_repo = MockTemplatesRepository()
targets_repo = MockTargetsRepository()


@analytics_bp.route("/analytics")
def index():
    """Display analytics dashboard with comprehensive metrics"""

    # Get overall statistics
    overall_stats = analytics_repo.get_overall_stats()

    # Get campaign performance data
    campaign_performance = analytics_repo.get_campaign_performance()

    # Get department breakdown
    department_breakdown = analytics_repo.get_department_breakdown()

    # Get template effectiveness
    template_effectiveness = analytics_repo.get_template_effectiveness()

    # Get device/browser/OS breakdowns
    device_breakdown = analytics_repo.get_device_breakdown()
    browser_breakdown = analytics_repo.get_browser_breakdown()
    os_breakdown = analytics_repo.get_os_breakdown()

    # Get top vulnerable users
    vulnerable_users = analytics_repo.get_top_vulnerable_users(limit=10)

    # Get recent events for timeline
    recent_events = analytics_repo.get_event_timeline(limit=20)

    # Get filter options (for dropdowns)
    all_campaigns = campaign_repo.get_all_campaigns()
    all_templates = templates_repo.get_all_templates()
    all_groups = targets_repo.get_all_groups()

    return render_template(
        "analytics.html",
        overall_stats=overall_stats,
        campaign_performance=campaign_performance,
        department_breakdown=department_breakdown,
        template_effectiveness=template_effectiveness,
        device_breakdown=device_breakdown,
        browser_breakdown=browser_breakdown,
        os_breakdown=os_breakdown,
        vulnerable_users=vulnerable_users,
        recent_events=recent_events,
        all_campaigns=all_campaigns,
        all_templates=all_templates,
        all_groups=all_groups,
    )


@analytics_bp.route("/api/analytics/time-series")
def get_time_series():
    """API endpoint for time series chart data"""
    days = request.args.get("days", default=30, type=int)

    # Limit to reasonable range
    if days < 1:
        days = 7
    elif days > 365:
        days = 365

    data = analytics_repo.get_time_series_data(days=days)

    return jsonify(
        {
            "success": True,
            "data": data,
            "days": days,
        }
    )


@analytics_bp.route("/api/analytics/filter", methods=["POST"])
def apply_filters():
    """API endpoint to get filtered analytics data"""
    filters = {
        "campaign_id": request.json.get("campaign_id"),
        "template_id": request.json.get("template_id"),
        "group_id": request.json.get("group_id"),
        "date_from": request.json.get("date_from"),
        "date_to": request.json.get("date_to"),
        "department": request.json.get("department"),
    }

    # Remove None values
    filters = {k: v for k, v in filters.items() if v is not None}

    filtered_data = analytics_repo.get_filtered_data(filters)

    return jsonify(
        {
            "success": True,
            "data": filtered_data,
        }
    )


@analytics_bp.route("/api/analytics/export")
def export_data():
    """Export analytics data as CSV"""
    # In production, this would generate a CSV file
    # For now, return a success message

    return jsonify(
        {
            "success": True,
            "message": "Export functionality will be implemented with database integration",
        }
    )


@analytics_bp.route("/analytics/campaign/<int:campaign_id>")
def campaign_detail(campaign_id):
    """Detailed analytics for a specific campaign"""
    campaign = campaign_repo.get_campaign_by_id(campaign_id)

    if not campaign:
        return "Campaign not found", 404

    # Get detailed metrics for this campaign
    # In production, filter all analytics by campaign_id

    return render_template(
        "analytics_campaign_detail.html",
        campaign=campaign,
        # Add campaign-specific metrics here
    )
