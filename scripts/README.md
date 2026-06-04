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

Normalizes and enriches regulatory entries in `robots.json` with external source discovery via official regulatory APIs.

**Features:**
- Normalizes regulatory entries to standard object format
- Ensures all entries have required fields: `body`, `year`, `url`
- Three merge strategies: `merge` (normalized merge), `overwrite` (re-normalize), `skip` (keep if populated)
- Queries official regulatory databases for additional sources (OpenFDA, EUDAMED) and can fall back to company press releases
- Configurable request rate limiting (2.0s default) to avoid bot detection
- Automatic backup creation with `--backup` flag

**Entry Format:**

Regulatory entries must be objects:
```json
{
  "body": "FDA",
  "year": 2024,
  "url": "https://www.accessdata.fda.gov/..."
}
```

**Usage:**

```bash
# Normalize existing regulatory data (merge strategy)
python3 scripts/update_regulatory.py

# Normalize + enrich with external sources (internet required)
python3 scripts/update_regulatory.py

# Process only robots with specific ID prefix (case-insensitive)
python3 scripts/update_regulatory.py --prefix momentis
# Example with prefix filtering (enrichment still performed):
python3 scripts/update_regulatory.py --prefix INTUITIVE

# View all options
python3 scripts/update_regulatory.py --help
```

**Prefix Filtering:**

The `--prefix` option filters robots by ID prefix (case-insensitive) for processing:
- Only robots matching the prefix are updated/enriched
- All robots (matching and non-matching) are preserved in the output file
- Useful for testing changes on specific manufacturers before full runs

Example: `--prefix intuitive` processes only `intuitive_da_vinci_5`, `intuitive_da_vinci_SP`, etc.

**External Source Discovery:**

External Source Discovery:
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

# Process only robots with specific ID prefix (case-insensitive)
python3 scripts/update_robots.py --verify-only --prefix edge
python3 scripts/update_robots.py --prefix momentis --photo-summary

# View all options
python3 scripts/update_robots.py --help
```

**Prefix Filtering:**

The `--prefix` option filters robots by ID prefix (case-insensitive) for validation:
- Only robots matching the prefix are validated/processed
- All robots (matching and non-matching) are preserved in the output file
- Useful for focused validation on specific manufacturers

Example: `--prefix edge` validates only `edge_multi_port` and `edge_single_port`.

**Note:** The `--verify-only` flag runs both schema validation and URL verification (including photo URLs). Schema validation always runs before URL checks or any write operations.

**Dependencies:** `requests`, `jsonschema`

---

### `update_robot_videos.py`

Validates and interactively updates video entries in `robots.json` with checks specific to YouTube/Vimeo curation.

**Features:**
- Validates `videos[]` structure for robot entries that include videos
- Extracts YouTube/Vimeo video IDs and reports canonical URLs
- Verifies supported providers match the current UI embed behavior
- Reports missing titles, provider-title mismatches, duplicate videos, and titles that do not clearly match the robot name/id
- Optionally checks video availability through YouTube/Vimeo oEmbed endpoints
- Interactive mode for deleting failed videos, previewing/renaming videos that need review, and reviewing/adding search candidates
- Search mode for discovering candidate new videos from provider-specific web searches
- Supports focused validation by robot ID prefix

**Usage:**

```bash
# Validate all robot video links, including YouTube/Vimeo availability checks
python3 scripts/update_robot_videos.py

# Run local-only checks without network requests
python3 scripts/update_robot_videos.py --no-network

# Show passing entries too
python3 scripts/update_robot_videos.py --show-passed

# Validate a specific robot/manufacturer prefix
python3 scripts/update_robot_videos.py --prefix titan

# Treat REVIEW results as CI failures
python3 scripts/update_robot_videos.py --strict

# Interactively curate FAIL and REVIEW entries
python3 scripts/update_robot_videos.py --interactive

# Run an interactive session without opening browser previews
python3 scripts/update_robot_videos.py --interactive --no-open

# Save interactive edits to another file instead of overwriting robots.json
python3 scripts/update_robot_videos.py --interactive --output reviewed-robots.json

