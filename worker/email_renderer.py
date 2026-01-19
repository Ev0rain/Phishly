"""
Email template rendering for Phishly phishing campaigns.

This module handles Jinja2 template rendering for phishing emails,
including variable substitution, tracking link injection, and HTML/text formatting.
"""

import base64
import hashlib
import hmac
import logging
import os
import secrets
from datetime import datetime, timedelta
from typing import Dict, Tuple
from urllib.parse import urlencode

from jinja2 import Template, TemplateSyntaxError, UndefinedError

logger = logging.getLogger(__name__)

# Secret key for HMAC-based tracking tokens
TRACKING_SECRET_KEY = os.getenv("TRACKING_SECRET_KEY", "default-tracking-secret-key")


class EmailRenderer:
    """Render email templates with Jinja2."""

    def __init__(self, phishing_domain: str = "phishing.example.com"):
        """
        Initialize email renderer.

        Args:
            phishing_domain: Domain for phishing landing pages
        """
        self.phishing_domain = phishing_domain

    def render_email(
        self,
        html_template: str,
        text_template: str,
        variables: Dict,
        tracking_token: str,
        landing_page_url: str,
    ) -> Tuple[str, str]:
        """
        Render both HTML and text versions of an email.

        Args:
            html_template: HTML email template with Jinja2 syntax
            text_template: Plain text email template with Jinja2 syntax
            variables: Dictionary of template variables
            tracking_token: Unique tracking token for this email
            landing_page_url: Landing page URL path

        Returns:
            Tuple of (html_content, text_content)

        Raises:
            TemplateSyntaxError: If template has syntax errors
            UndefinedError: If required variable is missing
        """
        # Build tracking URLs
        tracking_pixel_url = self._build_tracking_pixel_url(tracking_token)
        phishing_link_url = self._build_phishing_link_url(landing_page_url, tracking_token)
        unsubscribe_url = self._build_unsubscribe_url(tracking_token)

        # Add tracking URLs and auto-generated variables
        render_vars = {
            **variables,
            # Tracking URLs
            "tracking_pixel_url": tracking_pixel_url,
            "phishing_link": phishing_link_url,
            "landing_page_url": phishing_link_url,  # Alias for compatibility
            "unsubscribe_url": unsubscribe_url,
            # Auto-generated variables (for shipping templates, etc.)
            "tracking_number": self.generate_tracking_number(),
            "delivery_date": self.generate_delivery_date(),
            "year": str(datetime.now().year),
        }

        # Render HTML version
        try:
            html_jinja = Template(html_template)
            html_content = html_jinja.render(**render_vars)
        except TemplateSyntaxError as e:
            logger.error(f"HTML template syntax error: {e}")
            raise
        except UndefinedError as e:
            logger.error(f"HTML template undefined variable: {e}")
            raise

        # Render text version
        try:
            text_jinja = Template(text_template)
            text_content = text_jinja.render(**render_vars)
        except TemplateSyntaxError as e:
            logger.error(f"Text template syntax error: {e}")
            raise
        except UndefinedError as e:
            logger.error(f"Text template undefined variable: {e}")
            raise

        # Inject tracking pixel into HTML (at end of body)
        html_content = self._inject_tracking_pixel(html_content, tracking_pixel_url)

        logger.info(f"Email rendered successfully for token {tracking_token}")
        return html_content, text_content

    def _build_tracking_pixel_url(self, tracking_token: str) -> str:
        """
        Build tracking pixel URL for email opens.

        Args:
            tracking_token: Unique tracking token

        Returns:
            URL to tracking pixel image
        """
        params = urlencode({"t": tracking_token})
        return f"https://{self.phishing_domain}/track/open?{params}"

    def _build_phishing_link_url(self, landing_page_url: str, tracking_token: str) -> str:
        """
        Build phishing link URL with tracking.

        Args:
            landing_page_url: Landing page URL path
            tracking_token: Unique tracking token

        Returns:
            Full phishing link URL
        """
        params = urlencode({"t": tracking_token})
        # Remove leading slash if present
        landing_page_url = landing_page_url.lstrip("/")
        return f"https://{self.phishing_domain}/{landing_page_url}?{params}"

    def _build_unsubscribe_url(self, tracking_token: str) -> str:
        """
        Build unsubscribe URL (optional feature).

        Args:
            tracking_token: Unique tracking token

        Returns:
            URL to unsubscribe page
        """
        params = urlencode({"t": tracking_token})
        return f"https://{self.phishing_domain}/unsubscribe?{params}"

    def _inject_tracking_pixel(self, html_content: str, tracking_pixel_url: str) -> str:
        """
        Inject tracking pixel into HTML email.

        Args:
            html_content: HTML email content
            tracking_pixel_url: URL to tracking pixel

        Returns:
            HTML with tracking pixel injected
        """
        tracking_pixel = (
            f'<img src="{tracking_pixel_url}" width="1" height="1" alt="" style="display:none;" />'
        )

        # Try to inject before closing body tag
        if "</body>" in html_content.lower():
            # Case-insensitive replace
            import re

            html_content = re.sub(
                r"(</body>)", f"{tracking_pixel}\\1", html_content, flags=re.IGNORECASE
            )
        else:
            # No body tag, append to end
            html_content += tracking_pixel

        return html_content

    def render_subject(self, subject_template: str, variables: Dict) -> str:
        """
        Render email subject line.

        Args:
            subject_template: Subject template with Jinja2 syntax
            variables: Dictionary of template variables

        Returns:
            Rendered subject line

        Raises:
            TemplateSyntaxError: If template has syntax errors
        """
        try:
            subject_jinja = Template(subject_template)
            subject = subject_jinja.render(**variables)
            # Remove newlines and extra whitespace
            subject = " ".join(subject.split())
            return subject
        except TemplateSyntaxError as e:
            logger.error(f"Subject template syntax error: {e}")
            raise

    def generate_tracking_token(
        self, campaign_id: int = None, target_id: int = None
    ) -> str:
        """
        Generate a unique tracking token.

        If campaign_id and target_id are provided, generates a deterministic
        HMAC-based token. Otherwise, generates a random token.

        Args:
            campaign_id: Campaign ID (optional)
            target_id: Target ID (optional)

        Returns:
            Tracking token (32 characters, URL-safe base64)
        """
        if campaign_id is not None and target_id is not None:
            # Deterministic HMAC-based token for campaign-target pair
            message = f"c{campaign_id}t{target_id}".encode()
            signature = hmac.new(
                TRACKING_SECRET_KEY.encode(), message, hashlib.sha256
            ).digest()
            # URL-safe base64, truncated to 32 chars
            token = base64.urlsafe_b64encode(signature).decode().rstrip("=")[:32]
            return token
        else:
            # Fallback to random token
            return secrets.token_urlsafe(24)[:32]

    def generate_tracking_number(self) -> str:
        """
        Generate a realistic-looking tracking number (for shipping templates).

        Returns:
            UPS-style tracking number
        """
        return f"1Z{secrets.token_hex(4).upper()}{secrets.randbelow(10000000000):010d}"

    def generate_delivery_date(self, days_ahead: int = None) -> str:
        """
        Generate a delivery date (for shipping templates).

        Args:
            days_ahead: Specific number of days ahead (default: random 3-5)

        Returns:
            Formatted date string
        """
        if days_ahead is None:
            days_ahead = secrets.randbelow(3) + 3
        date = datetime.now() + timedelta(days=days_ahead)
        return date.strftime("%A, %B %d, %Y")


