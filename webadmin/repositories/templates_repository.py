"""
Templates Repository - Real database implementation.

All templates stored in database after import from source library.
"""

from repositories.base_repository import BaseRepository
from database import db
from db.models import EmailTemplate, LandingPage
from datetime import datetime
import os
import logging

logger = logging.getLogger(__name__)


class TemplatesRepository(BaseRepository):
    """Real database repository for email templates."""

    # Directory where source template library is located (read-only)
    # This is where we READ templates FROM for import to database
    TEMPLATES_LIBRARY_DIR = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
        "templates",
        "email_templates"
    )

    @staticmethod
    def get_all_templates():
        """Return all email templates with metadata from database."""
        try:
            templates = (
                db.session.query(EmailTemplate).order_by(EmailTemplate.created_at.desc()).all()
            )

            result = []
            for template in templates:
                # Get default landing page info if set
                landing_page_info = None
                if template.default_landing_page_id:
                    landing_page = template.default_landing_page
                    if landing_page:
                        landing_page_info = {
                            "id": landing_page.id,
                            "name": landing_page.name,
                            "url_path": landing_page.url_path,
                        }

                result.append(
                    {
                        "id": template.id,
                        "name": template.name,
                        "subject": template.subject,
                        "from_email": template.from_email,
                        "from_name": template.from_name,
                        "created_at": template.created_at,
                        "default_landing_page_id": template.default_landing_page_id,
                        "default_landing_page": landing_page_info,
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
        """Return a single template by ID."""
        try:
            template = (
                db.session.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
            )

            if not template:
                return None

            # Get default landing page info if set
            landing_page_info = None
            if template.default_landing_page_id:
                landing_page = template.default_landing_page
                if landing_page:
                    landing_page_info = {
                        "id": landing_page.id,
                        "name": landing_page.name,
                        "url_path": landing_page.url_path,
                    }

            return {
                "id": template.id,
                "name": template.name,
                "subject": template.subject,
                "from_email": template.from_email,
                "from_name": template.from_name,
                "created_at": template.created_at,
                "default_landing_page_id": template.default_landing_page_id,
                "default_landing_page": landing_page_info,
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
        """
        Read the HTML content of a template from database.

        Templates are stored in database after import from /templates library.
        """
        try:
            template = (
                db.session.query(EmailTemplate)
                .filter(EmailTemplate.id == template_id)
                .first()
            )

            if template and template.body_html:
                return template.body_html

            # Template not found in database
            logger.error(f"Template {template_id} not found in database")
            return f"<p>Error: Template {template_id} not found in database</p>"

        except Exception as e:
            logger.error(f"Error reading template {template_id}: {e}")
            return f"<p>Error reading template: {str(e)}</p>"

    @staticmethod
    def save_template(
        name,
        subject,
        from_email,
        from_name,
        html_content,
        created_by_id=None,
        default_landing_page_id=None,
    ):
        """
        Save a new template to database.

        HTML content from /templates library is imported and stored in database.

        Args:
            name: Template name
            subject: Email subject line
            from_email: Sender email address
            from_name: Sender display name
            html_content: HTML content of email
            created_by_id: ID of admin user creating the template (optional)
            default_landing_page_id: ID of default landing page (optional)

        Returns:
            tuple: (success: bool, message: str, template_id: int or None)
        """
        try:
            # Create database record with HTML content
            new_template = EmailTemplate(
                name=name,
                subject=subject,
                from_email=from_email,
                from_name=from_name,
                body_html=html_content,
                created_by_id=created_by_id,
                default_landing_page_id=default_landing_page_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(new_template)
            db.session.commit()

            logger.info(
                f"Saved email template {new_template.id}: {name}"
            )
            return True, "Template saved successfully", new_template.id

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error saving template: {e}")
            return False, f"Error saving template: {str(e)}", None

    @staticmethod
    def get_all_landing_pages():
        """Return all landing pages for template selection dropdown."""
        try:
            landing_pages = db.session.query(LandingPage).order_by(LandingPage.name.asc()).all()

            return [
                {
                    "id": lp.id,
                    "name": lp.name,
                    "url_path": lp.url_path,
                }
                for lp in landing_pages
            ]

        except Exception as e:
            logger.error(f"Error getting landing pages: {e}")
            return []

    @staticmethod
    def get_available_tags():
        """Return list of common tags for templates."""
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

    @staticmethod
    def delete_template(template_id):
        """
        Delete a template from database.

        Args:
            template_id: ID of the template to delete

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            template = (
                db.session.query(EmailTemplate)
                .filter(EmailTemplate.id == template_id)
                .first()
            )

            if not template:
                return False, "Template not found"

            template_name = template.name

            # Delete from database
            db.session.delete(template)
            db.session.commit()

            logger.info(f"Deleted email template {template_id}: {template_name}")
            return True, "Template deleted successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting template: {e}")
            return False, f"Error deleting template: {str(e)}"

    @staticmethod
    def update_template(
        template_id,
        name,
        subject,
        from_email=None,
        from_name=None,
        default_landing_page_id=None,
    ):
        """
        Update an existing email template's metadata.

        Args:
            template_id: ID of template to update
            name: New template name
            subject: New email subject
            from_email: New sender email (optional)
            from_name: New sender name (optional)
            default_landing_page_id: New default landing page (optional)

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            template = (
                db.session.query(EmailTemplate).filter(EmailTemplate.id == template_id).first()
            )

            if not template:
                return False, "Template not found"

            # Update fields
            template.name = name
            template.subject = subject

            if from_email is not None:
                template.from_email = from_email
            if from_name is not None:
                template.from_name = from_name
            if default_landing_page_id is not None:
                template.default_landing_page_id = default_landing_page_id

            template.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Updated email template {template_id}: {name}")
            return True, f"Template '{name}' updated successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating template {template_id}: {e}", exc_info=True)
            return False, f"Error updating template: {str(e)}"

    @staticmethod
    def list_available_template_files():
        """
        List all available email template .html files.

        Returns:
            List of template file dictionaries with keys:
            - filename: Template filename (e.g., "01_urgent_password_reset.html")
            - name: Display name (filename without extension and prefix)
            - path: Full path to template file
            - size_kb: File size in kilobytes
        """
        templates = []

        try:
            templates_dir = TemplatesRepository.TEMPLATES_LIBRARY_DIR

            if not os.path.exists(templates_dir):
                logger.warning(f"Templates directory not found: {templates_dir}")
                return templates

            # Scan for .html files
            for filename in os.listdir(templates_dir):
                if filename.endswith(".html") and not filename.endswith(".j2"):
                    filepath = os.path.join(templates_dir, filename)

                    # Get file size
                    size_bytes = os.path.getsize(filepath)
                    size_kb = round(size_bytes / 1024, 2)

                    # Create display name (remove number prefix and .html extension)
                    # e.g., "01_urgent_password_reset.html" -> "Urgent Password Reset"
                    display_name = filename.replace(".html", "")
                    # Remove number prefix if present (e.g., "01_")
                    if "_" in display_name and display_name.split("_")[0].isdigit():
                        display_name = "_".join(display_name.split("_")[1:])
                    # Replace underscores with spaces and title case
                    display_name = display_name.replace("_", " ").title()

                    templates.append(
                        {
                            "filename": filename,
                            "name": display_name,
                            "path": filepath,
                            "size_kb": size_kb,
                        }
                    )

            # Sort by filename
            templates.sort(key=lambda t: t["filename"])

        except Exception as e:
            logger.error(f"Error listing template files: {e}", exc_info=True)

        return templates

    @staticmethod
    def get_template_file_content(filename):
        """
        Read the content of a template file from the source library.

        Args:
            filename: Template filename (e.g., "01_urgent_password_reset.html")

        Returns:
            tuple: (success: bool, content: str or error message)
        """
        try:
            filepath = os.path.join(TemplatesRepository.TEMPLATES_LIBRARY_DIR, filename)

            if not os.path.exists(filepath):
                return False, f"Template file not found: {filename}"

            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            return True, content

        except Exception as e:
            logger.error(f"Error reading template file {filename}: {e}")
            return False, f"Error reading template file: {str(e)}"
