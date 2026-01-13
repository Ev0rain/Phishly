"""
Settings routes for Phishly admin interface
"""

from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from database import db
from db.models import AdminUser
from datetime import datetime

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
@login_required
def index():
    """Settings page"""
    # Get all admin users for user management section
    users = db.session.query(AdminUser).order_by(AdminUser.created_at.desc()).all()
    return render_template("settings.html", users=users)


@settings_bp.route("/settings/change-password", methods=["POST"])
@login_required
def change_password():
    """Handle password change request"""
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_password = request.form.get("confirm_password")

    # Validate inputs
    if not all([current_password, new_password, confirm_password]):
        flash("All fields are required", "error")
        return redirect(url_for("settings.index"))

    if new_password != confirm_password:
        flash("New passwords do not match", "error")
        return redirect(url_for("settings.index"))

    if len(new_password) < 8:
        flash("New password must be at least 8 characters long", "error")
        return redirect(url_for("settings.index"))

    # Get current user from database
    admin_user = db.session.get(AdminUser, current_user.id)

    if not admin_user:
        flash("User not found", "error")
        return redirect(url_for("settings.index"))

    # Verify current password
    if not check_password_hash(admin_user.password_hash, current_password):
        flash("Current password is incorrect", "error")
        return redirect(url_for("settings.index"))

    # Update password
    try:
        admin_user.password_hash = generate_password_hash(new_password)
        db.session.commit()
        flash("Password changed successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error changing password: {str(e)}", "error")

    return redirect(url_for("settings.index"))


@settings_bp.route("/settings/users/create", methods=["POST"])
@login_required
def create_user():
    """Create new admin user"""
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")
    full_name = request.form.get("full_name")

    # Validate inputs
    if not all([username, email, password]):
        return (
            jsonify({"success": False, "message": "Username, email, and password are required"}),
            400,
        )

    if len(password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters"}), 400

    # Check if username or email already exists
    existing_user = (
        db.session.query(AdminUser)
        .filter((AdminUser.username == username) | (AdminUser.email == email))
        .first()
    )

    if existing_user:
        return jsonify({"success": False, "message": "Username or email already exists"}), 400

    # Create new user
    try:
        new_user = AdminUser(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            full_name=full_name,
            is_active=True,
            created_at=datetime.utcnow(),
        )
        db.session.add(new_user)
        db.session.commit()

        return jsonify({"success": True, "message": f"User '{username}' created successfully"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error creating user: {str(e)}"}), 500


@settings_bp.route("/settings/users/<int:user_id>/toggle", methods=["POST"])
@login_required
def toggle_user_status(user_id):
    """Toggle user active/inactive status"""
    # Prevent deactivating yourself
    if user_id == current_user.id:
        return jsonify({"success": False, "message": "You cannot deactivate your own account"}), 400

    try:
        user = db.session.get(AdminUser, user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        # Toggle status
        user.is_active = not user.is_active
        action = "activated" if user.is_active else "deactivated"

        db.session.commit()

        return jsonify(
            {"success": True, "message": f"User '{user.username}' {action} successfully"}
        )

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error updating user: {str(e)}"}), 500


@settings_bp.route("/settings/users/<int:user_id>/reset-password", methods=["POST"])
@login_required
def reset_user_password(user_id):
    """Reset user password to a default"""
    new_password = request.form.get("new_password")

    if not new_password or len(new_password) < 8:
        return jsonify({"success": False, "message": "Password must be at least 8 characters"}), 400

    try:
        user = db.session.get(AdminUser, user_id)

        if not user:
            return jsonify({"success": False, "message": "User not found"}), 404

        user.password_hash = generate_password_hash(new_password)
        db.session.commit()

        return jsonify({"success": True, "message": f"Password reset for user '{user.username}'"})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": f"Error resetting password: {str(e)}"}), 500
