"""
Info Page Processor
Converts Flask Jinja2 templates to static HTML for deployment
"""

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def process_info_page_template(template_path: Path, output_path: Path, base_url: str = "/awareness") -> bool:
    """
    Process info_page Jinja2 template to static HTML.

    Replaces {{ url_for('static', filename='...') }} with hardcoded paths.

    Args:
        template_path: Path to the Jinja2 template file
        output_path: Path where processed HTML should be written
        base_url: Base URL for the awareness page (default: /awareness)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Read template
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Pattern to match {{ url_for('static', filename='...') }}
        # This regex captures the filename inside the quotes
        pattern = r"\{\{\s*url_for\s*\(\s*['\"]static['\"]\s*,\s*filename\s*=\s*['\"]([^'\"]+)['\"]\s*\)\s*\}\}"

        def replace_url_for(match):
            """Replace url_for with hardcoded path"""
            filename = match.group(1)
            # Return hardcoded path: /awareness/static/{filename}
            return f"{base_url}/static/{filename}"

        # Replace all url_for patterns
        processed_content = re.sub(pattern, replace_url_for, content)

        # Ensure output directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write processed HTML
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        logger.info(f"Successfully processed info_page template: {template_path} -> {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error processing info_page template: {e}", exc_info=True)
        return False


def deploy_info_page(
    source_dir: Path,
    deployment_dir: Path,
    base_url: str = "/awareness"
) -> tuple[bool, str]:
    """
    Deploy info_page to campaign deployment directory.

    This function:
    1. Processes the Jinja2 template to static HTML
    2. Copies all static assets (CSS, JS, images)
    3. Creates the awareness subdirectory structure

    Args:
        source_dir: Path to templates/landing_pages/info_page/
        deployment_dir: Path to /campaign_landing_pages/{campaign_id}/
        base_url: Base URL for the awareness page

    Returns:
        Tuple of (success: bool, message: str)
    """
    try:
        import shutil

        # Validate source directory
        if not source_dir.exists():
            return False, f"Source directory not found: {source_dir}"

        template_file = source_dir / "templates" / "index.html"
        if not template_file.exists():
            return False, f"Template file not found: {template_file}"

        # Create awareness subdirectory in deployment
        awareness_dir = deployment_dir / "awareness"
        awareness_dir.mkdir(parents=True, exist_ok=True)

        # Process and copy template
        output_html = awareness_dir / "index.html"
        if not process_info_page_template(template_file, output_html, base_url):
            return False, "Failed to process info_page template"

        # Copy static assets
        source_static = source_dir / "static"
        if source_static.exists():
            dest_static = awareness_dir / "static"

            # Remove existing static directory if it exists
            if dest_static.exists():
                shutil.rmtree(dest_static)

            # Copy entire static directory
            shutil.copytree(source_static, dest_static)
            logger.info(f"Copied static assets: {source_static} -> {dest_static}")

        # Verify deployment
        if not output_html.exists():
            return False, "Deployment verification failed: index.html not found"

        if not (awareness_dir / "static").exists():
            return False, "Deployment verification failed: static directory not found"

        logger.info(f"Successfully deployed info_page to {awareness_dir}")
        return True, f"Info page deployed to {awareness_dir}"

    except Exception as e:
        logger.error(f"Error deploying info_page: {e}", exc_info=True)
        return False, f"Error deploying info_page: {str(e)}"


if __name__ == "__main__":
    # Test the processor
    import sys

    logging.basicConfig(level=logging.INFO)

    # Test paths
    source_dir = Path("/home/skam/github/Phishly/templates/landing_pages/info_page")
    test_output_dir = Path("/tmp/test_info_page_deployment")

    print(f"Testing info_page processor...")
    print(f"Source: {source_dir}")
    print(f"Output: {test_output_dir}")

    # Run deployment test
    success, message = deploy_info_page(source_dir, test_output_dir)

    if success:
        print(f"✓ SUCCESS: {message}")
        print(f"\nDeployed files:")
        for file in sorted(test_output_dir.rglob("*")):
            if file.is_file():
                print(f"  {file.relative_to(test_output_dir)}")
    else:
        print(f"✗ FAILED: {message}")
        sys.exit(1)
