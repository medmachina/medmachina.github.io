import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ROBOTS_DIR = REPO_ROOT / 'public' / 'robots'
OUTPUT_FILE = REPO_ROOT / 'public' / 'robots.json'

def build_robots():
    """Aggregates all JSON files in public/robots/ into public/robots.json."""
    if not ROBOTS_DIR.exists():
        print(f"Error: Directory {ROBOTS_DIR} does not exist.")
        sys.exit(1)

    robots = []
    json_files = sorted(ROBOTS_DIR.glob('*.json'))
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                robot = json.load(f)
                robots.append(robot)
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            sys.exit(1)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(robots, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"Successfully built {OUTPUT_FILE} with {len(robots)} robots from {ROBOTS_DIR}.")

def split_robots():
    """Splits public/robots.json into individual files in public/robots/<id>.json."""
    if not OUTPUT_FILE.exists():
        print(f"Error: File {OUTPUT_FILE} does not exist.")
        sys.exit(1)

    ROBOTS_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        robots = json.load(f)

    count = 0
    for robot in robots:
        robot_id = robot.get('id')
        if not robot_id:
            print(f"Warning: robot missing 'id': {robot.get('name')}")
            continue
        file_path = ROBOTS_DIR / f"{robot_id}.json"
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(robot, f, indent=2, ensure_ascii=False)
            f.write('\n')
        count += 1

    print(f"Successfully split {count} robots into {ROBOTS_DIR}.")

if __name__ == '__main__':
    if '--split' in sys.argv:
        split_robots()
    else:
        build_robots()
