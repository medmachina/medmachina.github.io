#!/usr/bin/env python3
"""
update_companies.py

Enriches company data in companies.json with external metadata sources.
- Validates existing URLs (website, LinkedIn)
- Optionally fetches additional company metadata from:
  - OpenCorporates API (company registration, jurisdiction)
  - Crunchbase-like data via web scraping (funding, employee count)
  - Company website metadata (description, industry)
- Preserves existing LinkedIn URLs and validates accessibility
"""

import json
import requests
import jsonschema
from pathlib import Path
import sys
import argparse
import time
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

# Timeout for HTTP requests (seconds)
TIMEOUT = 60

# Rate limiting delay between external API calls (seconds)
RATE_LIMIT_DELAY = 2.0

# Get the repository root directory
REPO_ROOT = Path(__file__).parent.parent
COMPANIES_FILE = REPO_ROOT / 'public' / 'companies.json'
COMPANIES_SCHEMA_FILE = REPO_ROOT / 'public' / 'companies.schema.json'

# External API endpoints
OPENCORPORATES_API = "https://api.opencorporates.com/v0.4"


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
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        # LinkedIn URLs: just validate format, don't actually check (anti-bot protection)
        if 'linkedin.com' in url.lower():
            # LinkedIn URLs are valid if they match the expected pattern
            return company_name, url_type, url, '/company/' in url.lower()
        
        response = requests.head(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
        # Try GET if HEAD fails
        if response.status_code >= 400:
            response = requests.get(url, timeout=TIMEOUT, allow_redirects=True, headers=headers)
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
        # Collect URLs from the company's `urls` array
        urls_array = company.get('urls') or []
        for url_entry in urls_array:
            if isinstance(url_entry, dict):
                url_val = url_entry.get('url')
            else:
                url_val = url_entry
            if url_val:
                all_urls.append((company.get('name', '<unknown>'), 'url', url_val))

        # Check LinkedIn URL if present
        linkedin = company.get('linkedin_url')
        if linkedin:
            all_urls.append((company.get('name', '<unknown>'), 'linkedin_url', linkedin))

    valid_urls = []
    invalid_urls = []

    logger.info(f"\nVerifying {len(all_urls)} URLs from companies.json...")

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(verify_url, company_name, url_type, url): (company_name, url_type, url)
            for company_name, url_type, url in all_urls
        }

        completed = 0
        for future in as_completed(future_to_url):
            company_name, url_type, url, is_valid = future.result()
            completed += 1
            if is_valid:
                valid_urls.append((company_name, url_type, url))
            else:
                invalid_urls.append((company_name, url_type, url))

            # Periodic progress updates only (suppress per-URL invalid logging)
            if completed % 10 == 0 or completed == len(all_urls):
                logger.info(f"Progress: {completed}/{len(all_urls)} URLs verified")

    return valid_urls, invalid_urls


def fetch_opencorporates_data(company_name: str, jurisdiction: Optional[str] = None) -> Optional[Dict]:
    """
    Fetch company data from OpenCorporates API.
    Free tier has rate limits - use sparingly.
    """
    try:
        # Search for company by name
        params = {
            'q': company_name,
            'format': 'json'
        }
        if jurisdiction:
            params['jurisdiction_code'] = jurisdiction

        url = f"{OPENCORPORATES_API}/companies/search"
        response = requests.get(url, params=params, timeout=TIMEOUT)
        
        if response.status_code == 200:
            data = response.json()
            companies = data.get('results', {}).get('companies', [])
            if companies:
                # Return the first match
                company_data = companies[0].get('company', {})
                return {
                    'name': company_data.get('name'),
                    'jurisdiction': company_data.get('jurisdiction_code'),
                    'company_number': company_data.get('company_number'),
                    'incorporation_date': company_data.get('incorporation_date'),
                    'company_type': company_data.get('company_type'),
                    'registered_address': company_data.get('registered_address_in_full'),
                    'status': company_data.get('current_status')
                }
        time.sleep(RATE_LIMIT_DELAY)
        return None
    except Exception as e:
        logger.debug(f"OpenCorporates lookup failed for {company_name}: {e}")
        return None


