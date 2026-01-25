"""
Landing Pages Blueprint
Handles landing page management - create, edit, preview, delete
"""

import logging
from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from repositories.landing_pages_repository import LandingPagesRepository

logger = logging.getLogger(__name__)

landing_pages_bp = Blueprint("landing_pages", __name__)
landing_pages_repo = LandingPagesRepository()


@landing_pages_bp.route("/landing-pages")
@login_required
def index():
    """Display all landing pages"""
    from repositories.active_configuration_repository import ActiveConfigurationRepository

    landing_pages = landing_pages_repo.get_all_landing_pages()
    active_landing_page_id = ActiveConfigurationRepository.get_active_landing_page_id()

    # Get full active landing page info with campaign
    active_info = ActiveConfigurationRepository.get_active_with_campaign()

    return render_template(
        "landing_pages.html",
        landing_pages=landing_pages,
        total_pages=len(landing_pages),
        active_landing_page_id=active_landing_page_id,
        active_info=active_info,
    )


@landing_pages_bp.route("/landing-pages/<int:landing_page_id>/preview", methods=["POST"])
@login_required
def preview_landing_page(landing_page_id):
    """Deploy landing page to preview instance"""
    from utils.campaign_deployer import deploy_preview

    landing_page = landing_pages_repo.get_landing_page_by_id(landing_page_id)

    if not landing_page:
        return jsonify({"success": False, "message": "Landing page not found"}), 404

    template_path = landing_page.get("template_path")
    if not template_path:
        return (
            jsonify(
                {
                    "success": False,
                    "message": (
                        "This landing page uses legacy database storage "
                        "and cannot be previewed"
                    ),
                }
            ),
            400,
        )

    # Deploy to preview
    success, message, preview_url = deploy_preview(template_path)

    if success:
        # Preview is proxied through webadmin at /phishing-preview/
        full_preview_url = "/phishing-preview/"

        return jsonify(
            {
                "success": True,
                "message": message,
                "preview_url": full_preview_url,
                "template_path": template_path,
            }
        )
    else:
        return jsonify({"success": False, "message": message}), 500


@landing_pages_bp.route("/landing-pages/<int:landing_page_id>/details")
@login_required
def get_landing_page_details(landing_page_id):
    """Return full landing page details for editing"""
    landing_page = landing_pages_repo.get_landing_page_by_id(landing_page_id)

    if not landing_page:
        return jsonify({"success": False, "error": "Landing page not found"}), 404

    return jsonify(
        {
            "success": True,
            "landing_pages": landing_page,
        }
    )


@landing_pages_bp.route("/landing-pages/create", methods=["POST"])
@login_required
def create_landing_page():
    """Create a new landing page from template or HTML content"""
    # Get form data
    name = request.form.get("name", "").strip()
    url_path = request.form.get("url_path", "").strip()
    domain = request.form.get("domain", "").strip()
    template_path = request.form.get("template_path", "").strip()  # NEW: Template folder name
    html_content = request.form.get("html_content", "").strip()
    css_content = request.form.get("css_content", "").strip()
    js_content = request.form.get("js_content", "").strip()
    # Credential capture disabled for confidentiality - only track submission events
    capture_credentials = False
    capture_form_data = False
    redirect_url = request.form.get("redirect_url", "").strip()

    # Handle file upload if provided (legacy mode)
    if "html_file" in request.files:
        file = request.files["html_file"]
        if file and file.filename:
            valid_extensions = (".html", ".html.j2", ".j2")
            if any(file.filename.endswith(ext) for ext in valid_extensions):
                html_content = file.read().decode("utf-8")

    # Validate required fields
    if not name:
        return jsonify({"success": False, "message": "Name is required"}), 400

    if not url_path:
        return jsonify({"success": False, "message": "URL path is required"}), 400

    if not domain:
        return jsonify({"success": False, "message": "Domain is required"}), 400

    # NEW: Require either template_path OR html_content
    if not template_path and not html_content:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Either template or HTML content is required",
                }
            ),
            400,
        )

    # Create landing page
    success, message, landing_page_id = landing_pages_repo.create_landing_page(
        name=name,
        url_path=url_path,
        domain=domain,  # Required field
        template_path=template_path or None,  # NEW: Template reference
        html_content=html_content or None,  # Legacy: DB storage
        css_content=css_content or None,
        js_content=js_content or None,
        capture_credentials=capture_credentials,
        capture_form_data=capture_form_data,
        redirect_url=redirect_url or None,
        created_by_id=current_user.id if current_user and hasattr(current_user, "id") else None,
    )

    if success:
        return jsonify(
            {
                "success": True,
                "message": f"Landing page '{name}' created successfully",
                "landing_page_id": landing_page_id,
            }
        )
    else:
        return jsonify({"success": False, "message": message}), 400


