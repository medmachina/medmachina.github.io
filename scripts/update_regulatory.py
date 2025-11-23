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
TODAY = time.strftime('%Y-%m-%d')

REGION_MAP = {
    'FDA': ('US', 'Clearance'),
    'CE': ('EU', 'Mark'),
    'Japan': ('JP', None),
    'Singapore': ('SG', None),
    'Malaysia': ('MY', None),
    'TGA': ('AU', 'Register'),
    'PMDA': ('JP', 'Approval'),
    'NMPA': ('CN', 'Registration'),
    'ANVISA': ('BR', 'Registration'),
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

def search_fda_pma(robot_name: str) -> List[str]:
    """Search FDA PMA database via OpenFDA API for approval links."""
    if not HAS_REQUESTS:
        return []
    try:
        # https://open.fda.gov/apis/device/pma/
        query = f'device_name:"{robot_name}"'
        api_url = f'https://api.fda.gov/device/pma.json?search={quote(query)}&limit=10'
        response = requests.get(api_url, timeout=5)
        time.sleep(REQUEST_DELAY)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            urls = []
            for result in results:
                # PMA numbers appear as pma_number
                pma_number = result.get('pma_number') or result.get('supplement_number')
                if pma_number:
                    # There is no direct detail page pattern like 510k; link generic search portal
                    # Provide a search URL including PMA number for manual verification
                    pma_url = f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma_number}'
                    urls.append(pma_url)
            if urls:
                return urls
    except Exception as e:
        print(f'  [FDA PMA search skipped: {e}]', file=sys.stderr)
    return []

def search_fda_denovo(robot_name: str) -> List[str]:
    """Search FDA De Novo database via OpenFDA API for classification request links."""
    if not HAS_REQUESTS:
        return []
    try:
        # https://open.fda.gov/apis/device/denovo/
        query = f'device_name:"{robot_name}"'
        api_url = f'https://api.fda.gov/device/denovo.json?search={quote(query)}&limit=10'
        response = requests.get(api_url, timeout=5)
        time.sleep(REQUEST_DELAY)
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            urls = []
            for result in results:
                docket_number = result.get('docket_number') or result.get('denovo_number')
                if docket_number:
                    denovo_url = f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/denovo.cfm?denovo={docket_number}'
                    urls.append(denovo_url)
            if urls:
                return urls
    except Exception as e:
        print(f'  [FDA De Novo search skipped: {e}]', file=sys.stderr)
    return []


def _simple_domain_search(base_portal: str, domain: str, robot_name: str, company_name: str, extra: str = '') -> List[str]:
    if not HAS_REQUESTS:
        return []
    urls: List[str] = [base_portal]
    norm_robot = normalize_name(robot_name)
    norm_company = normalize_name(company_name)
    term = norm_robot or norm_company
    if term:
        query_phrase = f'"{term}" site:{domain}' + (f' {extra}' if extra else '')
        google_q = quote(query_phrase)
        urls.append(f'https://www.google.com/search?q={google_q}')
    # Deduplicate
    dedup: List[str] = []
    seen = set()
    for u in urls:
        if u not in seen:
            seen.add(u)
            dedup.append(u)
    return dedup

def search_tga_artg(robot_name: str, company_name: str) -> List[str]:
    """Heuristic collection of Australian TGA ARTG references.

    Provides base ARTG resource page and a site-limited Google query for robot/company.
    """
    return _simple_domain_search('https://www.tga.gov.au/resources/artg', 'tga.gov.au', robot_name, company_name, extra='artg')

def search_pmda(robot_name: str, company_name: str) -> List[str]:
    return _simple_domain_search('https://pmda.mhlw.go.jp/search/', 'pmda.mhlw.go.jp', robot_name, company_name)

def search_nmpa(robot_name: str, company_name: str) -> List[str]:
    return _simple_domain_search('https://www.nmpa.gov.cn/', 'nmpa.gov.cn', robot_name, company_name)

