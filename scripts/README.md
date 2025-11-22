# Scripts

Utility scripts for maintaining and verifying the medmachina.github.io dataset.

## Setup

### Create Virtual Environment

```bash
# Navigate to the project root
cd /path/to/medmachina.github.io

# Create a Python 3.9+ virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

### Install Dependencies

```bash
# Install required packages for all scripts
pip install -r scripts/requirements.txt
```

### Deactivate Virtual Environment

```bash
deactivate
```

## Available Scripts

### `update_regulatory.py`

Normalizes and enriches regulatory entries in `robots.json` with optional external source discovery via official regulatory APIs.

**Features:**
- Normalizes regulatory entries to standard object format
- Ensures all entries have required fields: `body`, `year`, `region`, `type`, `source_urls`
- Three merge strategies: `merge` (normalized merge), `overwrite` (re-normalize), `skip` (keep if populated)
- Optional `--search-external` flag to query official regulatory databases:
  - **FDA 510(k)** via OpenFDA API for device clearances (https://api.fda.gov)
  - **EU EUDAMED API** for CE mark devices
  - Company press releases and announcements as fallback
- Configurable request rate limiting (2.0s default) to avoid bot detection
- Automatic backup creation with `--backup` flag

**Entry Format:**

Regulatory entries must be objects:
```json
{
  "body": "FDA",
  "year": 2024,
  "region": "US",
  "type": "Clearance",
  "source_urls": ["https://www.accessdata.fda.gov/..."]
}
```

**Usage:**

```bash
# Normalize existing regulatory data (merge strategy)
python3 scripts/update_regulatory.py

# Normalize + enrich with external sources
python3 scripts/update_regulatory.py --search-external --backup

# Re-normalize all entries (overwrites existing)
python3 scripts/update_regulatory.py --strategy overwrite

# Skip if already normalized
python3 scripts/update_regulatory.py --strategy skip

# Custom source and output files
python3 scripts/update_regulatory.py --source custom.json --output updated.json

# View all options
python3 scripts/update_regulatory.py --help
```

**External Source Discovery:**

When `--search-external` is enabled:
1. Queries **OpenFDA API** for FDA 510(k) clearances (K-numbers and direct links)
2. Queries **EUDAMED API** for EU CE mark devices
3. Falls back to web portal URLs for unsupported authorities
4. Searches company press releases only if < 3 sources found per device

All requests respect a 2-second rate limit to avoid suspicion.

**Dependencies:** `requests`, `beautifulsoup4`

---

### `update_robots.py`

Validates and verifies robot data in `robots.json` with schema conformance checking and URL accessibility tests.

**Features:**
- Validates robot dataset against `public/robots.schema.json` for schema conformance
- Validates photo structure (required fields, proper format)
- Verifies URL format and accessibility for robot info URLs and photo URLs
- Performs HTTP HEAD requests to check URL accessibility
- Concurrent verification with 10 worker threads for faster processing
- 60-second timeout per request for slower servers
- Real-time progress tracking
- Optional photo URL summary display
- Automatic backup creation with `--backup` flag
- Suppresses per-URL invalid logging during verification (summary only)

**Usage:**

```bash
# Verify schema conformance and all URLs (info + photos)
python3 scripts/update_robots.py --verify-only

# Show photo URL summary after verification
python3 scripts/update_robots.py --verify-only --photo-summary

# Full validation and verification with backup
python3 scripts/update_robots.py --backup

# Custom source and output files
python3 scripts/update_robots.py --source custom.json --output updated.json

# View all options
python3 scripts/update_robots.py --help
```

**Note:** The `--verify-only` flag runs both schema validation and URL verification (including photo URLs). Schema validation always runs before URL checks or any write operations.

**Dependencies:** `requests`, `jsonschema`

---

### `update_companies.py`

Enriches company data in `companies.json` with external metadata sources while validating existing URLs.

**Features:**
- Validates company dataset against `public/companies.schema.json` for schema conformance
- Validates company website URLs and LinkedIn URLs for accessibility
- Optional external data enrichment via `--enrich-external` flag:
  - **OpenCorporates API** for company registration data (jurisdiction, incorporation date, company type)
  - **Website metadata extraction** for descriptions, titles, and Open Graph data
  - Falls back to registered address and company type when description is missing
- Concurrent URL verification with 10 worker threads
- 60-second timeout per request for slower servers
- 2-second rate limiting between external API calls to avoid detection
- Real-time progress tracking
- Automatic backup creation with `--backup` flag
- Preserves existing LinkedIn URLs and validates their accessibility

**Usage:**

```bash
# Verify schema conformance and company URLs (no enrichment)
python3 scripts/update_companies.py --verify-only

# Verify and enrich with external sources
python3 scripts/update_companies.py --enrich-external --backup

# Custom source and output files
python3 scripts/update_companies.py --source custom.json --output updated.json

# View all options
python3 scripts/update_companies.py --help
```

**Note:** The `--verify-only` flag runs both schema validation and URL verification. Schema validation always runs before URL checks, enrichment, or any write operations.

**External Data Sources:**

When `--enrich-external` is enabled:
1. Queries **OpenCorporates API** for company registration details (free tier with rate limits)
2. Extracts **website metadata** (meta tags, Open Graph) from company URLs
3. Adds missing fields: `description`, `founded_year`, `company_type`
4. Preserves existing data - only fills in missing fields

**Dependencies:** `requests`, `beautifulsoup4`, `jsonschema`

---

## Performance Notes

- **Concurrent Threads:** All update scripts use 10 concurrent worker threads for parallel URL validation
- **Request Timeout:** 60-second timeout per URL to accommodate slower servers
- **Rate Limiting:** `update_regulatory.py` and `update_companies.py` use 2-second delays between external API requests to avoid triggering bot detection
- **Progress Tracking:** All scripts display real-time progress during execution

---

## Notes

- `update_robots.py` operates on `public/robots.json` by default
- `update_companies.py` operates on `public/companies.json` by default
- `update_regulatory.py` operates on `public/robots.json` (modifies regulatory field) by default
- Use the `--backup` flag when modifying data to create automatic backups
- The `--search-external` flag in `update_regulatory.py` requires internet connectivity
- The `--enrich-external` flag in `update_companies.py` requires internet connectivity
- Regulatory entries must be objects (legacy string format no longer supported)
- All scripts support schema validation via JSON Schema Draft 2020-12
- All scripts are Python 3.9+ compatible
