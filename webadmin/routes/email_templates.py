"""
Email templates Blueprint
Handles template listing, preview, and import functionality
"""

from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from repositories.templates_repository import TemplatesRepository

templates_bp = Blueprint("templates", __name__)
templates_repo = TemplatesRepository()


@templates_bp.route("/templates")
@login_required
def index():
    """Display all email templates"""
    templates = templates_repo.get_all_templates()
    available_tags = templates_repo.get_available_tags()
    landing_pages = templates_repo.get_all_landing_pages()

    return render_template(
        "email_templates.html",
        templates=templates,
        available_tags=available_tags,
        landing_pages=landing_pages,
    )


@templates_bp.route("/templates/<int:template_id>/preview")
@login_required
def preview_template(template_id):
    """Return the HTML content of a template for preview"""
    template = templates_repo.get_template_by_id(template_id)

    if not template:
        return jsonify({"error": "Template not found"}), 404

    html_content = templates_repo.get_template_html(template_id)

    return jsonify(
        {
            "success": True,
            "name": template["name"],
            "subject": template["subject"],
            "html": html_content,
        }
    )


@templates_bp.route("/templates/<int:template_id>/details")
@login_required
def get_template_details(template_id):
    """Return template details including default landing page for campaign creation"""
    template = templates_repo.get_template_by_id(template_id)

    if not template:
        return jsonify({"success": False, "error": "Template not found"}), 404

    return jsonify(
        {
            "success": True,
            "template": {
                "id": template["id"],
                "name": template["name"],
                "subject": template["subject"],
                "from_email": template["from_email"],
                "from_name": template["from_name"],
                "default_landing_page_id": template.get("default_landing_page_id"),
                "default_landing_page": template.get("default_landing_page"),
            },
        }
    )


@templates_bp.route("/templates/import", methods=["POST"])
@login_required
def import_template():
    """
    Import a new email template from templates/email_templates/
    Accepts: name, subject, tags (comma-separated), and template filename
    """
    # Get form data
    name = request.form.get("name")
    subject = request.form.get("subject")
    template_filename = request.form.get("template_file")
    # tags_string = request.form.get("tags", "")  # Not currently used

    # Validate required fields
    if not name or not subject:
        return (
            jsonify({"success": False, "message": "Name and subject are required"}),
            400,
        )

    # Validate template file is selected
    if not template_filename:
        return jsonify({"success": False, "message": "No template file selected"}), 400

    # Read template content from filesystem
    success, html_content = templates_repo.get_template_file_content(template_filename)

    if not success:
        return (
            jsonify({"success": False, "message": html_content}),  # html_content contains error message
            400,
        )

    # Get sender information (use defaults for now)
    from_email = request.form.get("from_email", "noreply@company.com")
    from_name = request.form.get("from_name", "Company Name")

    # Get default landing page ID (optional)
    default_landing_page_id = request.form.get("default_landing_page_id")
    if default_landing_page_id:
        try:
            default_landing_page_id = int(default_landing_page_id)
        except ValueError:
            default_landing_page_id = None

    # Save template (metadata to DB, HTML to disk)
    success, message, template_id = templates_repo.save_template(
        name=name,
        subject=subject,
        from_email=from_email,
        from_name=from_name,
        html_content=html_content,
        created_by_id=current_user.id if current_user and hasattr(current_user, "id") else None,
        default_landing_page_id=default_landing_page_id,
    )

    if success:
        return jsonify(
            {
                "success": True,
                "message": f"Template '{name}' imported successfully",
                "template_id": template_id,
            }
        )
    else:
        return jsonify({"success": False, "message": message}), 500


@templates_bp.route("/templates/<int:template_id>/delete", methods=["POST", "DELETE"])
@login_required
def delete_template(template_id):
    """Delete an email template"""
    template = templates_repo.get_template_by_id(template_id)

    if not template:
        return jsonify({"success": False, "message": "Template not found"}), 404

    template_name = template.get("name", "Unknown")

    success, message = templates_repo.delete_template(template_id)

    if success:
        return jsonify({
            "success": True,
            "message": f"Template '{template_name}' deleted successfully"
        })
    else:
        return jsonify({"success": False, "message": message}), 500


@templates_bp.route("/templates/<int:template_id>/edit", methods=["POST"])
@login_required
def edit_template(template_id):
    """Update existing email template metadata"""
    # Get form data
    name = request.form.get("name")
    subject = request.form.get("subject")
    from_email = request.form.get("from_email")
    from_name = request.form.get("from_name")
    default_landing_page_id = request.form.get("default_landing_page_id")

    if not name or not subject:
        return jsonify({"success": False, "message": "Name and subject required"}), 400

    # Update template
    success, message = templates_repo.update_template(
        template_id=template_id,
        name=name,
        subject=subject,
        from_email=from_email,
        from_name=from_name,
        default_landing_page_id=int(default_landing_page_id) if default_landing_page_id else None
    )

    if success:
        return jsonify({"success": True, "message": message})
    else:
        return jsonify({"success": False, "message": message}), 500


@templates_bp.route("/templates/available-files")
@login_required
def list_available_template_files():
    """List all available email template .html files in templates/email_templates/"""
    templates = templates_repo.list_available_template_files()

    return jsonify({
        "success": True,
        "templates": templates,
        "count": len(templates),
    })


@templates_bp.route("/templates/file/<filename>/content")
@login_required
def get_template_file_content(filename):
    """Get the content of a template file"""
    success, content = templates_repo.get_template_file_content(filename)

    if success:
        return jsonify({
            "success": True,
            "filename": filename,
            "content": content,
        })
    else:
        return jsonify({"success": False, "message": content}), 404
