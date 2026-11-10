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

## 2. Update or Create Company Entry
- Check if manufacturer exists in `public/companies/<company_id>.json`.
- If existing: append the new robot's `id` to its `robots` array.
- If new: create `public/companies/<company_id>.json` with `id`, `name`, standardized full `country` name, official `urls`, and initialize `robots: ["<robot_id>"]`.

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

