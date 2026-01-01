"""
Mock repository for email template data
This returns hardcoded data and handles file operations until the database is ready
"""

from datetime import datetime, timedelta
import os


class MockTemplatesRepository:
    """Mock data access layer for email templates"""

    # Directory where template HTML files are stored
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "email_templates")

    @staticmethod
    def get_all_templates():
        """Return all email templates with metadata"""
        return [
            {
                "id": 1,
                "name": "CEO Email Compromise",
                "subject": "Urgent: Wire Transfer Required",
                "tags": ["executive", "urgent", "financial"],
                "filename": "ceo_compromise.html",
                "created_at": datetime.now() - timedelta(days=45),
                "last_used": datetime.now() - timedelta(days=2),
                "times_used": 12,
            },
            {
                "id": 2,
                "name": "Invoice Request",
                "subject": "RE: Invoice #2024-1847",
                "tags": ["finance", "billing"],
                "filename": "invoice_request.html",
                "created_at": datetime.now() - timedelta(days=60),
                "last_used": datetime.now() - timedelta(days=5),
                "times_used": 8,
            },
            {
                "id": 3,
                "name": "Password Reset Request",
                "subject": "Reset Your Password",
                "tags": ["it-security", "credentials"],
                "filename": "password_reset.html",
                "created_at": datetime.now() - timedelta(days=30),
                "last_used": datetime.now() - timedelta(days=14),
                "times_used": 15,
            },
            {
                "id": 4,
                "name": "Survey Invitation",
                "subject": "Your Feedback Matters",
                "tags": ["hr", "survey"],
                "filename": "survey_invitation.html",
                "created_at": datetime.now() - timedelta(days=90),
                "last_used": datetime.now() - timedelta(days=21),
                "times_used": 6,
            },
            {
                "id": 5,
                "name": "Urgent Meeting Request",
                "subject": "URGENT: Board Meeting Today",
                "tags": ["executive", "urgent", "meeting"],
                "filename": "urgent_meeting.html",
                "created_at": datetime.now() - timedelta(days=20),
                "last_used": datetime.now() - timedelta(days=1),
                "times_used": 3,
            },
            {
                "id": 6,
                "name": "Client Complaint",
                "subject": "Customer Escalation - Action Required",
                "tags": ["support", "urgent"],
                "filename": "client_complaint.html",
                "created_at": datetime.now() - timedelta(days=15),
                "last_used": datetime.now() - timedelta(days=7),
                "times_used": 5,
            },
            {
                "id": 7,
                "name": "IT Support Alert",
                "subject": "Security Update Required",
                "tags": ["it-security", "alert"],
                "filename": "it_support_alert.html",
                "created_at": datetime.now() - timedelta(days=50),
                "last_used": datetime.now() - timedelta(days=10),
                "times_used": 9,
            },
            {
                "id": 8,
                "name": "HR Policy Update",
                "subject": "New Company Policy - Review Required",
                "tags": ["hr", "policy"],
                "filename": "hr_policy_update.html",
                "created_at": datetime.now() - timedelta(days=35),
                "last_used": datetime.now() - timedelta(days=28),
                "times_used": 4,
            },
            {
                "id": 9,
                "name": "Shipping Notification",
                "subject": "Package Delivery Confirmation Required",
                "tags": ["delivery", "package"],
                "filename": "shipping_notification.html",
                "created_at": datetime.now() - timedelta(days=25),
                "last_used": datetime.now() - timedelta(days=3),
                "times_used": 7,
            },
            {
                "id": 10,
                "name": "LinkedIn Connection Request",
                "subject": "You have a new connection request",
                "tags": ["social", "linkedin"],
                "filename": "linkedin_connection.html",
                "created_at": datetime.now() - timedelta(days=18),
                "last_used": datetime.now() - timedelta(days=6),
                "times_used": 11,
            },
        ]

    @staticmethod
    def get_template_by_id(template_id):
        """Return a single template by ID"""
        templates = MockTemplatesRepository.get_all_templates()
        for template in templates:
            if template["id"] == template_id:
                return template
        return None

    @staticmethod
    def get_template_html(filename):
        """Read the HTML content of a template file"""
        filepath = os.path.join(MockTemplatesRepository.TEMPLATES_DIR, filename)

        # If file doesn't exist, return a mock HTML template
        if not os.path.exists(filepath):
            return MockTemplatesRepository._get_mock_html(filename)

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"<p>Error reading template: {str(e)}</p>"

    @staticmethod
    def _get_mock_html(filename):
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
    def save_template(name, subject, tags, html_content, filename):
        """
        Save a new template (mock implementation)
        In production, this would save to the filesystem and database
        """
        # Ensure email_templates directory exists
        os.makedirs(MockTemplatesRepository.TEMPLATES_DIR, exist_ok=True)

        # Save HTML file
        filepath = os.path.join(MockTemplatesRepository.TEMPLATES_DIR, filename)

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html_content)
            return True, "Template saved successfully"
        except Exception as e:
            return False, f"Error saving template: {str(e)}"

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
