#!/usr/bin/env python3
"""
Download and match EUDAMED (European medical device database) data using the official API.
Replaces the old browser automation approach with direct API calls for better reliability.
"""
import json
import argparse
import re
import requests
import time
from typing import List, Dict, Any, Optional

# Official EUDAMED API URL
EUDAMED_API_URL = "https://ec.europa.eu/tools/eudamed/api/devices/udiDiData"

# Search terms for robotic surgical devices
ROBOT_SEARCH_TERMS = [
    "da vinci",
    "hugo",
    "versius",
    "senhance",
    "mako",
    "rosa",
    "monarch",
    "ion",
    "symani",
    "hinotori",
    "cyberknife",
    "zapping"
]

def load_robots_json(path: str = "public/robots.json"):
    with open(path, 'r') as f:
        return json.load(f)

def load_companies_json(path: str = "public/companies.json"):
    with open(path, 'r') as f:
        return json.load(f)

def load_regulatory_json(path: str = "public/regulatory.json"):
    """Load regulatory data from regulatory.json."""
    import os
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_regulatory_json(data: dict, path: str = "public/regulatory.json"):
    """Save regulatory data to regulatory.json."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def search_beudamed_scraping(search_term: str, max_pages: int = 3) -> List[Dict[str, Any]]:
    """
    Search BEUDAMED by scraping the search results page.
    """
    from bs4 import BeautifulSoup
    devices = []
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
    }
    
    for page in range(1, max_pages + 1):
        try:
            url = f"https://beudamed.com/search?search%5Bquery%5D={search_term.replace(' ', '+')}&page={page}"
            print(f"  Scraping: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"    Error: Received status code {response.status_code}")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all result cards (<a> tags with group block classes)
            cards = soup.select('a.group.block')
            if not cards:
                print("    No more results found.")
                break
                
            print(f"    Found {len(cards)} results on page {page}")
            
            for card in cards:
                try:
                    # Extract trade name
                    trade_name_elem = card.select_one('p.font-bold')
                    trade_name = trade_name_elem.text.strip() if trade_name_elem else ""
                    
                    # Extract result type (Device, FDA registration, etc.)
                    # Type is usually in the second child div
                    type_elem = card.select_one('div:nth-child(2) p')
                    result_type = type_elem.text.strip() if type_elem else ""
                    
                    # Skip if it's an FDA entry (as requested)
                    if "FDA" in result_type.upper() or "FDA" in trade_name.upper():
                        continue
                        
                    # Extract manufacturer
                    # Manufacturer is usually in the metadata row (third child div)
                    meta_row = card.select_one('div.mt-2.text-xs.flex.flex-wrap, div.mt-2.flex.flex-wrap')
                    manufacturer = ""
                    if meta_row:
                        # Manufacturer is often a span or a div without specific classes, but it's usually the first or second item
                        items = meta_row.find_all(['div', 'span'], recursive=False)
                        # More specific lookup: sometimes it's explicitly marked or just a text item
                        for item in items:
                            text = item.text.strip()
                            if text and text not in ["EU MDR", "EU IVDR", "On the market", "Not on the market", "Missing data"]:
                                # Heuristic: if it doesn't look like a status or class, it's probably the manufacturer
                                if not any(c.isdigit() for c in text): # Risk classes usually have digits like 2b
                                    manufacturer = text
                                    break
                    
                    # Store device info
                    href = card.get('href', '')
                    if href:
                        devices.append({
                            "trade_name": trade_name,
                            "manufacturer": manufacturer,
                            "url": f"https://beudamed.com{href}" if href.startswith('/') else href,
                            "type": result_type
                        })
                except Exception as e:
                    continue
                    
        except Exception as e:
            print(f"    Error during scraping: {e}")
            break
            
    return devices

def is_relevant_match(search_names: List[str], device_data: Dict, company_name: Optional[str], excludes: List[str] = []) -> Optional[str]:
    """
    Determine if a EUDAMED device is a relevant match for a robot.
    """
    trade_name = device_data.get('trade_name', '').lower()
    manufacturer = device_data.get('manufacturer', '').lower()
    
    # Clean names
    trade_name_clean = re.sub(r'[^\w\s]', ' ', trade_name)
    trade_name_clean = ' '.join(trade_name_clean.split())
    
    # Check exclusions
    for ex in excludes:
        if ex.lower() in trade_name_clean:
            return None
    
    # Name match check with word boundaries
    best_matching_string = None
    for sn in search_names:
        sn_clean = sn.lower().strip()
        if not sn_clean: continue
        sn_clean = re.sub(r'[^\w\s]', ' ', sn_clean)
        sn_clean = ' '.join(sn_clean.split())
        
        # Exact word match
        pattern = r'\b' + re.escape(sn_clean) + r'\b'
        if re.search(pattern, trade_name_clean):
            if not best_matching_string or len(sn_clean) > len(best_matching_string):
                best_matching_string = sn_clean
    
    if not best_matching_string:
        return None
    
    # Company match check
    if company_name and manufacturer:
        company_clean = company_name.lower().strip()
        company_words = company_clean.split()
        first_word = company_words[0] if company_words else company_clean
        
        if company_clean in manufacturer or (len(first_word) > 3 and first_word in manufacturer):
            return best_matching_string
            
        # Check subsidiary map
        subsidiary_map = {
            "johnson & johnson": ["auris", "ethicon", "verb", "monarch", "depuy", "synthes"],
            "medtronic": ["mazor", "covidien"],
            "stryker": ["mako", "orthosoft"],
            "zimmer": ["rosa", "medtech", "orthosoft"],
            "smith & nephew": ["blue belt", "navio"],
            "cmr surgical": ["cmr"],
            "intuitive": ["intuitive"],
            "accray": ["accray", "cyberknife", "zapping"]
        }
        
        for parent, subs in subsidiary_map.items():
            if parent in company_clean:
                for sub in subs:
                    if sub in manufacturer:
                        return best_matching_string
        
        return None
    
    return best_matching_string

def main():
    parser = argparse.ArgumentParser(description="Download and match EUDAMED data using official API.")
    parser.add_argument("--yes", "-y", action="store_true", help="Automatically accept additions.")
    parser.add_argument("--search-only", action="store_true", help="Only search, don't update regulatory.json")
    args = parser.parse_args()
    
    print("Loading robot and company data...")
    robots = load_robots_json()
    companies = load_companies_json()
    regulatory_data = load_regulatory_json()
    
    # Pre-calculate company map
    rid_to_company = {}
    for c in companies:
        for rid in c.get('robots', []):
            rid_to_company[rid] = c['name']
    
    # Collect all devices
    all_devices = []
    
    print("\nSearching EUDAMED (via Beudamed) for robotic surgical devices...")
    for search_term in ROBOT_SEARCH_TERMS:
        devices = search_beudamed_scraping(search_term)
        all_devices.extend(devices)
        print(f"    Found {len(devices)} devices")
        time.sleep(1)  # Rate limiting
    
    print(f"\nTotal devices found: {len(all_devices)}")
    
    # Remove duplicates based on URL
    unique_devices = {}
    for device in all_devices:
        url = device.get('url')
        if url and url not in unique_devices:
            unique_devices[url] = device
    
    print(f"Unique devices: {len(unique_devices)}")
    
    if args.search_only:
        print("\nSearch-only mode. Sample devices found:")
        for i, (url, device) in enumerate(list(unique_devices.items())[:20]):
            print(f"  {i+1}. {device.get('trade_name')} - {device.get('manufacturer')}")
            print(f"      URL: {url}")
        return
    
    # Match devices to robots
    print("\nMatching devices to robots...")
    new_entries_count = 0
    modified_count = 0
    
    # Pre-calculate existing CE mark entries
    id_to_existing_ce = {}
    for rid, reg_list in regulatory_data.items():
        for reg in reg_list:
            url = reg.get('url', '')
            if 'beudamed.com' in url or 'eudamed' in url:
                id_to_existing_ce[(rid, url)] = reg
    
    for url, device in unique_devices.items():
        best_robot_id = None
        best_match_len = -1
        
        for robot in robots:
            rid = robot.get('id')
            company = rid_to_company.get(rid, "")
            
            excludes = robot.get('excludes_from_automated_searches', [])
            excludes_clean = [e.lower().strip() for e in excludes]
            
            search_names = [robot['name']] + robot.get('also_known_as', [])
            search_names = [sn for sn in search_names if sn.lower().strip() not in excludes_clean]
            
            match_string = is_relevant_match(search_names, device, company, excludes)
            if match_string:
                if len(match_string) > best_match_len:
                    best_match_len = len(match_string)
                    best_robot_id = rid
        
        if best_robot_id:
            # Check if this is a new entry
            if (best_robot_id, url) not in id_to_existing_ce:
                if best_robot_id not in regulatory_data:
                    regulatory_data[best_robot_id] = []
                
                # Add new CE mark entry
                entry = {
                    "url": url,
                    "body": "CE Mark",
                    "year": None, # Will need detailed view for year
                    "trade_name": device.get('trade_name'),
                    "manufacturer": device.get('manufacturer')
                }
                
                regulatory_data[best_robot_id].append(entry)
                new_entries_count += 1
                modified_count += 1
                print(f"  Added CE mark for {best_robot_id}: {device.get('trade_name')}")
    
    print(f"\nProcessed: {new_entries_count} CE marks added.")
    
    # Save
    if modified_count > 0:
        save_regulatory_json(regulatory_data)
        print(f"Successfully updated public/regulatory.json")
    else:
        print("No new CE mark entries found.")

if __name__ == "__main__":
    main()

if __name__ == "__main__":
    main()
