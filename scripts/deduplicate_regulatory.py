#!/usr/bin/env python3

import json
from pathlib import Path
import sys

def deduplicate_robots_json():
    """Deduplicate regulatory entries in robots.json"""
    json_path = Path('public/robots.json')
    if not json_path.exists():
        print(f"Error: {json_path} not found.", file=sys.stderr)
        return False

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
            print(f"Total removed duplicate entries from robots.json: {total_removed}\n")
        else:
            print("No duplicate regulatory entries found in robots.json.")
        
        return True
            
    except Exception as e:
        print(f"Error processing {json_path}: {e}", file=sys.stderr)
        return False

def deduplicate_rejected_regulatory():
    """Deduplicate entries in rejected-regulatory.json"""
    json_path = Path('public/rejected-regulatory.json')
    if not json_path.exists():
        print(f"Warning: {json_path} not found, skipping.", file=sys.stderr)
        return True

    try:
        data = json.loads(json_path.read_text())
        total_removed = 0
        
        for robot_id, entries in data.items():
            if not entries:
                continue
            
            unique_entries = []
            seen_urls = set()
            removed_count = 0
            
            for entry in entries:
                url = entry.get('url')
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    unique_entries.append(entry)
                else:
                    removed_count += 1
            
            if removed_count > 0:
                data[robot_id] = unique_entries
                total_removed += removed_count
                print(f"Removed {removed_count} duplicates from rejected entries for {robot_id}")
        
        if total_removed > 0:
            json_path.write_text(json.dumps(data, indent=2))
            print(f"Total removed duplicate entries from rejected-regulatory.json: {total_removed}\n")
        else:
            print("No duplicate entries found in rejected-regulatory.json.")
        
        return True
            
    except Exception as e:
        print(f"Error processing {json_path}: {e}", file=sys.stderr)
        return False

def main():
    success = True
    
    # Deduplicate robots.json
    if not deduplicate_robots_json():
        success = False
    
    # Deduplicate rejected-regulatory.json
    if not deduplicate_rejected_regulatory():
        success = False
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()

