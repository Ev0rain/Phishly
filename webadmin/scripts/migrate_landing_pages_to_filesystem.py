#!/usr/bin/env python3
"""
Migrate Landing Pages from Database to Filesystem

This script exports existing landing pages that store HTML/CSS/JS in the database
to the filesystem structure under /templates/landing_pages/.

Usage:
    python migrate_landing_pages_to_filesystem.py [--dry-run]

Options:
    --dry-run    Show what would be migrated without making changes
"""

import sys
import os
from pathlib import Path
import re
import argparse

# Add parent directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from database import db
from db.models import LandingPage
from datetime import datetime


def sanitize_directory_name(name: str) -> str:
    """
    Sanitize landing page name for use as directory name.

    Args:
        name: Landing page name

    Returns:
        Sanitized directory name
    """
    # Convert to lowercase
    sanitized = name.lower()

    # Replace spaces and special characters with hyphens
    sanitized = re.sub(r'[^a-z0-9]+', '-', sanitized)

    # Remove leading/trailing hyphens
    sanitized = sanitized.strip('-')

    # Limit length
    if len(sanitized) > 50:
        sanitized = sanitized[:50].rstrip('-')

    return sanitized


def export_landing_page(landing_page, templates_dir: Path, dry_run: bool = False):
    """
    Export a single landing page from database to filesystem.

    Args:
        landing_page: LandingPage model instance
        templates_dir: Base templates directory
        dry_run: If True, only show what would be done

    Returns:
        Tuple of (success: bool, message: str, template_path: str or None)
    """
    # Skip if already using template_path
    if landing_page.template_path:
        return True, f"Landing page '{landing_page.name}' already uses template_path: {landing_page.template_path}", None

    # Skip if no HTML content
    if not landing_page.html_content:
        return False, f"Landing page '{landing_page.name}' has no HTML content to export", None

    # Create sanitized directory name
    dir_name = sanitize_directory_name(landing_page.name)

    # Ensure uniqueness by appending ID if directory already exists
    template_dir = templates_dir / dir_name
    if template_dir.exists():
        dir_name = f"{dir_name}-{landing_page.id}"
        template_dir = templates_dir / dir_name

    if dry_run:
        print(f"  [DRY RUN] Would create: {template_dir}")
        print(f"  [DRY RUN] Would write index.html ({len(landing_page.html_content)} chars)")
        if landing_page.css_content:
            print(f"  [DRY RUN] Would write style.css ({len(landing_page.css_content)} chars)")
        if landing_page.js_content:
            print(f"  [DRY RUN] Would write script.js ({len(landing_page.js_content)} chars)")
        print(f"  [DRY RUN] Would update template_path to: {dir_name}")
        return True, f"Would export landing page '{landing_page.name}' to {dir_name}", dir_name

    # Create template directory
    try:
        template_dir.mkdir(parents=True, exist_ok=True)

        # Write index.html
        index_file = template_dir / "index.html"
        with open(index_file, 'w', encoding='utf-8') as f:
            f.write(landing_page.html_content)

        # Write style.css if present
        if landing_page.css_content:
            css_file = template_dir / "style.css"
            with open(css_file, 'w', encoding='utf-8') as f:
                f.write(landing_page.css_content)

        # Write script.js if present
        if landing_page.js_content:
            js_file = template_dir / "script.js"
            with open(js_file, 'w', encoding='utf-8') as f:
                f.write(landing_page.js_content)

        # Update landing page to use template_path
        landing_page.template_path = dir_name
        # Clear database content columns (but keep for rollback if needed)
        # landing_pages.html_content = None  # Comment out to keep for rollback
        # landing_pages.css_content = None
        # landing_pages.js_content = None
        db.session.commit()

        return True, f"Exported landing page '{landing_page.name}' to {dir_name}", dir_name

    except Exception as e:
        return False, f"Error exporting landing page '{landing_page.name}': {e}", None


def main():
    """Main migration function."""
    parser = argparse.ArgumentParser(description='Migrate landing pages from database to filesystem')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be migrated without making changes')
    args = parser.parse_args()

    dry_run = args.dry_run

    print("=" * 80)
    print("Landing Pages Database to Filesystem Migration")
    print("=" * 80)
    if dry_run:
        print("MODE: DRY RUN (no changes will be made)")
    else:
        print("MODE: LIVE (changes will be made)")
    print()

    # Templates base directory
    templates_dir = Path("/templates/landing_pages")

    # Create templates directory if it doesn't exist
    if not dry_run:
        templates_dir.mkdir(parents=True, exist_ok=True)
        print(f"Templates directory: {templates_dir}")
    else:
        print(f"Templates directory: {templates_dir} (would be created if needed)")
    print()

    # Query all landing pages
    landing_pages = db.session.query(LandingPage).all()

    if not landing_pages:
        print("No landing pages found in database.")
        return

    print(f"Found {len(landing_pages)} landing pages in database:")
    print("-" * 80)

    success_count = 0
    skip_count = 0
    error_count = 0

    for lp in landing_pages:
        print(f"\nLanding Page: {lp.name} (ID: {lp.id})")
        print(f"  URL Path: {lp.url_path}")
        print(f"  Template Path: {lp.template_path or 'None'}")
        print(f"  HTML Content: {'Yes' if lp.html_content else 'No'} ({len(lp.html_content or '')} chars)")

        success, message, template_path = export_landing_page(lp, templates_dir, dry_run)

        if success:
            if template_path:
                print(f"  ✓ {message}")
                success_count += 1
            else:
                print(f"  → {message}")
                skip_count += 1
        else:
            print(f"  ✗ {message}")
            error_count += 1

    print()
    print("=" * 80)
    print("Migration Summary:")
    print(f"  Total: {len(landing_pages)} landing pages")
    print(f"  Exported: {success_count}")
    print(f"  Skipped: {skip_count}")
    print(f"  Errors: {error_count}")
    print("=" * 80)

    if not dry_run and success_count > 0:
        print("\nMigration completed!")
        print("Note: Original HTML/CSS/JS content is kept in database for rollback if needed.")
        print("To permanently remove it, manually clear the html_content/css_content/js_content columns.")


if __name__ == "__main__":
    # Create Flask app context for database access
    from app import create_app
    app = create_app()

    with app.app_context():
        main()
