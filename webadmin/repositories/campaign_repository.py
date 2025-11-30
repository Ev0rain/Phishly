"""
Mock repository for campaign data
This returns hardcoded data until the database is ready
"""

from datetime import datetime, timedelta


class MockCampaignRepository:
    """Mock data access layer for campaigns"""

    @staticmethod
    def get_dashboard_stats():
        """Return dashboard statistics"""
        return {
            "total_campaigns": 12,
            "active_campaigns": 3,
            "total_targets": 487,
            "emails_sent": 1842,
            "emails_opened": 734,
            "links_clicked": 156,
            "credentials_submitted": 42,
            "open_rate": 39.8,
            "click_rate": 8.5,
            "submission_rate": 2.3,
        }

    @staticmethod
    def get_recent_campaigns():
        """Return list of recent campaigns"""
        return [
            {
                "id": 1,
                "name": "Q4 Security Awareness Test",
                "status": "active",
                "created_at": datetime.now() - timedelta(days=2),
                "targets": 150,
                "opened": 67,
                "clicked": 14,
            },
            {
                "id": 2,
                "name": "Finance Department Phishing",
                "status": "active",
                "created_at": datetime.now() - timedelta(days=5),
                "targets": 42,
                "opened": 28,
                "clicked": 8,
            },
            {
                "id": 3,
                "name": "IT Security Training Campaign",
                "status": "completed",
                "created_at": datetime.now() - timedelta(days=14),
                "targets": 85,
                "opened": 71,
                "clicked": 12,
            },
        ]
