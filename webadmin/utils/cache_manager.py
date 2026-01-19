"""
Landing Page Cache Manager for Phishly.

This module handles caching landing page HTML to the shared filesystem
for fast serving by the phishing server.
"""

import logging
import os
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Cache directory (shared volume between webadmin and phishing-server)
CACHE_DIR = Path(os.getenv("LANDING_PAGE_CACHE_DIR", "/app/shared_cache"))


def cache_landing_page(
    campaign_id: int,
    landing_page,
) -> Optional[Path]:
    """
    Cache landing page HTML to filesystem for phishing server.

    Creates the following structure:
    cache/{campaign_id}/{url_path}/
        ├── index.html
        ├── style.css (optional)
        └── script.js (optional)

    Args:
        campaign_id: Campaign ID
        landing_page: LandingPage model instance

    Returns:
        Path to cached directory, or None if caching failed
    """
    if not landing_page or not landing_page.html_content:
        logger.warning(f"Cannot cache landing page for campaign {campaign_id}: no content")
        return None

    try:
        # Normalize URL path
        url_path = (landing_page.url_path or "default").strip("/")

        # Create cache directory
        cache_dir = CACHE_DIR / str(campaign_id) / url_path
        cache_dir.mkdir(parents=True, exist_ok=True)

        # Write HTML file
        html_file = cache_dir / "index.html"
        html_file.write_text(landing_page.html_content, encoding="utf-8")
        logger.info(f"Cached landing page HTML: {html_file}")

        # Write CSS file if exists
        if landing_page.css_content:
            css_file = cache_dir / "style.css"
            css_file.write_text(landing_page.css_content, encoding="utf-8")
            logger.info(f"Cached landing page CSS: {css_file}")

        # Write JS file if exists
        if landing_page.js_content:
            js_file = cache_dir / "script.js"
            js_file.write_text(landing_page.js_content, encoding="utf-8")
            logger.info(f"Cached landing page JS: {js_file}")

        logger.info(
            f"Successfully cached landing page for campaign {campaign_id} "
            f"at {cache_dir}"
        )
        return cache_dir

    except Exception as e:
        logger.error(f"Error caching landing page for campaign {campaign_id}: {e}")
        return None


def clear_campaign_cache(campaign_id: int) -> bool:
    """
    Clear all cached landing pages for a campaign.

    Args:
        campaign_id: Campaign ID

    Returns:
        True if successful, False otherwise
    """
    try:
        campaign_cache_dir = CACHE_DIR / str(campaign_id)

        if campaign_cache_dir.exists():
            import shutil

            shutil.rmtree(campaign_cache_dir)
            logger.info(f"Cleared cache for campaign {campaign_id}")

        return True

    except Exception as e:
        logger.error(f"Error clearing cache for campaign {campaign_id}: {e}")
        return False


def get_cache_info(campaign_id: int) -> dict:
    """
    Get information about cached landing pages for a campaign.

    Args:
        campaign_id: Campaign ID

    Returns:
        Dictionary with cache information
    """
    campaign_cache_dir = CACHE_DIR / str(campaign_id)

    if not campaign_cache_dir.exists():
        return {"cached": False, "pages": []}

    pages = []
    for page_dir in campaign_cache_dir.iterdir():
        if page_dir.is_dir():
            index_file = page_dir / "index.html"
            pages.append({
                "url_path": page_dir.name,
                "has_html": index_file.exists(),
                "has_css": (page_dir / "style.css").exists(),
                "has_js": (page_dir / "script.js").exists(),
                "size_bytes": index_file.stat().st_size if index_file.exists() else 0,
            })

    return {
        "cached": True,
        "campaign_id": campaign_id,
        "cache_dir": str(campaign_cache_dir),
        "pages": pages,
    }


def generate_task_id(campaign_id: int, target_id: int) -> str:
    """
    Generate a campaign-specific Celery task ID.

    Format: phishly-c{campaign_id}-t{target_id}-{timestamp}-{random}

    Args:
        campaign_id: Campaign ID
        target_id: Target ID

    Returns:
        Unique task ID string
    """
    import time
    import secrets

    timestamp = int(time.time())
    random_suffix = secrets.token_hex(4)
    return f"phishly-c{campaign_id}-t{target_id}-{timestamp}-{random_suffix}"
