#!/usr/bin/env python3
"""
Create a minimal test email template
"""

import os
import sys

# Add webadmin to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'webadmin'))

from app import create_app
from repositories.templates_repository import TemplatesRepository

def main():
    app = create_app()
    with app.app_context():
        # Create simple test template
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test Email</title>
        </head>
        <body>
            <h1>Urgent Action Required</h1>
            <p>Dear {{ target.name }},</p>
            <p>Please click the link below to verify your account:</p>
            <p><a href="{{ phishing_url }}">Verify Account</a></p>
            <p>Thank you</p>
        </body>
        </html>
        """

        success, message, template_id = TemplatesRepository.save_template(
            name="Test Phishing Template",
            subject="Action Required: Verify Your Account",
            from_email="noreply@company.com",
            from_name="IT Department",
            html_content=html_content,
            created_by_id=1
        )

        if success:
            print(f"✅ SUCCESS: {message}")
            print(f"   Template ID: {template_id}")
        else:
            print(f"❌ FAIL: {message}")
            return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())
