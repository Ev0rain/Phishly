"""
Campaign Deployment Utilities

Handles copying landing page templates from the template library to campaign-specific
directories for isolated deployment.
"""
import shutil
from pathlib import Path
from typing import Tuple
import logging

logger = logging.getLogger(__name__)

# Template library base directory
TEMPLATES_BASE_DIR = Path("/templates/landing_pages")

# Campaign deployments base directory
CAMPAIGN_DEPLOYMENTS_DIR = Path("/app/campaign_landing_pages")


def deploy_landing_page_to_campaign(campaign_id: int, template_path: str) -> Tuple[bool, str, str]:
    """
    Copy entire landing page template to campaign-specific directory.

    This creates an isolated copy of the template for the campaign, ensuring that:
    - Changes to the template library don't affect running campaigns
    - Each campaign has its own resources
    - Cleanup is simple when the campaign ends

    Args:
        campaign_id: Campaign ID
        template_path: Template folder name (e.g., "phish-page", "info_page")

    Returns:
        Tuple of (success: bool, message: str, deployed_path: str)

    Example:
        >>> success, msg, path = deploy_landing_page_to_campaign(1, "phish-page")
        >>> if success:
        ...     print(f"Deployed to: {path}")
    """
    try:
        # Validate source template exists
        source = TEMPLATES_BASE_DIR / template_path
        if not source.exists():
            msg = f"Template '{template_path}' not found at {source}"
            logger.error(msg)
            return False, msg, ""

        if not source.is_dir():
            msg = f"Template path '{template_path}' is not a directory"
            logger.error(msg)
            return False, msg, ""

        # Prepare destination directory
        dest = CAMPAIGN_DEPLOYMENTS_DIR / str(campaign_id)

        # Remove existing deployment if any
        if dest.exists():
            logger.info(f"Removing existing deployment for campaign {campaign_id}")
            shutil.rmtree(dest)

        # Ensure parent directory exists
        CAMPAIGN_DEPLOYMENTS_DIR.mkdir(parents=True, exist_ok=True)

        # Copy entire template folder to campaign directory
        logger.info(f"Deploying template '{template_path}' to campaign {campaign_id}")
        shutil.copytree(source, dest)

        # Add cookie consent disabler to all HTML files
        try:
            from utils.cookie_consent_disabler import process_campaign_deployment
            process_campaign_deployment(str(campaign_id))
            logger.info(f"Added cookie consent disabler to campaign {campaign_id}")
        except Exception as e:
            logger.warning(f"Failed to add cookie consent disabler: {e}")

        # Deploy info_page as awareness redirect for phish pages
        if template_path == "ups_phish_page_full":
            from utils.info_page_processor import deploy_info_page

            info_page_source = TEMPLATES_BASE_DIR / "info_page"
            if info_page_source.exists():
                logger.info(f"Deploying info_page to /awareness for campaign {campaign_id}")

                success, info_msg = deploy_info_page(
                    source_dir=info_page_source,
                    deployment_dir=dest,
                    base_url="/awareness"
                )

                if success:
                    logger.info(f"Info page deployed: {info_msg}")
                else:
                    logger.warning(f"Failed to deploy info_page: {info_msg}")
                    # Don't fail the whole deployment, just log the warning

        msg = f"Successfully deployed template '{template_path}' to campaign {campaign_id}"
        logger.info(msg)
        return True, msg, str(dest)

    except PermissionError as e:
        msg = f"Permission denied while deploying template: {e}"
        logger.error(msg)
        return False, msg, ""
    except Exception as e:
        msg = f"Error deploying template: {e}"
        logger.error(msg, exc_info=True)
        return False, msg, ""


def cleanup_campaign_deployment(campaign_id: int) -> Tuple[bool, str]:
    """
    Remove campaign deployment when campaign ends or is deleted.

    This cleans up the campaign-specific copy of the landing page template,
    freeing disk space.

    Args:
        campaign_id: Campaign ID

    Returns:
        Tuple of (success: bool, message: str)

    Example:
        >>> success, msg = cleanup_campaign_deployment(1)
        >>> print(msg)
        'Successfully cleaned up deployment for campaign 1'
    """
    try:
        dest = CAMPAIGN_DEPLOYMENTS_DIR / str(campaign_id)

        if not dest.exists():
            msg = f"No deployment found for campaign {campaign_id}"
            logger.info(msg)
            return True, msg  # Not an error - already cleaned up

        # Remove the entire deployment directory
        logger.info(f"Cleaning up deployment for campaign {campaign_id}")
        shutil.rmtree(dest)

        msg = f"Successfully cleaned up deployment for campaign {campaign_id}"
        logger.info(msg)
        return True, msg

    except PermissionError as e:
        msg = f"Permission denied while cleaning up deployment: {e}"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Error cleaning up deployment: {e}"
        logger.error(msg, exc_info=True)
        return False, msg


def list_available_templates() -> list:
    """
    List all available landing page templates in the template library.

    Scans /templates/landing_pages/ for subdirectories and returns their metadata.

    Returns:
        List of template dictionaries with keys:
        - name: Template folder name
        - path: Full path to template
        - size_mb: Total size in megabytes
        - file_count: Number of files in template

    Example:
        >>> templates = list_available_templates()
        >>> for t in templates:
        ...     print(f"{t['name']}: {t['size_mb']} MB, {t['file_count']} files")
    """
    templates = []

    try:
        if not TEMPLATES_BASE_DIR.exists():
            logger.warning(f"Templates directory not found: {TEMPLATES_BASE_DIR}")
            return templates

        # Scan for subdirectories
        for item in TEMPLATES_BASE_DIR.iterdir():
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


