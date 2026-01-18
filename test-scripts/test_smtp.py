"""
One-off SMTP test script for Phishly.

Edit the SMTP_* variables below with real credentials before running.
This file is intended to be temporary and can be deleted after testing.
"""

import smtplib
from email.message import EmailMessage
import ssl
import sys

# ----- Configuration (edit before running) -----
SMTP_HOST = ""
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASS = ""
USE_TLS = True  # If True use STARTTLS (port 587). If False and port 465, uses SSL.

FROM_EMAIL = ""
TO_EMAIL = ""


def send_test_email() -> int:
    msg = EmailMessage()
    msg["Subject"] = "Phishly SMTP Test"
    msg["From"] = FROM_EMAIL
    msg["To"] = TO_EMAIL
    msg.set_content("This is a plain-text body for SMTP test.")
    msg.add_alternative(
        "<html><body><p>This is an <b>HTML</b> SMTP test.</p></body></html>",
        subtype="html",
    )

    try:
        if USE_TLS:
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as s:
                s.ehlo()
                s.starttls(context=ssl.create_default_context())
                s.ehlo()
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)
        else:
            with smtplib.SMTP_SSL(
                SMTP_HOST, SMTP_PORT, context=ssl.create_default_context(), timeout=30
            ) as s:
                s.login(SMTP_USER, SMTP_PASS)
                s.send_message(msg)

        print("✅ Email sent successfully to", TO_EMAIL)
        return 0

    except Exception as e:
        print("❌ Error sending email:", e)
        return 2


if __name__ == "__main__":
    exit_code = send_test_email()
    if exit_code != 0:
        print(
            "See error above. Common issues: wrong credentials, port, or SMTP provider blocking less-secure logins."
        )
    sys.exit(exit_code)
