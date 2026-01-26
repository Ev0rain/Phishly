"""
Phishly Phishing Server

This server handles:
1. Serving cached landing pages
2. Tracking link clicks via tracking tokens
3. Logging form submissions
4. Tracking pixel for email opens
5. Handling anonymous/invalid token visits

Landing pages are cached to the filesystem by webadmin when campaigns launch.
The server reads from this cache for fast response times.
"""

import os
import json
import logging
from pathlib import Path
from datetime import datetime

from flask import (
    Flask,
    abort,
    request,
    send_from_directory,
    redirect,
    Response,
    jsonify,
)

from database import (
    db_manager,
    get_campaign_target_by_token,
    get_landing_page_by_url_path,
    get_active_landing_page_config,
    log_event,
    update_campaign_target_status,
    create_form_submission,
    Campaign,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = Path(os.getenv("CACHE_DIR", "/app/cache"))  # Legacy cache support
CAMPAIGN_DEPLOYMENTS_DIR = Path("/app/campaign_landing_pages")  # NEW: Campaign deployments
PHISHING_DOMAIN = os.getenv("PHISHING_DOMAIN", "phishing.example.com")

# Create Flask app
app = Flask(__name__, static_folder=None)


# ============================================
# Helper Functions
# ============================================


def get_client_ip() -> str:
    """Get the real client IP address, handling proxies."""
    if request.headers.get("X-Forwarded-For"):
        return request.headers.get("X-Forwarded-For").split(",")[0].strip()
    if request.headers.get("X-Real-IP"):
        return request.headers.get("X-Real-IP")
    return request.remote_addr or "unknown"


def parse_user_agent(user_agent_str: str) -> dict:
    """Parse user agent string to extract browser, OS, and device type."""
    ua = user_agent_str.lower() if user_agent_str else ""

    # Simple browser detection
    browser = "unknown"
    if "chrome" in ua and "edg" not in ua:
        browser = "Chrome"
    elif "firefox" in ua:
        browser = "Firefox"
    elif "safari" in ua and "chrome" not in ua:
        browser = "Safari"
    elif "edg" in ua:
        browser = "Edge"
    elif "msie" in ua or "trident" in ua:
        browser = "Internet Explorer"

    # Simple OS detection
    os_name = "unknown"
    if "windows" in ua:
        os_name = "Windows"
    elif "mac os" in ua or "macintosh" in ua:
        os_name = "macOS"
    elif "linux" in ua:
        os_name = "Linux"
    elif "android" in ua:
        os_name = "Android"
    elif "iphone" in ua or "ipad" in ua:
        os_name = "iOS"

    # Simple device type detection
    device_type = "desktop"
    if "mobile" in ua or "android" in ua or "iphone" in ua:
        device_type = "mobile"
    elif "ipad" in ua or "tablet" in ua:
        device_type = "tablet"

    return {
        "browser": browser,
        "os": os_name,
        "device_type": device_type,
    }


def get_active_campaign_id() -> int | None:
    """
    Get the active campaign ID from the database.

    Returns:
        Campaign ID if found, None otherwise
    """
    try:
        with db_manager.get_session() as session:
            # Query for active landing page configuration
            config = get_active_landing_page_config(session)
            if config and config.active_landing_page_id:
                # Get campaign using this landing page
                campaign = session.query(Campaign).filter(
                    Campaign.landing_page_id == config.active_landing_page_id,
                    Campaign.status == 'active'
                ).first()
                if campaign:
                    return campaign.id
    except Exception as e:
        logger.error(f"Error getting active campaign: {e}")
    return None


def find_cached_landing_page(url_path: str) -> tuple[Path, dict] | None:
    """
    Find cached landing page by URL path.

    Priority:
    1. Preview deployment (campaign_landing_pages/preview/) - if path starts with "preview/"
    2. Campaign deployments (campaign_landing_pages/{campaign_id}/)
    3. Active landing page cache (cache/active/{url_path}/) - LEGACY
    4. Campaign-specific cache (cache/{campaign_id}/{url_path}/) - LEGACY

    Returns:
        Tuple of (cache_dir_path, landing_page_info) or None if not found
    """
    normalized_path = url_path.strip("/")

    # PREVIEW: Check if this is a preview request (path starts with "preview/")
    if normalized_path.startswith("preview/") or normalized_path == "preview":
        preview_dir = CAMPAIGN_DEPLOYMENTS_DIR / "preview"
        if preview_dir.exists():
            # Remove "preview/" prefix from path
            preview_path = normalized_path.replace("preview/", "", 1) if normalized_path.startswith("preview/") else ""

            if not preview_path:
                # Just "/preview" - serve index.html
                index_file = preview_dir / "index.html"
                if index_file.exists():
                    return preview_dir, {"preview": True}
            else:
                # "/preview/something.html" or "/preview/assets/..."
                direct_file = preview_dir / preview_path
                if direct_file.exists() and direct_file.is_file():
                    return preview_dir, {"preview": True, "file": preview_path}

                # Try as directory with index.html
                page_dir = preview_dir / preview_path
                index_file = page_dir / "index.html"
                if index_file.exists():
                    return page_dir, {"preview": True}

    # NEW: Check campaign deployments (highest priority for non-preview)
    if CAMPAIGN_DEPLOYMENTS_DIR.exists():
        # Try to find active campaign
        active_campaign_id = get_active_campaign_id()
        if active_campaign_id:
            campaign_dir = CAMPAIGN_DEPLOYMENTS_DIR / str(active_campaign_id)
            if campaign_dir.exists():
                # Try exact path match first (e.g., "login.html")
                direct_file = campaign_dir / normalized_path
                if direct_file.exists() and direct_file.is_file():
                    return campaign_dir, {"campaign_id": active_campaign_id, "file": normalized_path}

                # Try as directory with index.html
                page_dir = campaign_dir / normalized_path
                index_file = page_dir / "index.html"
                if index_file.exists():
                    return page_dir, {"campaign_id": active_campaign_id}

                # Try root index.html if path is empty or "/"
                if not normalized_path:
                    index_file = campaign_dir / "index.html"
                    if index_file.exists():
                        return campaign_dir, {"campaign_id": active_campaign_id}

                # FALLBACK: If path not found, serve from campaign root
                # This handles cases where url_path like "/en/home" is configured
                # but files are deployed to campaign root (not a subdirectory)
                root_index = campaign_dir / "index.html"
                if root_index.exists():
                    logger.info(f"Path '{normalized_path}' not found, falling back to campaign root")
                    return campaign_dir, {"campaign_id": active_campaign_id}
        else:
            # No active campaign - check for "active" deployment (for testing without campaign)
            active_dir = CAMPAIGN_DEPLOYMENTS_DIR / "active"
            if active_dir.exists():
                # Try exact path match first
                direct_file = active_dir / normalized_path
                if direct_file.exists() and direct_file.is_file():
                    return active_dir, {"source": "active", "file": normalized_path}

                # Try as directory with index.html
                page_dir = active_dir / normalized_path
                index_file = page_dir / "index.html"
                if index_file.exists():
                    return page_dir, {"source": "active"}

                # Try root index.html if path is empty or "/"
                if not normalized_path:
                    index_file = active_dir / "index.html"
                    if index_file.exists():
                        return active_dir, {"source": "active"}

                # FALLBACK: If path not found, serve from active root
                root_index = active_dir / "index.html"
                if root_index.exists():
                    logger.info(f"Path '{normalized_path}' not found, falling back to active root")
                    return active_dir, {"source": "active"}

    # LEGACY: Check active cache
    active_cache_dir = CACHE_DIR / "active"
    if active_cache_dir.exists():
        page_dir = active_cache_dir / normalized_path
        index_file = page_dir / "index.html"
        if index_file.exists():
            return page_dir, {"source": "active"}

    # LEGACY: Fall back to campaign-specific caches
    if CACHE_DIR.exists():
        for campaign_dir in CACHE_DIR.iterdir():
            if campaign_dir.is_dir() and campaign_dir.name != "active":
                page_dir = campaign_dir / normalized_path
                index_file = page_dir / "index.html"
                if index_file.exists():
                    return page_dir, {"campaign_id": campaign_dir.name}

    return None


# ============================================
# Routes
# ============================================


@app.route("/health")
def health_check():
    """Health check endpoint for Docker."""
    try:
        db_connected = db_manager.test_connection()
        return jsonify({
            "status": "healthy" if db_connected else "degraded",
            "database": "connected" if db_connected else "disconnected",
            "cache_dir": str(CACHE_DIR),
            "cache_exists": CACHE_DIR.exists(),
        })
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 500


@app.route("/track/open")
def track_email_open():
    """
    Track email opens via tracking pixel.

    Returns a 1x1 transparent GIF.
    """
    token = request.args.get("t")
    ip_address = get_client_ip()
    user_agent = request.headers.get("User-Agent", "")
    ua_info = parse_user_agent(user_agent)

    if token:
        try:
            with db_manager.get_session() as session:
                campaign_target = get_campaign_target_by_token(session, token)

                if campaign_target:
                    # Log email_opened event
                    log_event(
                        session,
                        campaign_target_id=campaign_target.id,
                        event_type_name="email_opened",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        browser=ua_info["browser"],
                        os_name=ua_info["os"],
                        device_type=ua_info["device_type"],
                    )

                    # Update status to "opened"
                    update_campaign_target_status(session, campaign_target.id, "opened")

                    logger.info(
                        f"Email opened: token={token[:8]}... target_id={campaign_target.target_id}"
                    )
                else:
                    logger.warning(f"Invalid tracking token for email open: {token[:8]}...")

        except Exception as e:
            logger.error(f"Error tracking email open: {e}")

    # Return 1x1 transparent GIF
    gif_data = (
        b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\xff\xff\xff"
        b"\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00"
        b"\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b"
    )
    return Response(gif_data, mimetype="image/gif")


@app.route("/api/submit", methods=["POST"])
def handle_form_submission():
    """
    Handle form submissions from landing pages.

    Expects form data or JSON with tracking token.
    """
    token = request.args.get("t") or request.form.get("t") or request.form.get("_token")
    ip_address = get_client_ip()
    user_agent = request.headers.get("User-Agent", "")
    ua_info = parse_user_agent(user_agent)

    # Get form data
    if request.is_json:
        form_data = request.get_json()
    else:
        form_data = dict(request.form)

    # Remove tracking token from form data
    form_data.pop("t", None)
    form_data.pop("_token", None)

    redirect_url = None

    if token:
        try:
            with db_manager.get_session() as session:
                campaign_target = get_campaign_target_by_token(session, token)

                if campaign_target:
                    # Check if credentials were captured
                    has_credentials = any(
                        key.lower() in ["password", "pwd", "pass", "secret"]
                        for key in form_data.keys()
                    )

                    event_type = (
                        "credentials_captured" if has_credentials else "form_submitted"
                    )

                    # Log event
                    log_event(
                        session,
                        campaign_target_id=campaign_target.id,
                        event_type_name=event_type,
                        ip_address=ip_address,
                        user_agent=user_agent,
                        browser=ua_info["browser"],
                        os_name=ua_info["os"],
                        device_type=ua_info["device_type"],
                    )

                    # Create form submission record
                    create_form_submission(
                        session,
                        campaign_target_id=campaign_target.id,
                        ip_address=ip_address,
                        user_agent=user_agent,
                    )

                    # Update status to "submitted"
                    update_campaign_target_status(
                        session, campaign_target.id, "submitted"
                    )

                    # Get redirect URL from campaign's landing page
                    if campaign_target.campaign and campaign_target.campaign.landing_page:
                        redirect_url = campaign_target.campaign.landing_page.redirect_url

                    logger.info(
                        f"Form submitted: token={token[:8]}... "
                        f"event={event_type} fields={list(form_data.keys())}"
                    )
                else:
                    # Anonymous submission
                    log_event(
                        session,
                        campaign_target_id=None,
                        event_type_name="anonymous_submission",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        browser=ua_info["browser"],
                        os_name=ua_info["os"],
                        device_type=ua_info["device_type"],
                    )
                    logger.warning(f"Anonymous form submission: invalid token {token[:8]}...")

        except Exception as e:
            logger.error(f"Error handling form submission: {e}")

    else:
        # No token provided
        try:
            with db_manager.get_session() as session:
                log_event(
                    session,
                    campaign_target_id=None,
                    event_type_name="anonymous_submission",
                    ip_address=ip_address,
                    user_agent=user_agent,
                    browser=ua_info["browser"],
                    os_name=ua_info["os"],
                    device_type=ua_info["device_type"],
                )
        except Exception as e:
            logger.error(f"Error logging anonymous submission: {e}")

    # Redirect to configured URL or return success
    if redirect_url:
        return redirect(redirect_url)

    return jsonify({"status": "success", "message": "Form received"})


@app.route("/<path:url_path>")
def serve_landing_page(url_path):
    """
    Serve landing page and track link clicks.

    1. Look up landing page in cache or campaign deployment
    2. Validate tracking token (if present)
    3. Log link_clicked or anonymous_visit event (for HTML pages only)
    4. Serve the content with proper MIME type
    """
    token = request.args.get("t")
    ip_address = get_client_ip()
    user_agent = request.headers.get("User-Agent", "")
    ua_info = parse_user_agent(user_agent)

    # Track credential submission when target reaches the awareness page.
    # This MUST happen before the cache/DB content lookup because the
    # awareness page may not exist as a cached landing page, which would
    # cause the tracking code to never execute if it were nested inside
    # the cache_result or landing_page blocks.
    normalized_url = url_path.strip("/").lower()
    is_awareness_page = normalized_url == "awareness" or normalized_url.startswith("awareness/")

    if is_awareness_page and token:
        try:
            with db_manager.get_session() as session:
                campaign_target = get_campaign_target_by_token(session, token)
                if campaign_target:
                    log_event(
                        session,
                        campaign_target_id=campaign_target.id,
                        event_type_name="form_submitted",
                        ip_address=ip_address,
                        user_agent=user_agent,
                        browser=ua_info["browser"],
                        os_name=ua_info["os"],
                        device_type=ua_info["device_type"],
                    )
                    update_campaign_target_status(
                        session, campaign_target.id, "submitted"
                    )
                    logger.info(
                        f"Credentials submitted (awareness page): token={token[:8]}... "
                        f"target_id={campaign_target.target_id}"
                    )
        except Exception as e:
            logger.error(f"Error tracking credential submission: {e}")

    # Try to find cached landing page first
    cache_result = find_cached_landing_page(url_path)

    if cache_result:
        cache_dir, cache_info = cache_result

        # Determine file to serve
        file_to_serve = "index.html"
        is_html_page = True

        # Check if this is a direct file reference (e.g., "login.html", "assets/css/style.css")
        if "file" in cache_info:
            file_to_serve = cache_info["file"]
            is_html_page = file_to_serve.endswith(".html")
        elif url_path.endswith((".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".avif", ".ico", ".woff", ".woff2", ".ttf", ".eot")):
            # This is a static asset, not a landing page
            is_html_page = False
            file_to_serve = url_path.split("/")[-1]  # Get filename
        elif url_path.endswith(".html"):
            # Direct HTML file reference
            file_to_serve = url_path.split("/")[-1]
            is_html_page = True

        # Track the visit (only for HTML pages, not for static assets)
        # Note: awareness page credential tracking is handled above, before cache lookup
        if is_html_page and not is_awareness_page:
            if token:
                try:
                    with db_manager.get_session() as session:
                        campaign_target = get_campaign_target_by_token(session, token)

                        if campaign_target:
                            log_event(
                                session,
                                campaign_target_id=campaign_target.id,
                                event_type_name="link_clicked",
                                ip_address=ip_address,
                                user_agent=user_agent,
                                browser=ua_info["browser"],
                                os_name=ua_info["os"],
                                device_type=ua_info["device_type"],
                            )
                            update_campaign_target_status(
                                session, campaign_target.id, "clicked"
                            )
                            logger.info(
                                f"Link clicked: token={token[:8]}... "
                                f"url_path={url_path} target_id={campaign_target.target_id}"
                            )
                        else:
                            log_event(
                                session,
                                campaign_target_id=None,
                                event_type_name="anonymous_visit",
                                ip_address=ip_address,
                                user_agent=user_agent,
                                browser=ua_info["browser"],
                                os_name=ua_info["os"],
                                device_type=ua_info["device_type"],
                            )
                            logger.warning(
                                f"Anonymous visit (invalid token): url_path={url_path}"
                            )

                except Exception as e:
                    logger.error(f"Error tracking link click: {e}")

            else:
                # No token - anonymous visit
                try:
                    with db_manager.get_session() as session:
                        log_event(
                            session,
                            campaign_target_id=None,
                            event_type_name="anonymous_visit",
                            ip_address=ip_address,
                            user_agent=user_agent,
                            browser=ua_info["browser"],
                            os_name=ua_info["os"],
                            device_type=ua_info["device_type"],
                        )
                        logger.warning(f"Anonymous visit (no token): url_path={url_path}")

                except Exception as e:
                    logger.error(f"Error logging anonymous visit: {e}")

        # Serve the file from the campaign deployment or cache directory
        # Handle nested paths for assets (e.g., "assets/home/style.css")
        if "file" in cache_info:
            # Direct file reference - serve from campaign root
            return send_from_directory(cache_dir, cache_info["file"])
        else:
            # Serve index.html or other file
            return send_from_directory(cache_dir, file_to_serve)

    # No cache found - try database lookup
    try:
        with db_manager.get_session() as session:
            landing_page = get_landing_page_by_url_path(session, url_path)

            if landing_page:
                # Track link click (awareness page tracking already handled above)
                if not is_awareness_page:
                    if token:
                        campaign_target = get_campaign_target_by_token(session, token)
                        if campaign_target:
                            log_event(
                                session,
                                campaign_target_id=campaign_target.id,
                                event_type_name="link_clicked",
                                ip_address=ip_address,
                                user_agent=user_agent,
                                browser=ua_info["browser"],
                                os_name=ua_info["os"],
                                device_type=ua_info["device_type"],
                            )
                            update_campaign_target_status(
                                session, campaign_target.id, "clicked"
                            )
                        else:
                            log_event(
                                session,
                                campaign_target_id=None,
                                event_type_name="anonymous_visit",
                                ip_address=ip_address,
                                user_agent=user_agent,
                            )
                    else:
                        log_event(
                            session,
                            campaign_target_id=None,
                            event_type_name="anonymous_visit",
                            ip_address=ip_address,
                            user_agent=user_agent,
                        )

                # Return HTML content directly from database
                return Response(
                    landing_page.html_content,
                    mimetype="text/html",
                )

    except Exception as e:
        logger.error(f"Error serving landing page from database: {e}")

    # Nothing found
    logger.warning(f"Landing page not found: {url_path}")
    abort(404)


@app.route("/")
def index():
    """Root endpoint - serve landing page if available."""
    # Try to serve from active deployment
    return serve_landing_page("")


# ============================================
# Error Handlers
# ============================================


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors with a generic page."""
    return Response(
        "<html><body><h1>Page Not Found</h1></body></html>",
        status=404,
        mimetype="text/html",
    )


@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors."""
    logger.error(f"Server error: {e}")
    return Response(
        "<html><body><h1>Server Error</h1></body></html>",
        status=500,
        mimetype="text/html",
    )


# ============================================
# Main
# ============================================

if __name__ == "__main__":
    logger.info(f"Starting Phishly Phishing Server")
    logger.info(f"Cache directory: {CACHE_DIR}")
    logger.info(f"Phishing domain: {PHISHING_DOMAIN}")

    # Test database connection
    if db_manager.test_connection():
        logger.info("Database connection: OK")
    else:
        logger.error("Database connection: FAILED")

    app.run(host="0.0.0.0", port=8000, debug=os.getenv("FLASK_DEBUG", "false").lower() == "true")
