#!/usr/bin/env python3
"""
update_robots.py

Validates and enriches robot data in robots.json.
- Validates against robots.schema.json for schema conformance
- Verifies URL accessibility (website links)
- Verifies photo URL accessibility
- Optional backup and output file support
"""

import json
import requests
import jsonschema
from pathlib import Path
import sys
import argparse
import logging
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Timeout for HTTP requests (seconds)
TIMEOUT = 60

# Get the repository root directory
REPO_ROOT = Path(__file__).parent.parent
ROBOTS_FILE = REPO_ROOT / 'public' / 'robots.json'
ROBOTS_SCHEMA_FILE = REPO_ROOT / 'public' / 'robots.schema.json'


def is_valid_url(url: str) -> bool:
    """Check if the URL string is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False


def verify_url(robot_name: str, url_type: str, url: str) -> Tuple[str, str, str, bool]:
    """
    Verify if a URL is accessible.
    Returns tuple of (robot_name, url_type, url, is_valid)
    """
    if not is_valid_url(url):
        return robot_name, url_type, url, False
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
        # Try GET if HEAD fails
        if response.status_code >= 400:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
        return robot_name, url_type, url, response.status_code < 400
    except requests.RequestException:
        return robot_name, url_type, url, False


def validate_photo_structure(robots_data: List[Dict]) -> bool:
    """
    Validate that all photo entries have the required structure.
    Returns True if valid, False otherwise.
    """
    issues = []
    
    for robot in robots_data:
        if 'photos' not in robot:
            continue
            
        if not isinstance(robot['photos'], list):
            issues.append(f"Robot '{robot['name']}': 'photos' is not a list")
            continue
            
        for i, photo in enumerate(robot['photos']):
            if not isinstance(photo, dict):
                issues.append(f"Robot '{robot['name']}': photo {i} is not an object")
                continue
                
            if 'url' not in photo:
                issues.append(f"Robot '{robot['name']}': photo {i} missing 'url' field")
            
            # 'site' is optional, so we don't require it
    
    if issues:
        logger.error("\n=== Photo Structure Validation Issues ===")
        for issue in issues:
            logger.error(f"- {issue}")
        return False
    
    return True


def print_photo_summary(robots_data: List[Dict]) -> None:
    """Print a summary of photo URLs for each robot, sorted by count."""
    robot_url_info = []
    for robot in robots_data:
        photo_count = len(robot.get('photos', []))
        sites = set(photo['site'] for photo in robot.get('photos', []) if 'site' in photo)
        robot_url_info.append((robot['name'], photo_count, sites))
    
    # Sort by URL count descending, then by name
    robot_url_info.sort(key=lambda x: (-x[1], x[0]))
    
    logger.info("\n=== Photo URL Count Summary ===")
    logger.info(f"{'Robot Name'.ljust(35)} {'Photos'.ljust(8)} Sites")
    logger.info("-" * 70)
    for name, count, sites in robot_url_info:
        sites_str = ", ".join(sorted(sites)) if sites else "N/A"
        logger.info(f"{name[:34].ljust(35)} {str(count).ljust(8)} {sites_str}")


def verify_all_urls(robots_data: List[Dict], verify_photos: bool = True) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """
    Verify all URLs in the robots data (info URLs and optionally photo URLs).
    Returns tuple of (valid_urls, invalid_urls)
    """
    all_urls = []
    for robot in robots_data:
        robot_name = robot.get('name', '<unknown>')
        
        # Collect info URLs
        urls_array = robot.get('urls') or []
        for url_entry in urls_array:
            if isinstance(url_entry, dict):
                url_val = url_entry.get('url')
                caption = url_entry.get('caption', 'url')
            else:
                url_val = url_entry
                caption = 'url'
            if url_val:
                all_urls.append((robot_name, f"info:{caption}", url_val))
        
        # Collect photo URLs if requested
        if verify_photos:
            photos_array = robot.get('photos') or []
            for photo_entry in photos_array:
                if isinstance(photo_entry, dict):
                    photo_url = photo_entry.get('url')
                    site_url = photo_entry.get('site')
                    if photo_url:
                        all_urls.append((robot_name, 'photo:url', photo_url))
                    if site_url:
                        all_urls.append((robot_name, 'photo:site', site_url))

    valid_urls = []
    invalid_urls = []

    logger.info(f"\nVerifying {len(all_urls)} URLs from robots.json...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(verify_url, robot_name, url_type, url): (robot_name, url_type, url)
            for robot_name, url_type, url in all_urls
        }

        completed = 0
        for future in as_completed(future_to_url):
            robot_name, url_type, url, is_valid = future.result()
            completed += 1
            if is_valid:
                valid_urls.append((robot_name, url_type, url))
            else:
                invalid_urls.append((robot_name, url_type, url))

            # Periodic progress updates only
            if completed % 10 == 0 or completed == len(all_urls):
                logger.info(f"Progress: {completed}/{len(all_urls)} URLs verified")

    return valid_urls, invalid_urls


def main():
    parser = argparse.ArgumentParser(
        description='Validate and verify robot data in robots.json'
    )
    parser.add_argument(
        '--source',
        type=Path,
        default=ROBOTS_FILE,
        help='Path to robots.json file (default: public/robots.json)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (default: overwrites source)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Verify schema conformance and URL accessibility without modifying data'
    )
    parser.add_argument(
        '--photo-summary',
        action='store_true',
        help='Display photo URL summary after verification'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create a backup of the original file before updating'
    )
    
    args = parser.parse_args()
    
    source_file = args.source
    output_file = args.output or source_file
    
    if not source_file.exists():
        logger.error(f"Source file not found: {source_file}")
        sys.exit(1)
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            robots_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing {source_file}: {e}")
        sys.exit(1)
    
    logger.info(f"Loaded {len(robots_data)} robots from {source_file}")

    # Validate photo structure first
    if not validate_photo_structure(robots_data):
        logger.error("Photo structure validation failed")
        sys.exit(1)

    # Schema validation (always runs)
    if not ROBOTS_SCHEMA_FILE.exists():
        logger.error(f"Schema file not found: {ROBOTS_SCHEMA_FILE}")
        sys.exit(1)
    with open(ROBOTS_SCHEMA_FILE, 'r', encoding='utf-8') as sf:
        schema = json.load(sf)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(robots_data), key=lambda e: e.path)
    if errors:
        logger.error(f"\n✗ Schema validation failed: {len(errors)} error(s)")
        for err in errors[:50]:  # cap output
            path = '.'.join(str(p) for p in err.path) or '<root>'
            logger.error(f"  - {path}: {err.message}")
        if len(errors) > 50:
            logger.error("  ... (additional errors truncated)")
        sys.exit(1)
    logger.info("✓ Schema validation passed")
    
    # Verify URLs (always include photos)
    valid_urls, invalid_urls = verify_all_urls(robots_data, verify_photos=True)
    
    if invalid_urls:
        logger.warning(f"\n⚠ Found {len(invalid_urls)} invalid URLs")
        for robot_name, url_type, url in invalid_urls:
            logger.warning(f"  - {robot_name}: {url_type} = {url}")
    else:
        logger.info("\n✓ All URLs are valid!")
    
    # Show photo summary if requested
    if args.photo_summary:
        print_photo_summary(robots_data)
    
    if args.verify_only:
        logger.info("\nVerification complete (--verify-only mode)")
        sys.exit(1 if invalid_urls else 0)
    
    # No enrichment for robots currently - would go here if needed in the future
    
    # Create backup if requested
    if args.backup and output_file.exists():
        backup_file = output_file.with_suffix('.json.bak')
        import shutil
        shutil.copy2(output_file, backup_file)
        logger.info(f"\n✓ Backup created: {backup_file}")
    
    # Write output (only if validation passes)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(robots_data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"\n✓ Updated robots written to: {output_file}")
    logger.info(f"Total robots: {len(robots_data)}")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