def get_template_entry_pages(template_path: str) -> list:
    """
    Get all HTML entry pages in a template.

    Scans the template directory for HTML files that can serve as entry points.

    Args:
        template_path: Template folder name (e.g., "phish-page")

    Returns:
        List of HTML file paths relative to template root

    Example:
        >>> pages = get_template_entry_pages("phish-page")
        >>> print(pages)
        ['index.html', 'login.html', 'login-alt.html']
    """
    entry_pages = []

    try:
        template_dir = TEMPLATES_BASE_DIR / template_path
        if not template_dir.exists():
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


def get_deployed_campaign_path(campaign_id: int) -> Path:
    """
    Get the deployed path for a campaign.

    Args:
        campaign_id: Campaign ID

    Returns:
        Path object for the campaign deployment directory
    """
    return CAMPAIGN_DEPLOYMENTS_DIR / str(campaign_id)


def is_campaign_deployed(campaign_id: int) -> bool:
    """
    Check if a campaign has been deployed.

    Args:
        campaign_id: Campaign ID

    Returns:
        True if the campaign deployment directory exists, False otherwise
    """
    return get_deployed_campaign_path(campaign_id).exists()


def deploy_preview(template_path: str) -> Tuple[bool, str, str]:
    """
    Deploy landing page template to a preview directory for testing.

    The preview is deployed to campaign_landing_pages/preview/ and includes
    both the main template and info_page if deploying phish_page.

    Args:
        template_path: Template folder name (e.g., "phish_page")

    Returns:
        Tuple of (success: bool, message: str, preview_url: str)
    """
    try:
        # Validate source template exists
        source = TEMPLATES_BASE_DIR / template_path
        if not source.exists():
            msg = f"Template '{template_path}' not found at {source}"
            logger.error(msg)
            return False, msg, ""

        if not source.is_dir():
            msg = f"Template path '{template_path}' is not a directory"
            logger.error(msg)
            return False, msg, ""

        # Use "preview" as the campaign ID
        preview_dir = CAMPAIGN_DEPLOYMENTS_DIR / "preview"

        # Remove existing preview if any
        if preview_dir.exists():
            logger.info("Removing existing preview deployment")
            shutil.rmtree(preview_dir)

        # Ensure parent directory exists
        CAMPAIGN_DEPLOYMENTS_DIR.mkdir(parents=True, exist_ok=True)

        # Copy entire template folder to preview directory
        logger.info(f"Deploying preview for template '{template_path}'")
        shutil.copytree(source, preview_dir)

        # Add cookie consent disabler to all HTML files
        try:
            from utils.cookie_consent_disabler import process_campaign_deployment
            process_campaign_deployment("preview")
            logger.info("Added cookie consent disabler to preview")
        except Exception as e:
            logger.warning(f"Failed to add cookie consent disabler: {e}")

        # Deploy info_page as awareness redirect for phish pages (preview)
        if template_path == "ups_phish_page_full":
            from utils.info_page_processor import deploy_info_page

            info_page_source = TEMPLATES_BASE_DIR / "info_page"
            if info_page_source.exists():
                logger.info(f"Deploying info_page to /preview/awareness")

                success, info_msg = deploy_info_page(
                    source_dir=info_page_source,
                    deployment_dir=preview_dir,
                    base_url="/preview/awareness"
                )

                if success:
                    logger.info(f"Info page deployed to preview: {info_msg}")
                else:
                    logger.warning(f"Failed to deploy info_page to preview: {info_msg}")
                    # Don't fail the whole preview deployment

        # Create a special marker file so the phishing server knows this is preview mode
        marker_file = preview_dir / ".preview_mode"
        marker_file.write_text(template_path)

        preview_url = "/preview/"  # Relative URL, phishing server will handle it
        msg = f"Preview deployed successfully for template '{template_path}'"
        logger.info(msg)
        return True, msg, preview_url

    except PermissionError as e:
        msg = f"Permission denied while deploying preview: {e}"
        logger.error(msg)
        return False, msg, ""
    except Exception as e:
        msg = f"Error deploying preview: {e}"
        logger.error(msg, exc_info=True)
        return False, msg, ""


def cleanup_preview() -> Tuple[bool, str]:
    """
    Remove preview deployment.

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        preview_dir = CAMPAIGN_DEPLOYMENTS_DIR / "preview"

        if not preview_dir.exists():
            msg = "No preview deployment found"
            logger.info(msg)
            return True, msg

        # Remove the preview directory
        logger.info("Cleaning up preview deployment")
        shutil.rmtree(preview_dir)

        msg = "Preview deployment cleaned up successfully"
        logger.info(msg)
        return True, msg

    except PermissionError as e:
        msg = f"Permission denied while cleaning up preview: {e}"
        logger.error(msg)
        return False, msg
    except Exception as e:
        msg = f"Error cleaning up preview: {e}"
        logger.error(msg, exc_info=True)
        return False, msg


def is_preview_deployed() -> bool:
    """
    Check if a preview deployment exists.

    Returns:
        True if preview directory exists, False otherwise
    """
    preview_dir = CAMPAIGN_DEPLOYMENTS_DIR / "preview"
    return preview_dir.exists()