def search_anvisa(robot_name: str, company_name: str) -> List[str]:
    return _simple_domain_search('https://www.gov.br/anvisa/pt-br', 'anvisa.gov.br', robot_name, company_name, extra='dispositivo')

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

def normalize_name(name: str) -> str:
    """Produce a simplified variant for broader query attempts."""
    if not name:
        return ''
    # Remove trademark symbols and punctuation except spaces
    cleaned = re.sub(r'[™®]', '', name)
    cleaned = re.sub(r'[,;:()\-]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

def search_fda_endpoint(endpoint: str, robot_name: str, company_name: str) -> List[str]:
    """Generic broadened search across device_name and applicant with variants.

    endpoint: one of '510k', 'pma', 'denovo'
    Returns list of detail or portal URLs.
    """
    if not HAS_REQUESTS:
        return []
    base = f'https://api.fda.gov/device/{endpoint}.json'
    variants = []
    norm_robot = normalize_name(robot_name)
    if norm_robot:
        variants.append(f'device_name:"{norm_robot}"')
        # wildcard attempt on first token if multi-word
        first_token = norm_robot.split()[0]
        if len(first_token) > 3:
            variants.append(f'device_name:"{first_token}*"')
    norm_company = normalize_name(company_name)
    if norm_company:
        # restrict applicant/company queries to avoid overbroad results
        variants.append(f'applicant:"{norm_company}"')
    # Deduplicate while preserving order
    seen = set()
    ordered_variants = []
    for v in variants:
        if v not in seen:
            seen.add(v)
            ordered_variants.append(v)

    collected: List[dict] = []
    for v in ordered_variants:
        query = quote(v)
        url = f'{base}?search={query}&limit=20'
        try:
            resp = requests.get(url, timeout=6)
            time.sleep(REQUEST_DELAY)
            if resp.status_code == 200:
                js = resp.json()
                results = js.get('results', [])
                if results:
                    collected.extend(results)
                    # Stop early if we got enough hits (avoid noise)
                    if len(collected) >= 10:
                        break
        except Exception as e:
            print(f'  [FDA {endpoint} broadened search skipped variant {v}: {e}]', file=sys.stderr)
            continue

    urls: List[str] = []
    for result in collected:
        if endpoint == '510k':
            k_number = result.get('k_number')
            if k_number:
                urls.append(f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={k_number}')
        elif endpoint == 'pma':
            pma_number = result.get('pma_number') or result.get('supplement_number')
            if pma_number:
                urls.append(f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={pma_number}')
        elif endpoint == 'denovo':
            docket_number = result.get('docket_number') or result.get('denovo_number')
            if docket_number:
                urls.append(f'https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/denovo.cfm?denovo={docket_number}')

    # Fallback generic portal search if nothing found
    if not urls and endpoint == '510k':
        urls.append('https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm')
    if not urls and endpoint == 'pma':
        urls.append('https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm')
    if not urls and endpoint == 'denovo':
        urls.append('https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/denovo.cfm')

    # Deduplicate final URL list
    final_urls = []
    seen_u = set()
    for u in urls:
        if u not in seen_u:
            seen_u.add(u)
            final_urls.append(u)
    return final_urls

def discover_regulatory_sources(robot_name: str, company_name: str, body: str) -> List[str]:
    """Discover external regulatory sources for a robot and authority using official APIs and databases."""
    sources = []
    
    # Query official regulatory APIs based on authority body
    if body == 'FDA':
        # Broadened queries via unified endpoint searches
        aggregate = []
        for ep in ('510k', 'pma', 'denovo'):
            ep_urls = search_fda_endpoint(ep, robot_name, company_name)
            for u in ep_urls:
                if u not in aggregate:
                    aggregate.append(u)
        sources.extend(aggregate)
    elif body == 'CE':
        eu_urls = search_eu_eudamed(robot_name)
        sources.extend(eu_urls)
    elif body == 'TGA':
        tga_urls = search_tga_artg(robot_name, company_name)
        sources.extend(tga_urls)
    elif body == 'PMDA':
        pmda_urls = search_pmda(robot_name, company_name)
        sources.extend(pmda_urls)
    elif body == 'NMPA':
        nmpa_urls = search_nmpa(robot_name, company_name)
        sources.extend(nmpa_urls)
    elif body == 'ANVISA':
        anvisa_urls = search_anvisa(robot_name, company_name)
        sources.extend(anvisa_urls)
    
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
    result['source_urls'] = sorted(existing_urls | fresh_urls)
    # Update last_verified if sources changed
    if set(result.get('source_urls', [])) != set(existing_urls):
        result['last_verified'] = TODAY
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
            # Preserve any existing source_urls and union with newly collected ones
            existing_urls = set(entry.get('source_urls', []) or [])
            collected_urls = set(collect_source_urls(entry['body'], robot))
            combined = existing_urls | collected_urls
            entry['source_urls'] = sorted(combined)
            if combined and (set(entry.get('source_urls', [])) != existing_urls or not entry.get('last_verified')):
                entry['last_verified'] = TODAY
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
        entry['source_urls'] = sorted(existing_urls | external_urls)
        if external_urls and (external_urls - existing_urls or not entry.get('last_verified')):
            entry['last_verified'] = TODAY

    existing_bodies = {e.get('body') for e in robot.get('regulatory', []) if isinstance(e, dict)}
    if 'TGA' not in existing_bodies and ('FDA' in existing_bodies or 'CE' in existing_bodies):
        tga_sources = search_tga_artg(robot_name, company_name)
        if tga_sources:
            robot.setdefault('regulatory', []).append({
                'body': 'TGA',
                'region': 'AU',
                'type': 'Register',
                'year': None,
                'source_urls': sorted(set(tga_sources)),
                'last_verified': TODAY
            })
    # Auto-add PMDA / NMPA / ANVISA under same condition
    if ('FDA' in existing_bodies or 'CE' in existing_bodies):
        if 'PMDA' not in existing_bodies:
            pmda_sources = search_pmda(robot_name, company_name)
            if pmda_sources:
                robot.setdefault('regulatory', []).append({
                    'body': 'PMDA',
                    'region': 'JP',
                    'type': 'Approval',
                    'year': None,
                    'source_urls': sorted(set(pmda_sources)),
                    'last_verified': TODAY
                })
        if 'NMPA' not in existing_bodies:
            nmpa_sources = search_nmpa(robot_name, company_name)
            if nmpa_sources:
                robot.setdefault('regulatory', []).append({
                    'body': 'NMPA',
                    'region': 'CN',
                    'type': 'Registration',
                    'year': None,
                    'source_urls': sorted(set(nmpa_sources)),
                    'last_verified': TODAY
                })
        if 'ANVISA' not in existing_bodies:
            anvisa_sources = search_anvisa(robot_name, company_name)
            if anvisa_sources:
                robot.setdefault('regulatory', []).append({
                    'body': 'ANVISA',
                    'region': 'BR',
                    'type': 'Registration',
                    'year': None,
                    'source_urls': sorted(set(anvisa_sources)),
                    'last_verified': TODAY
                })
    
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
    
    # Helper for diffing entries
    def entry_key(e: dict) -> tuple:
        return (
            e.get('body'),
            e.get('year'),
            e.get('region'),
            e.get('type'),
            tuple(sorted(e.get('source_urls', []))),
            e.get('last_verified')
        )

    updated_count = 0
    unchanged_count = 0
    added_entries_details: List[tuple] = []  # (robot_name, body)
    removed_entries_details: List[tuple] = []  # (robot_name, body)
    added_urls_details: List[tuple] = []  # (robot_name, body, url)

    for i, robot in enumerate(data):
        robot_name = robot.get('name', f'robot_{i}')
        before_list = robot.get('regulatory', []) or []
        # Snapshot for URL diffing by body
        before_by_body = { (e.get('body') or f'body_{idx}'): e for idx, e in enumerate(before_list) if isinstance(e, dict) }

        robot = update_robot_with_sources(robot, strategy=args.strategy, search_external=args.search_external)
        after_list = robot.get('regulatory', []) or []
        after_by_body = { (e.get('body') or f'body_{idx}'): e for idx, e in enumerate(after_list) if isinstance(e, dict) }

        before_keys = { entry_key(e) for e in before_list if isinstance(e, dict) }
        after_keys = { entry_key(e) for e in after_list if isinstance(e, dict) }

        # Added / removed whole entries
        added_entries = [e for e in after_list if isinstance(e, dict) and entry_key(e) not in before_keys]
        removed_entries = [e for e in before_list if isinstance(e, dict) and entry_key(e) not in after_keys]

        # Added URLs inside existing bodies
        intersect_bodies = set(before_by_body.keys()) & set(after_by_body.keys())
        new_urls_this_robot = []
        for body in intersect_bodies:
            b_urls = set(before_by_body[body].get('source_urls', []) or [])
            a_urls = set(after_by_body[body].get('source_urls', []) or [])
            new_urls = a_urls - b_urls
            for u in sorted(new_urls):
                added_urls_details.append((robot_name, body, u))
                new_urls_this_robot.append(u)

        # Determine if this robot changed (new entry, removed entry, or new URLs within existing entry)
        if added_entries or removed_entries or new_urls_this_robot:
            updated_count += 1
            for e in added_entries:
                added_entries_details.append((robot_name, e.get('body')))
            for e in removed_entries:
                removed_entries_details.append((robot_name, e.get('body')))
        else:
            unchanged_count += 1

        # Progress indicator for external search
        if args.search_external and (i + 1) % 10 == 0:
            print(f'  Processed {i + 1}/{len(data)} robots...', file=sys.stderr)
    
    # Write output
    out_path.write_text(json.dumps(data, indent=2))
    total_robots = len(data)
    print(f'Updated {updated_count} robots; unchanged {unchanged_count} (strategy: {args.strategy})')
    if args.search_external:
        print('External source discovery enabled.')

    # Aggregate stats
    print('\nRegulatory diff summary:')
    print(f'  Total robots processed: {total_robots}')
    print(f'  Robots updated: {updated_count}')
    print(f'  Robots unchanged: {unchanged_count}')
    print(f'  Added entries: {len(added_entries_details)}')
    print(f'  Removed entries: {len(removed_entries_details)}')
    print(f'  New source URLs added within existing entries: {len(added_urls_details)}')

    # Detail samples (limit to avoid excessive output)
    def sample(lst: List[tuple], limit: int = 15):
        return lst[:limit], max(0, len(lst) - limit)

    added_sample, added_remaining = sample(added_entries_details)
    removed_sample, removed_remaining = sample(removed_entries_details)
    url_sample, url_remaining = sample(added_urls_details)

    if added_sample:
        print('\n  Added Entries (sample):')
        for robot_name, body in added_sample:
            print(f'    + {robot_name}: {body}')
        if added_remaining:
            print(f'    ... {added_remaining} more')
    if removed_sample:
        print('\n  Removed Entries (sample):')
        for robot_name, body in removed_sample:
            print(f'    - {robot_name}: {body}')
        if removed_remaining:
            print(f'    ... {removed_remaining} more')
    if url_sample:
        print('\n  Added Source URLs (sample):')
        for robot_name, body, url in url_sample:
            print(f'    * {robot_name} [{body}]: {url}')
        if url_remaining:
            print(f'    ... {url_remaining} more')

    print(f'\nWrote {out_path}')

if __name__ == '__main__':
    main()
