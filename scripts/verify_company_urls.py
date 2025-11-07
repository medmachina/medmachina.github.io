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

# Timeout for HTTP requests (seconds) — increase this if some hosts are slow
TIMEOUT = 30

# Get the repository root directory
REPO_ROOT = Path(__file__).parent.parent
COMPANIES_FILE = REPO_ROOT / 'public' / 'companies.json'

def is_valid_url(url: str) -> bool:
    """Check if the URL string is valid."""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def verify_url(company_name: str, url_type: str, url: str) -> Tuple[str, str, str, bool]:
    """
    Verify if a URL is accessible.
    Returns tuple of (company_name, url_type, url, is_valid)
    """
    if not is_valid_url(url):
        return company_name, url_type, url, False
    
    try:
        response = requests.head(url, timeout=TIMEOUT)
        # Try GET if HEAD fails
        if response.status_code >= 400:
            response = requests.get(url, timeout=TIMEOUT)
        return company_name, url_type, url, response.status_code < 400
    except requests.RequestException:
        return company_name, url_type, url, False

def verify_all_urls(companies_data: List[Dict]) -> Tuple[List[Tuple[str, str, str]], List[Tuple[str, str, str]]]:
    """
    Verify all URLs in the companies data.
    Returns tuple of (valid_urls, invalid_urls)
    """
    all_urls = []
    for company in companies_data:
        # Collect URLs from the company's `urls` array. Each item may be an object with a
        # `url` field or a plain string. We handle both cases.
        urls_array = company.get('urls') or []
        for url_entry in urls_array:
            if isinstance(url_entry, dict):
                url_val = url_entry.get('url')
            else:
                url_val = url_entry
            if url_val:
                all_urls.append((company.get('name', '<unknown>'), 'url', url_val))

        # Also check LinkedIn URL if present
        linkedin = company.get('linkedin_url')
        if linkedin:
            all_urls.append((company.get('name', '<unknown>'), 'linkedin_url', linkedin))

    valid_urls = []
    invalid_urls = []

    logger.info(f"\nChecking {len(all_urls)} URLs from companies.json...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(verify_url, company_name, url_type, url): (company_name, url_type, url)
            for company_name, url_type, url in all_urls
        }

        for future in as_completed(future_to_url):
            company_name, url_type, url, is_valid = future.result()
            if is_valid:
                valid_urls.append((company_name, url_type, url))
            else:
                invalid_urls.append((company_name, url_type, url))
                logger.error(f"✗ Invalid {url_type} for {company_name}: {url}")

    return valid_urls, invalid_urls



def main():
    if not COMPANIES_FILE.exists():
        logger.error(f"Companies file not found at {COMPANIES_FILE}")
        sys.exit(1)

    try:
        with open(COMPANIES_FILE, 'r', encoding='utf-8') as f:
            companies_data = json.load(f)
    except json.JSONDecodeError:
        logger.error(f"Error parsing {COMPANIES_FILE}")
        sys.exit(1)

    valid_urls, invalid_urls = verify_all_urls(companies_data)

    if not invalid_urls:
        logger.info("\nAll URLs are valid!")
        sys.exit(0)

    logger.info(f"\nFound {len(invalid_urls)} invalid URLs out of {len(valid_urls) + len(invalid_urls)} total URLs")
    sys.exit(1 if invalid_urls else 0)

if __name__ == "__main__":
    main()