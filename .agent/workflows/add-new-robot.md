---
description: How to add a new surgical robot to the dataset
---
# Adding a New Robot

Follow these steps to successfully add a new surgical robot to the MedMachina dataset.

1. **Add to robots.json:**
   - Create a new entry in `public/robots.json`.
   - Provide a `name` and a unique `id` (e.g., `company_robotname`).
   - Use the `search_web` tool to find the official product page URL and high-quality image URLs. Add these to the `urls` and `photos` arrays.
   - Review `public/robots.schema.json` to assign the most appropriate `tags` and `usages` to the robot.
   - Add a brief `description` if requested or available.

2. **Update companies.json:**
   - Check if the manufacturer already exists in `public/companies.json`.
   - If the company exists, carefully append the new robot's `id` to its `robots` array.
   - If the company does not exist, create a new company entry including its `name`, `country`, `urls`, and the initialized `robots` array containing the new robot's `id`.

// turbo
3. **Fetch FDA Regulatory Data:**
   - Execute the FDA data processing script targeted specifically at the new robot's ID to fetch and append its regulatory registrations (510k, PMA, etc.) to `public/regulatory.json`.
   - Make sure to replace `<ROBOT_ID>` with the actual ID you assigned in `robots.json`.

```bash
python3 scripts/download_fda_data.py --robot <ROBOT_ID> --yes
```
