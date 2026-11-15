---
name: add-robot
description: Step-by-step procedure to add a new surgical robot and its manufacturer to Med Machina, fetch FDA regulatory filings, and rebuild data bundles.
---

# Adding a New Robot to Med Machina

Follow these steps to add a new surgical robot and maintain database integrity:

## 1. Create Individual Robot JSON File
- Create `public/robots/<robot_id>.json` (e.g. `public/robots/company_robotname.json`).
- Set a clear `name` and unique snake_case `id`.
- Use `search_web` to locate official product pages, manufacturer announcements, and high-resolution product photos.
- Assign appropriate `categories` (matching `public/robots.schema.json`), `usages`, and mechanical/clinical `tags`.
- Draft a neutral, factual `description` adhering to the guidelines in `AGENTS.md` (no superlatives or PR copy).
- Cross-link related platforms or manufacturers using snake_case router URLs (`[Company Name](/company/company_id)`).

## 2. Update or Create Company Entry & Ecosystem Relationships
- Check if manufacturer exists in `public/companies/<company_id>.json`.
- If existing: append the new robot's `id` to its `robots` array.
- If new: create `public/companies/<company_id>.json` with `id`, `name`, standardized full `country` name, `founded_year` (integer), official `urls`, `description`, and initialize `robots: ["<robot_id>"]`.
- **Keep Prose and `public/relationships/` Synchronized:** If the robot or company uses OEM components from another company in the database (e.g. Force Dimension master controllers, KUKA/Stäubli/Kinova robot arms, KARL STORZ/Schölly optics) or involves an acquisition, merger, spin-off, or distribution partnership, you must **both**:
  1. Cross-link the partner/OEM company in the `description` text (`[Company Name](/company/company_id)`), and
  2. Create or update the corresponding `public/relationships/<source>_<target>.json` file (including a non-empty `"sources": ["https://..."]` array of full source URLs) so the Company Time Graph stays in sync with the prose.
- **Full Source URLs Required:** Keep at least one full source URL (`https://...`) for every piece of information added to the database (`urls`, `status.source_url`, `sources` in `public/relationships/*.json`, `regulatory[].url`, `units_deployed.source_url`).

## 3. Fetch Regulatory Data
- Query FDA CDRH databases for 510(k), De Novo, or PMA clearances:
  ```bash
  python3 scripts/download_fda_data.py --robot <robot_id> --yes
  ```
- If manually adding De Novo entries, always use the `?ID=DENxxxxxx` parameter format.

## 4. Rebuild & Verify
- Run the full build command to aggregate JSON bundles, verify schemas, and update pre-rendered SEO pages:
  ```bash
  npm run build
  ```
- Inspect changes with `git status` and `git diff` to ensure clean formatting.

