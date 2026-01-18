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
            "pool_recycle": 300,  # Recycle connections after 5 minutes
        }
        db_display = database_url.split("@")[1] if "@" in database_url else "configured"
        print(f"✅ Database configured: {db_display}")
    else:
        print("⚠️  WARNING: DATABASE_URL not set. Database features disabled.")
        app.config["SQLALCHEMY_DATABASE_URI"] = None

    # Redis Configuration (for Flask-Session)
    redis_url = os.environ.get("REDIS_URL")
    if redis_url:
        # Flask-Session configuration for Redis
        app.config["SESSION_TYPE"] = "redis"
        app.config["SESSION_PERMANENT"] = True
        app.config["PERMANENT_SESSION_LIFETIME"] = 7200  # 2 hours
        app.config["SESSION_USE_SIGNER"] = True  # Sign session cookies for security
        app.config["SESSION_KEY_PREFIX"] = "phishly:session:"

        # CRITICAL: Use JSON serialization instead of msgpack/pickle
        # This prevents UnicodeDecodeError from incompatible formats
        app.config["SESSION_SERIALIZATION_FORMAT"] = "json"

        # Redis connection - must use decode_responses=True for proper string handling
        import redis

        # CRITICAL FIX: Clear ALL session data on startup to prevent corruption issues
        # This is safe because users just need to log in again
        try:
            r = redis.from_url(redis_url, decode_responses=False)
            session_keys = r.keys("phishly:session:*")
            if session_keys:
                deleted = r.delete(*session_keys)
                print(f"🧹 Cleared {deleted} session keys to prevent format corruption")
        except Exception as e:
            print(f"⚠️  Could not clear sessions: {e}")

        # Now create the proper Redis connection for Flask-Session
        app.config["SESSION_REDIS"] = redis.from_url(redis_url, decode_responses=True)

        print(f"✅ Redis configured: {redis_url}")
        print("✅ Redis sessions enabled with JSON serialization")
    else:
        warning_msg = (
            "⚠️  WARNING: REDIS_URL not set. Using filesystem sessions "
            "(not recommended for production)."
        )
        print(warning_msg)
        app.config["SESSION_TYPE"] = "filesystem"
        app.config["SESSION_PERMANENT"] = True
        app.config["PERMANENT_SESSION_LIFETIME"] = 7200

    # Cookie security settings
    app.config["SESSION_COOKIE_HTTPONLY"] = True  # Prevent JavaScript access
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"  # CSRF protection

    # Only use Secure flag in production (HTTPS)
    if not is_debug:
        app.config["SESSION_COOKIE_SECURE"] = True

    # Custom configuration override
    if config:
        app.config.update(config)

    # Initialize database
    from database import db

    db.init_app(app)

    # Initialize Flask-Login (authentication)
    from auth_utils import login_manager

    login_manager.init_app(app)
    print("✅ Flask-Login initialized")

    # Initialize Flask-Session (Redis or filesystem backed)
    from flask_session import Session

    Session(app)
    session_type = app.config.get("SESSION_TYPE", "unknown")
    print(f"✅ Flask-Session initialized with {session_type} backend")

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

    # Session corruption error handler
    # Catches UnicodeDecodeError from corrupted Redis sessions
    @app.before_request
    def handle_corrupted_session():
        """Clear corrupted session data before processing request"""
        from flask import session as flask_session, request, redirect, url_for

        try:
            # Try to access session to trigger any decoding errors
            _ = dict(flask_session)
        except (ValueError, TypeError) as e:
            # Session is corrupted, clear it
            print(f"⚠️  Corrupted session detected: {e}")
            print(f"   Clearing session for: {request.remote_addr}")

            # Clear the session
            flask_session.clear()

            # If Redis is configured, try to delete the session key directly
            if app.config.get("SESSION_TYPE") == "redis":
                try:
                    from flask import request as req

                    session_cookie = req.cookies.get(
                        app.config.get("SESSION_COOKIE_NAME", "session")
                    )
                    if session_cookie:
                        redis_conn = app.config.get("SESSION_REDIS")
                        if redis_conn:
                            key_prefix = app.config.get("SESSION_KEY_PREFIX", "session:")
                            key = f"{key_prefix}{session_cookie}"
                            redis_conn.delete(key)
                            print(f"   Deleted corrupted Redis key: {key}")
                except Exception as redis_err:
                    print(f"   Could not delete Redis key: {redis_err}")

            # Redirect to login page if not already there
            if not request.path.startswith("/login") and not request.path.startswith("/static"):
                return redirect(url_for("auth.login_page"))

    # Register CLI commands
    from cli_commands import register_commands

    register_commands(app)

    # Health check endpoint for Docker
    @app.route("/health")
    def health():
        """Docker health check endpoint"""
        from database import test_connection

        status = {
            "status": "healthy",
            "service": "webadmin",
            "debug_mode": app.config.get("DEBUG", False),
        }

        # Test database connectivity
        if app.config.get("SQLALCHEMY_DATABASE_URI"):
            db_connected = test_connection()
            status["database"] = "connected" if db_connected else "disconnected"
            if not db_connected:
                status["status"] = "degraded"

        # Check Redis configuration
        session_type = app.config.get("SESSION_TYPE", "unknown")
        if os.environ.get("REDIS_URL") and session_type == "redis":
            status["redis"] = "connected (redis sessions active)"
        elif os.environ.get("REDIS_URL"):
            status["redis"] = "configured (filesystem fallback)"
        else:
            status["redis"] = "not configured"

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
