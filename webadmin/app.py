"""
Phishly WebAdmin - Flask Application Factory

This is the main Flask application for the Phishly admin dashboard.
For authorized security awareness testing only.
"""

from flask import Flask
import os
import secrets


def create_app(config=None):
    """Flask application factory"""
    app = Flask(__name__)

    # Load SECRET_KEY with security validation
    secret_key = os.environ.get("SECRET_KEY", "")
    is_debug = os.environ.get("FLASK_DEBUG", "True") == "True"

    # Security check: prevent using placeholder or empty key
    if not secret_key or secret_key == "CHANGE_THIS_TO_RANDOM_64_CHARACTER_HEX_STRING":
        if is_debug:
            # Development: Auto-generate with warning
            secret_key = secrets.token_hex(32)
            print("⚠️  WARNING: Using auto-generated SECRET_KEY for development.")
            print("   Generate a secure key for production with:")
            print('   python -c "import secrets; print(secrets.token_hex(32))"\n')
        else:
            # Production: Refuse to start
            raise ValueError(
                "\n" + "=" * 70 + "\n"
                "ERROR: SECRET_KEY not configured!\n"
                "\n"
                "Generate a secure random key with:\n"
                '  python -c "import secrets; print(secrets.token_hex(32))"\n'
                "\n"
                "Then add it to your .env file or environment variables.\n"
                "NEVER commit the actual SECRET_KEY to version control!\n"
                "=" * 70
            )

    app.config["SECRET_KEY"] = secret_key
    app.config["DEBUG"] = is_debug

    # Custom configuration override
    if config:
        app.config.update(config)

    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.about import about_bp
    from routes.auth import auth_bp
    from routes.campaigns import campaigns_bp
    from routes.email_templates import templates_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(templates_bp)

    # Health check endpoint for Docker
    @app.route("/health")
    def health():
        return {"status": "healthy", "service": "webadmin"}, 200

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
