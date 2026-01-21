"""
Active Configuration Repository - Manages active landing page state
"""

from repositories.base_repository import BaseRepository
from database import db
from db.models import ActiveConfiguration, LandingPage, Campaign
import logging
from datetime import datetime
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class ActiveConfigurationRepository(BaseRepository):
    """Repository for active landing page configuration"""

    @staticmethod
    def get_active_configuration():
        """Get the singleton active configuration"""
        try:
            config = db.session.query(ActiveConfiguration).get(1)
            if not config:
                # Create if doesn't exist
                config = ActiveConfiguration(id=1)
                db.session.add(config)
                db.session.commit()
            return config
        except Exception as e:
            logger.error(f"Error getting active configuration: {e}")
            return None

    @staticmethod
    def get_active_landing_page():
        """Get the currently active landing page"""
        config = ActiveConfigurationRepository.get_active_configuration()
        if config and config.active_landing_page_id:
            return db.session.query(LandingPage).get(config.active_landing_page_id)
        return None

    @staticmethod
    def get_active_landing_page_id():
        """Get just the ID of the active landing page"""
        config = ActiveConfigurationRepository.get_active_configuration()
        return config.active_landing_page_id if config else None

    @staticmethod
    def has_running_campaigns():
        """Check if any campaigns are currently running"""
        count = db.session.query(Campaign).filter(
            Campaign.status == 'active'
        ).count()
        return count > 0

    @staticmethod
    def get_running_campaigns_count():
        """Get count of running campaigns"""
        return db.session.query(Campaign).filter(
            Campaign.status == 'active'
        ).count()

    @staticmethod
    def activate_landing_page(landing_page_id, user_id=None,
                               phishing_domain=None, public_ip=None):
        """
        Activate a landing page.

        Returns:
            tuple: (success: bool, message: str, dns_zone_path: str or None)
        """
        try:
            config = ActiveConfigurationRepository.get_active_configuration()
            landing_page = db.session.query(LandingPage).get(landing_page_id)

            if not landing_page:
                return False, "Landing page not found", None

            # Check if this is actually a change
            is_new_activation = config.active_landing_page_id != landing_page_id

            # Update configuration
            config.active_landing_page_id = landing_page_id
            config.activated_at = datetime.utcnow()
            config.activated_by_id = user_id

            if phishing_domain:
                config.phishing_domain = phishing_domain
            if public_ip:
                config.public_ip = public_ip

            # Generate DNS zone file if this is a new activation
            dns_zone_path = None
            if is_new_activation:
                dns_zone_path = ActiveConfigurationRepository._generate_dns_zone_file(
                    config, landing_page
                )
                config.dns_zone_file_path = dns_zone_path

            db.session.commit()

            message = f"Landing page '{landing_page.name}' activated successfully"
            if is_new_activation and dns_zone_path:
                message += f". DNS zone file generated at {dns_zone_path}"

            return True, message, dns_zone_path

        except Exception as e:
            db.session.rollback()
            logger.error(f"Error activating landing page: {e}")
            return False, f"Error: {str(e)}", None

    @staticmethod
    def _generate_dns_zone_file(config, landing_page):
        """Generate DNS zone entry file"""
        zone_dir = Path("/app/dns_zones")
        zone_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        filename = f"dns-zone-entry_{timestamp}.txt"
        filepath = zone_dir / filename

        # Use landing page domain if specified, otherwise fall back to global config
        domain = landing_page.domain or config.phishing_domain or os.getenv("PHISHING_DOMAIN", "phishing.example.com")
        ip = config.public_ip or "YOUR_SERVER_IP"

        # If domain includes protocol or path, extract just the domain
        if "://" in domain:
            # Full URL provided, extract domain
            domain = domain.split("://")[1].split("/")[0]
        elif "/" in domain:
            # Domain with path, extract just domain
            domain = domain.split("/")[0]

        zone_content = f"""; Phishly DNS Zone Entry
; Generated: {datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")}
; Landing Page: {landing_page.name}
; URL Path: {landing_page.url_path}
; Domain: {domain}

; ==============================================
; ADD THE FOLLOWING TO YOUR DNS ZONE FILE
; ==============================================

; A Record - Point phishing domain to your server IP
{domain}.    IN    A    {ip}

; If using a subdomain, you may also need:
; *.{domain}.    IN    A    {ip}

; ==============================================
; NOTES
; ==============================================
; 1. Replace {ip} with your actual server IP if not set
; 2. TTL is typically 300-3600 seconds
; 3. Ensure SSL certificates are configured for HTTPS
"""

        filepath.write_text(zone_content)
        logger.info(f"Generated DNS zone file: {filepath}")

        return str(filepath)

    @staticmethod
    def update_phishing_domain(domain, public_ip=None):
        """Update the phishing domain configuration"""
        try:
            config = ActiveConfigurationRepository.get_active_configuration()
            config.phishing_domain = domain
            if public_ip:
                config.public_ip = public_ip
            db.session.commit()
            return True, "Domain configuration updated"
        except Exception as e:
            db.session.rollback()
            return False, f"Error: {str(e)}"

    @staticmethod
    def deactivate_landing_page():
        """
        Deactivate the currently active landing page.

        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            config = ActiveConfigurationRepository.get_active_configuration()

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
    def can_deactivate_landing_page():
        """
        Check if the currently active landing page can be deactivated.

        A landing page can only be deactivated if its campaign is paused or completed.

        Returns:
            tuple: (can_deactivate: bool, reason: str, campaign_status: str or None)
        """
        try:
            config = ActiveConfigurationRepository.get_active_configuration()

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

    @staticmethod
    def get_active_with_campaign():
        """
        Get the currently active landing page with campaign info.

        Returns:
            Dictionary with landing page and campaign info, or None
        """
        try:
            config = ActiveConfigurationRepository.get_active_configuration()

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
            logger.error(f"Error getting active landing page with campaign: {e}")
            return None
