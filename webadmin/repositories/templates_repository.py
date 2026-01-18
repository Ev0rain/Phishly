"""
Templates Repository - Real database implementation with hybrid storage

Metadata stored in database, HTML files stored on disk
"""

from repositories.base_repository import BaseRepository
from database import db
from db.models import EmailTemplate
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class TemplatesRepository(BaseRepository):
    """Real database repository for email templates with hybrid storage"""

    # Directory where template HTML files are stored
    TEMPLATES_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Templates", "email_templates"
    )

    @staticmethod
    def get_all_templates():
        """Return all email templates with metadata from database"""
        try:
            templates = (
                db.session.query(EmailTemplate).order_by(EmailTemplate.created_at.desc()).all()
            )

            result = []
            for template in templates:
                result.append(
                    {
                        "id": template.id,
                        "name": template.name,
                        "subject": template.subject,
                        "from_email": template.from_email,
                        "from_name": template.from_name,
                        "created_at": template.created_at,
                        # For compatibility with existing UI
                        "filename": f"{template.id}.html",
                        "tags": [],  # TODO: Add tags support if needed
                        "last_used": None,  # TODO: Track usage
                        "times_used": 0,  # TODO: Track usage
                    }
                )

            return result

        except Exception as e:
            logger.error(f"Error getting all templates: {e}")
            return []

    @staticmethod
    def get_template_by_id(template_id):
        """Return a single template by ID"""
        try:
            template = (
                db.session.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
            )

            if not template:
                return None

            return {
                "id": template.id,
                "name": template.name,
                "subject": template.subject,
                "from_email": template.from_email,
                "from_name": template.from_name,
                "created_at": template.created_at,
                "filename": f"{template.id}.html",
                "tags": [],
                "last_used": None,
                "times_used": 0,
            }

        except Exception as e:
            logger.error(f"Error getting template by id {template_id}: {e}")
            return None

    @staticmethod
    def get_template_html(template_id):
        """Read the HTML content of a template file from disk"""
        # Build file path based on template ID
        filename = f"{template_id}.html"
        filepath = os.path.join(TemplatesRepository.TEMPLATES_DIR, filename)

        # If file doesn't exist, return a mock HTML template
        if not os.path.exists(filepath):
            logger.warning(f"Template file not found: {filepath}")
            return TemplatesRepository._get_mock_html()

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading template file: {e}")
            return f"<p>Error reading template: {str(e)}</p>"

    @staticmethod
    def _get_mock_html():
        """Return mock HTML content for templates"""
        # Generic phishing email template
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Email Template</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
            border-radius: 8px 8px 0 0;
        }
        .content {
            background: white;
            padding: 30px;
            border: 1px solid #e5e7eb;
            border-top: none;
        }
        .btn {
            display: inline-block;
            background: #2563eb;
            color: white;
            padding: 12px 24px;
            text-decoration: none;
            border-radius: 6px;
            margin-top: 20px;
        }
        .footer {
            background: #f9fafb;
            padding: 20px;
            text-align: center;
            font-size: 12px;
            color: #6b7280;
            border: 1px solid #e5e7eb;
            border-top: none;
            border-radius: 0 0 8px 8px;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>Important Notice</h1>
    </div>
    <div class="content">
        <p>Dear Employee,</p>

        <p>We need your immediate attention regarding an important matter that
        requires your verification.</p>

        <p>Please click the button below to complete the required action within
        the next 24 hours to avoid any disruption to your account.</p>

        <a href="{{tracking_link}}" class="btn">Verify Now</a>

        <p>If you have any questions, please contact our support team.</p>

        <p>Best regards,<br>IT Security Team</p>
    </div>
    <div class="footer">
        <p>This is an automated message. Please do not reply to this email.</p>
        <p>&copy; 2024 Company Name. All rights reserved.</p>
    </div>
</body>
</html>
"""

    @staticmethod
    def save_template(name, subject, from_email, from_name, html_content, created_by_id=None):
        """
        Save a new template (metadata to DB, HTML to disk)

        Args:
            name: Template name
            subject: Email subject line
            from_email: Sender email address
            from_name: Sender display name
            html_content: HTML content of email
            created_by_id: ID of admin user creating the template (optional)

        Returns:
            tuple: (success: bool, message: str, template_id: int or None)
        """
        try:
            # Create database record
            new_template = EmailTemplate(
                name=name,
                subject=subject,
                from_email=from_email,
                from_name=from_name,
                body_html="",  # Empty placeholder, actual HTML stored in file
                created_by_id=created_by_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(new_template)
            db.session.flush()  # Get ID without committing

            # Ensure templates directory exists
            os.makedirs(TemplatesRepository.TEMPLATES_DIR, exist_ok=True)

            # Save HTML file using template ID
            filename = f"{new_template.id}.html"
            filepath = os.path.join(TemplatesRepository.TEMPLATES_DIR, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)

            # Commit database transaction
            db.session.commit()

            return True, "Template saved successfully", new_template.id

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving template: {e}")
            return False, f"Error saving template: {str(e)}", None

    @staticmethod
    def get_available_tags():
        """Return list of common tags for templates"""
        return [
            "executive",
            "urgent",
            "financial",
            "finance",
            "billing",
            "it-security",
            "credentials",
            "hr",
            "survey",
            "meeting",
            "support",
            "alert",
            "policy",
            "delivery",
            "package",
            "social",
            "linkedin",
            "microsoft",
            "google",
        ]
