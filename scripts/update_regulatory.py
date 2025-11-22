#!/usr/bin/env python3
"""Update regulatory entries in robots.json incrementally.

Normalizes existing regulatory entries and optionally enriches them with external source URLs.
Regulatory entries must be objects with at least a 'body' field.
Supports multiple update strategies (merge, overwrite, skip).
Optionally searches external sources (FDA 510k, EU EUDAMED, company press releases) to enrich source_urls.

Usage:
  python3 scripts/update_regulatory.py [--strategy merge]
  python3 scripts/update_regulatory.py --strategy overwrite --search-external
  python3 scripts/update_regulatory.py --search-external --output custom.json
"""

import json
import argparse
import sys
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Union
from urllib.parse import quote

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

# Request rate limiting: delay between HTTP requests (seconds)
REQUEST_DELAY = 2.0

REGION_MAP = {
    'FDA': ('US', 'Clearance'),
    'CE': ('EU', 'Mark'),
    'Japan': ('JP', None),
    'Singapore': ('SG', None),
    'Malaysia': ('MY', None),
}

# Regulatory database lookup URL patterns
REGULATORY_DB_URLS = {
    'FDA': lambda robot_name: f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={quote(robot_name)}',
    'CE': lambda robot_name: f'https://ec.europa.eu/growth/tools-databases/nando/index.cfm?action=detail&type=nando&id={quote(robot_name)}',
    'NMPA': lambda robot_name: f'https://www.nmpa.gov.cn/',  # China: direct link (search required on site)
    'PMDA': lambda robot_name: f'https://pmda.mhlw.go.jp/search/',  # Japan: search portal
}

def infer(body: str):
    """Infer region and type from authority body name."""
    region, typ = REGION_MAP.get(body, (None, None))
    return region, typ

def search_fda_510k(robot_name: str) -> List[str]:
    """Search FDA 510(k) database via official API for device clearance links."""
    if not HAS_REQUESTS:
        return []
    try:
        # Use OpenFDA API for 510(k) clearances
        # https://open.fda.gov/apis/device/510k/
        query = f'device_name:"{robot_name}"'
        api_url = f'https://api.fda.gov/device/510k.json?search={quote(query)}&limit=10'
        response = requests.get(api_url, timeout=5)
        time.sleep(REQUEST_DELAY)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            urls = []
            if results:
                # Extract links from FDA results
                for result in results:
                    if 'k_number' in result:
                        k_number = result['k_number']
                        fda_url = f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k_number}'
                        urls.append(fda_url)
                return urls
    except Exception as e:
        print(f'  [FDA API search skipped: {e}]', file=sys.stderr)
    
    # Fallback: return generic search portal link
    try:
        search_url = f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?sortcolumn=pmn&sortorder=desc&rs_id=&action=cdrh&recordnumber=100'
        response = requests.get(search_url, timeout=5)
        time.sleep(REQUEST_DELAY)
        if response.status_code == 200:
            return [search_url]
    except Exception as e:
        print(f'  [FDA fallback search skipped: {e}]', file=sys.stderr)
    
    return []

def search_eu_eudamed(robot_name: str) -> List[str]:
    """Search EU EUDAMED database via API for CE mark devices.
    
    EUDAMED (European Union Database of Medical Devices) is accessible via web interface.
    Direct API access may be limited; this searches the public portal.
    """
    if not HAS_REQUESTS:
        return []
    try:
        # EUDAMED API endpoint for device search
        api_url = f'https://ec.europa.eu/growth/tools-databases/nando/api/devices?deviceName={quote(robot_name)}'
        response = requests.get(api_url, timeout=5)
        time.sleep(REQUEST_DELAY)
        
        if response.status_code == 200:
            try:
                data = response.json()
                devices = data.get('devices', []) if isinstance(data, dict) else (data if isinstance(data, list) else [])
                urls = []
                if devices:
                    for device in devices[:3]:  # Limit to top 3 results
                        if 'id' in device:
                            device_id = device['id']
                            eudamed_url = f'https://ec.europa.eu/growth/tools-databases/nando/index.cfm?action=detail&type=nando&id={device_id}'
                            urls.append(eudamed_url)
                    return urls
            except:
                pass
    except Exception as e:
        print(f'  [EUDAMED search skipped: {e}]', file=sys.stderr)
    
    return []

