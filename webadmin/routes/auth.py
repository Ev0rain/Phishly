"""
Authentication routes for Phishly WebAdmin
Handles login, logout using Flask-Login and database authentication
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from auth_utils import authenticate_user

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def login_page():
    """Display the login page"""
    # Redirect to dashboard if already logged in
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Handle login form submission with database authentication
    """
    username = request.form.get("username")
    password = request.form.get("password")
    remember = request.form.get("remember") == "on"

    # Validate input
    if not username or not password:
        flash("Please provide both username and password", "error")
        return redirect(url_for("auth.login_page"))

    # Authenticate user
    user = authenticate_user(username, password)

    if not user:
        flash("Username or Password is incorrect", "error")
        return redirect(url_for("auth.login_page"))

    # Login successful - create session
    login_user(user, remember=remember)
    flash(f"Welcome back, {user.full_name or user.username}!", "success")

    # Redirect to next page or dashboard
    next_page = request.args.get("next")
    if next_page:
        return redirect(next_page)

    return redirect(url_for("dashboard.index"))


@auth_bp.route("/logout")
@login_required
def logout():
    """
    Handle logout and clear session
    """
    logout_user()
    flash("You have been logged out successfully", "info")
    return redirect(url_for("auth.login_page"))