@landing_pages_bp.route("/landing-pages/<int:landing_page_id>/update", methods=["POST"])
@login_required
def update_landing_page(landing_page_id):
    """Update an existing landing page"""
    # Get form data
    name = request.form.get("name", "").strip()
    url_path = request.form.get("url_path", "").strip()
    domain = request.form.get("domain", "").strip()
    html_content = request.form.get("html_content", "").strip()
    css_content = request.form.get("css_content", "").strip()
    js_content = request.form.get("js_content", "").strip()
    # Credential capture disabled for confidentiality - only track submission events
    capture_credentials = False
    capture_form_data = False
    redirect_url = request.form.get("redirect_url", "").strip()

    # Handle file upload if provided
    if "html_file" in request.files:
        file = request.files["html_file"]
        if file and file.filename:
            valid_extensions = (".html", ".html.j2", ".j2")
            if any(file.filename.endswith(ext) for ext in valid_extensions):
                html_content = file.read().decode("utf-8")

    # Update landing page
    success, message = landing_pages_repo.update_landing_page(
        landing_page_id=landing_page_id,
        name=name or None,
        url_path=url_path or None,
        domain=domain or None,
        html_content=html_content or None,
        css_content=css_content,
        js_content=js_content,
        capture_credentials=capture_credentials,
        capture_form_data=capture_form_data,
        redirect_url=redirect_url,
    )

    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 400


@landing_pages_bp.route("/landing-pages/<int:landing_page_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_landing_page(landing_page_id):
    """Delete a landing page"""
    landing_page = landing_pages_repo.get_landing_page_by_id(landing_page_id)

    if not landing_page:
        return jsonify({"success": False, "message": "Landing page not found"}), 404

    landing_page_name = landing_page.get("name", "Unknown")

    success, message = landing_pages_repo.delete_landing_page(landing_page_id)

    if success:
        return jsonify(
            {"success": True, "message": f"Landing page '{landing_page_name}' deleted successfully"}
        )
    else:
        return jsonify({"success": False, "message": message}), 400


@landing_pages_bp.route("/landing-pages/active")
@login_required
def get_active_landing_page():
    """Get the currently active landing page"""
    from repositories.active_configuration_repository import ActiveConfigurationRepository

    config = ActiveConfigurationRepository.get_active_configuration()
    active_page = ActiveConfigurationRepository.get_active_landing_page()
    running_campaigns = ActiveConfigurationRepository.get_running_campaigns_count()

    return jsonify(
        {
            "success": True,
            "active_landing_page": {
                "id": active_page.id,
                "name": active_page.name,
                "url_path": active_page.url_path,
            }
            if active_page
            else None,
            "activated_at": config.activated_at.isoformat()
            if config and config.activated_at
            else None,
            "phishing_domain": config.phishing_domain if config else None,
            "running_campaigns": running_campaigns,
            "can_change": running_campaigns == 0,
        }
    )


@landing_pages_bp.route("/landing-pages/<int:landing_page_id>/activate", methods=["POST"])
@login_required
def activate_landing_page(landing_page_id):
    """Activate a landing page"""
    from repositories.active_configuration_repository import ActiveConfigurationRepository
    from utils.cache_manager import cache_active_landing_page, clear_active_cache
    from flask_login import current_user

    # Check if campaigns are running
    if ActiveConfigurationRepository.has_running_campaigns():
        current_active = ActiveConfigurationRepository.get_active_landing_page_id()
        if current_active != landing_page_id:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": "Cannot change active landing page while campaigns are running",
                    }
                ),
                400,
            )

    # Get optional domain/IP from request
    phishing_domain = request.form.get("phishing_domain")
    public_ip = request.form.get("public_ip")

    # Activate the landing page
    success, message, dns_zone_path = ActiveConfigurationRepository.activate_landing_page(
        landing_page_id=landing_page_id,
        user_id=current_user.id if hasattr(current_user, "id") else None,
        phishing_domain=phishing_domain,
        public_ip=public_ip,
    )

    if success:
        landing_page = landing_pages_repo.get_landing_page_by_id(landing_page_id)
        if landing_page:
            # Check if this is a template-based landing page
            if landing_page.get("template_path"):
                # Deploy template to "active" directory for immediate testing
                from utils.campaign_deployer import deploy_landing_page_to_campaign

                deploy_success, deploy_msg, deploy_path = deploy_landing_page_to_campaign(
                    campaign_id="active", template_path=landing_page["template_path"]
                )
                if deploy_success:
                    logger.info(f"Deployed active landing page to: {deploy_path}")
                else:
                    logger.warning(f"Failed to deploy active landing page: {deploy_msg}")
            else:
                # Legacy: Cache HTML content
                clear_active_cache()
                cache_active_landing_page(landing_page)

    return jsonify(
        {
            "success": success,
            "message": message,
            "dns_zone_path": dns_zone_path,
        }
    )


