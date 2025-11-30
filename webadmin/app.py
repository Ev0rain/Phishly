"""
Phishly WebAdmin - Flask Application Factory

This is the main Flask application for the Phishly admin dashboard.
For authorized security awareness testing only.
"""

from flask import Flask
import os


def create_app(config=None):
    """Flask application factory"""
    app = Flask(__name__)

    # Default configuration
    app.config["SECRET_KEY"] = os.environ.get(
        "SECRET_KEY", "dev-secret-key-change-in-production"
    )
    app.config["DEBUG"] = os.environ.get("FLASK_DEBUG", "True") == "True"

    # Custom configuration override
    if config:
        app.config.update(config)

    # Register blueprints
    from routes.dashboard import dashboard_bp

    app.register_blueprint(dashboard_bp)

    return app


if __name__ == "__main__":
    # This block only runs when you execute: python app.py
    # In production, use a proper WSGI server like Gunicorn instead

    # Get configuration from environment variables
    is_debug = os.environ.get("FLASK_DEBUG", "True") == "True"
    port = int(os.environ.get("FLASK_PORT", "8006"))

    app = create_app()

    # WARNING: Never use debug=True in production!
    # For production, deploy with: gunicorn -w 4 -b 0.0.0.0:8006 app:create_app()
    app.run(host="0.0.0.0", port=port, debug=is_debug)
