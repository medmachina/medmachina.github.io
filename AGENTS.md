# Med Machina Editorial & Data Guidelines

## 1. Tone & Style
- **Neutral, technical, and factual:** Describe robotic systems, kinematics, clinical indications, and corporate history objectively.
- **No PR copy or superlatives:** Do not use promotional language, marketing fluff, or superlatives (e.g., ban words like *"pioneering"*, *"revolutionary"*, *"next-generation"*, *"game-changing"*, *"creating the future"*, or first-person pronouns like *"our/we"*).
- **Concise descriptions:** Highlight concrete mechanism types (Cartesian, parallel linkage, concentric tubes), degrees of freedom, endoscopes/optics, console layout, control schemes, and regulatory clearances.

## 2. URL, Link & Source Provenance Conventions
- **Full Source URLs Required for All Information:**
  - Keep at least one full, direct source URL (`https://...`) for all factual information entered into this database—never store bare domain names or unverified claims without a source link:
    - **Relationships (`public/relationships/<source>_<target>.json`):** Must include a non-empty `"sources": ["https://...", ...]` array of full URLs (press releases, regulatory filings, product/partner pages) verifying the M&A, OEM, or collaboration relationship.
    - **Company & Robot Pages (`public/companies/*.json`, `public/robots/*.json`):** Must include full URLs in `"urls": [{ "caption": "...", "url": "https://..." }]`.
    - **Corporate Status Events (`status`):** Any non-active status (`acquired`, `merged`, `liquidated`, `restructuring`, `defunct`) must include `"source_url": "https://..."`.
    - **Regulatory Clearances (`regulatory`) & Deployed Units (`units_deployed`):** Must include full `"url"` / `"source_url"` links to the regulatory database record, SEC filing, or press release.
- **Internal Cross-Links (Wikipedia-Style First Mention):**
  - Link the first mention of any robot or company in `description` text—including a company's own robots on its company page, and a robot's manufacturer or OEM/commercial partners on its robot page.
  - Company links: `[Company Name](/company/company_id)` (always use snake_case IDs with `_`, e.g., `/company/karl_storz`, `/company/virtuoso_surgical`).
  - Robot links: `[Robot Name](/robot/robot_id)` (e.g., `/robot/medtronic_hugo_ras`).
  - **Never use `%20` or raw spaces in internal URLs.**
- **FDA Regulatory URLs:**
  - **De Novo:** Always use `?ID=`, never `?denovo=`:  
    `https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMN/denovo.cfm?ID=DENxxxxxx`
  - **510(k):**  
    `https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=Kxxxxxx`
  - **PMA:**  
    `https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfPMA/pma.cfm?id=Pxxxxxx`

## 3. Country Standardization
- Always use the full, standard English country name in `country` fields (e.g., `"South Korea"`, not `"KR"`; `"United States"`, not `"US"` or `"USA"`).

## 4. Dataset Consistency & Schema
- Every robot file in `public/robots/<id>.json` must be listed in its company's `robots` array in `public/companies/<company_id>.json`.
- All companies must have valid `id` (snake_case slug), `name`, `country`, `founded_year` (integer), `urls`, and `robots` fields.
- **Company Ecosystem Relationships (`public/relationships/<source>_<target>.json`):** Mergers, acquisitions, OEM hardware/optics/haptics supply contracts, and strategic distribution/investment/JV alliances are stored as standalone files in `public/relationships/<source>_<target>.json` (`{ "id": "<source>_<target>", "source": "company_a", "target": "company_b", "type": "acquired" | "merged" | "oem" | "collaboration", "subtype": "...", "year": 2026, "note": "...", "sources": ["https://..."] }`) and aggregated into `public/relationships.json` by `scripts/build_relationships.py`.
- **Prose ↔ Relationship Consistency (Preventing Divergence):**
  - Whenever an M&A event, OEM component integration (e.g. Force Dimension haptic masters, KUKA/Stäubli/Kinova arms, KARL STORZ/Schölly optics), or strategic alliance is added or updated in a company or robot `description` (or `status`), you **must** also create or update the corresponding file in `public/relationships/<source>_<target>.json`.
  - Conversely, whenever a relationship file is added to `public/relationships/`, ensure the participating company/robot `description` text includes matching `[Company Name](/company/company_id)` cross-links. `scripts/build_relationships.py` automatically checks for prose/relationship drift during `npm run build`.
- OpenCorporates URLs: If a verified company record exists on OpenCorporates, provide the link. If not indexed, leave as `""` (do not guess court codes or registration numbers).
- LinkedIn URLs: Prefer official global corporate company pages (`https://www.linkedin.com/company/<handle>/`).

## 5. Build & Validation
- After modifying any robot, company, or relationship JSON file, always run:
  ```bash
  npm run build
  ```
  This command automatically:
  1. Runs `scripts/build_companies.py` to aggregate `public/companies.json`.
  2. Runs `scripts/build_robots.py` to aggregate `public/robots.json`.
  3. Runs `scripts/build_relationships.py` to aggregate and validate `public/relationships.json`.
  4. Builds Vite assets (`dist/`).
  5. Runs `scripts/generate_seo.py` to update `sitemap.xml`, `robots.txt`, and generate pre-rendered HTML pages.

