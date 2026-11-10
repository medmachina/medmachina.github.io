# Med Machina Editorial & Data Guidelines

## 1. Tone & Style
- **Neutral, technical, and factual:** Describe robotic systems, kinematics, clinical indications, and corporate history objectively.
- **No PR copy or superlatives:** Do not use promotional language, marketing fluff, or superlatives (e.g., ban words like *"pioneering"*, *"revolutionary"*, *"next-generation"*, *"game-changing"*, *"creating the future"*, or first-person pronouns like *"our/we"*).
- **Concise descriptions:** Highlight concrete mechanism types (Cartesian, parallel linkage, concentric tubes), degrees of freedom, endoscopes/optics, console layout, control schemes, and regulatory clearances.

## 2. URL & Link Conventions
- **Internal Cross-Links:**
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
- All companies must have valid `id` (snake_case slug), `name`, `country`, `urls`, and `robots` fields.
- OpenCorporates URLs: If a verified company record exists on OpenCorporates, provide the link. If not indexed, leave as `""` (do not guess court codes or registration numbers).
- LinkedIn URLs: Prefer official global corporate company pages (`https://www.linkedin.com/company/<handle>/`).

## 5. Build & Validation
- After modifying any robot or company JSON file, always run:
  ```bash
  npm run build
  ```
  This command automatically:
  1. Runs `scripts/build_companies.py` to aggregate `public/companies.json`.
  2. Runs `scripts/build_robots.py` to aggregate `public/robots.json`.
  3. Builds Vite assets (`dist/`).
  4. Runs `scripts/generate_seo.py` to update `sitemap.xml`, `robots.txt`, and generate pre-rendered HTML pages.

