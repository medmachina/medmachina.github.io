#!/usr/bin/env python3

import json
import zipfile
import requests
import io
import os
import re
import argparse
from typing import List, Dict, Any, Optional

# FDA Download URLs
URL_510K = "https://www.accessdata.fda.gov/premarket/ftparea/pmn96cur.zip"
URL_PMA = "https://www.accessdata.fda.gov/premarket/ftparea/pma.zip"

# Product codes often associated with surgical robots
ROBOTIC_PRODUCT_CODES = {
    "NAY", "OAY", "PQC", "BWS", "LLZ", "NUV", "SCV", "NEQ", "PLV",
    "EOQ", "QNW", "HAW", "HSX", "PSQ", "OLO", "SDD", "QNM",
    "OJP", "IYO", "GCJ", "SAQ", "NQT", "PBF", "PNH", "OYC"
}

def download_and_extract_zip(url: str, extract_to: str = "tmp_fda", force: bool = False):
    """Download a zip file and extract its contents."""
    if not force and os.path.exists(extract_to) and os.listdir(extract_to):
        print(f"Skipping download for {url}, using existing files in {extract_to}")
        return os.listdir(extract_to)
    
    print(f"Downloading {url}...")
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to download {url}")
        return None
    
    os.makedirs(extract_to, exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        z.extractall(extract_to)
        return z.namelist()

def parse_510k_line(line: str) -> Dict[str, Any]:
    """Parse a pipe-delimited line from the 510(k) file."""
    # Layout (approximate based on research):
    # 510K_NUMBER|APPLICANT|CONTACT|STREET1|STREET2|CITY|STATE|COUNTRY_CODE|ZIP|POSTAL_CODE|DATE_RECEIVED|DECISION_DATE|DECISION|REVIEW_ADVISORY_COMMITTEE|PRODUCT_CODE|STATE_FLAG|CLASSIFICATION_ADVISORY_COMMITTEE|BLANK|TYPE|THIRD_PARTY|EXPEDITED|DEVICE_NAME
    fields = line.split('|')
    if len(fields) < 22:
        return {}
    
    return {
        "id": fields[0].strip(),
        "applicant": fields[1].strip(),
        "device_name": fields[21].strip(),
        "product_code": fields[14].strip(),
        "decision_date": fields[11].strip(), # MMDDYYYY
        "panel": fields[16].strip(), # Classification Advisory Committee
        "type": "510k" if not fields[0].startswith("DEN") else "denovo"
    }

def parse_pma_line(line: str) -> Dict[str, Any]:
    """Parse a fixed-width line from the PMA file."""
    # Applying widths from research/common CDRH layout
    pma_num = line[0:7].strip()
    supplement = line[7:10].strip()
    applicant = line[10:50].strip()
    generic_name = line[167:247].strip()
    trade_name = line[247:327].strip()
    product_code = line[327:330].strip()
    panel = line[330:332].strip()
    decision_date = line[357:367].strip() # MMDDYYYY
    
    return {
        "id": pma_num + (f"/S{supplement}" if supplement and supplement != "000" else ""),
        "applicant": applicant,
        "device_name": trade_name or generic_name,
        "product_code": product_code,
        "panel": panel,
        "decision_date": decision_date,
        "type": "pma"
    }

def load_robots_json(path: str = "public/robots.json") -> List[Dict[str, Any]]:
    with open(path, 'r') as f:
        return json.load(f)

def load_companies_json(path: str = "public/companies.json") -> List[Dict[str, Any]]:
    with open(path, 'r') as f:
        return json.load(f)

def load_regulatory_json(path: str = "public/regulatory.json"):
    """Load regulatory data from regulatory.json."""
    if not os.path.exists(path):
        return {}
    with open(path, 'r') as f:
        return json.load(f)

def save_regulatory_json(data: dict, path: str = "public/regulatory.json"):
    """Save regulatory data to regulatory.json."""
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def is_relevant_match(search_names: List[str], device_name: str, applicant: str, company_name: Optional[str], product_code: str, excludes: List[str] = []) -> Optional[str]:
    """Determine if an FDA record is a relevant match for a robot.
    
    Returns the matching string if found and relevant, else None.
    """
    # Clean name: remove special chars (trademarks etc) and normalize whitespace
    device_name_clean = re.sub(r'[^\w\s]', ' ', device_name).lower()
    device_name_clean = ' '.join(device_name_clean.split())
    
    applicant_clean = applicant.lower()
    
    # 0. Exclude if device name contains any excluded strings
    for ex in excludes:
        if ex.lower() in device_name_clean:
            return None

    # 1. Product code check (Hard Filter)
    if product_code not in ROBOTIC_PRODUCT_CODES:
        return None

    # 2. Name match check (Word Boundaries)
    best_matching_string = None
    for sn in search_names:
        sn_clean = sn.lower().strip()
        if not sn_clean: continue
        # Also clean search name just in case
        sn_clean = re.sub(r'[^\w\s]', ' ', sn_clean).lower()
        sn_clean = ' '.join(sn_clean.split())
        
        pattern = r'\b' + re.escape(sn_clean) + r'\b'
        if re.search(pattern, device_name_clean):
            if not best_matching_string or len(sn_clean) > len(best_matching_string):
                best_matching_string = sn_clean
    
    if not best_matching_string:
        return None

    # 3. Company match check
    company_matched = False
    if company_name:
        company_clean = company_name.lower().strip()
        
        # Check first word for better catching (e.g. Zimmer Biomet -> Zimmer)
        company_words = company_clean.split()
        first_word = company_words[0] if company_words else company_clean
        
        # Direct match or any keyword from company name
        if company_clean in applicant_clean or (len(first_word) > 3 and first_word in applicant_clean):
            company_matched = True
        else:
            # Specific subsidiary/acquisition mapping
            subsidiary_map = {
                "johnson & johnson": ["auris", "ethicon", "verb surgical", "monarch", "depuy", "synthes"],
                "j&j": ["auris", "ethicon", "verb surgical", "monarch", "depuy", "synthes"],
                "medtronic": ["mazor", "covidien"],
                "stryker": ["mako", "orthosoft"],
                "zimmer": ["rosa", "medtech", "orthosoft"],
                "smith & nephew": ["blue belt", "navio"],
                "asensus": ["transenterix"],
                "intuitive": ["intuitive"],
                "mmi": ["medical microinstruments"],
                "integrated surgical systems": ["curexo", "think surgical"]
            }
            
            for parent, subs in subsidiary_map.items():
                if parent in company_clean:
                    for sub in subs:
                        if sub in applicant_clean:
                            company_matched = True
                            break
                if company_matched: break
        
        if not company_matched:
            return None
        
    return best_matching_string

def main():
    parser = argparse.ArgumentParser(description="Download and match FDA regulatory data.")
    parser.add_argument("--yes", "-y", action="store_true", help="Automatically accept removals.")
    args = parser.parse_args()

    # 1. Download
    files_510k = download_and_extract_zip(URL_510K, "tmp_fda/510k")
    files_pma = download_and_extract_zip(URL_PMA, "tmp_fda/pma")
    
    if not files_510k or not files_pma:
        print("Download failed.")
        return

    # 2. Parse 510(k) / De Novo
    fda_records = []
    pmn_file = "tmp_fda/510k/pmn96cur.txt"
    if os.path.exists(pmn_file):
        print(f"Parsing {pmn_file}...")
        with open(pmn_file, 'r', encoding='latin-1') as f:
            for line in f:
                record = parse_510k_line(line)
                if record:
                    fda_records.append(record)

    # 3. Parse PMA
    pma_file = "tmp_fda/pma/pma.txt"
    if os.path.exists(pma_file):
        print(f"Parsing {pma_file}...")
        with open(pma_file, 'r', encoding='latin-1') as f:
            for line in f:
                record = parse_pma_line(line)
                if record:
                    fda_records.append(record)

    print(f"Total FDA records loaded: {len(fda_records)}")

    # 4. Load robot data
    robots = load_robots_json()
    companies = load_companies_json()
    regulatory_data = load_regulatory_json()

    # Pre-calculate company map
    rid_to_company = {}
    for c in companies:
        for rid in c.get('robots', []):
            rid_to_company[rid] = c['name']

    # Pre-calculate existing entries from regulatory.json
    id_to_existing_reg = {} # (robot_id, reg_id) -> entry
    for rid, reg_list in regulatory_data.items():
        for reg in reg_list:
            url = reg.get('url', '')
            reg_id = None
            if 'ID=' in url: reg_id = url.split('ID=')[-1]
            elif 'id=' in url: reg_id = url.split('id=')[-1]
            elif 'denovo=' in url: reg_id = url.split('denovo=')[-1]
            if reg_id:
                id_to_existing_reg[(rid, reg_id)] = reg

    modified_count = 0
    new_entries_count = 0
    removed_entries_count = 0

    # Assignment logic: for each record, find the "best" robot
    record_assignments = {} # robot_id -> list of records

    print("Assigning records to robots...")
    for rec in fda_records:
        best_robot_id = None
        best_match_len = -1
        
        for robot in robots:
            rid = robot.get('id')
            company = rid_to_company.get(rid, "")
            
            # Filter out names that should be excluded from search_names
            # but also pass excludes to is_relevant_match for substring rejection
            excludes = robot.get('excludes_from_automated_searches', [])
            excludes_clean = [e.lower().strip() for e in excludes]
            
            search_names = [robot['name']] + robot.get('also_known_as', [])
            # Also filter search_names themselves if they are in excludes
            search_names = [sn for sn in search_names if sn.lower().strip() not in excludes_clean]
            
            match_string = is_relevant_match(search_names, rec['device_name'], rec['applicant'], company, rec['product_code'], excludes)
            if match_string:
                if len(match_string) > best_match_len:
                    best_match_len = len(match_string)
                    best_robot_id = rid
        
        if best_robot_id:
            if best_robot_id not in record_assignments:
                record_assignments[best_robot_id] = set()
            record_assignments[best_robot_id].add(rec['id'])
            
            # If it's a new match, add it to regulatory_data
            if (best_robot_id, rec['id']) not in id_to_existing_reg:
                if best_robot_id not in regulatory_data:
                    regulatory_data[best_robot_id] = []
                
                # Add new regulatory entry
                entry = {
                    "url": "",
                    "body": "",
                    "year": int(rec['decision_date'][-4:]) if rec['decision_date'] and len(rec['decision_date']) >= 8 else None,
                    "product_code": rec['product_code'],
                    "panel": rec['panel']
                }
                
                if rec['type'] == '510k':
                    entry['url'] = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID={rec['id']}"
                    entry['body'] = "FDA 510k"
                elif rec['type'] == 'denovo':
                    entry['url'] = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/denovo.cfm?denovo={rec['id']}"
                    entry['body'] = "FDA denovo"
                elif rec['type'] == 'pma':
                    entry['url'] = f"https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpma/pma.cfm?id={rec['id']}"
                    entry['body'] = "FDA PMA"
                
                regulatory_data[best_robot_id].append(entry)
                new_entries_count += 1
                modified_count += 1

    # Now check for stale entries (in regulatory.json but not in record_assignments)
    for rid in list(regulatory_data.keys()):
        current_reg = regulatory_data.get(rid, [])
        new_reg = []
        to_remove = []
        
        for reg in current_reg:
            url = reg.get('url', '')
            reg_id = None
            if 'ID=' in url: reg_id = url.split('ID=')[-1]
            elif 'id=' in url: reg_id = url.split('id=')[-1]
            elif 'denovo=' in url: reg_id = url.split('denovo=')[-1]
            
            # If it's an FDA entry and NOT assigned to this robot by current logic
            if reg_id and (reg.get('body', '').startswith('FDA ')) and reg_id not in record_assignments.get(rid, set()):
                to_remove.append(reg)
            else:
                new_reg.append(reg)
        
        if to_remove:
            print(f"\nRobot '{rid}' has {len(to_remove)} potentially stale entries:")
            for tr in to_remove:
                print(f"  - {tr.get('body')} {tr.get('url')} (Year: {tr.get('year')})")
            
            confirmed = args.yes
            if not confirmed:
                ans = input(f"Remove these {len(to_remove)} entries? [y/N]: ").lower().strip()
                confirmed = ans == 'y'
            
            if confirmed:
                regulatory_data[rid] = new_reg
                removed_entries_count += len(to_remove)
                modified_count += 1
            else:
                print(f"Skipping removal for {rid}.")

    print(f"\nProcessed: {new_entries_count} added, {removed_entries_count} removed.")

    # 6. Save
    if modified_count > 0:
        save_regulatory_json(regulatory_data)
        print(f"Successfully updated public/regulatory.json")
        print(f"Updated {modified_count} robots with {new_entries_count} new regulatory entries.")
    else:
        print("No new regulatory entries found.")

if __name__ == "__main__":
    main()
