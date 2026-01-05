"""
Settings routes for Phishly admin interface
"""

from flask import Blueprint, render_template

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
def index():
    """Settings page"""
    return render_template("settings.html")