def validate_template(template_str: str) -> Tuple[bool, str]:
    """
    Validate Jinja2 template syntax.

    Args:
        template_str: Template string to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        Template(template_str)
        return True, ""
    except TemplateSyntaxError as e:
        return False, str(e)


def get_available_variables() -> Dict[str, str]:
    """
    Get list of available template variables with descriptions.

    Returns:
        Dictionary mapping variable names to descriptions
    """
    return {
        # Core target variables
        "salutation": "Target's salutation (Mr., Ms., Dr., etc.)",
        "first_name": "Target's first name",
        "last_name": "Target's last name",
        "email": "Target's email address",
        "position": "Target's job position/title",
        "department": "Target's department name",
        # Campaign variables
        "campaign_name": "Campaign name",
        # Sender variables
        "sender_name": "Sender's display name",
        "sender_email": "Sender's email address",
        # Utility variables
        "year": "Current year (for copyright footers)",
        # Auto-generated variables (for shipping templates)
        "tracking_number": "Auto-generated package tracking number",
        "delivery_date": "Auto-generated delivery date (3-5 days ahead)",
        # Tracking variables (automatically injected)
        "tracking_pixel_url": "URL to tracking pixel (auto-injected in HTML)",
        "phishing_link": "Phishing link URL with tracking",
        "landing_page_url": "Alias for phishing_link",
        "unsubscribe_url": "Unsubscribe link URL",
    }


# Example template usage
EXAMPLE_HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{{ campaign_name }}</title>
</head>
<body>
    <p>Dear {{ first_name }},</p>

    <p>Your account requires immediate attention. Please click the link below to
    verify your information:</p>

    <p><a href="{{ phishing_link }}">Verify Account</a></p>

    <p>If you did not request this, please ignore this email.</p>

    <p>Best regards,<br>
    {{ sender_name }}<br>
    <a href="mailto:{{ sender_email }}">{{ sender_email }}</a></p>

    <hr>
    <p style="font-size: 10px; color: #999;">
        <a href="{{ unsubscribe_url }}">Unsubscribe</a>
    </p>
</body>
</html>
"""

EXAMPLE_TEXT_TEMPLATE = """
Dear {{ first_name }},

Your account requires immediate attention. Please visit the link below to verify your information:

{{ phishing_link }}

If you did not request this, please ignore this email.

Best regards,
{{ sender_name }}
{{ sender_email }}

---
Unsubscribe: {{ unsubscribe_url }}
"""

EXAMPLE_SUBJECT_TEMPLATE = "{{ campaign_name }}: Action Required for {{ first_name }}"
