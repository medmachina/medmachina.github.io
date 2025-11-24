#!/usr/bin/env python3
"""Clear all regulatory entries in public/robots.json.

Usage:
  python3 scripts/clear_regulatory.py --source public/robots.json --backup
"""
import json
from pathlib import Path
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--source', default='public/robots.json')
parser.add_argument('--backup', action='store_true')
args = parser.parse_args()

p = Path(args.source)
if not p.exists():
    print(f'{p} not found')
    raise SystemExit(1)

data = json.loads(p.read_text())
if args.backup:
    bak = p.with_suffix('.bak')
    bak.write_text(p.read_text())

changed = 0
for item in data:
    if isinstance(item, dict):
        if item.get('regulatory'):
            item['regulatory'] = []
            changed += 1
        else:
            # ensure field exists as empty list
            item['regulatory'] = []

p.write_text(json.dumps(data, indent=2))
print(f'Cleared regulatory entries for {changed} robots; ensured empty `regulatory` field for all {len(data)} robots.')
