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

### `verify_robot_urls.py`

Verifies that all robot detail URLs and company website URLs in `robots.json` are valid and reachable.

**Features:**
- Validates URL format for each robot and company
- Performs HTTP HEAD requests to check URL accessibility
- Concurrent verification with 10 worker threads for faster processing
- 60-second timeout per request for slower servers
- Real-time progress tracking
- Detailed logging of broken links and errors

**Usage:**

```bash
# Verify all URLs in robots.json
python3 scripts/verify_robot_urls.py

# Output shows validation status for each robot and URL
```

**Dependencies:** `requests`

---

### `verify_photo_urls.py`

Validates image URLs referenced in `robots.json` (avatar, primary photos, gallery images).

**Features:**
- Checks existence and accessibility of avatar and photo URLs
- Verifies gallery image URLs
- Concurrent verification with 10 worker threads
- 60-second timeout per request
- Real-time progress tracking
- Reports broken or missing images
- Optional: prompts to remove invalid URLs from robots.json

**Usage:**

```bash
# Verify all photo URLs in robots.json
python3 scripts/verify_photo_urls.py

# Output shows status for each robot's images
# Script can optionally remove broken image URLs
```

**Dependencies:** `requests`

---

### `verify_company_urls.py`

Validates company URLs and details associated with each robot (manufacturers, distributors, resellers).

**Features:**
- Checks company website URLs for validity
- Verifies company contact and social media URLs (LinkedIn, etc.)
- Concurrent verification with 10 worker threads
- 60-second timeout per request
- Real-time progress tracking
- Detailed error reporting for unreachable URLs

**Usage:**

```bash
# Verify all company URLs in robots.json
python3 scripts/verify_company_urls.py

# Output shows company validation results
```

**Dependencies:** `requests`

---

## Performance Notes

- **Concurrent Threads:** All URL verification scripts use 10 concurrent worker threads for parallel validation
- **Request Timeout:** 60-second timeout per URL to accommodate slower servers
- **Rate Limiting:** `update_regulatory.py` uses 2-second delays between requests to avoid triggering bot detection
- **Progress Tracking:** All scripts display real-time progress during execution

---

## Notes

- All scripts operate on `public/robots.json` by default
- Use the `--backup` flag when modifying data to create automatic backups
- The `--search-external` flag in `update_regulatory.py` requires internet connectivity
- Regulatory entries must be objects (legacy string format no longer supported)
- URL verification scripts use 10 concurrent worker threads and 60-second timeout per request
- All scripts are Python 3.9+ compatible
