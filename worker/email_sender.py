"""
SMTP email sending for Phishly phishing campaigns.

This module handles sending phishing emails via SMTP with support for
multiple SMTP providers, TLS/SSL, authentication, and error handling.
"""

import os
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from typing import Optional, Dict

logger = logging.getLogger(__name__)


class EmailSender:
    """Send emails via SMTP."""

    def __init__(
        self,
        smtp_host: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_user: Optional[str] = None,
        smtp_password: Optional[str] = None,
        smtp_use_tls: bool = True,
        smtp_use_ssl: bool = False,
    ):
        """
        Initialize SMTP email sender.

        Args:
            smtp_host: SMTP server hostname (default: from SMTP_HOST env var)
            smtp_port: SMTP server port (default: from SMTP_PORT env var or 587)
            smtp_user: SMTP username (default: from SMTP_USER env var)
            smtp_password: SMTP password (default: from SMTP_PASSWORD env var)
            smtp_use_tls: Use STARTTLS (default: True)
            smtp_use_ssl: Use SSL/TLS from start (default: False)
        """
        self.smtp_host = smtp_host or os.getenv("SMTP_HOST", "localhost")
        self.smtp_port = smtp_port or int(os.getenv("SMTP_PORT", "587" if smtp_use_tls else "25"))
        self.smtp_user = smtp_user or os.getenv("SMTP_USER", "")
        self.smtp_password = smtp_password or os.getenv("SMTP_PASSWORD", "")
        self.smtp_use_tls = smtp_use_tls
        self.smtp_use_ssl = smtp_use_ssl

        logger.info(
            f"EmailSender initialized: {self.smtp_host}:{self.smtp_port} "
            f"(TLS: {self.smtp_use_tls}, SSL: {self.smtp_use_ssl})"
        )

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Send a multipart email (HTML + text).

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body
            from_email: Sender email address
            from_name: Sender display name (optional)
            reply_to: Reply-to email address (optional)
            custom_headers: Custom email headers (optional)

        Returns:
            True if sent successfully, False otherwise

        Raises:
            SMTPException: If SMTP error occurs
        """
        try:
            # Create multipart message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = formataddr((from_name, from_email)) if from_name else from_email
            msg["To"] = to_email
            msg["Date"] = formatdate(localtime=True)

            # Add reply-to if specified
            if reply_to:
                msg["Reply-To"] = reply_to

            # Add custom headers
            if custom_headers:
                for header, value in custom_headers.items():
                    msg[header] = value

            # Attach text and HTML parts
            # Text part first (fallback for email clients that don't support HTML)
            text_part = MIMEText(text_content, "plain", "utf-8")
            html_part = MIMEText(html_content, "html", "utf-8")

            msg.attach(text_part)
            msg.attach(html_part)

            # Send email via SMTP
            self._send_via_smtp(from_email, to_email, msg.as_string())

            logger.info(f"Email sent successfully to {to_email}")
            return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP error sending to {to_email}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error sending to {to_email}: {e}")
            raise

    def _send_via_smtp(self, from_email: str, to_email: str, message: str):
        """
        Send email via SMTP server.

        Args:
            from_email: Sender email
            to_email: Recipient email
            message: Full email message as string

        Raises:
            SMTPException: If SMTP error occurs
        """
        # Choose SMTP class based on SSL setting
        if self.smtp_use_ssl:
            smtp_class = smtplib.SMTP_SSL
        else:
            smtp_class = smtplib.SMTP

        # Connect to SMTP server
        with smtp_class(self.smtp_host, self.smtp_port, timeout=30) as server:
            # Enable debug output (disable in production)
            # server.set_debuglevel(1)

            # Use STARTTLS if enabled
            if self.smtp_use_tls and not self.smtp_use_ssl:
                server.starttls()

            # Authenticate if credentials provided
            if self.smtp_user and self.smtp_password:
                server.login(self.smtp_user, self.smtp_password)
                logger.debug(f"SMTP authenticated as {self.smtp_user}")

            # Send email
            server.sendmail(from_email, to_email, message)
            logger.debug(f"SMTP sendmail completed: {from_email} -> {to_email}")

    def test_connection(self) -> bool:
        """
        Test SMTP connection and authentication.

        Returns:
            True if connection successful, False otherwise
        """
        try:
            if self.smtp_use_ssl:
                smtp_class = smtplib.SMTP_SSL
            else:
                smtp_class = smtplib.SMTP

            with smtp_class(self.smtp_host, self.smtp_port, timeout=10) as server:
                if self.smtp_use_tls and not self.smtp_use_ssl:
                    server.starttls()

                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)

                logger.info("SMTP connection test: SUCCESS")
                return True

        except smtplib.SMTPException as e:
            logger.error(f"SMTP connection test: FAILED - {e}")
            return False
        except Exception as e:
            logger.error(f"SMTP connection test: FAILED (unexpected) - {e}")
            return False


class MockEmailSender(EmailSender):
    """
    Mock email sender for testing (doesn't actually send emails).

    Logs email details instead of sending via SMTP.
    Useful for development and testing without SMTP server.
    """

    def __init__(self):
        """Initialize mock sender."""
        super().__init__(smtp_host="mock", smtp_port=0)
        logger.info("MockEmailSender initialized (emails will NOT be sent)")

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str,
        from_email: str,
        from_name: Optional[str] = None,
        reply_to: Optional[str] = None,
        custom_headers: Optional[Dict[str, str]] = None,
    ) -> bool:
        """
        Mock send email (logs instead of sending).

        Args:
            Same as EmailSender.send_email

        Returns:
            Always returns True
        """
        logger.info("=" * 80)
        logger.info("MOCK EMAIL (NOT ACTUALLY SENT)")
        logger.info("=" * 80)
        logger.info(f"From: {formataddr((from_name, from_email)) if from_name else from_email}")
        logger.info(f"To: {to_email}")
        logger.info(f"Subject: {subject}")
        if reply_to:
            logger.info(f"Reply-To: {reply_to}")
        if custom_headers:
            logger.info(f"Custom Headers: {custom_headers}")
        logger.info("-" * 80)
        logger.info("TEXT CONTENT:")
        logger.info(text_content[:500] + ("..." if len(text_content) > 500 else ""))
        logger.info("-" * 80)
        logger.info("HTML CONTENT:")
        logger.info(html_content[:500] + ("..." if len(html_content) > 500 else ""))
        logger.info("=" * 80)

        return True

    def test_connection(self) -> bool:
        """Mock connection test (always succeeds)."""
        logger.info("Mock SMTP connection test: SUCCESS (mock mode)")
        return True


def get_email_sender(mock: bool = False) -> EmailSender:
    """
    Get email sender instance.

    Args:
        mock: If True, return MockEmailSender (default: False)

    Returns:
        EmailSender or MockEmailSender instance
    """
    # Check environment variable for mock mode
    if mock or os.getenv("SMTP_MOCK", "false").lower() == "true":
        return MockEmailSender()

    # Return real SMTP sender
    return EmailSender()


# Common SMTP configurations for popular providers

SMTP_CONFIGS = {
    "gmail": {
        "smtp_host": "smtp.gmail.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
        # Note: Gmail requires app-specific password if 2FA is enabled
    },
    "outlook": {
        "smtp_host": "smtp-mail.outlook.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
    },
    "office365": {
        "smtp_host": "smtp.office365.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
    },
    "yahoo": {
        "smtp_host": "smtp.mail.yahoo.com",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
    },
    "sendgrid": {
        "smtp_host": "smtp.sendgrid.net",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
        # Use API key as password
    },
    "mailgun": {
        "smtp_host": "smtp.mailgun.org",
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
    },
    "amazon-ses": {
        "smtp_host": "email-smtp.us-east-1.amazonaws.com",  # Region-specific
        "smtp_port": 587,
        "smtp_use_tls": True,
        "smtp_use_ssl": False,
        # Use SES SMTP credentials
    },
}


def get_smtp_config(provider: str) -> Dict:
    """
    Get SMTP configuration for a provider.

    Args:
        provider: Provider name (gmail, outlook, sendgrid, etc.)

    Returns:
        Dictionary of SMTP configuration

    Raises:
        ValueError: If provider not found
    """
    if provider.lower() not in SMTP_CONFIGS:
        raise ValueError(
            f"Unknown SMTP provider: {provider}. " f"Available: {', '.join(SMTP_CONFIGS.keys())}"
        )

    return SMTP_CONFIGS[provider.lower()]
