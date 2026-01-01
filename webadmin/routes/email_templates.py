"""
Email Templates Blueprint
Handles template listing, preview, and import functionality
"""

from flask import Blueprint, render_template, request, jsonify
from repositories.templates_repository import MockTemplatesRepository
from werkzeug.utils import secure_filename

templates_bp = Blueprint("templates", __name__)
templates_repo = MockTemplatesRepository()


@templates_bp.route("/templates")
def index():
    """Display all email templates"""
    templates = templates_repo.get_all_templates()
    available_tags = templates_repo.get_available_tags()

    return render_template(
        "email_templates.html",
        templates=templates,
        available_tags=available_tags,
    )


@templates_bp.route("/templates/<int:template_id>/preview")
def preview_template(template_id):
    """Return the HTML content of a template for preview"""
    template = templates_repo.get_template_by_id(template_id)

    if not template:
        return jsonify({"error": "Template not found"}), 404

    html_content = templates_repo.get_template_html(template["filename"])

    return jsonify(
        {
            "success": True,
            "name": template["name"],
            "subject": template["subject"],
            "html": html_content,
        }
    )


@templates_bp.route("/templates/import", methods=["POST"])
def import_template():
    """
    Import a new email template
    Accepts: name, subject, tags (comma-separated), and HTML file
    """
    # Get form data
    name = request.form.get("name")
    subject = request.form.get("subject")
    tags_string = request.form.get("tags", "")

    # Validate required fields
    if not name or not subject:
        return (
            jsonify({"success": False, "message": "Name and subject are required"}),
            400,
        )

    # Get uploaded file
    if "template_file" not in request.files:
        return jsonify({"success": False, "message": "No file uploaded"}), 400

    file = request.files["template_file"]

    if file.filename == "":
        return jsonify({"success": False, "message": "No file selected"}), 400

    # Validate file extension
    if not file.filename.endswith(".html"):
        return (
            jsonify({"success": False, "message": "Only HTML files are allowed"}),
            400,
        )

    # Read file content
    try:
        html_content = file.read().decode("utf-8")
    except Exception as e:
        return (
            jsonify({"success": False, "message": f"Error reading file: {str(e)}"}),
            400,
        )

    # Process tags
    tags = [tag.strip() for tag in tags_string.split(",") if tag.strip()]

    # Generate safe filename
    safe_name = secure_filename(name.lower().replace(" ", "_"))
    filename = f"{safe_name}.html"

    # Save template
    success, message = templates_repo.save_template(
        name=name,
        subject=subject,
        tags=tags,
        html_content=html_content,
        filename=filename,
    )

    if success:
        return jsonify({"success": True, "message": f"Template '{name}' imported successfully"})
    else:
        return jsonify({"success": False, "message": message}), 500