# Create public/robots.json.bak before writing interactive edits
python3 scripts/update_robot_videos.py --interactive --backup

# Search for candidate new videos, without modifying robots.json
python3 scripts/update_robot_videos.py --search --prefix intuitive_da_vinci_5

# Search YouTube, Vimeo, and Dailymotion candidates
python3 scripts/update_robot_videos.py --search --providers youtube,vimeo,dailymotion --prefix 'j&j'

# Tune search breadth and strictness
python3 scripts/update_robot_videos.py --search --search-limit 3 --search-min-score 8

# Run a very gentle unattended search to reduce 403/429 throttling
python3 scripts/update_robot_videos.py --search --search-delay 15 --search-backoff 300 --search-retries 2

# Search, preview candidates, and add accepted YouTube/Vimeo links
python3 scripts/update_robot_videos.py --search --interactive --prefix stryker

# Review search candidates but write accepted links to a separate file
python3 scripts/update_robot_videos.py --search --interactive --output reviewed-robots.json --prefix stryker

# Ignore the rejected-video file for a one-off search
python3 scripts/update_robot_videos.py --search --no-rejected-filter --prefix stryker
```

**Interactive Mode:**
- `FAIL` entries prompt for `(k)eep` or `(d)elete`
- `REVIEW` entries open in the default web browser, then prompt for `(k)eep`, `(d)elete`, or `(r)ename`
- Rename prompts default to the provider title when YouTube/Vimeo oEmbed metadata is available
- Changes are summarized before the script asks whether to write them

**Search Mode:**
- `--search` by itself is report-only and never modifies `robots.json`
- Default providers are YouTube and Vimeo; Dailymotion can be included with `--providers dailymotion`
- Candidates are found via direct YouTube search and provider-scoped web searches, canonicalized, deduplicated against existing videos, and scored by robot-name/alias/context matches
- Search requests sleep between HTTP calls (`--search-delay`, default 5s) and back off after HTTP 403/429 (`--search-backoff`, default 60s)
- `--search --interactive` opens each candidate for preview and prompts for `(a)dd`, `(r)ename+add`, `(s)kip`, `(x)reject`, or `(q)uit`
- `(s)kip` ignores a candidate only for the current run; `(x)reject` records it in `public/rejected-video.json`
- Search filters out candidates listed in `public/rejected-video.json` unless `--no-rejected-filter` is used
- Interactive search additions respect the schema maximum of 4 videos per robot
- Accepted search additions are written in relevance-score order, with existing videos on affected robots re-sorted by the same heuristic
- Dailymotion is search-only by default because the current app embed path supports YouTube/Vimeo
- Use `--prefix` for focused searches; searching every robot can take a while

**Result Categories:**
- `PASS`: URL parses, provider is supported, and metadata/title checks look sane
- `REVIEW`: Link may be usable, but needs human curation (for example, missing title or weak title match)
- `FAIL`: Malformed URL, unsupported provider, duplicate within one robot, or unavailable oEmbed result

**Dependencies:** `requests`, `beautifulsoup4`

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

# Process only companies with robots matching ID prefix (case-insensitive)
python3 scripts/update_companies.py --verify-only --prefix momentis
python3 scripts/update_companies.py --enrich-external --prefix intuitive --backup

# View all options
python3 scripts/update_companies.py --help
```

**Prefix Filtering:**

The `--prefix` option filters companies by their robots' ID prefixes (case-insensitive):
- Only companies with robots matching the prefix are validated/enriched
- All companies (matching and non-matching) are preserved in the output file
- Useful for focused updates on specific manufacturers

Example: `--prefix momentis` processes only companies with `momentis_anovo` in their robots array.

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
-- External enrichment in `update_regulatory.py` requires internet connectivity
- The `--enrich-external` flag in `update_companies.py` requires internet connectivity
- Regulatory entries must be objects (legacy string format no longer supported)
- All scripts support schema validation via JSON Schema Draft 2020-12
- All scripts are Python 3.9+ compatible
