#!/usr/bin/env python3
"""
Seed Database Script

Populates the database with sample development data:
- Event types (required)
- Departments
- Targets
- Email templates
- Target lists
- Campaigns with events
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import db
from db.models import (
    Department, Target, TargetList, TargetListMember,
    EmailTemplate, Campaign, CampaignTargetList,
    CampaignTarget, EventType, Event
)
from app import create_app


def seed_event_types():
    """Seed required event types"""
    print("📝 Seeding event types...")

    event_types = [
        ("email_sent", "Email was sent to target"),
        ("email_opened", "Target opened the email"),
        ("link_clicked", "Target clicked on phishing link"),
        ("form_submitted", "Target submitted form data"),
        ("credentials_captured", "Target credentials were captured"),
    ]

    for name, description in event_types:
        existing = db.session.query(EventType).filter(EventType.name == name).first()
        if not existing:
            event_type = EventType(name=name, description=description)
            db.session.add(event_type)
            print(f"  ✓ Created event type: {name}")
        else:
            print(f"  - Event type already exists: {name}")

    db.session.commit()


def seed_departments():
    """Seed sample departments"""
    print("\n🏢 Seeding departments...")

    departments = [
        "Engineering",
        "Finance",
        "Sales",
        "Marketing",
        "Human Resources",
        "Executive",
        "Customer Support",
        "IT & Security",
    ]

    dept_objects = []
    for dept_name in departments:
        existing = db.session.query(Department).filter(Department.name == dept_name).first()
        if not existing:
            dept = Department(name=dept_name)
            db.session.add(dept)
            dept_objects.append(dept)
            print(f"  ✓ Created department: {dept_name}")
        else:
            dept_objects.append(existing)
            print(f"  - Department already exists: {dept_name}")

    db.session.commit()
    return dept_objects


def seed_targets(departments):
    """Seed sample targets"""
    print("\n👥 Seeding targets...")

    first_names = ["John", "Jane", "Mike", "Sarah", "David", "Emily", "Robert", "Lisa",
                   "James", "Mary", "Michael", "Patricia", "William", "Jennifer", "Richard"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
                  "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Wilson"]
    positions = ["Manager", "Senior Analyst", "Coordinator", "Director", "Specialist",
                 "Associate", "VP", "Lead", "Executive", "Administrator"]

    targets = []
    for i in range(30):
        first = random.choice(first_names)
        last = random.choice(last_names)
        email = f"{first.lower()}.{last.lower()}{i}@company.com"

        # Check if target exists
        existing = db.session.query(Target).filter(Target.email == email).first()
        if existing:
            targets.append(existing)
            continue

        target = Target(
            email=email,
            first_name=first,
            last_name=last,
            position=random.choice(positions),
            department_id=random.choice(departments).id
        )
        db.session.add(target)
        targets.append(target)

    db.session.commit()
    print(f"  ✓ Created {len(targets)} targets")
    return targets


def seed_email_templates():
    """Seed sample email templates"""
    print("\n📧 Seeding email templates...")

    templates_data = [
        ("CEO Email Compromise", "Urgent: Wire Transfer Required", "ceo@company.com", "CEO John Smith"),
        ("Invoice Request", "RE: Invoice #2024-1847", "billing@company.com", "Billing Department"),
        ("Password Reset Request", "Reset Your Password", "noreply@company.com", "IT Support"),
        ("HR Benefits Update", "Important: Benefits Enrollment", "hr@company.com", "Human Resources"),
        ("IT Security Alert", "Security Update Required", "security@company.com", "IT Security Team"),
    ]

    templates = []
    for name, subject, from_email, from_name in templates_data:
        existing = db.session.query(EmailTemplate).filter(EmailTemplate.name == name).first()
        if existing:
            templates.append(existing)
            print(f"  - Template already exists: {name}")
            continue

        template = EmailTemplate(
            name=name,
            subject=subject,
            from_email=from_email,
            from_name=from_name,
            created_at=datetime.utcnow() - timedelta(days=random.randint(10, 90))
        )
        db.session.add(template)
        templates.append(template)
        print(f"  ✓ Created template: {name}")

    db.session.commit()
    return templates


def seed_target_lists(targets, departments):
    """Seed sample target lists"""
    print("\n📋 Seeding target lists...")

    # Create department-based lists
    target_lists = []
    for dept in departments[:5]:  # First 5 departments
        list_name = f"{dept.name} Team"

        existing = db.session.query(TargetList).filter(TargetList.name == list_name).first()
        if existing:
            target_lists.append(existing)
            print(f"  - Target list already exists: {list_name}")
            continue

        target_list = TargetList(
            name=list_name,
            description=f"All members of {dept.name} department",
            created_at=datetime.utcnow() - timedelta(days=random.randint(20, 120)),
            updated_at=datetime.utcnow() - timedelta(days=random.randint(1, 20))
        )
        db.session.add(target_list)
        db.session.flush()

        # Add targets from this department
        dept_targets = [t for t in targets if t.department_id == dept.id]
        for target in dept_targets[:10]:  # Max 10 per list
            membership = TargetListMember(
                target_list_id=target_list.id,
                target_id=target.id
            )
            db.session.add(membership)

        target_lists.append(target_list)
        print(f"  ✓ Created target list: {list_name} ({len(dept_targets[:10])} members)")

    db.session.commit()
    return target_lists


def seed_campaigns(templates, target_lists):
    """Seed sample campaigns with events"""
    print("\n🎯 Seeding campaigns with events...")

    campaign_names = [
        "Q4 2025 Security Training",
        "Executive Phishing Assessment",
        "Finance Team Awareness Test",
        "Company-wide Security Check",
        "New Hire Training Campaign",
    ]

    # Get event type IDs
    event_types = {
        et.name: et.id for et in db.session.query(EventType).all()
    }

    for i, name in enumerate(campaign_names):
        existing = db.session.query(Campaign).filter(Campaign.name == name).first()
        if existing:
            print(f"  - Campaign already exists: {name}")
            continue

        template = templates[i % len(templates)]
        target_list = target_lists[i % len(target_lists)]

        # Create campaign
        start_date = datetime.utcnow() - timedelta(days=random.randint(5, 60))
        campaign = Campaign(
            name=name,
            status=random.choice(['active', 'completed', 'completed']),
            email_template_id=template.id,
            start_date=start_date,
            created_at=start_date - timedelta(days=2),
            updated_at=datetime.utcnow()
        )
        db.session.add(campaign)
        db.session.flush()

        # Link target list to campaign
        campaign_list = CampaignTargetList(
            campaign_id=campaign.id,
            target_list_id=target_list.id
        )
        db.session.add(campaign_list)
        db.session.flush()

        # Get targets from the list
        members = db.session.query(TargetListMember)\
            .filter(TargetListMember.target_list_id == target_list.id).all()

        # Create campaign targets and events
        for member in members:
            campaign_target = CampaignTarget(
                campaign_id=campaign.id,
                target_id=member.target_id,
                status='sent'
            )
            db.session.add(campaign_target)
            db.session.flush()

            # Create events for this target
            base_time = start_date + timedelta(hours=random.randint(1, 48))

            # Email sent (always happens)
            event_sent = Event(
                campaign_target_id=campaign_target.id,
                event_type_id=event_types['email_sent'],
                created_at=base_time,
                ip_address=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            )
            db.session.add(event_sent)

            # Email opened (60% chance)
            if random.random() < 0.6:
                event_opened = Event(
                    campaign_target_id=campaign_target.id,
                    event_type_id=event_types['email_opened'],
                    created_at=base_time + timedelta(minutes=random.randint(5, 300)),
                    ip_address=event_sent.ip_address
                )
                db.session.add(event_opened)

                # Link clicked (40% of those who opened)
                if random.random() < 0.4:
                    event_clicked = Event(
                        campaign_target_id=campaign_target.id,
                        event_type_id=event_types['link_clicked'],
                        created_at=base_time + timedelta(minutes=random.randint(10, 320)),
                        ip_address=event_sent.ip_address
                    )
                    db.session.add(event_clicked)

                    # Form submitted (50% of those who clicked)
                    if random.random() < 0.5:
                        event_submitted = Event(
                            campaign_target_id=campaign_target.id,
                            event_type_id=event_types['form_submitted'],
                            created_at=base_time + timedelta(minutes=random.randint(15, 330)),
                            ip_address=event_sent.ip_address
                        )
                        db.session.add(event_submitted)

        print(f"  ✓ Created campaign: {name} ({len(members)} targets)")

    db.session.commit()


def main():
    """Main function to seed database"""
    print("\n" + "=" * 60)
    print("Phishly WebAdmin - Seed Database")
    print("=" * 60 + "\n")

    # Create Flask app context
    app = create_app()

    with app.app_context():
        try:
            # Seed data in order
            seed_event_types()
            departments = seed_departments()
            targets = seed_targets(departments)
            templates = seed_email_templates()
            target_lists = seed_target_lists(targets, departments)
            seed_campaigns(templates, target_lists)

            print("\n" + "=" * 60)
            print("✅ Database seeded successfully!")
            print("=" * 60 + "\n")
            return 0

        except Exception as e:
            print(f"\n❌ Error seeding database: {e}")
            import traceback
            traceback.print_exc()
            return 1


if __name__ == "__main__":
    sys.exit(main())

