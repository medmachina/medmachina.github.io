#!/usr/bin/env python3

import json
from pathlib import Path
import sys

def main():
    json_path = Path('public/robots.json')
    if not json_path.exists():
        print(f"Error: {json_path} not found.", file=sys.stderr)
        sys.exit(1)

    try:
        data = json.loads(json_path.read_text())
        total_removed = 0
        
        for robot in data:
            regulatory = robot.get('regulatory', [])
            if not regulatory:
                continue
                
            unique_entries = []
            seen_urls = set()
            removed_count = 0
            
            for entry in regulatory:
                url = entry.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_entries.append(entry)
                else:
                    removed_count += 1
            
            if removed_count > 0:
                robot['regulatory'] = unique_entries
                total_removed += removed_count
                print(f"Removed {removed_count} duplicates for {robot.get('name', 'unknown')}")
        
        if total_removed > 0:
            json_path.write_text(json.dumps(data, indent=2))
            print(f"\nTotal removed duplicate entries: {total_removed}")
        else:
            print("No duplicate regulatory entries found.")
            
    except Exception as e:
        print(f"Error processing {json_path}: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
