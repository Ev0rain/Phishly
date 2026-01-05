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

    # Database Configuration (PostgreSQL via SQLAlchemy)
    # Format: postgresql://user:password@host:port/database
    database_url = os.environ.get("DATABASE_URL")
    if database_url:
        app.config["SQLALCHEMY_DATABASE_URI"] = database_url
        app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,  # Verify connections before using
            "pool_recycle": 300,    # Recycle connections after 5 minutes
        }
        print(f"✅ Database configured: {database_url.split('@')[1] if '@' in database_url else 'configured'}")
    else:
        print("⚠️  WARNING: DATABASE_URL not set. Database features disabled.")
        app.config["SQLALCHEMY_DATABASE_URI"] = None

    # Redis Configuration (for Flask-Session)
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        # Flask-Session configuration
        app.config["SESSION_TYPE"] = "redis"
        app.config["SESSION_PERMANENT"] = True
        app.config["PERMANENT_SESSION_LIFETIME"] = 7200  # 2 hours
        app.config["SESSION_USE_SIGNER"] = True  # Sign session cookies
        app.config["SESSION_KEY_PREFIX"] = "phishly:session:"
        
        # Redis connection will be initialized when Flask-Session is set up
        app.config["SESSION_REDIS_URL"] = redis_url
        
        # Cookie security settings
        app.config["SESSION_COOKIE_HTTPONLY"] = True   # Prevent JavaScript access
        app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # CSRF protection
        
        # Only use Secure flag in production (HTTPS)
        if not is_debug:
            app.config["SESSION_COOKIE_SECURE"] = True
        
        print(f"✅ Redis configured: {redis_url}")
    else:
        print("⚠️  WARNING: REDIS_URL not set. Using filesystem sessions (not recommended for production).")
        app.config["SESSION_TYPE"] = "filesystem"

    # Custom configuration override
    if config:
        app.config.update(config)

    # Initialize extensions (when database/redis are available)
    # Note: SQLAlchemy and Flask-Session will be initialized when implemented
    # For now, these are just configuration placeholders

    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.about import about_bp
    from routes.auth import auth_bp
    from routes.campaigns import campaigns_bp
    from routes.email_templates import templates_bp
    from routes.targets import targets_bp
    from routes.analytics import analytics_bp
    from routes.settings import settings_bp

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(about_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(campaigns_bp)
    app.register_blueprint(templates_bp)
    app.register_blueprint(targets_bp)
    app.register_blueprint(analytics_bp)
    app.register_blueprint(settings_bp)

    # Health check endpoint for Docker
    @app.route("/health")
    def health():
        """Docker health check endpoint"""
        status = {
            "status": "healthy",
            "service": "webadmin",
            "debug_mode": app.config.get("DEBUG", False)
        }
        
        # Optional: Add database connectivity check
        if app.config.get("SQLALCHEMY_DATABASE_URI"):
            status["database"] = "configured"
        
        # Optional: Add Redis connectivity check
        if app.config.get("SESSION_REDIS_URL"):
            status["redis"] = "configured"
        
        return status, 200

    return app


if __name__ == "__main__":
    # This block only runs when you execute: python app.py
    # In production, use a proper WSGI server like Gunicorn instead

    # Get configuration from environment variables
    is_debug = os.environ.get("FLASK_DEBUG", "True") == "True"
    port = int(os.environ.get("FLASK_PORT", "8006"))

    app = create_app()

    print("\n" + "=" * 70)
    print(f"🚀 Phishly WebAdmin starting on http://0.0.0.0:{port}")
    print(f"   Debug Mode: {'ENABLED' if is_debug else 'DISABLED'}")
    print(f"   Environment: {'Development' if is_debug else 'Production'}")
    print("=" * 70 + "\n")

    # WARNING: Never use debug=True in production!
    # For production, deploy with: gunicorn -w 4 -b 0.0.0.0:8006 app:create_app()
    app.run(host="0.0.0.0", port=port, debug=is_debug)