def extract_website_metadata(url: str) -> Optional[Dict]:
    """
    Extract metadata from company website (description, industry hints, employee count).
    Looks for meta tags, Open Graph tags, structured data (JSON-LD), etc.
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; CompanyBot/1.0; +https://medmachina.github.io)'
        }
        response = requests.get(url, timeout=TIMEOUT, headers=headers, allow_redirects=True)
        
        if response.status_code != 200:
            return None

        soup = BeautifulSoup(response.content, 'html.parser')
        
        metadata = {}
        
        # Try to get description from meta tags
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or \
                   soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc:
            metadata['description'] = meta_desc.get('content', '').strip()
        
        # Try to get title
        og_title = soup.find('meta', attrs={'property': 'og:title'})
        if og_title:
            metadata['title'] = og_title.get('content', '').strip()
        elif soup.title:
            metadata['title'] = soup.title.string.strip()
        
        # Try to get site name
        og_site = soup.find('meta', attrs={'property': 'og:site_name'})
        if og_site:
            metadata['site_name'] = og_site.get('content', '').strip()
        
        # Try to extract employee count from structured data (JSON-LD)
        import re
        json_ld_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_ld_scripts:
            try:
                data = json.loads(script.string)
                # Check for Organization schema with numberOfEmployees
                if isinstance(data, dict) and data.get('@type') == 'Organization':
                    if 'numberOfEmployees' in data:
                        metadata['employee_count'] = data['numberOfEmployees']
                        break
            except:
                pass
        
        # Try to find employee count in page text (common patterns)
        if 'employee_count' not in metadata:
            text = soup.get_text()
            # Pattern: "X employees", "X+ employees", "over X employees"
            patterns = [
                r'(\d+[\d,]*)\s*\+?\s*employees',
                r'over\s*(\d+[\d,]*)\s*employees',
                r'more than\s*(\d+[\d,]*)\s*employees',
                r'(\d+[\d,]*)\s*team members'
            ]
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    count_str = match.group(1).replace(',', '')
                    try:
                        metadata['employee_count'] = int(count_str)
                        break
                    except:
                        pass
        
        return metadata if metadata else None
        
    except Exception as e:
        logger.debug(f"Website metadata extraction failed for {url}: {e}")
        return None


def enrich_company(company: Dict, enrich_external: bool = False) -> Dict:
    """
    Enrich a single company entry with additional metadata.
    """
    enriched = company.copy()
    
    if not enrich_external:
        return enriched
    
    company_name = company.get('name', '')
    logger.info(f"Enriching: {company_name}")
    
    # Try OpenCorporates if we have a country hint
    country = company.get('country')
    jurisdiction_map = {
        'United States': 'us',
        'Germany': 'de',
        'United Kingdom': 'gb',
        'France': 'fr',
        'Switzerland': 'ch',
        'Netherlands': 'nl',
        'Israel': 'il',
        'Canada': 'ca',
        'Japan': 'jp',
        'South Korea': 'kr'
    }
    jurisdiction = jurisdiction_map.get(country)
    
    oc_data = fetch_opencorporates_data(company_name, jurisdiction)
    if oc_data:
        if not enriched.get('description') and oc_data.get('registered_address'):
            enriched['description'] = f"Registered at: {oc_data['registered_address']}"
        if oc_data.get('incorporation_date'):
            enriched['founded_year'] = oc_data['incorporation_date'][:4]  # Extract year
        if oc_data.get('company_type'):
            enriched['company_type'] = oc_data['company_type']
    
    # Try to enrich from website metadata
    urls_array = company.get('urls', [])
    if urls_array:
        first_url_entry = urls_array[0]
        website_url = first_url_entry.get('url') if isinstance(first_url_entry, dict) else first_url_entry
        
        if website_url:
            web_meta = extract_website_metadata(website_url)
            if web_meta:
                # Only add description if not already present
                if not enriched.get('description') and web_meta.get('description'):
                    enriched['description'] = web_meta['description']
                # Add employee count if found
                if web_meta.get('employee_count') and not enriched.get('employee_count'):
                    enriched['employee_count'] = web_meta['employee_count']
    
    time.sleep(RATE_LIMIT_DELAY)
    return enriched


def enrich_companies(companies_data: List[Dict], enrich_external: bool = False) -> List[Dict]:
    """
    Enrich all companies with external data sources.
    """
    if not enrich_external:
        logger.info("Skipping external enrichment (use --enrich-external to enable)")
        return companies_data
    
    logger.info(f"\nEnriching {len(companies_data)} companies with external sources...")
    enriched_companies = []
    
    for idx, company in enumerate(companies_data, 1):
        enriched = enrich_company(company, enrich_external)
        enriched_companies.append(enriched)
        logger.info(f"Progress: {idx}/{len(companies_data)} companies processed")
    
    return enriched_companies


def main():
    parser = argparse.ArgumentParser(
        description='Update and enrich company data in companies.json'
    )
    parser.add_argument(
        '--source',
        type=Path,
        default=COMPANIES_FILE,
        help='Path to companies.json file (default: public/companies.json)'
    )
    parser.add_argument(
        '--output',
        type=Path,
        help='Output file path (default: overwrites source)'
    )
    parser.add_argument(
        '--enrich-external',
        action='store_true',
        help='Fetch additional company metadata from external sources (OpenCorporates, website scraping)'
    )
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Verify schema conformance and URL accessibility without enriching data'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create a backup of the original file before updating'
    )
    parser.add_argument(
        '--prefix',
        type=str,
        help='Process only robots whose IDs start with this prefix (case-insensitive)'
    )
    
    args = parser.parse_args()
    
    source_file = args.source
    output_file = args.output or source_file
    
    if not source_file.exists():
        logger.error(f"Source file not found: {source_file}")
        sys.exit(1)
    
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            companies_data = json.load(f)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing {source_file}: {e}")
        sys.exit(1)
    
    logger.info(f"Loaded {len(companies_data)} companies from {source_file}")
    
    # Apply prefix filter if specified (filter companies by their robots for processing only)
    full_companies_data = companies_data
    if args.prefix:
        prefix_lower = args.prefix.lower()
        filtered_companies = []
        for company in companies_data:
            robots = company.get('robots', [])
            matching_robots = [r for r in robots if r.lower().startswith(prefix_lower)]
            if matching_robots:
                filtered_companies.append(company)
        companies_data = filtered_companies
        logger.info(f"Processing {len(companies_data)} companies with robots matching prefix '{args.prefix}'")
    
    # Schema validation (always runs first)
    if not COMPANIES_SCHEMA_FILE.exists():
        logger.error(f"Schema file not found: {COMPANIES_SCHEMA_FILE}")
        sys.exit(1)
    with open(COMPANIES_SCHEMA_FILE, 'r', encoding='utf-8') as sf:
        schema = json.load(sf)
    validator = jsonschema.Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(companies_data), key=lambda e: e.path)
    if errors:
        logger.error(f"\n✗ Schema validation failed: {len(errors)} error(s)")
        for err in errors[:50]:  # cap output
            path = '.'.join(str(p) for p in err.path) or '<root>'
            logger.error(f"  - {path}: {err.message}")
        if len(errors) > 50:
            logger.error("  ... (additional errors truncated)")
        sys.exit(1)
    logger.info("✓ Schema validation passed")
    
    # Verify URLs
    valid_urls, invalid_urls = verify_all_urls(companies_data)
    
    if invalid_urls:
        logger.warning(f"\n⚠ Found {len(invalid_urls)} invalid URLs")
        for company_name, url_type, url in invalid_urls:
            logger.warning(f"  - {company_name}: {url_type} = {url}")
    else:
        logger.info("\n✓ All URLs are valid!")
    
    if args.verify_only:
        logger.info("\nVerification complete (--verify-only mode)")
        sys.exit(1 if invalid_urls else 0)
    
    # Enrich companies
    enriched_companies = enrich_companies(companies_data, args.enrich_external)
    
    # Merge enriched companies back into full dataset if prefix filter was used
    if args.prefix:
        # Create a map of enriched companies by name
        enriched_by_name = {company.get('name'): company for company in enriched_companies}
        # Merge back into full dataset
        final_companies = []
        for company in full_companies_data:
            company_name = company.get('name')
            if company_name in enriched_by_name:
                final_companies.append(enriched_by_name[company_name])
            else:
                final_companies.append(company)
        enriched_companies = final_companies
    
    # Create backup if requested
    if args.backup and output_file.exists():
        backup_file = output_file.with_suffix('.json.bak')
        import shutil
        shutil.copy2(output_file, backup_file)
        logger.info(f"\n✓ Backup created: {backup_file}")
    
    # Validate enriched dataset before writing (reuse schema loaded earlier)
    errors = list(validator.iter_errors(enriched_companies))
    if errors:
        logger.error(f"\n✗ Enriched data failed schema validation ({len(errors)} error(s)); aborting write")
        for err in errors[:50]:
            path = '.'.join(str(p) for p in err.path) or '<root>'
            logger.error(f"  - {path}: {err.message}")
        if len(errors) > 50:
            logger.error("  ... (additional errors truncated)")
        sys.exit(1)

    # Write output (only if validation passes)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enriched_companies, f, indent=2, ensure_ascii=False)

    logger.info(f"\n✓ Updated companies written to: {output_file}")
    logger.info(f"Total companies: {len(enriched_companies)}")
    logger.info("✓ Enriched dataset passed schema validation")
    
    sys.exit(0)


if __name__ == "__main__":
    main()
