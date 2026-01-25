"""
About Blueprint - Information about Phishly
"""

from flask import Blueprint, render_template

about_bp = Blueprint("about", __name__)


@about_bp.route("/about")
def index():
    """About page with team info and ethical guidelines"""
    return render_template("about.html")
