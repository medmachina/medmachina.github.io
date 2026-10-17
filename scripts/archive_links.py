#!/usr/bin/env python3
"""
Archive Links Utility for MedMachina

This script verifies URL accessibility for robots and companies in MedMachina,
finds historical Wayback Machine snapshots via the CDX API, and writes canonical
`archive_url` fields back to the dataset JSON files so documentation and reference
links remain preserved indefinitely even if target websites go offline.
"""

import warnings
warnings.filterwarnings("ignore")

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path
from urllib.parse import urlparse
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
ROBOTS_DIR = REPO_ROOT / 'public' / 'robots'
COMPANIES_DIR = REPO_ROOT / 'public' / 'companies'

USER_AGENT = 'MedMachina/1.0 (+https://medmachina.github.io)'
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}


def is_live_url(url: str, timeout: int = 6) -> bool:
    """Check if a URL is currently reachable.
    401/403/429 indicate the server is online but challenging automated clients.
    Only 404, 410, DNS resolution failures, or connection errors mean the resource is offline.
    """
    if not url or not url.startswith(('http://', 'https://')):
        return False
    try:
        resp = requests.head(url, headers=REQUEST_HEADERS, timeout=timeout, allow_redirects=True)
        # Any 2xx, 3xx, 401, 403, 429 means server is up
        if resp.status_code < 400 or resp.status_code in (401, 403, 406, 429):
            return True
        if resp.status_code in (404, 410):
            return False
        # For other status codes, attempt GET with stream=True
        resp = requests.get(url, headers=REQUEST_HEADERS, timeout=timeout, stream=True, allow_redirects=True)
        return resp.status_code < 400 or resp.status_code in (401, 403, 406, 429)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        return False
    except Exception:
        return False


def get_latest_wayback_snapshot(target_url: str, timeout: int = 10) -> str:
    """Look up the most recent successful HTTP 200 snapshot on the Wayback Machine."""
    clean_target = target_url.strip()
    # Strip protocol for CDX query matching
    match = re.sub(r'^https?://', '', clean_target).rstrip('/')
    cdx_url = (
        f"https://web.archive.org/cdx/search/cdx?"
        f"url={match}&filter=statuscode:200&output=json&limit=-1&fastLatest=true"
    )
    try:
        resp = requests.get(cdx_url, headers=REQUEST_HEADERS, timeout=timeout)
        if resp.status_code == 200:
            data = resp.json()
            if len(data) > 1:
                row = data[1]
                timestamp = row[1]
                original = row[2]
                return f"https://web.archive.org/web/{timestamp}/{original}"
    except Exception as e:
        logger.debug(f"CDX lookup failed for {target_url}: {e}")
    return None


def request_wayback_save(target_url: str, timeout: int = 15) -> bool:
    """Request the Wayback Machine to save a live webpage snapshot."""
    save_url = f"https://web.archive.org/save/{target_url}"
    try:
        resp = requests.get(save_url, headers=REQUEST_HEADERS, timeout=timeout)
        return resp.status_code in (200, 302)
    except Exception as e:
        logger.debug(f"Wayback save failed for {target_url}: {e}")
        return False


def process_entry_urls(filepath: Path, data: dict, apply: bool, check_dead: bool, save_live: bool):
    """Scan and process urls and photos in a robot or company file."""
    modified = False
    name = data.get('name', filepath.stem)

    # 1. Process 'urls' list
    urls_list = data.get('urls', [])
    for entry in urls_list:
        if not isinstance(entry, dict):
            continue
        original_url = entry.get('url')
        if not original_url:
            continue

        # If already an archive link in 'url', normalize into url + archive_url
        if 'web.archive.org/web/' in original_url and not entry.get('archive_url'):
            m = re.search(r'https?://web\.archive\.org/web/[^/]+/(https?://.+)$', original_url)
            if m:
                canonical = m.group(1)
                logger.info(f"[{name}] Normalizing legacy archive link: {original_url} -> {canonical}")
                entry['archive_url'] = original_url
                entry['url'] = canonical
                modified = True
                continue

        # Check live status
        has_archive = bool(entry.get('archive_url'))
        if not has_archive:
            live = is_live_url(original_url)
            if not live:
                logger.info(f"[{name}] URL offline: {original_url}")
                snapshot = get_latest_wayback_snapshot(original_url)
                if snapshot:
                    logger.info(f"  ✓ Found archive snapshot: {snapshot}")
                    if apply:
                        entry['archive_url'] = snapshot
                        modified = True
                else:
                    logger.warning(f"  ✗ No archive snapshot found for {original_url}")
            elif save_live:
                logger.info(f"[{name}] Requesting archive capture for live URL: {original_url}")
                ok = request_wayback_save(original_url)
                if ok:
                    logger.info(f"  ✓ Saved to Wayback Machine")
                time.sleep(1)

    # 2. Process 'photos' list (for robots)
    photos_list = data.get('photos', [])
    for photo in photos_list:
        if not isinstance(photo, dict):
            continue
        photo_url = photo.get('url')
        site_url = photo.get('site')
        if not photo.get('archive_url') and photo_url:
            # Check if photo is dead
            if not is_live_url(photo_url):
                logger.info(f"[{name}] Photo offline: {photo_url}")
                snapshot = get_latest_wayback_snapshot(photo_url)
                if snapshot:
                    logger.info(f"  ✓ Found archive photo snapshot: {snapshot}")
                    if apply:
                        photo['archive_url'] = snapshot
                        modified = True

    if modified and apply:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        logger.info(f"Updated {filepath.name}")

    return modified


def main():
    parser = argparse.ArgumentParser(description="Find and manage archived snapshots for MedMachina URLs.")
    parser.add_argument('--apply', action='store_true', help="Write discovered archive_url fields back to JSON files.")
    parser.add_argument('--save-live', action='store_true', help="Ask Wayback Machine to archive currently active URLs.")
    parser.add_argument('--robot', type=str, help="Process only a specific robot ID.")
    parser.add_argument('--company', type=str, help="Process only a specific company ID.")
    args = parser.parse_args()

    # Process Robots
    if not args.company or args.robot:
        robot_files = sorted(ROBOTS_DIR.glob('*.json'))
        if args.robot:
            robot_files = [f for f in robot_files if f.stem == args.robot]

        logger.info(f"Processing {len(robot_files)} robot files...")
        for rf in robot_files:
            try:
                with open(rf, 'r', encoding='utf-8') as f:
                    rdata = json.load(f)
                process_entry_urls(rf, rdata, apply=args.apply, check_dead=True, save_live=args.save_live)
            except Exception as e:
                logger.error(f"Error reading {rf}: {e}")

    # Process Companies
    if not args.robot or args.company:
        company_files = sorted(COMPANIES_DIR.glob('*.json'))
        if args.company:
            company_files = [f for f in company_files if f.stem == args.company]

        logger.info(f"Processing {len(company_files)} company files...")
        for cf in company_files:
            try:
                with open(cf, 'r', encoding='utf-8') as f:
                    cdata = json.load(f)
                process_entry_urls(cf, cdata, apply=args.apply, check_dead=True, save_live=args.save_live)
            except Exception as e:
                logger.error(f"Error reading {cf}: {e}")

    logger.info("Archive processing finished.")


if __name__ == '__main__':
    main()
