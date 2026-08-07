"""
Generate patent search metadata for each company in companies.json.

Approach:
- Builds Google Patents and Lens.org search URLs per company
- Optionally fetches patent counts from Lens.org API (requires free API key)
- Writes patent_search data into companies.json

Usage:
    # Just generate URLs (no API key needed):
    python3 scripts/update_patents.py

    # Fetch live patent counts from Lens.org (requires API key):
    python3 scripts/update_patents.py --lens-key YOUR_API_KEY_HERE

Get a free Lens.org API key at: https://www.lens.org/lens/user/subscriptions
"""

import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import subprocess

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPANIES_DIR = REPO_ROOT / "public" / "companies"
COMPANIES_FILE = REPO_ROOT / "public" / "companies.json"

LENS_API_URL = "https://api.lens.org/patent/search"

# -----------------------------------------------------------------------------
# Known assignee name overrides for companies whose legal patent-filing name
# differs from their display name in companies.json
# Add entries here when Google Patents / Lens returns 0 results for the company name.
# -----------------------------------------------------------------------------
ASSIGNEE_OVERRIDES = {
    "Intuitive":         ["Intuitive Surgical Operations", "Intuitive Surgical"],
    "J&J MedTech":       ["Ethicon", "DePuy Synthes", "Johnson & Johnson"],
    "Stryker":           ["Stryker Corporation", "Stryker"],
    "Medtronic":         ["Medtronic", "Mazor Robotics"],
    "CMR Surgical":      ["CMR Surgical"],
    "Zimmer Biomet":     ["Zimmer Biomet", "Biomet"],
    "Think Surgical":    ["Think Surgical"],
    "Renishaw":          ["Renishaw"],
    "Vicarious Surgical":["Vicarious Surgical"],
    "Momentis Surgical": ["Momentis Surgical"],
    "Moon Surgical":     ["Moon Surgical"],
    "Distal Motion":     ["Distal Motion", "DistalMotion"],
    "Avatera Medical":   ["Avatera Medical"],
    "Microsure":         ["Microsure"],
    "MMI":               ["Medical Microinstruments", "MMI"],
    "Haply Robotics":    ["Haply Robotics"],
    "Asensus Surgical":  ["Asensus Surgical", "TransEnterix"],
    "ISS":               ["Integrated Surgical Systems"],
    "Kinova":            ["Kinova", "Kinova Robotics"],
    "KUKA":              ["KUKA", "KUKA Roboter"],
    "Stäubli":           ["Staubli", "Stäubli"],
    "LEM Surgical":      ["LEM Surgical"],
    "Neocis":            ["Neocis"],
}


def get_assignee_names(company: dict) -> list[str]:
    """Return list of patent assignee name(s) to use for this company."""
    name = company.get("name", "")
    return ASSIGNEE_OVERRIDES.get(name, [name])


def build_google_patents_url(assignee_names: list[str]) -> str:
    """Build a Google Patents search URL for the given assignee name(s)."""
    primary = assignee_names[0]
    return "https://patents.google.com/?assignee=" + urllib.parse.quote_plus(primary)


def build_lens_url(assignee_names: list[str]) -> str:
    """Build a Lens.org patent search URL for the given assignee name(s)."""
    if len(assignee_names) == 1:
        q = f'applicant:"{assignee_names[0]}"'
    else:
        parts = " OR ".join(f'applicant:"{n}"' for n in assignee_names)
        q = f"({parts})"
    return (
        "https://www.lens.org/lens/search/patent?q="
        + urllib.parse.quote(q)
        + "&s=_score&d=%2B&p=0&n=50"
    )


def fetch_lens_count(assignee_names, api_key):
    """Fetch patent count from Lens.org API for the given assignee names."""
    should_clauses = [
        {"match": {"applicants.name": name}} for name in assignee_names
    ]
    query = {
        "query": {"bool": {"should": should_clauses, "minimum_should_match": 1}},
        "size": 0,
        "include": []
    }
    data = json.dumps(query).encode()
    req = urllib.request.Request(
        LENS_API_URL,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            return result.get("total", {}).get("value") or result.get("total")
    except urllib.error.HTTPError as e:
        body = e.read().decode()
        print(f"  Lens API error {e.code}: {body[:200]}")
        return None
    except Exception as e:
        print(f"  Lens request failed: {e}")
        return None


def main():
    lens_key = None
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--lens-key" and i + 1 < len(sys.argv) - 1:
            lens_key = sys.argv[i + 2]
            break
        if arg.startswith("--lens-key="):
            lens_key = arg.split("=", 1)[1]

    dry_run = "--dry-run" in sys.argv

    company_files = sorted(COMPANIES_DIR.glob("*.json"))
    print(f"Processing {len(company_files)} company files in {COMPANIES_DIR}...")
    if lens_key:
        print("Lens.org API key provided — will fetch live patent counts.")
    else:
        print("No Lens.org API key — building URLs only. Use --lens-key=KEY to fetch counts.")
    print()

    changed = 0
    for filepath in company_files:
        with open(filepath, "r", encoding="utf-8") as f:
            company = json.load(f)

        name = company.get("name", "?")
        assignee_names = get_assignee_names(company)

        gp_url = build_google_patents_url(assignee_names)
        lens_url = build_lens_url(assignee_names)

        patent_data = {
            "assignee_names": assignee_names,
            "google_patents_url": gp_url,
            "lens_url": lens_url,
        }

        if lens_key:
            print(f"  Fetching count for {name}...")
            count = fetch_lens_count(assignee_names, lens_key)
            if count is not None:
                patent_data["count"] = count
                print(f"    → {count} patents")
            else:
                print(f"    → count unavailable")
            time.sleep(0.5)

        existing = company.get("patents")
        if existing != patent_data:
            company["patents"] = patent_data
            changed += 1
            if not dry_run:
                with open(filepath, "w", encoding="utf-8") as f:
                    json.dump(company, f, indent=2, ensure_ascii=False)
                    f.write("\n")
            print(f"  ✓ {name} ({filepath.name}): {gp_url}")
        else:
            print(f"  = {name} ({filepath.name}): already up to date")

    if not dry_run:
        print(f"\nUpdated {changed} company files. Rebuilding public/companies.json...")
        subprocess.run([sys.executable, str(REPO_ROOT / "scripts" / "build_companies.py")], check=True)
    else:
        print(f"\n[DRY RUN] Would have updated {changed} company files.")


if __name__ == "__main__":
    main()
