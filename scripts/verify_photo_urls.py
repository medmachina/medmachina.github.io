#!/usr/bin/env python3

import json
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlparse
import sys
from pathlib import Path

def is_valid_url(url):
    """Check if the URL is well-formed"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

# Timeout for HTTP requests (seconds)
TIMEOUT = 60

def check_url(url):
    """Check if a URL is accessible"""
    if not is_valid_url(url):
        return url, False, "Invalid URL format"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.head(url, allow_redirects=True, timeout=TIMEOUT, headers=headers)
        if response.status_code == 405:  # If HEAD method not allowed, try GET
            response = requests.get(url, allow_redirects=True, timeout=TIMEOUT, headers=headers)
        return url, response.status_code == 200, f"Status code: {response.status_code}"
    except requests.RequestException as e:
        return url, False, str(e)

def load_json_file(file_path):
    """Load and parse a JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def save_json_file(file_path, data):
    """Save data to a JSON file"""
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {file_path}: {e}")
        return False

def remove_invalid_urls(robots_data, broken_urls):
    """Remove invalid URLs from the robots data"""
    broken_urls_set = set(url for url, _, _ in broken_urls)
    changes_made = False
    
    for robot in robots_data:
        if 'photos' in robot:
            original_photos = robot['photos']
            valid_photos = [photo for photo in original_photos if photo['url'] not in broken_urls_set]
            if len(valid_photos) != len(original_photos):
                changes_made = True
                robot['photos'] = valid_photos
    
    return changes_made

def verify_urls(robots_data, companies_data):
    """Verify all photo URLs in the data"""
    all_urls = []
    url_sources = {}
    
    # Collect URLs from robots data
    for robot in robots_data:
        for photo in robot.get('photos', []):
            if photo and photo.get('url'):  # Only check non-empty URLs
                url = photo['url']
                all_urls.append(url)
                url_sources[url] = f"Robot: {robot['name']}"
    
    print(f"Found {len(all_urls)} URLs to verify")
    
    # Use ThreadPoolExecutor to check URLs concurrently
    results = []
    completed = 0
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {executor.submit(check_url, url): url for url in all_urls}
        for future in as_completed(future_to_url):
            results.append(future.result())
            completed += 1
            print(f"Progress: {completed}/{len(all_urls)} URLs checked")
    
    # Process and display results
    broken_links = []
    working_links = []
    
    for url, is_valid, message in results:
        if is_valid:
            working_links.append((url, message))
        else:
            broken_links.append((url, message, url_sources.get(url, "Unknown source")))
    
    # Print report
    print("\n=== URL Verification Report ===")
    print(f"\nTotal URLs checked: {len(results)}")
    print(f"Working URLs: {len(working_links)}")
    print(f"Broken URLs: {len(broken_links)}")
    
    if broken_links:
        print("\nBroken Links:")
        for url, message, source in broken_links:
            print(f"\nSource: {source}")
            print(f"URL: {url}")
            print(f"Error: {message}")
        
        # Ask user if they want to remove invalid URLs
        while True:
            response = input("\nWould you like to remove these invalid URLs from the robots.json file? (yes/no): ").lower()
            if response in ['yes', 'no']:
                if response == 'yes':
                    if remove_invalid_urls(robots_data, broken_links):
                        script_dir = Path(__file__).parent.parent
                        robots_path = script_dir / "public" / "robots.json"
                        if save_json_file(robots_path, robots_data):
                            print("Invalid URLs have been removed and robots.json has been updated.")
                        else:
                            print("Error: Failed to save changes to robots.json")
                    else:
                        print("No changes were necessary in robots.json")
                break
            print("Please answer 'yes' or 'no'")
    
    return len(broken_links) == 0

def print_photo_url_summary(robots_data):
    """Print a summary of photo URLs for each robot, sorted by count"""
    # Create a list of tuples (name, url_count, sites)
    robot_url_info = []
    for robot in robots_data:
        photo_count = len(robot.get('photos', []))
        sites = set(photo['site'] for photo in robot.get('photos', []) if 'site' in photo)
        robot_url_info.append((robot['name'], photo_count, sites))
    
    # Sort by URL count, then by name for same counts
    robot_url_info.sort(key=lambda x: (x[1], x[0]))
    
    print("\n=== Photo URL Count Summary ===")
    print("Robot Name".ljust(30), "Photos", "Sites")
    print("-" * 60)
    for name, count, sites in robot_url_info:
        sites_str = ", ".join(sorted(sites)) if sites else "N/A"
        print(f"{name[:29].ljust(30)} {str(count).ljust(6)} {sites_str}")

def validate_photo_structure(robots_data):
    """Validate that all photo entries have the required structure"""
    issues = []
    
    for robot in robots_data:
        if 'photos' not in robot:
            continue
            
        if not isinstance(robot['photos'], list):
            issues.append(f"Robot '{robot['name']}': 'photos' is not a list")
            continue
            
        for i, photo in enumerate(robot['photos']):
            if not isinstance(photo, dict):
                issues.append(f"Robot '{robot['name']}': photo {i} is not an object")
                continue
                
            if 'url' not in photo:
                issues.append(f"Robot '{robot['name']}': photo {i} missing 'url' field")
            
            if 'site' not in photo:
                issues.append(f"Robot '{robot['name']}': photo {i} missing 'site' field")
    
    if issues:
        print("\n=== Photo Structure Validation Issues ===")
        for issue in issues:
            print(f"- {issue}")
        return False
    
    return True

def main():
    # Get the script's directory
    script_dir = Path(__file__).parent.parent
    
    # Construct paths to JSON files
    robots_path = script_dir / "public" / "robots.json"
    companies_path = script_dir / "public" / "companies.json"
    
    # Load data
    robots_data = load_json_file(robots_path)
    companies_data = load_json_file(companies_path)
    
    if not robots_data or not companies_data:
        print("Failed to load JSON files")
        sys.exit(1)
        
    # Validate photo structure
    structure_valid = validate_photo_structure(robots_data)
    if not structure_valid:
        sys.exit(1)
    
    # Verify URLs
    all_valid = verify_urls(robots_data, companies_data)
    
    # Print summary of photo URLs
    print_photo_url_summary(robots_data)
    
    # Exit with appropriate status code
    sys.exit(0 if all_valid else 1)

if __name__ == "__main__":
    main()