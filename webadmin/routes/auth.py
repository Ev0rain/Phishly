"""
Authentication routes for Phishly WebAdmin
Handles login, logout (frontend only for now - no backend implementation)
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def login_page():
    """Display the login page"""
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Handle login form submission
    TODO: Implement actual authentication when database and Redis are ready
    """
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember")

    # Placeholder - no authentication yet
    # When ready, implement:
    # 1. Query database for user
    # 2. Verify password hash
    # 3. Create session in Redis
    # 4. Redirect to dashboard

    # For now, just redirect back to login with a message
    flash("Authentication not yet implemented - database pending", "error")
    return redirect(url_for("auth.login_page"))


@auth_bp.route("/logout")
def logout():
    """
    Handle logout
    TODO: Clear Redis session when implemented
    """
    # Placeholder - no session management yet
    return redirect(url_for("auth.login_page"))
