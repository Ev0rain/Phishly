"""
Landing Pages Repository - Database operations for landing pages
"""

from repositories.base_repository import BaseRepository
from database import db
from db.models import LandingPage, ActiveConfiguration, Campaign
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Landing page templates directory
LANDING_PAGES_DIR = Path("/templates/landing_pages")


class LandingPagesRepository(BaseRepository):
    """Repository for landing page CRUD operations"""

    @staticmethod
    def get_all_landing_pages():
        """Return all landing pages"""
        try:
            landing_pages = (
                db.session.query(LandingPage)
                .order_by(LandingPage.created_at.desc())
                .all()
            )

            return [
                {
                    "id": lp.id,
                    "name": lp.name,
                    "url_path": lp.url_path,
                    "domain": lp.domain,
                    "template_path": lp.template_path,  # NEW: Template directory reference
                    "capture_credentials": lp.capture_credentials,
                    "capture_form_data": lp.capture_form_data,
                    "redirect_url": lp.redirect_url,
                    "created_at": lp.created_at,
                    "updated_at": lp.updated_at,
                }
                for lp in landing_pages
            ]

        except Exception as e:
            logger.error(f"Error getting all landing pages: {e}")
            return []

    @staticmethod
    def get_landing_page_by_id(landing_page_id):
        """
        Return a single landing page by ID.

        For template-based pages (template_path is set), html/css/js content is read from filesystem.
        For legacy pages (html_content is set), content is read from database.
        """
        try:
            lp = (
                db.session.query(LandingPage)
                .filter(LandingPage.id == landing_page_id)
                .first()
            )

            if not lp:
                return None

            # Base response data
            response = {
                "id": lp.id,
                "name": lp.name,
                "url_path": lp.url_path,
                "domain": lp.domain,
                "template_path": lp.template_path,
                "capture_credentials": lp.capture_credentials,
                "capture_form_data": lp.capture_form_data,
                "redirect_url": lp.redirect_url,
                "created_at": lp.created_at,
                "updated_at": lp.updated_at,
            }

            # If template_path is set, read from filesystem
            if lp.template_path:
                # Note: html/css/js content is NOT loaded here - it's served directly from filesystem
                # The template_path is used by the phishing server to serve files
                response["html_content"] = None  # Not loaded from DB
                response["css_content"] = None
                response["js_content"] = None
            else:
                # Legacy mode: read from database
                response["html_content"] = lp.html_content
                response["css_content"] = lp.css_content
                response["js_content"] = lp.js_content

            return response

        except Exception as e:
            logger.error(f"Error getting landing page {landing_page_id}: {e}")
            return None

    @staticmethod
    def create_landing_page(
        name,
        url_path,
        domain=None,
        template_path=None,
        html_content=None,
        css_content=None,
        js_content=None,
        capture_credentials=True,
        capture_form_data=True,
        redirect_url=None,
        created_by_id=None,
    ):
        """
        Create a new landing page

        Args:
            name: Landing page name
            url_path: URL path (e.g., /login)
            domain: Domain (e.g., phishing.example.com)
            template_path: Template folder name (e.g., "phish-page") - NEW
            html_content: HTML content (legacy, for DB storage)
            css_content: CSS content (legacy)
            js_content: JS content (legacy)
            capture_credentials: Whether to capture credentials
            capture_form_data: Whether to capture form data
            redirect_url: Redirect URL after submission
            created_by_id: Admin user ID

        Returns:
            tuple: (success: bool, message: str, landing_page_id: int or None)
        """
        try:
            # Ensure url_path starts with /
            if not url_path.startswith("/"):
                url_path = "/" + url_path

            # Check for duplicate url_path
            existing = (
                db.session.query(LandingPage)
                .filter(LandingPage.url_path == url_path)
                .first()
            )
            if existing:
                return False, f"URL path '{url_path}' already exists", None

            # Validate that either template_path OR html_content is provided
            if not template_path and not html_content:
                return False, "Either template_path or html_content must be provided", None

            # Validate template exists if template_path is provided
            if template_path:
                template_dir = LANDING_PAGES_DIR / template_path
                if not template_dir.exists():
                    return False, f"Template '{template_path}' not found at {template_dir}", None

            new_landing_page = LandingPage(
                name=name,
                url_path=url_path,
                domain=domain,
                template_path=template_path,  # NEW: Template reference
                html_content=html_content,  # Legacy: DB storage
                css_content=css_content,
                js_content=js_content,
                capture_credentials=capture_credentials,
                capture_form_data=capture_form_data,
                redirect_url=redirect_url,
                created_by_id=created_by_id,
                created_at=datetime.utcnow(),
            )
            db.session.add(new_landing_page)
            db.session.commit()

            return True, "Landing page created successfully", new_landing_page.id

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating landing page: {e}")
            return False, f"Error creating landing page: {str(e)}", None

    @staticmethod
    def update_landing_page(
        landing_page_id,
        name=None,
        url_path=None,
        domain=None,
        template_path=None,
        html_content=None,
        css_content=None,
        js_content=None,
        capture_credentials=None,
        capture_form_data=None,
        redirect_url=None,
    ):
        """
        Update an existing landing page

        Args:
            landing_page_id: Landing page ID
            name: Landing page name
            url_path: URL path
            domain: Domain
            template_path: Template folder name (NEW)
            html_content: HTML content (legacy)
            css_content: CSS content (legacy)
            js_content: JS content (legacy)
            capture_credentials: Whether to capture credentials
            capture_form_data: Whether to capture form data
            redirect_url: Redirect URL after submission

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            lp = (
                db.session.query(LandingPage)
                .filter(LandingPage.id == landing_page_id)
                .first()
            )

            if not lp:
                return False, "Landing page not found"

            # Check for duplicate url_path if changing it
            if url_path and url_path != lp.url_path:
                if not url_path.startswith("/"):
                    url_path = "/" + url_path
                existing = (
                    db.session.query(LandingPage)
                    .filter(LandingPage.url_path == url_path, LandingPage.id != landing_page_id)
                    .first()
                )
                if existing:
                    return False, f"URL path '{url_path}' already exists"
                lp.url_path = url_path

            # Validate template if template_path is being changed
            if template_path is not None:
                template_dir = LANDING_PAGES_DIR / template_path
                if not template_dir.exists():
                    return False, f"Template '{template_path}' not found at {template_dir}"
                lp.template_path = template_path

            if name is not None:
                lp.name = name
            if domain is not None:
                lp.domain = domain
            if html_content is not None:
                lp.html_content = html_content
            if css_content is not None:
                lp.css_content = css_content
            if js_content is not None:
                lp.js_content = js_content
            if capture_credentials is not None:
                lp.capture_credentials = capture_credentials
            if capture_form_data is not None:
                lp.capture_form_data = capture_form_data
            if redirect_url is not None:
                lp.redirect_url = redirect_url

            lp.updated_at = datetime.utcnow()
            db.session.commit()

            return True, "Landing page updated successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating landing page: {e}")
            return False, f"Error updating landing page: {str(e)}"

    @staticmethod
    def delete_landing_page(landing_page_id):
        """
        Delete a landing page

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            # Check if landing page can be deleted
            can_delete, reason = LandingPagesRepository.can_delete_landing_page(landing_page_id)

            if not can_delete:
                return False, reason

            # Proceed with deletion
            lp = db.session.query(LandingPage).filter(
                LandingPage.id == landing_page_id
            ).first()

            if not lp:
                return False, "Landing page not found"

            db.session.delete(lp)
            db.session.commit()

            return True, "Landing page deleted successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting landing page: {e}")
            return False, f"Error deleting landing page: {str(e)}"

    @staticmethod
    def list_available_templates():
        """
        List all available landing page templates in /templates/landing_pages/

        Returns:
            List of template dictionaries with keys:
            - name: Template folder name
            - path: Full path to template
            - size_mb: Total size in megabytes
            - file_count: Number of files in template
        """
        templates = []

        try:
            if not LANDING_PAGES_DIR.exists():
                logger.warning(f"Templates directory not found: {LANDING_PAGES_DIR}")
                return templates

            # Scan for subdirectories
            for item in LANDING_PAGES_DIR.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    # Calculate size and file count
                    total_size = 0
                    file_count = 0
                    for file in item.rglob('*'):
                        if file.is_file():
                            total_size += file.stat().st_size
                            file_count += 1

                    templates.append({
                        'name': item.name,
                        'path': str(item),
                        'size_mb': round(total_size / (1024 * 1024), 2),
                        'file_count': file_count
                    })

            # Sort by name
            templates.sort(key=lambda t: t['name'])

        except Exception as e:
            logger.error(f"Error listing templates: {e}", exc_info=True)

        return templates

    @staticmethod
    def get_template_entry_pages(template_path):
        """
        Get all HTML entry pages in a template.

        Args:
            template_path: Template folder name (e.g., "phish-page")

        Returns:
            List of HTML file paths relative to template root
        """
        entry_pages = []

        try:
            template_dir = LANDING_PAGES_DIR / template_path
            if not template_dir.exists():
                logger.warning(f"Template directory not found: {template_dir}")
                return entry_pages

            # Find all HTML files (both root and in subdirectories)
            for html_file in template_dir.rglob('*.html'):
                # Get path relative to template root
                rel_path = html_file.relative_to(template_dir)
                entry_pages.append(str(rel_path))

            # Sort: root-level first, then alphabetically
            entry_pages.sort(key=lambda p: (Path(p).parent != Path('.'), p))

        except Exception as e:
            logger.error(f"Error getting entry pages for template '{template_path}': {e}")

        return entry_pages

    # ============================================
    # Landing Page Activation Management
    # ============================================

    @staticmethod
    def get_active_landing_page_config():
        """
        Get the active landing page configuration (singleton record).

        Returns:
            ActiveConfiguration object or None
        """
        try:
            config = db.session.query(ActiveConfiguration).first()
            return config
        except Exception as e:
            logger.error(f"Error getting active landing page config: {e}")
            return None

    @staticmethod
    def get_active_landing_page():
        """
        Get the currently active landing page with campaign info.

        Returns:
            Dictionary with landing page and campaign info, or None
        """
        try:
            config = LandingPagesRepository.get_active_landing_page_config()

            if not config or not config.active_landing_page_id:
                return None

            # Get the landing page
            landing_page = db.session.query(LandingPage).filter(
                LandingPage.id == config.active_landing_page_id
            ).first()

            if not landing_page:
                return None

            # Get the active campaign using this landing page
            active_campaign = db.session.query(Campaign).filter(
                Campaign.landing_page_id == config.active_landing_page_id,
                Campaign.status.in_(['active', 'paused'])
            ).first()

            return {
                'config': config,
                'landing_page': landing_page,
                'campaign': active_campaign,
                'dns_zone_path': config.dns_zone_file_path,
                'phishing_domain': config.phishing_domain,
                'public_ip': config.public_ip,
                'activated_at': config.activated_at,
            }

        except Exception as e:
            logger.error(f"Error getting active landing page: {e}")
            return None

    @staticmethod
    def activate_landing_page(landing_page_id, campaign_id, user_id, dns_zone_path=None):
        """
        Activate a landing page for a campaign.

        This updates the active_configuration singleton record.

        Args:
            landing_page_id: ID of the landing page to activate
            campaign_id: ID of the campaign activating this page
            user_id: ID of the user performing the activation
            dns_zone_path: Optional path to DNS zone file

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Verify landing page exists
            landing_page = db.session.query(LandingPage).filter(
                LandingPage.id == landing_page_id
            ).first()

            if not landing_page:
                return False, "Landing page not found"

            # Get or create the singleton active_configuration record
            config = db.session.query(ActiveConfiguration).first()

            if not config:
                config = ActiveConfiguration(
                    id=1,  # Singleton ID
                    active_landing_page_id=landing_page_id,
                    activated_at=datetime.utcnow(),
                    activated_by_id=user_id,
                    dns_zone_file_path=dns_zone_path,
                    phishing_domain=landing_page.domain,
                    created_at=datetime.utcnow(),
                )
                db.session.add(config)
            else:
                # Update existing configuration
                config.active_landing_page_id = landing_page_id
                config.activated_at = datetime.utcnow()
                config.activated_by_id = user_id
                if dns_zone_path:
                    config.dns_zone_file_path = dns_zone_path
                config.phishing_domain = landing_page.domain
                config.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(
                f"Activated landing page {landing_page_id} for campaign {campaign_id} by user {user_id}"
            )
            return True, f"Landing page '{landing_page.name}' activated successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error activating landing page: {e}", exc_info=True)
            return False, f"Error activating landing page: {str(e)}"

    @staticmethod
    def deactivate_landing_page():
        """
        Deactivate the currently active landing page.

        This clears the active_landing_page_id in active_configuration.

        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            config = db.session.query(ActiveConfiguration).first()

            if not config or not config.active_landing_page_id:
                return True, "No active landing page to deactivate"

            landing_page_id = config.active_landing_page_id
            config.active_landing_page_id = None
            config.updated_at = datetime.utcnow()

            db.session.commit()

            logger.info(f"Deactivated landing page {landing_page_id}")
            return True, "Landing page deactivated successfully"

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deactivating landing page: {e}", exc_info=True)
            return False, f"Error deactivating landing page: {str(e)}"

    @staticmethod
    def can_delete_landing_page(landing_page_id):
        """
        Check if a landing page can be deleted.

        A landing page cannot be deleted if:
        - It is currently active
        - It is used by any campaigns
        - It is set as default for any email templates

        Args:
            landing_page_id: ID of the landing page

        Returns:
            Tuple of (can_delete: bool, reason: str)
        """
        try:
            # Check if it's the active landing page
            config = db.session.query(ActiveConfiguration).first()
            if config and config.active_landing_page_id == landing_page_id:
                return False, "Cannot delete: This is the currently active landing page. Deactivate it first."

            # Check if landing page exists and has relationships
            lp = db.session.query(LandingPage).filter(
                LandingPage.id == landing_page_id
            ).first()

            if not lp:
                return False, "Landing page not found"

            # Check if used by campaigns
            if lp.campaigns:
                campaign_names = [c.name for c in lp.campaigns[:3]]
                more = len(lp.campaigns) - 3
                names_str = ', '.join(campaign_names)
                if more > 0:
                    names_str += f" and {more} more"
                return False, f"Cannot delete: Used by campaigns: {names_str}"

            # Check if default for email templates
            if lp.email_templates:
                template_names = [t.name for t in lp.email_templates[:3]]
                more = len(lp.email_templates) - 3
                names_str = ', '.join(template_names)
                if more > 0:
                    names_str += f" and {more} more"
                return False, f"Cannot delete: Default for email templates: {names_str}"

            return True, "Can be deleted"

        except Exception as e:
            logger.error(f"Error checking if landing page can be deleted: {e}")
            return False, f"Error checking delete status: {str(e)}"

    @staticmethod
    def can_deactivate_landing_page():
        """
        Check if the currently active landing page can be deactivated.

        A landing page can only be deactivated if its campaign is paused or completed.

        Returns:
            Tuple of (can_deactivate: bool, reason: str, campaign_status: str or None)
        """
        try:
            config = db.session.query(ActiveConfiguration).first()

            if not config or not config.active_landing_page_id:
                return True, "No active landing page", None

            # Find active campaign using this landing page
            campaign = db.session.query(Campaign).filter(
                Campaign.landing_page_id == config.active_landing_page_id,
                Campaign.status.in_(['active', 'paused', 'scheduled'])
            ).first()

            if not campaign:
                # No active campaign - safe to deactivate
                return True, "No active campaign using this landing page", None

            if campaign.status == 'active':
                return False, f"Cannot deactivate: Campaign '{campaign.name}' is currently running", campaign.status

            if campaign.status == 'scheduled':
                return False, f"Cannot deactivate: Campaign '{campaign.name}' is scheduled to launch", campaign.status

            # Campaign is paused - can deactivate
            return True, f"Campaign '{campaign.name}' is paused - safe to deactivate", campaign.status

        except Exception as e:
            logger.error(f"Error checking if landing page can be deactivated: {e}")
            return False, f"Error checking deactivation status: {str(e)}", None
