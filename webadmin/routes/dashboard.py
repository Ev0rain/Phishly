"""
Dashboard Blueprint - Main admin dashboard
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from repositories.campaign_repository import CampaignRepository

dashboard_bp = Blueprint("dashboard", __name__)

# Initialize repository (now using real database)
campaign_repo = CampaignRepository()


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
@login_required
def index():
    """Main dashboard page"""
    stats = campaign_repo.get_dashboard_stats()
    recent_campaigns = campaign_repo.get_recent_campaigns()

    return render_template(
        "dashboard.html", stats=stats, campaigns=recent_campaigns, current_user=current_user
    )
