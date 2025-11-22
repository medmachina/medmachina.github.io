# Med Machina

A medical robot directory. 

A simple site to track and sort medical robots, their capabilities, and their manufacturers.


See [Vite Configuration Reference](https://vite.dev/config/).

## Data Files

- `public/robots.json`: Primary dataset of robot entries consumed by the UI.
- `public/companies.json`: Company metadata.
- `public/companies.schema.json`: JSON Schema (Draft 2020-12) for companies dataset.
- `public/robots.schema.json`: JSON Schema (Draft 2020-12) for robots dataset (includes inline tag & usage descriptions).

### Validating Data

Company dataset validation (schema conformance and URL verification):

```bash
python3 scripts/update_companies.py --verify-only
```

Robot dataset validation (schema conformance and URL verification):

```bash
python3 scripts/update_robots.py --verify-only
```

Both commands validate against JSON Schema (Draft 2020-12) and verify all URLs. The update scripts also validate automatically before writing output.

### Regulatory Schema

The `regulatory` field in each robot is an array of objects with standardized structure:

```json
{
  "body": "FDA",
  "year": 2024,
  "region": "US",
  "type": "Clearance",
  "source_urls": ["https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm?ID=K123456"]
}
```

Field semantics:
- `body`: Regulatory authority or descriptor (e.g., `FDA`, `CE`, `Japan`, `NMPA`).
- `year`: Integer year of clearance/approval; null if unknown or not applicable.
- `region`: Geographic region/market code (e.g., `US`, `EU`, `JP`) when applicable.
- `type`: Nature of the status (e.g., `Clearance`, `Mark`, `Authorization`); null if unspecified.
- `source_urls`: Array of evidence URLs supporting the regulatory status.

**Updating Regulatory Data:**

Use `scripts/update_regulatory.py` to normalize and enrich regulatory entries:

```bash
# Normalize existing regulatory data
python3 scripts/update_regulatory.py

# Enrich with external sources (FDA 510k, EUDAMED, press releases)
python3 scripts/update_regulatory.py --search-external --backup
```

See [scripts/README.md](scripts/README.md) for full documentation.

## Project Setup

```sh
npm install
```

### Compile and Hot-Reload for Development

```sh
npm run dev
```

### Compile and Minify for Production

```sh
npm run build
```

  
