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
    log_event,
    update_campaign_target_status,
    create_form_submission,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Configuration
BASE_DIR = Path(__file__).resolve().parent
CACHE_DIR = Path(os.getenv("CACHE_DIR", "/app/cache"))
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


def find_cached_landing_page(url_path: str) -> tuple[Path, dict] | None:
    """
    Find cached landing page by URL path.

    Searches in cache directory structure:
    cache/{campaign_id}/{url_path}/index.html

    Returns:
        Tuple of (cache_dir_path, landing_page_info) or None if not found
    """
    normalized_path = url_path.strip("/")

    # Search all campaign cache directories
    if CACHE_DIR.exists():
        for campaign_dir in CACHE_DIR.iterdir():
            if campaign_dir.is_dir():
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

    1. Look up landing page in cache
    2. Validate tracking token (if present)
    3. Log link_clicked or anonymous_visit event
    4. Serve the HTML content
    """
    token = request.args.get("t")
    ip_address = get_client_ip()
    user_agent = request.headers.get("User-Agent", "")
    ua_info = parse_user_agent(user_agent)

    # Try to find cached landing page first
    cache_result = find_cached_landing_page(url_path)

    if cache_result:
        cache_dir, cache_info = cache_result

        # Track the visit
        if token:
            try:
                with db_manager.get_session() as session:
                    campaign_target = get_campaign_target_by_token(session, token)

                    if campaign_target:
                        # Valid token - log link_clicked
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

                        # Update status to "clicked"
                        update_campaign_target_status(
                            session, campaign_target.id, "clicked"
                        )

                        logger.info(
                            f"Link clicked: token={token[:8]}... "
                            f"url_path={url_path} target_id={campaign_target.target_id}"
                        )
                    else:
                        # Invalid token
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

        # Serve the cached landing page
        return send_from_directory(cache_dir, "index.html")

    # No cache found - try database lookup
    try:
        with db_manager.get_session() as session:
            landing_page = get_landing_page_by_url_path(session, url_path)

            if landing_page:
                # Track the visit (same logic as above)
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
    """Root endpoint - return minimal response."""
    return Response("", status=204)


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
