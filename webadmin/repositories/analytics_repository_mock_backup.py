"""
Mock repository for analytics data
This returns hardcoded metrics and statistics until the database is ready
"""

from datetime import datetime, timedelta
import random


class MockAnalyticsRepository:
    """Mock data access layer for analytics and metrics"""

    @staticmethod
    def get_overall_stats():
        """Return overall platform statistics"""
        return {
            "total_campaigns": 28,
            "active_campaigns": 5,
            "total_emails_sent": 4850,
            "total_targets": 342,
            "average_open_rate": 42.3,
            "average_click_rate": 18.7,
            "average_submission_rate": 8.2,
            "total_form_submissions": 398,
            "total_credentials_captured": 245,
            "campaigns_this_month": 8,
            "emails_sent_this_month": 1240,
            "most_effective_template": "Password Reset Request",
            "least_effective_template": "Survey Invitation",
            "riskiest_department": "Sales",
            "safest_department": "IT & Security",
        }

    @staticmethod
    def get_campaign_performance():
        """Return performance metrics for all campaigns"""
        campaigns = []
        campaign_names = [
            "Q4 Security Training",
            "Executive Phishing Test",
            "Finance Department Assessment",
            "Company-wide Awareness Test",
            "Sales Team Training",
            "IT Department Validation",
            "HR Policy Update Test",
            "New Hire Training Campaign",
        ]

        for i in range(8):
            sent = random.randint(80, 250)
            opened = int(sent * random.uniform(0.30, 0.65))
            clicked = int(opened * random.uniform(0.25, 0.55))
            submitted = int(clicked * random.uniform(0.30, 0.70))

            campaigns.append(
                {
                    "id": i + 1,
                    "name": campaign_names[i],
                    "status": random.choice(
                        ["completed", "active", "active", "completed", "completed"]
                    ),
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": round((opened / sent) * 100, 1),
                    "click_rate": round((clicked / sent) * 100, 1),
                    "submission_rate": round((submitted / sent) * 100, 1),
                    "start_date": datetime.now() - timedelta(days=random.randint(5, 90)),
                    "template_name": random.choice(
                        [
                            "CEO Email Compromise",
                            "Invoice Request",
                            "Password Reset",
                            "Urgent Meeting",
                        ]
                    ),
                    "target_group": random.choice(
                        [
                            "Engineering Team",
                            "Finance Department",
                            "Executive Team",
                            "Sales Team",
                        ]
                    ),
                }
            )

        return campaigns

    @staticmethod
    def get_time_series_data(days=30):
        """Return time series data for charts (last N days)"""
        data = []
        base_date = datetime.now() - timedelta(days=days)

        for i in range(days):
            date = base_date + timedelta(days=i)
            # Simulate varying activity levels
            day_of_week = date.weekday()
            is_weekend = day_of_week >= 5

            emails_sent = 0 if is_weekend else random.randint(40, 150)
            opened = int(emails_sent * random.uniform(0.35, 0.50)) if emails_sent > 0 else 0
            clicked = int(opened * random.uniform(0.30, 0.55)) if opened > 0 else 0
            submitted = int(clicked * random.uniform(0.40, 0.70)) if clicked > 0 else 0

            data.append(
                {
                    "date": date.strftime("%Y-%m-%d"),
                    "emails_sent": emails_sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": round((opened / emails_sent) * 100, 1) if emails_sent > 0 else 0,
                    "click_rate": round((clicked / emails_sent) * 100, 1) if emails_sent > 0 else 0,
                    "submission_rate": (
                        round((submitted / emails_sent) * 100, 1) if emails_sent > 0 else 0
                    ),
                }
            )

        return data

    @staticmethod
    def get_department_breakdown():
        """Return metrics broken down by department"""
        departments = [
            "Engineering",
            "Finance",
            "Sales",
            "Marketing",
            "HR & Admin",
            "Executive",
            "Customer Support",
            "IT & Security",
        ]

        data = []
        for dept in departments:
            total_targets = random.randint(10, 60)
            sent = total_targets
            opened = int(sent * random.uniform(0.25, 0.70))
            clicked = int(opened * random.uniform(0.20, 0.60))
            submitted = int(clicked * random.uniform(0.30, 0.80))

            data.append(
                {
                    "department": dept,
                    "total_targets": total_targets,
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": round((opened / sent) * 100, 1),
                    "click_rate": round((clicked / sent) * 100, 1),
                    "submission_rate": round((submitted / sent) * 100, 1),
                    "risk_score": round((submitted / sent) * 100, 1),  # Higher = more risky
                }
            )

        # Sort by risk score descending
        data.sort(key=lambda x: x["risk_score"], reverse=True)

        return data

    @staticmethod
    def get_template_effectiveness():
        """Return effectiveness metrics for each email template"""
        templates = [
            "CEO Email Compromise",
            "Invoice Request",
            "Password Reset Request",
            "Urgent Meeting Request",
            "Survey Invitation",
            "IT Support Alert",
            "Client Complaint",
            "HR Policy Update",
        ]

        data = []
        for template in templates:
            sent = random.randint(150, 600)
            opened = int(sent * random.uniform(0.30, 0.70))
            clicked = int(opened * random.uniform(0.25, 0.65))
            submitted = int(clicked * random.uniform(0.30, 0.75))

            data.append(
                {
                    "template_name": template,
                    "times_used": random.randint(3, 15),
                    "emails_sent": sent,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "open_rate": round((opened / sent) * 100, 1),
                    "click_rate": round((clicked / sent) * 100, 1),
                    "submission_rate": round((submitted / sent) * 100, 1),
                    "effectiveness_score": round(
                        ((opened + clicked * 2 + submitted * 3) / (sent * 6)) * 100, 1
                    ),
                }
            )

        # Sort by effectiveness score descending
        data.sort(key=lambda x: x["effectiveness_score"], reverse=True)

        return data

    @staticmethod
    def get_device_breakdown():
        """Return metrics by device type"""
        return [
            {
                "device_type": "Desktop",
                "count": 245,
                "percentage": 58.4,
                "open_rate": 45.2,
                "click_rate": 22.1,
                "submission_rate": 10.3,
            },
            {
                "device_type": "Mobile",
                "count": 142,
                "percentage": 33.8,
                "open_rate": 38.7,
                "click_rate": 15.4,
                "submission_rate": 5.8,
            },
            {
                "device_type": "Tablet",
                "count": 33,
                "percentage": 7.8,
                "open_rate": 41.3,
                "click_rate": 18.9,
                "submission_rate": 7.2,
            },
        ]

    @staticmethod
    def get_browser_breakdown():
        """Return metrics by browser"""
        return [
            {"browser": "Chrome", "count": 198, "percentage": 47.1},
            {"browser": "Firefox", "count": 87, "percentage": 20.7},
            {"browser": "Safari", "count": 65, "percentage": 15.5},
            {"browser": "Edge", "count": 45, "percentage": 10.7},
            {"browser": "Other", "count": 25, "percentage": 6.0},
        ]

    @staticmethod
    def get_os_breakdown():
        """Return metrics by operating system"""
        return [
            {"os": "Windows", "count": 215, "percentage": 51.2},
            {"os": "macOS", "count": 95, "percentage": 22.6},
            {"os": "iOS", "count": 58, "percentage": 13.8},
            {"os": "Android", "count": 42, "percentage": 10.0},
            {"os": "Linux", "count": 10, "percentage": 2.4},
        ]

    @staticmethod
    def get_event_timeline(limit=50):
        """Return recent events for timeline view"""
        event_types = [
            "email_sent",
            "email_opened",
            "link_clicked",
            "form_submitted",
            "credentials_captured",
        ]

        events = []
        base_time = datetime.now()

        for i in range(limit):
            event_type = random.choice(event_types)
            time_ago = timedelta(minutes=random.randint(1, 1440))  # Last 24 hours

            events.append(
                {
                    "id": i + 1,
                    "event_type": event_type,
                    "campaign_name": random.choice(
                        [
                            "Q4 Security Training",
                            "Executive Phishing Test",
                            "HR Benefits Update",
                        ]
                    ),
                    "target_email": f"user{random.randint(1, 300)}@company.com",
                    "timestamp": base_time - time_ago,
                    "ip_address": (
                        f"{random.randint(1, 255)}.{random.randint(1, 255)}."
                        f"{random.randint(1, 255)}.{random.randint(1, 255)}"
                    ),
                    "device": random.choice(["Desktop", "Mobile", "Tablet"]),
                    "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                }
            )

        # Sort by timestamp descending (most recent first)
        events.sort(key=lambda x: x["timestamp"], reverse=True)

        return events

    @staticmethod
    def get_top_vulnerable_users(limit=10):
        """Return users who are most vulnerable (clicked/submitted most)"""
        users = []

        for i in range(limit):
            submitted = random.randint(2, 8)
            clicked = submitted + random.randint(1, 5)
            opened = clicked + random.randint(2, 8)
            received = opened + random.randint(1, 5)

            users.append(
                {
                    "email": f"user{i+1}@company.com",
                    "name": f"Employee #{i+1}",
                    "department": random.choice(
                        [
                            "Sales",
                            "Marketing",
                            "Finance",
                            "Engineering",
                            "Customer Support",
                        ]
                    ),
                    "emails_received": received,
                    "emails_opened": opened,
                    "links_clicked": clicked,
                    "credentials_submitted": submitted,
                    "vulnerability_score": round(
                        (clicked * 2 + submitted * 5) / (received * 7) * 100, 1
                    ),
                }
            )

        # Sort by vulnerability score descending
        users.sort(key=lambda x: x["vulnerability_score"], reverse=True)

        return users

    @staticmethod
    def get_filtered_data(filters):
        """
        Return analytics data filtered by criteria

        Args:
            filters: dict with keys like campaign_id, template_id, group_id, date_from, date_to

        Returns:
            dict: Filtered analytics data
        """
        # In production, this would query database with WHERE clauses
        # For now, return slightly modified overall stats

        base_stats = MockAnalyticsRepository.get_overall_stats()

        # Simulate filtering reducing the numbers
        filter_count = len([v for v in filters.values() if v])
        reduction_factor = 1 - (filter_count * 0.2)  # Each filter reduces data by ~20%

        return {
            "emails_sent": int(base_stats["total_emails_sent"] * reduction_factor),
            "emails_opened": int(base_stats["total_emails_sent"] * reduction_factor * 0.42),
            "links_clicked": int(base_stats["total_emails_sent"] * reduction_factor * 0.18),
            "credentials_submitted": int(base_stats["total_emails_sent"] * reduction_factor * 0.08),
            "filters_applied": filters,
        }