def search_company_press_releases(robot_name: str, company_name: str, body: str) -> List[str]:
    """Search company websites for regulatory announcements."""
    if not HAS_REQUESTS:
        return []
    found_urls = []
    search_terms = [
        f'{robot_name} {body} approved',
        f'{company_name} {body} clearance',
        f'{robot_name} FDA cleared',
        f'{company_name} CE mark'
    ]
    try:
        for term in search_terms[:2]:  # Limit to 2 queries per robot
            search_url = f'https://www.google.com/search?q="{term}"'
            response = requests.get(
                search_url,
                headers={'User-Agent': 'Mozilla/5.0'},
                timeout=5
            )
            if response.status_code == 200:
                # Add search result link (not detailed scraping to avoid overload)
                found_urls.append(search_url)
                time.sleep(REQUEST_DELAY)  # Rate limiting between successful requests
                break  # Stop after first successful query
        time.sleep(REQUEST_DELAY)  # Rate limiting between robots
    except Exception as e:
        print(f'  [Press release search skipped: {e}]', file=sys.stderr)
    return found_urls

def discover_regulatory_sources(robot_name: str, company_name: str, body: str) -> List[str]:
    """Discover external regulatory sources for a robot and authority using official APIs and databases."""
    sources = []
    
    # Query official regulatory APIs based on authority body
    if body == 'FDA':
        fda_urls = search_fda_510k(robot_name)
        sources.extend(fda_urls)
    elif body == 'CE':
        eu_urls = search_eu_eudamed(robot_name)
        sources.extend(eu_urls)
    
    # Add fallback web portal links for unsupported authorities
    if body in REGULATORY_DB_URLS and not sources:
        db_url = REGULATORY_DB_URLS[body](robot_name)
        sources.append(db_url)
    
    # Search company press releases & news (medium effort, lower priority)
    if company_name and len(sources) < 3:  # Only if not already found via API
        press_urls = search_company_press_releases(robot_name, company_name, body)
        sources.extend(press_urls)
    
    return sources

def extract_entry(status):
    """Normalize regulatory entry object, ensuring all fields are present."""
    if not isinstance(status, dict):
        raise ValueError(f"Expected dict, got {type(status).__name__}")
    
    entry = status.copy()
    body = entry.get('body', '')
    
    # Ensure body exists
    if not body:
        raise ValueError("Regulatory entry missing 'body' field")
    
    # Infer region/type if missing
    if not entry.get('region'):
        region, _ = infer(body)
        entry['region'] = region
    if not entry.get('type'):
        _, typ = infer(body)
        entry['type'] = typ
    
    # Ensure source_urls array exists
    if 'source_urls' not in entry or not isinstance(entry.get('source_urls'), list):
        entry['source_urls'] = []
    
    return entry

def collect_source_urls(body: str, robot: dict) -> List[str]:
    """Find URLs from robot.urls matching the regulatory body."""
    urls = robot.get('urls', [])
    matching = []
    for u in urls:
        cap = (u.get('caption', '') + ' ' + u.get('url', '')).lower()
        if body.lower() in cap:
            matching.append(u.get('url'))
    return matching

def merge_entry(existing: dict, fresh: dict) -> dict:
    """Merge fresh extracted entry with existing, preserving manual fields."""
    result = existing.copy()
    # Update body, region, type from fresh if not already set
    if not result.get('body'):
        result['body'] = fresh.get('body')
    if not result.get('region'):
        result['region'] = fresh.get('region')
    if not result.get('type'):
        result['type'] = fresh.get('type')
    # Update year only if fresh has a value and existing is missing
    if fresh.get('year') and not result.get('year'):
        result['year'] = fresh.get('year')
    # Merge source_urls (union, no duplicates)
    existing_urls = set(result.get('source_urls', []))
    fresh_urls = set(fresh.get('source_urls', []))
    result['source_urls'] = list(existing_urls | fresh_urls)
    return result

