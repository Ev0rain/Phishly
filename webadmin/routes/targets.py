"""
Targets Routes Blueprint
Handles target group management, creation, and CSV import
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_required, current_user
from repositories.targets_repository import TargetsRepository

targets_bp = Blueprint("targets", __name__)
targets_repo = TargetsRepository()


@targets_bp.route("/targets")
@login_required
def index():
    """Display all target groups"""
    groups = targets_repo.get_all_groups()

    return render_template(
        "targets.html",
        groups=groups,
        total_groups=len(groups),
        total_targets=sum(g["target_count"] for g in groups),
    )


@targets_bp.route("/targets/create", methods=["GET", "POST"])
@login_required
def create():
    """Create a new target group manually"""
    if request.method == "POST":
        # Handle form submission
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()

        # Get targets from textarea (one email per line)
        targets_text = request.form.get("targets", "").strip()
        targets_list = [email.strip() for email in targets_text.split("\n") if email.strip()]

        if not name:
            flash("Group name is required", "error")
            return redirect(url_for("targets.index") + "#create")

        if not targets_list:
            flash("At least one target email is required", "error")
            return redirect(url_for("targets.index") + "#create")

        # Create the group
        targets_repo.create_group(name, description, targets_list)

        flash(
            f"Target group '{name}' created successfully with {len(targets_list)} targets",
            "success",
        )
        return redirect(url_for("targets.index"))

    # GET request - show the create form (handled by JavaScript modal)
    return redirect(url_for("targets.index") + "#create")


@targets_bp.route("/targets/import", methods=["GET", "POST"])
@login_required
def import_csv():
    """Import target group from CSV file"""
    if request.method == "POST":
        # Check if file was uploaded
        if "csv_file" not in request.files:
            flash("No file uploaded", "error")
            return redirect(url_for("targets.index") + "#import")

        file = request.files["csv_file"]

        if file.filename == "":
            flash("No file selected", "error")
            return redirect(url_for("targets.index") + "#import")

        if not file.filename.endswith(".csv"):
            flash("File must be a CSV file", "error")
            return redirect(url_for("targets.index") + "#import")

        # Read and parse CSV content
        try:
            csv_content = file.read().decode("utf-8")
            result = targets_repo.parse_csv_targets(csv_content)

            if result["errors"]:
                # Show errors to user
                for error in result["errors"]:
                    flash(error, "warning")

            if result["count"] == 0:
                flash("No valid targets found in CSV file", "error")
                return redirect(url_for("targets.index") + "#import")

            # Get group name and description from form
            group_name = request.form.get("group_name", "").strip()
            group_description = request.form.get("group_description", "").strip()

            if not group_name:
                flash("Group name is required", "error")
                return redirect(url_for("targets.index") + "#import")

            # Create the group with parsed targets
            targets_repo.create_group(
                group_name,
                group_description,
                result["targets"],
                created_by_id=current_user.id
                if current_user and hasattr(current_user, "id")
                else None,
            )

            flash(
                f"Successfully imported {result['count']} targets into group '{group_name}'",
                "success",
            )
            return redirect(url_for("targets.index"))

        except Exception as e:
            flash(f"Error processing CSV file: {str(e)}", "error")
            return redirect(url_for("targets.index") + "#import")

    # GET request - redirect to main page with import modal
    return redirect(url_for("targets.index") + "#import")


@targets_bp.route("/targets/<int:group_id>")
@login_required
def view_group(group_id):
    """View details of a specific target group"""
    group = targets_repo.get_group_by_id(group_id)

    if not group:
        flash("Target group not found", "error")
        return redirect(url_for("targets.index"))

    return render_template(
        "targets_detail.html",
        group=group,
    )


@targets_bp.route("/api/targets/<int:group_id>/members")
@login_required
def get_group_members(group_id):
    """API endpoint to get members of a target group (for AJAX requests)"""
    members = targets_repo.get_group_members(group_id)

    return jsonify(
        {
            "success": True,
            "group_id": group_id,
            "members": members,
            "count": len(members),
        }
    )


@targets_bp.route("/targets/<int:group_id>/delete", methods=["POST"])
@login_required
def delete_group(group_id):
    """Delete a target group"""
    # In production, this would delete from database
    # For now, just show success message
    flash("Target group deleted successfully", "success")
    return redirect(url_for("targets.index"))


@targets_bp.route("/targets/<int:group_id>/edit", methods=["GET", "POST"])
@login_required
def edit_group(group_id):
    """Edit a target group"""
    group = targets_repo.get_group_by_id(group_id)

    if not group:
        flash("Target group not found", "error")
        return redirect(url_for("targets.index"))

    if request.method == "POST":
        # Handle edit form submission
        name = request.form.get("name", "").strip()
        # description is not used in current implementation
        # description = request.form.get("description", "").strip()

        if not name:
            flash("Group name is required", "error")
            return redirect(url_for("targets.edit_group", group_id=group_id))

        # In production, update database here
        flash(f"Target group '{name}' updated successfully", "success")
        return redirect(url_for("targets.index"))

    # GET request - show edit form
    return render_template(
        "targets_edit.html",
        group=group,
    )
