#!/usr/bin/env python3

import json
import argparse
import sys
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Union
from urllib.parse import quote
import traceback
import webbrowser
import requests

class SaveAndExit(Exception):
    """Raised to exit the script early when user chooses to save and exit during URL review."""
    pass
from bs4 import BeautifulSoup

# Request rate limiting: delay between HTTP requests (seconds)
REQUEST_DELAY = 2.0


def search_fda_510k(robot_name: str):
    """Search FDA 510(k) database via official API for device clearance links."""
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
                        urls.append(('FDA 510k', fda_url))
                return urls
    except Exception as e:
        print(f'  [FDA API search skipped: {e}]', file=sys.stderr)
    return []


def search_fda_pma(robot_name: str):
    """Search FDA PMA database via OpenFDA API for approval links."""
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
                    urls.append(('FDA PMA', pma_url))
            if urls:
                return urls
    except Exception as e:
        print(f'  [FDA PMA search skipped: {e}]', file=sys.stderr)
    return []


def search_fda_denovo(robot_name: str):
    """Search FDA De Novo database via OpenFDA API for classification request links."""
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
                    urls.append(('FDA denovo', denovo_url))
            if urls:
                return urls
    except Exception as e:
        print(f'  [FDA De Novo search skipped: {e}]', file=sys.stderr)
    return []





def search_eu_eudamed(robot_name: str):
    """Search EU EUDAMED database for CE mark devices.
    
    Uses the EUDAMED public API endpoint that powers the official search interface.
    """
    try:
        # EUDAMED public API endpoint for device search
        # This is the endpoint used by the official EUDAMED UI
        api_url = 'https://ec.europa.eu/tools/eudamed/api/devices/udiDiData'
        
        params = {
            'page': 0,  # Page number (0-indexed)
            'size': 10,  # Results per page
            'search': robot_name  # Search query
        }
        
        response = requests.get(api_url, params=params, timeout=10)
        time.sleep(REQUEST_DELAY)
        
        if response.status_code == 200:
            data = response.json()
            urls = []
            
            # Results are in the 'content' key
            devices = data.get('content', [])
            
            if devices:
                for device in devices[:3]:  # Limit to top 3 results
                    # Extract device UUID for creating detail URL
                    device_uuid = device.get('uuid')
                    if device_uuid:
                        # Create URL to device detail page
                        eudamed_url = f'https://ec.europa.eu/tools/eudamed/#/screen/search-device/{device_uuid}'
                        urls.append(('CE Mark', eudamed_url))
                        
            return urls
    except Exception as e:
        print(f'  [EUDAMED search skipped: {e}]', file=sys.stderr)
    return []



class UrlReviewer:
    def __init__(self, rejected_path: str = 'public/rejected-regulatory.json', existing_data: list = None):
        self.rejected_path = Path(rejected_path)
        self.rejected_by_robot = {}  # dict[robot_id, set[urls]]
        self.approved_by_robot = {}  # dict[robot_id, set[urls]]
        self._load_rejected()
        if existing_data:
            self._load_existing(existing_data)

    def _load_rejected(self):
        if self.rejected_path.exists():
            try:
                data = json.loads(self.rejected_path.read_text())
                # New format: dict of robot_id -> list of urls
                for robot_id, urls in data.items():
                    self.rejected_by_robot[robot_id] = set(tuple(u) for u in urls)
            except Exception as e:
                print(f"Warning: Could not load rejected URLs: {e}", file=sys.stderr)

    def _load_existing(self, data: list):
        for robot in data:
            robot_id = robot.get('id')
            if not robot_id:
                continue
            if robot_id not in self.approved_by_robot:
                self.approved_by_robot[robot_id] = set()

            for entry in robot.get('regulatory', []):
                if isinstance(entry, dict):
                    url = entry.get('url')
                    if url:
                        self.approved_by_robot[robot_id].add(url)

    def _save_rejected(self):
        try:
            # Convert sets to sorted lists for JSON serialization
            output = {}
            for robot_id, urls in self.rejected_by_robot.items():
                if urls:  # Only save non-empty sets
                    output[robot_id] = sorted(list(urls))

            self.rejected_path.write_text(json.dumps(output, indent=2))
        except Exception as e:
            print(f"Error saving rejected URLs: {e}", file=sys.stderr)

    def review(self, urls: List[str], robot_id: str) -> tuple[List[str], bool]:
        """Review URLs and return (approved_urls, should_exit)."""
        approved = []
        for url in urls:
            if url[1] in self.approved_by_robot.get(robot_id, set()):
                print(f"  [previously approved] {url[1]}")
                approved.append(url)
                continue
            # Check if URL is rejected for this robot
            if url in self.rejected_by_robot.get(robot_id, set()):
                print(f"  [previously rejected] {url[1]}")
                continue

            # New URL, ask user
            print(f"\nReviewing URL: {url[1]} for robot {robot_id}")
            try:
                webbrowser.open(url[1])
            except Exception as e:
                print(f"  (Could not open browser: {e})")

            while True:
                choice = input("Approve this link? [y/n/s]: ").lower().strip()
                if choice == 's':
                    return (approved, True)  # Return approved URLs so far and exit flag
                elif choice in ('y', 'yes'):
                    if robot_id not in self.approved_by_robot:
                        self.approved_by_robot[robot_id] = set()
                    self.approved_by_robot[robot_id].add(url[1])
                    approved.append(url)
                    break
                elif choice in ('n', 'no'):
                    if robot_id not in self.rejected_by_robot:
                        self.rejected_by_robot[robot_id] = set()
                    self.rejected_by_robot[robot_id].add(url)
                    self._save_rejected()
                    break
        return (approved, False)


