import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RELATIONSHIPS_DIR = REPO_ROOT / 'public' / 'relationships'
COMPANIES_DIR = REPO_ROOT / 'public' / 'companies'
OUTPUT_FILE = REPO_ROOT / 'public' / 'relationships.json'


def build_relationships():
    """Aggregates all JSON files in public/relationships/ into public/relationships.json and checks prose consistency."""
    if not RELATIONSHIPS_DIR.exists():
        print(f"Error: Directory {RELATIONSHIPS_DIR} does not exist.")
        sys.exit(1)

    companies = {}
    if COMPANIES_DIR.exists():
        for p in sorted(COMPANIES_DIR.glob('*.json')):
            with open(p, 'r', encoding='utf-8') as f:
                c = json.load(f)
                companies[c.get('id', p.stem)] = c

    company_ids = set(companies.keys())

    relationships = []
    rel_pairs = set()
    json_files = sorted(RELATIONSHIPS_DIR.glob('*.json'))
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                rel = json.load(f)

            if 'id' not in rel:
                rel['id'] = filepath.stem

            # Validate required fields
            for req in ('source', 'target', 'type', 'year'):
                if req not in rel:
                    print(f"Error in {filepath.name}: missing required field '{req}'")
                    sys.exit(1)

            s, t = rel['source'], rel['target']

            # If source or target is not a standalone company in public/companies/, ensure display name exists
            if company_ids and s not in company_ids and not rel.get('source_name'):
                print(f"Error in {filepath.name}: source '{s}' not in public/companies/ and missing 'source_name'")
                sys.exit(1)
            if company_ids and t not in company_ids and not rel.get('target_name'):
                print(f"Error in {filepath.name}: target '{t}' not in public/companies/ and missing 'target_name'")
                sys.exit(1)

            rel_pairs.add((s, t))
            rel_pairs.add((t, s))

            # Consistency check 1: if both companies exist, at least one company description should cross-link the other
            if s in companies and t in companies:
                s_desc = companies[s].get('description', '')
                t_desc = companies[t].get('description', '')
                if f'/company/{t})' not in s_desc and f'/company/{s})' not in t_desc:
                    print(f"  [Consistency Warning] {filepath.name}: neither {s}.json nor {t}.json links to the other in 'description'")

            relationships.append(rel)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            sys.exit(1)

    # Consistency check 2: every /company/<other_id> link in company descriptions should have a relationship file
    for cid, c in companies.items():
        desc = c.get('description', '')
        for m in re.finditer(r'/company/([a-z0-9_]+)\)', desc):
            other = m.group(1)
            if other != cid and other in company_ids and (cid, other) not in rel_pairs:
                print(f"  [Consistency Warning] {cid}.json links to /company/{other} in prose, but no file exists in public/relationships/ for ({cid}, {other})")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(relationships, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"Successfully built {OUTPUT_FILE} with {len(relationships)} relationships from {RELATIONSHIPS_DIR}.")


if __name__ == '__main__':
    build_relationships()
