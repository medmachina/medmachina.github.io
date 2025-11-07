#!/usr/bin/env python3

import json
import requests
from pathlib import Path
import sys
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Dict, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Timeout for HTTP requests (seconds) - increase if needed
TIMEOUT = 30

# Get the repository root directory
REPO_ROOT = Path(__file__).parent.parent
ROBOTS_FILE = REPO_ROOT / 'public' / 'robots.json'

def is_valid_url(url: str) -> bool:
    """Check if the URL string is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def verify_url(robot_name: str, url_info: Dict[str, str]) -> Tuple[str, str, str, bool]:
    """
    Verify if a URL is accessible.
    Returns tuple of (robot_name, caption, url, is_valid)
    """
    url = url_info.get('url', '')
    caption = url_info.get('caption', '')
    
    if not is_valid_url(url):
        return robot_name, caption, url, False
    
    try:
        response = requests.head(url, timeout=TIMEOUT)
        # Try GET if HEAD fails
        if response.status_code >= 400:
            response = requests.get(url, timeout=TIMEOUT)
        return robot_name, caption, url, response.status_code < 400
    except requests.RequestException:
        return robot_name, caption, url, False

def verify_all_urls(robots_data: List[Dict]) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """
    Verify all URLs in the robots data (excluding photo URLs).
    Returns tuple of (valid_urls, invalid_urls)
    """
    all_urls = []
    for robot in robots_data:
        if 'urls' in robot and robot['urls']:
            for url_info in robot['urls']:
                all_urls.append((robot['name'], url_info))

    valid_urls = []
    invalid_urls = []

    logger.info(f"\nChecking {len(all_urls)} URLs from robots.json (excluding photo URLs)...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(verify_url, robot_name, url_info): (robot_name, url_info)
            for robot_name, url_info in all_urls
        }

        for future in as_completed(future_to_url):
            robot_name, caption, url, is_valid = future.result()
            if is_valid:
                valid_urls.append((robot_name, caption, url))
            else:
                invalid_urls.append((robot_name, caption, url))
                logger.error(f"✗ Invalid URL for {robot_name} ({caption}): {url}")

    return valid_urls, invalid_urls



def main():
    if not ROBOTS_FILE.exists():
        logger.error(f"Robots file not found at {ROBOTS_FILE}")
        sys.exit(1)

    try:
        with open(ROBOTS_FILE, 'r', encoding='utf-8') as f:
            robots_data = json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Error parsing {ROBOTS_FILE}")
        sys.exit(1)

    valid_urls, invalid_urls = verify_all_urls(robots_data)

    if not invalid_urls:
        logger.info("\nAll URLs are valid!")
        sys.exit(0)

    logger.info(f"\nFound {len(invalid_urls)} invalid URLs out of {len(valid_urls) + len(invalid_urls)} total URLs")
    sys.exit(1 if invalid_urls else 0)

if __name__ == "__main__":
    main()