@landing_pages_bp.route("/landing-pages/deactivate", methods=["POST"])
@login_required
def deactivate_landing_page():
    """Deactivate the currently active landing page"""
    from repositories.active_configuration_repository import ActiveConfigurationRepository
    from db.models import Campaign
    from database import db

    # Check if deactivation is allowed
    (
        can_deactivate,
        reason,
        campaign_status,
    ) = ActiveConfigurationRepository.can_deactivate_landing_page()

    if not can_deactivate:
        return (
            jsonify(
                {
                    "success": False,
                    "message": reason,
                    "campaign_status": campaign_status,
                }
            ),
            400,
        )

    # Additional check: Count how many campaigns use this landing page
    config = ActiveConfigurationRepository.get_active_configuration()
    if config and config.active_landing_page_id:
        active_campaigns = (
            db.session.query(Campaign)
            .filter(
                Campaign.landing_page_id == config.active_landing_page_id,
                Campaign.status.in_(["active", "scheduled"]),
            )
            .count()
        )

        if active_campaigns > 0:
            return (
                jsonify(
                    {
                        "success": False,
                        "message": (
                            f"Cannot deactivate: {active_campaigns} campaign(s) "
                            "are using this landing page and are active or scheduled."
                        ),
                        "campaign_status": "active",
                    }
                ),
                400,
            )

    # Deactivate
    success, message = ActiveConfigurationRepository.deactivate_landing_page()

    if success:
        # Clean up the "active" deployment directory
        from utils.campaign_deployer import cleanup_campaign_deployment

        cleanup_success, cleanup_msg = cleanup_campaign_deployment("active")
        if cleanup_success:
            logger.info(f"Cleaned up active deployment: {cleanup_msg}")
        else:
            logger.warning(f"Failed to cleanup active deployment: {cleanup_msg}")

    return jsonify(
        {
            "success": success,
            "message": message,
        }
    )


@landing_pages_bp.route("/landing-pages/dns-zone")
@login_required
def get_dns_zone_file():
    """Download the latest DNS zone file"""
    from repositories.active_configuration_repository import ActiveConfigurationRepository
    from flask import send_file

    config = ActiveConfigurationRepository.get_active_configuration()

    if not config or not config.dns_zone_file_path:
        return jsonify({"success": False, "message": "No DNS zone file generated"}), 404

    from pathlib import Path

    filepath = Path(config.dns_zone_file_path)

    if not filepath.exists():
        return jsonify({"success": False, "message": "DNS zone file not found"}), 404

    return send_file(
        filepath, as_attachment=True, download_name="dns-zone-entry.txt", mimetype="text/plain"
    )


@landing_pages_bp.route("/landing-pages/templates")
@login_required
def list_templates():
    """List all available landing page templates in /templates/landing_pages/"""
    templates = landing_pages_repo.list_available_templates()

    return jsonify(
        {
            "success": True,
            "templates": templates,
            "count": len(templates),
        }
    )


@landing_pages_bp.route("/landing-pages/templates/<template_name>/pages")
@login_required
def get_template_pages(template_name):
    """Get all HTML entry pages in a template"""
    entry_pages = landing_pages_repo.get_template_entry_pages(template_name)

    return jsonify(
        {
            "success": True,
            "template_name": template_name,
            "entry_pages": entry_pages,
            "count": len(entry_pages),
        }
    )


@landing_pages_bp.route("/landing-pages/preview/cleanup", methods=["POST"])
@login_required
def cleanup_preview():
    """Cleanup preview deployment"""
    from utils.campaign_deployer import cleanup_preview as cleanup_preview_deployment

    success, message = cleanup_preview_deployment()

    return jsonify(
        {
            "success": success,
            "message": message,
        }
    )


@landing_pages_bp.route("/landing-pages/preview/status")
@login_required
def preview_status():
    """Check if preview is currently deployed"""
    from utils.campaign_deployer import is_preview_deployed

    is_deployed = is_preview_deployed()

    return jsonify(
        {
            "success": True,
            "is_deployed": is_deployed,
        }
    )