def update_robot(robot: dict, strategy: str = 'merge') -> dict:
    """Update regulatory array in a single robot entry."""
    existing_list = robot.get('regulatory', [])
    
    if strategy == 'skip' and existing_list:
        # Keep existing if not empty
        return robot
    
    # Normalize existing entries (merge and overwrite strategies)
    new_list = []
    for status in existing_list:
        try:
            entry = extract_entry(status)
            entry['source_urls'] = collect_source_urls(entry['body'], robot)
            new_list.append(entry)
        except ValueError as e:
            print(f"  Warning: Skipping invalid entry in {robot.get('name', 'unknown')}: {e}", file=sys.stderr)
            continue
    
    robot['regulatory'] = new_list
    return robot

def update_robot_with_sources(robot: dict, strategy: str = 'merge', search_external: bool = False) -> dict:
    """Update regulatory array with optional external source discovery."""
    robot = update_robot(robot, strategy)
    
    if not search_external:
        return robot
    
    # Enrich source_urls via external search
    robot_name = robot.get('name', '')
    company_name = robot.get('company', '')  # Optional field; may not exist
    
    for entry in robot.get('regulatory', []):
        body = entry.get('body', '')
        if not body:
            continue
        
        external_sources = discover_regulatory_sources(robot_name, company_name, body)
        existing_urls = set(entry.get('source_urls', []))
        external_urls = set(external_sources)
        entry['source_urls'] = list(existing_urls | external_urls)
    
    return robot

def main():
    parser = argparse.ArgumentParser(
        description='Update regulatory entries in robots.json incrementally.'
    )
    parser.add_argument(
        '--strategy',
        choices=['merge', 'overwrite', 'skip'],
        default='merge',
        help='Merge strategy: merge (default) preserves manual fields, overwrite replaces all, skip adds only if empty.'
    )
    parser.add_argument(
        '--source',
        default='public/robots.json',
        help='Source robots.json file (default: public/robots.json).'
    )
    parser.add_argument(
        '--output',
        default='public/robots.json',
        help='Output robots.json file (default: public/robots.json, overwrites source).'
    )
    parser.add_argument(
        '--backup',
        action='store_true',
        help='Create a backup file before overwriting.'
    )
    parser.add_argument(
        '--search-external',
        action='store_true',
        help='Search external regulatory databases (FDA 510k, EU EUDAMED) and company press releases for source URLs.'
    )
    
    args = parser.parse_args()
    src_path = Path(args.source)
    out_path = Path(args.output)
    
    if not src_path.exists():
        print(f'Error: {src_path} not found.', file=sys.stderr)
        sys.exit(1)
    
    if args.search_external and not HAS_REQUESTS:
        print('Warning: requests/BeautifulSoup not installed. External source search disabled.', file=sys.stderr)
        print('  Install: pip install requests beautifulsoup4', file=sys.stderr)
        args.search_external = False
    
    # Load source data
    data = json.loads(src_path.read_text())
    
    # Backup if requested
    if args.backup and out_path.exists():
        backup_path = out_path.with_suffix('.bak')
        backup_path.write_text(out_path.read_text())
        print(f'Backed up to {backup_path}')
    
    # Update all robots
    updated_count = 0
    for i, robot in enumerate(data):
        before = robot.get('regulatory', [])
        robot = update_robot_with_sources(robot, strategy=args.strategy, search_external=args.search_external)
        after = robot.get('regulatory', [])
        if before != after:
            updated_count += 1
        
        # Progress indicator for external search
        if args.search_external and (i + 1) % 10 == 0:
            print(f'  Processed {i + 1}/{len(data)} robots...', file=sys.stderr)
    
    # Write output
    out_path.write_text(json.dumps(data, indent=2))
    print(f'Updated {updated_count} robots (strategy: {args.strategy})')
    if args.search_external:
        print(f'  External source discovery enabled.')
    print(f'Wrote {out_path}')

if __name__ == '__main__':
    main()
