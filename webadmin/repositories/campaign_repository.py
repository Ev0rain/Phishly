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

    @staticmethod
    def get_all_campaigns():
        """Return all campaigns with full details"""
        return [
            {
                "id": 1,
                "name": "Q4 Security Awareness Test",
                "template_name": "CEO Email Compromise",
                "group_name": "All Employees",
                "emails_sent": 150,
                "status": "active",
                "created_at": datetime.now() - timedelta(days=2),
                "opened": 67,
                "clicked": 14,
            },
            {
                "id": 2,
                "name": "Finance Department Phishing",
                "template_name": "Invoice Request",
                "group_name": "Finance Team",
                "emails_sent": 42,
                "status": "active",
                "created_at": datetime.now() - timedelta(days=5),
                "opened": 28,
                "clicked": 8,
            },
            {
                "id": 3,
                "name": "IT Security Training Campaign",
                "template_name": "Password Reset Request",
                "group_name": "IT Department",
                "emails_sent": 85,
                "status": "completed",
                "created_at": datetime.now() - timedelta(days=14),
                "opened": 71,
                "clicked": 12,
            },
            {
                "id": 4,
                "name": "HR Benefits Survey",
                "template_name": "Survey Invitation",
                "group_name": "All Employees",
                "emails_sent": 320,
                "status": "completed",
                "created_at": datetime.now() - timedelta(days=21),
                "opened": 256,
                "clicked": 89,
            },
            {
                "id": 5,
                "name": "Executive Team Test",
                "template_name": "Urgent Meeting Request",
                "group_name": "Executives",
                "emails_sent": 12,
                "status": "scheduled",
                "created_at": datetime.now() - timedelta(days=1),
                "opened": 0,
                "clicked": 0,
            },
            {
                "id": 6,
                "name": "Sales Team Awareness",
                "template_name": "Client Complaint",
                "group_name": "Sales Department",
                "emails_sent": 67,
                "status": "active",
                "created_at": datetime.now() - timedelta(days=7),
                "opened": 45,
                "clicked": 18,
            },
        ]

    @staticmethod
    def get_email_templates():
        """Return available email templates"""
        return [
            {
                "id": 1,
                "name": "CEO Email Compromise",
                "subject": "Urgent: Wire Transfer Required",
            },
            {"id": 2, "name": "Invoice Request", "subject": "RE: Invoice #2024-1847"},
            {
                "id": 3,
                "name": "Password Reset Request",
                "subject": "Reset Your Password",
            },
            {"id": 4, "name": "Survey Invitation", "subject": "Your Feedback Matters"},
            {
                "id": 5,
                "name": "Urgent Meeting Request",
                "subject": "URGENT: Board Meeting Today",
            },
            {
                "id": 6,
                "name": "Client Complaint",
                "subject": "Customer Escalation - Action Required",
            },
            {
                "id": 7,
                "name": "IT Support Alert",
                "subject": "Security Update Required",
            },
            {
                "id": 8,
                "name": "HR Policy Update",
                "subject": "New Company Policy - Review Required",
            },
        ]

    @staticmethod
    def get_target_groups():
        """Return available target groups"""
        return [
            {"id": 1, "name": "All Employees", "size": 487},
            {"id": 2, "name": "Finance Team", "size": 42},
            {"id": 3, "name": "IT Department", "size": 85},
            {"id": 4, "name": "Executives", "size": 12},
            {"id": 5, "name": "Sales Department", "size": 67},
            {"id": 6, "name": "HR Team", "size": 18},
            {"id": 7, "name": "Marketing", "size": 34},
            {"id": 8, "name": "Customer Support", "size": 56},
        ]
