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

**Filtering by Robot ID Prefix:**

All update scripts support `--prefix` to process only robots (or companies with matching robots) whose IDs start with the given prefix (case-insensitive):

```bash
# Validate only Intuitive robots
python3 scripts/update_robots.py --verify-only --prefix intuitive

# Update regulatory data for Momentis robots only
python3 scripts/update_regulatory.py --prefix momentis

# Verify companies with Edge robots
python3 scripts/update_companies.py --verify-only --prefix edge
```

When `--prefix` is used, only matching entries are processed/validated, but **all entries are preserved** in the output file.

**Updating Regulatory Data:**

Use `scripts/update_regulatory.py` to normalize and enrich regulatory entries:

```bash
# Normalize existing regulatory data
python3 scripts/update_regulatory.py

# Enrich with external sources (FDA 510k, EUDAMED, press releases; internet required)
python3 scripts/update_regulatory.py --backup
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

  
