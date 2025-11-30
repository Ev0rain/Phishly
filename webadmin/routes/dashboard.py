"""
Dashboard Blueprint - Main admin dashboard
"""

from flask import Blueprint, render_template
from repositories.campaign_repository import MockCampaignRepository

dashboard_bp = Blueprint("dashboard", __name__)

# Initialize repository (will be swapped with real DB later)
campaign_repo = MockCampaignRepository()


@dashboard_bp.route("/")
@dashboard_bp.route("/dashboard")
def index():
    """Main dashboard page"""
    stats = campaign_repo.get_dashboard_stats()
    recent_campaigns = campaign_repo.get_recent_campaigns()

    return render_template("dashboard.html", stats=stats, campaigns=recent_campaigns)
