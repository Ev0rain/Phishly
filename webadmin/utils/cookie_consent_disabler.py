"""
Cookie Consent Disabler for Phishing Landing Pages

This utility adds JavaScript to automatically accept and hide cookie consent banners
in phishing landing pages. This is necessary because third-party consent management
systems (like OneTrust) don't work properly on localhost or phishing domains.
"""

import re
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# JavaScript to auto-accept and hide cookie consent banners
CONSENT_DISABLER_SCRIPT = """
<script>
// Auto-accept cookie consent for phishing simulation
// This prevents consent banners from repeatedly appearing
(function() {
    'use strict';

    // Set consent cookies
    function setConsentCookies() {
        try {
            var expires = new Date();
            expires.setFullYear(expires.getFullYear() + 1);
            var expiresStr = expires.toUTCString();

            // OneTrust consent cookies
            var consentValue = 'isGpcEnabled=0&datestamp=' + new Date().toISOString() +
                '&version=6.33.0&isIABGlobal=false&consentId=&interactionCount=1&' +
                'landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A1%2CC0003%3A1%2CC0004%3A1&' +
                'AwaitingReconsent=false';

            document.cookie = 'OptanonConsent=' + consentValue + '; expires=' + expiresStr + '; path=/';
            document.cookie = 'OptanonAlertBoxClosed=' + new Date().toISOString() + '; expires=' + expiresStr + '; path=/';

            // Generic consent cookie
            document.cookie = 'cookie_consent=accepted; expires=' + expiresStr + '; path=/';

            console.log('[Phishly] Cookie consent auto-accepted');
        } catch(e) {
            console.error('[Phishly] Error setting consent cookies:', e);
        }
    }

    // Hide all consent banners
    function hideConsentBanners() {
        var selectors = [
            '#onetrust-banner-sdk',
            '#onetrust-consent-sdk',
            '.onetrust-pc-dark-filter',
            '[id*="cookie"]',
            '[class*="cookie-banner"]',
            '[class*="consent-banner"]'
        ];

        selectors.forEach(function(selector) {
            var elements = document.querySelectorAll(selector);
            elements.forEach(function(el) {
                el.style.display = 'none';
                el.style.visibility = 'hidden';
                el.remove();
            });
        });
    }

    // Override OneTrust functions if they exist
    function disableOneTrust() {
        if (window.OneTrust) {
            try {
                window.OneTrust.Close = function() {};
                window.OneTrust.ToggleInfoDisplay = function() {};
                console.log('[Phishly] OneTrust disabled');
            } catch(e) {}
        }

        if (window.Optanon) {
            try {
                window.Optanon.Close = function() {};
                console.log('[Phishly] Optanon disabled');
            } catch(e) {}
        }
    }

    // Run immediately
    setConsentCookies();
    hideConsentBanners();
    disableOneTrust();

    // Run after DOM loads
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setConsentCookies();
            hideConsentBanners();
            disableOneTrust();
        });
    }

    // Run periodically to catch late-loading banners
    setTimeout(function() { hideConsentBanners(); disableOneTrust(); }, 500);
    setTimeout(function() { hideConsentBanners(); disableOneTrust(); }, 1000);
    setTimeout(function() { hideConsentBanners(); disableOneTrust(); }, 2000);

    // Watch for banners being added to DOM
    if (typeof MutationObserver !== 'undefined') {
        var observer = new MutationObserver(function(mutations) {
            hideConsentBanners();
            disableOneTrust();
        });

        var observeTarget = document.body || document.documentElement;
        if (observeTarget) {
            observer.observe(observeTarget, {
                childList: true,
                subtree: true
            });
        }
    }

    console.log('[Phishly] Cookie consent disabler initialized');
})();
</script>
"""


def add_consent_disabler_to_file(file_path: Path) -> bool:
    """
    Add consent disabler script to an HTML file.

    Args:
        file_path: Path to HTML file

    Returns:
        True if successful, False otherwise
    """
    try:
        if not file_path.exists():
            logger.warning(f"File not found: {file_path}")
            return False

        content = file_path.read_text(encoding='utf-8', errors='ignore')

        # Check if script already exists
        if '[Phishly] Cookie consent' in content:
            logger.info(f"Consent disabler already present in {file_path.name}")
            return True

        # Insert after <head> tag
        if '<head>' in content:
            content = content.replace('<head>', f'<head>{CONSENT_DISABLER_SCRIPT}', 1)
            file_path.write_text(content, encoding='utf-8')
            logger.info(f"Added consent disabler to {file_path.name}")
            return True
        else:
            logger.warning(f"No <head> tag found in {file_path.name}")
            return False

    except Exception as e:
        logger.error(f"Error adding consent disabler to {file_path}: {e}")
        return False


def add_consent_disabler_to_directory(directory: Path, recursive: bool = True) -> int:
    """
    Add consent disabler to all HTML files in a directory.

    Args:
        directory: Path to directory
        recursive: Whether to process subdirectories

    Returns:
        Number of files processed
    """
    count = 0

    try:
        pattern = "**/*.html" if recursive else "*.html"
        for html_file in directory.glob(pattern):
            if add_consent_disabler_to_file(html_file):
                count += 1

        logger.info(f"Processed {count} HTML files in {directory}")
        return count

    except Exception as e:
        logger.error(f"Error processing directory {directory}: {e}")
        return count


def process_campaign_deployment(campaign_id: str) -> bool:
    """
    Add consent disabler to all HTML files in a campaign deployment.

    Args:
        campaign_id: Campaign ID (or "active" for active deployment)

    Returns:
        True if successful, False otherwise
    """
    try:
        deployment_dir = Path("/app/campaign_landing_pages") / str(campaign_id)

        if not deployment_dir.exists():
            logger.error(f"Campaign deployment not found: {deployment_dir}")
            return False

        count = add_consent_disabler_to_directory(deployment_dir, recursive=True)
        logger.info(f"Added consent disabler to {count} files in campaign {campaign_id}")
        return count > 0

    except Exception as e:
        logger.error(f"Error processing campaign {campaign_id}: {e}")
        return False


if __name__ == "__main__":
    # Process active deployment
    import sys
    campaign_id = sys.argv[1] if len(sys.argv) > 1 else "active"

    logging.basicConfig(level=logging.INFO)
    success = process_campaign_deployment(campaign_id)

    if success:
        print(f"✓ Cookie consent disabler added to campaign '{campaign_id}'")
        sys.exit(0)
    else:
        print(f"✗ Failed to add consent disabler to campaign '{campaign_id}'")
        sys.exit(1)
