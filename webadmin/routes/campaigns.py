"""
Campaigns Blueprint - Campaign management and creation
"""

from flask import Blueprint, render_template, request, jsonify
from repositories.campaign_repository import MockCampaignRepository

campaigns_bp = Blueprint("campaigns", __name__)

# Initialize repository (will be swapped with real DB later)
campaign_repo = MockCampaignRepository()


@campaigns_bp.route("/campaigns")
def index():
    """Campaigns overview page"""
    campaigns = campaign_repo.get_all_campaigns()
    templates = campaign_repo.get_email_templates()
    groups = campaign_repo.get_target_groups()

    return render_template(
        "campaigns.html", campaigns=campaigns, templates=templates, groups=groups
    )


@campaigns_bp.route("/campaigns/create", methods=["POST"])
def create():
    """
    Create new campaign (placeholder - no database yet)
    """
    campaign_name = request.form.get("campaign_name")
    template_id = request.form.get("template_id")
    group_id = request.form.get("group_id")

    # TODO: When database is ready, create actual campaign
    # For now, just return success
    return jsonify(
        {
            "success": True,
            "message": "Campaign created successfully",
            "campaign": {
                "name": campaign_name,
                "template_id": template_id,
                "group_id": group_id,
            },
        }
    )
