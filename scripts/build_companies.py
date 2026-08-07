import json
import re
import sys
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
COMPANIES_DIR = REPO_ROOT / 'public' / 'companies'
OUTPUT_FILE = REPO_ROOT / 'public' / 'companies.json'


def slugify(text: str) -> str:
    """Generate a clean URL/filename-safe slug from a string."""
    text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
    text = text.lower().strip()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text


def build_companies():
    """Aggregates all JSON files in public/companies/ into public/companies.json."""
    if not COMPANIES_DIR.exists():
        print(f"Error: Directory {COMPANIES_DIR} does not exist.")
        sys.exit(1)

    companies = []
    json_files = sorted(COMPANIES_DIR.glob('*.json'))
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                company = json.load(f)
            
            # Ensure id exists
            if 'id' not in company and 'name' in company:
                company['id'] = slugify(company['name'])
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(company, f, indent=2, ensure_ascii=False)
                    f.write('\n')
                print(f"  Auto-set id={company['id']} for {filepath.name}")

            companies.append(company)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            sys.exit(1)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(companies, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"Successfully built {OUTPUT_FILE} with {len(companies)} companies from {COMPANIES_DIR}.")


def split_companies():
    """Splits public/companies.json into individual files in public/companies/<id>.json."""
    if not OUTPUT_FILE.exists():
        print(f"Error: File {OUTPUT_FILE} does not exist.")
        sys.exit(1)

    COMPANIES_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        companies = json.load(f)

    count = 0
    for company in companies:
        name = company.get('name')
        if not name:
            print(f"Warning: company missing 'name': {company}")
            continue

        company_id = company.get('id') or slugify(name)
        company['id'] = company_id

        # Order fields cleanly: id, name, country...
        ordered = {'id': company_id, 'name': name}
        for k, v in company.items():
            if k not in ordered:
                ordered[k] = v

        file_path = COMPANIES_DIR / f"{company_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(ordered, f, indent=2, ensure_ascii=False)
            f.write('\n')
        count += 1

    print(f"Successfully split {count} companies into {COMPANIES_DIR}.")


if __name__ == '__main__':
    if '--split' in sys.argv:
        split_companies()
    else:
        build_companies()