# Cache for companies mapping from robot id -> company name
COMPANIES_MAP = None

def load_companies_map(path: str = 'public/companies.json') -> dict:
    """Load companies.json and return a mapping of robot_id -> company_name."""
    global COMPANIES_MAP
    if COMPANIES_MAP is not None:
        return COMPANIES_MAP
    COMPANIES_MAP = {}
    try:
        p = Path(path)
        if not p.exists():
            return COMPANIES_MAP
        data = json.loads(p.read_text())
        for comp in data:
            name = comp.get('name')
            for rid in comp.get('robots', []) or []:
                if rid:
                    COMPANIES_MAP[rid] = name
    except Exception:
        # Non-fatal; just leave map empty
        COMPANIES_MAP = {}
    return COMPANIES_MAP


def find_company_for_robot(robot_id: str) -> str:
    if not robot_id:
        return ''
    m = load_companies_map()
    return m.get(robot_id, '')


def normalize_name(name: str) -> str:
    """Produce a simplified variant for broader query attempts."""
    if not name:
        return ''
    # Remove trademark symbols and punctuation except spaces
    cleaned = re.sub(r'[™®]', '', name)
    cleaned = re.sub(r'[,;:()\-]', ' ', cleaned)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned


def discover_regulatory_sources(robot_name: str, company_name: str):
    """Discover external regulatory sources for a robot and authority using official APIs and databases."""
    sources = []

    # Query official regulatory APIs
    sources.extend(search_fda_510k(robot_name))
    sources.extend(search_fda_pma(robot_name))
    sources.extend(search_fda_denovo(robot_name))
    sources.extend(search_eu_eudamed(robot_name))

    return sources


def update_robot_with_sources(robot: dict, reviewer: 'UrlReviewer') -> dict:
    # Enrich source_urls via external search
    robot_name = robot.get('name', '')
    robot_id = robot.get('id', '')
    if robot_id:
        company_name = find_company_for_robot(robot_id)

    # Collect all external sources for this robot across all regulatory entries
    all_external_sources = []
    seen_urls = set()

    # Search for primary name and aliases
    names_to_search = [robot_name]
    also_known_as = robot.get('also_known_as', [])
    if isinstance(also_known_as, list):
        names_to_search.extend(also_known_as)

    for name in names_to_search:
        if not name:
            continue
        print(f"  Searching for '{name}'...")
        sources = discover_regulatory_sources(name, company_name)
        for source in sources:
            # source is (body, url)
            if source[1] not in seen_urls:
                seen_urls.add(source[1])
                all_external_sources.append(source)

    # Review all collected external sources for this robot at once
    approved_sources, should_exit = reviewer.review(all_external_sources, robot_id)

    regulatory = robot.get('regulatory')
    for approved in approved_sources:
        # add approved source to regulatory
        regulatory.append({
            'url': approved[1],
            'body': approved[0]
        })

    return robot, should_exit


def main():
    parser = argparse.ArgumentParser(
        description='Update regulatory entries in robots.json incrementally.'
    )

    parser.add_argument(
        '--prefix',
        type=str,
        help='Process only robots whose IDs start with this prefix (case-insensitive)'
    )

    args = parser.parse_args()

    src_path = Path('public/robots.json')
    out_path = Path('public/robots.json')

    if not src_path.exists():
        print(f'Error: {src_path} not found.', file=sys.stderr)
        sys.exit(1)

    # Load source data
    full_data = json.loads(src_path.read_text())

    # Apply prefix filter if specified (for processing only)
    if args.prefix:
        prefix_lower = args.prefix.lower()
        original_count = len(full_data)
        data = [robot for robot in full_data if robot.get('id', '').lower().startswith(prefix_lower)]
        print(f"Processing {len(data)}/{original_count} robots with ID prefix '{args.prefix}'", file=sys.stderr)
    else:
        data = full_data

    # Initialize URL reviewer with existing data
    reviewer = UrlReviewer(existing_data=full_data)

    
    for i, robot in enumerate(data):
        robot_name = robot.get('name', f'robot_{i}')
        print(f"Updating {robot_name}")
        updated_robot, should_exit = update_robot_with_sources(
            robot,
            reviewer=reviewer
        )
        data[i] = updated_robot  # Update robot in the list
        if should_exit:
            break

    # Merge updated robots back into full dataset if prefix filter was used
    if args.prefix:
        # Create a map of updated robots by ID
        updated_by_id = {robot.get('id'): robot for robot in data}
        # Merge back into full dataset
        final_data = []
        for robot in full_data:
            robot_id = robot.get('id')
            if robot_id in updated_by_id:
                final_data.append(updated_by_id[robot_id])
            else:
                final_data.append(robot)
        data = final_data

    # Write output (after merging if prefix filter was used)
    out_path.write_text(json.dumps(data, indent=2))
    print(f'\nWrote {out_path}')

if __name__ == '__main__':
    main()
