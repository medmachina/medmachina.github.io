#!/usr/bin/env python3
"""
update_robot_videos.py

Validates and interactively updates video entries in public/robots.json.
- Checks videos[] structure and supported providers
- Extracts YouTube/Vimeo IDs and canonical URLs
- Reports missing titles, provider-title mismatches, and duplicate videos
- Optionally verifies video availability through oEmbed endpoints
- Offers an interactive keep/delete/rename workflow
- Offers an interactive search/preview/add workflow
- Supports polite search throttling and persisted rejected candidates
"""

import argparse
import json
import logging
import re
import shutil
import sys
import time
import webbrowser
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.parse import parse_qs, quote, quote_plus, unquote, urlparse

import requests
from bs4 import BeautifulSoup


logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).parent.parent
ROBOTS_FILE = REPO_ROOT / "public" / "robots.json"
REJECTED_VIDEOS_FILE = REPO_ROOT / "public" / "rejected-video.json"

DEFAULT_TIMEOUT = 20
DEFAULT_SEARCH_LIMIT = 5
DEFAULT_SEARCH_PROVIDERS = "youtube,vimeo"
DEFAULT_SEARCH_DELAY = 5.0
DEFAULT_SEARCH_BACKOFF = 60.0
DEFAULT_SEARCH_RETRIES = 1
MAX_VIDEOS_PER_ROBOT = 4
SUPPORTED_ADD_PROVIDERS = {"youtube", "vimeo"}
STATUS_PASS = "PASS"
STATUS_REVIEW = "REVIEW"
STATUS_FAIL = "FAIL"

YOUTUBE_ID_RE = re.compile(r"^[A-Za-z0-9_-]{11}$")
VIMEO_ID_RE = re.compile(r"^\d+$")

TOKEN_RE = re.compile(r"[a-z0-9]+")
TITLE_STOPWORDS = {
    "and",
    "for",
    "inc",
    "llc",
    "medical",
    "overview",
    "platform",
    "robot",
    "robotic",
    "robotics",
    "surgery",
    "surgical",
    "system",
    "technology",
    "the",
    "with",
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

SEARCH_PROVIDER_CONFIG = {
    "youtube": {
        "site": "youtube.com/watch",
        "label": "YouTube",
    },
    "vimeo": {
        "site": "vimeo.com",
        "label": "Vimeo",
    },
    "dailymotion": {
        "site": "dailymotion.com/video",
        "label": "Dailymotion",
    },
}

SEARCH_CONTEXT_TERMS = [
    "surgical robot",
    "robotic surgery",
    "system overview",
]


@dataclass
class ParsedVideo:
    provider: str
    video_id: str
    canonical_url: str


@dataclass
class VideoCheck:
    robot_id: str
    robot_name: str
    index: int
    url: str
    title: str = ""
    provider: str = ""
    video_id: str = ""
    canonical_url: str = ""
    metadata_title: str = ""
    metadata_author: str = ""
    issues: List[str] = field(default_factory=list)
    review_notes: List[str] = field(default_factory=list)

    @property
    def status(self) -> str:
        if self.issues:
            return STATUS_FAIL
        if self.review_notes:
            return STATUS_REVIEW
        return STATUS_PASS

    @property
    def duplicate_key(self) -> str:
        if self.provider and self.video_id:
            return f"{self.provider}:{self.video_id}"
        return self.url.strip().lower()


@dataclass
class InteractiveActions:
    deletes: List[Tuple[str, int]] = field(default_factory=list)
    renames: Dict[Tuple[str, int], str] = field(default_factory=dict)

    @property
    def has_changes(self) -> bool:
        return bool(self.deletes or self.renames)


@dataclass
class VideoCandidate:
    robot_id: str
    robot_name: str
    provider: str
    title: str
    url: str
    canonical_url: str
    query: str
    score: int
    matched_terms: List[str] = field(default_factory=list)


@dataclass
class VideoAddition:
    robot_id: str
    robot_name: str
    provider: str
    url: str
    title: str
    score: int


@dataclass
class RejectedVideo:
    robot_id: str
    robot_name: str
    provider: str
    url: str
    title: str
    score: int
    reason: str
    query: str


@dataclass
class SearchReviewActions:
    additions: List[VideoAddition] = field(default_factory=list)
    rejections: List[RejectedVideo] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.additions or self.rejections)


class SearchRateLimiter:
    def __init__(self, delay: float) -> None:
        self.delay = max(0.0, delay)
        self.last_request_at = 0.0

    def wait(self) -> None:
        if self.delay <= 0:
            return

        elapsed = time.monotonic() - self.last_request_at
        remaining = self.delay - elapsed
        if remaining > 0:
            logger.info(f"Sleeping {remaining:.1f}s before next search request")
            time.sleep(remaining)

    def mark_request(self) -> None:
        self.last_request_at = time.monotonic()


def load_robots(source_file: Path) -> List[Dict]:
    if not source_file.exists():
        logger.error(f"Source file not found: {source_file}")
        sys.exit(1)

    try:
        with open(source_file, "r", encoding="utf-8") as robots_file:
            data = json.load(robots_file)
    except json.JSONDecodeError as exc:
        logger.error(f"Error parsing {source_file}: {exc}")
        sys.exit(1)

    if not isinstance(data, list):
        logger.error(f"Expected {source_file} to contain a JSON array")
        sys.exit(1)

    return data


def load_rejected_videos(rejected_file: Path) -> Dict[str, List[Dict]]:
    if not rejected_file.exists():
        return {}

    try:
        with open(rejected_file, "r", encoding="utf-8") as input_file:
            data = json.load(input_file)
    except json.JSONDecodeError as exc:
        logger.error(f"Error parsing {rejected_file}: {exc}")
        sys.exit(1)

    if not isinstance(data, dict):
        logger.error(f"Expected {rejected_file} to contain a JSON object")
        sys.exit(1)

    cleaned: Dict[str, List[Dict]] = {}
    for robot_id, entries in data.items():
        if isinstance(robot_id, str) and isinstance(entries, list):
            cleaned[robot_id] = [entry for entry in entries if isinstance(entry, dict)]

    return cleaned


def write_rejected_videos(rejected_file: Path, rejected_data: Dict[str, List[Dict]]) -> None:
    rejected_file.parent.mkdir(parents=True, exist_ok=True)
    with open(rejected_file, "w", encoding="utf-8") as output:
        json.dump(rejected_data, output, indent=2, ensure_ascii=False)
        output.write("\n")

    logger.info(f"Updated rejected videos written to: {rejected_file}")


def normalize_host(hostname: Optional[str]) -> str:
    if not hostname:
        return ""
    host = hostname.lower()
    return host[4:] if host.startswith("www.") else host


def parse_youtube_url(parsed_url) -> Optional[ParsedVideo]:
    host = normalize_host(parsed_url.hostname)
    path_parts = [part for part in parsed_url.path.split("/") if part]
    query = parse_qs(parsed_url.query)
    video_id = ""

    if host == "youtu.be" and path_parts:
        video_id = path_parts[0]
    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com", "youtube-nocookie.com"}:
        if path_parts and path_parts[0] == "watch":
            video_id = query.get("v", [""])[0]
        elif len(path_parts) >= 2 and path_parts[0] in {"embed", "shorts", "live"}:
            video_id = path_parts[1]
        elif "v" in query:
            video_id = query.get("v", [""])[0]

    video_id = video_id.strip()
    if not video_id:
        return None

    canonical_url = f"https://www.youtube.com/watch?v={video_id}"
    return ParsedVideo("youtube", video_id, canonical_url)


def parse_vimeo_url(parsed_url) -> Optional[ParsedVideo]:
    host = normalize_host(parsed_url.hostname)
    if host not in {"vimeo.com", "player.vimeo.com"}:
        return None

    path_parts = [part for part in parsed_url.path.split("/") if part]
    if not path_parts:
        return None

    # Vimeo URLs can be /123456, /channels/name/123456, or /video/123456.
    for part in reversed(path_parts):
        if VIMEO_ID_RE.match(part):
            canonical_url = f"https://vimeo.com/{part}"
            return ParsedVideo("vimeo", part, canonical_url)

    return None


def parse_dailymotion_search_url(parsed_url) -> Optional[ParsedVideo]:
    host = normalize_host(parsed_url.hostname)
    if host not in {"dailymotion.com", "dai.ly"}:
        return None

    path_parts = [part for part in parsed_url.path.split("/") if part]
    if not path_parts:
        return None

    if host == "dai.ly":
        video_id = path_parts[0]
    elif len(path_parts) >= 2 and path_parts[0] == "video":
        video_id = path_parts[1]
    else:
        return None

    if not video_id:
        return None

    canonical_url = f"https://www.dailymotion.com/video/{video_id}"
    return ParsedVideo("dailymotion", video_id, canonical_url)


def parse_video_url(url: str) -> Tuple[Optional[ParsedVideo], Optional[str]]:
    if not isinstance(url, str) or not url.strip():
        return None, "missing video URL"

    try:
        parsed_url = urlparse(url.strip())
    except ValueError as exc:
        return None, f"invalid URL: {exc}"

    if parsed_url.scheme not in {"http", "https"}:
        return None, "URL must use http or https"

    host = normalize_host(parsed_url.hostname)
    if host in {"youtu.be", "youtube.com", "m.youtube.com", "music.youtube.com", "youtube-nocookie.com"}:
        parsed_video = parse_youtube_url(parsed_url)
        if not parsed_video:
            return None, "could not extract YouTube video ID"
        if not YOUTUBE_ID_RE.match(parsed_video.video_id):
            return None, f"invalid YouTube video ID: {parsed_video.video_id}"
        return parsed_video, None

    if host in {"vimeo.com", "player.vimeo.com"}:
        parsed_video = parse_vimeo_url(parsed_url)
        if not parsed_video:
            return None, "could not extract Vimeo video ID"
        return parsed_video, None

    return None, f"unsupported video provider: {host or '<missing host>'}"


def parse_search_candidate_url(url: str, provider: str) -> Optional[ParsedVideo]:
    try:
        parsed_url = urlparse(url.strip())
    except ValueError:
        return None

    if provider in {"youtube", "vimeo"}:
        parsed_video, parse_error = parse_video_url(url)
        if parse_error or not parsed_video or parsed_video.provider != provider:
            return None
        return parsed_video

    if provider == "dailymotion":
        return parse_dailymotion_search_url(parsed_url)

    return None


def meaningful_tokens(*values: object) -> List[str]:
    tokens = set()
    for value in values:
        if value is None:
            continue
        if isinstance(value, list):
            values_to_scan = value
        else:
            values_to_scan = [value]

        for item in values_to_scan:
            for token in TOKEN_RE.findall(str(item).lower()):
                if len(token) >= 3 and token not in TITLE_STOPWORDS:
                    tokens.add(token)

    return sorted(tokens)


def normalize_title_for_compare(value: str) -> str:
    return " ".join(TOKEN_RE.findall(value.lower()))


def add_metadata_title_note(check: VideoCheck) -> None:
    if not check.title or not check.metadata_title:
        return

    stored_title = normalize_title_for_compare(check.title)
    provider_title = normalize_title_for_compare(check.metadata_title)
    if stored_title != provider_title:
        check.review_notes.append("stored title differs from provider title")


def title_matches_robot(check: VideoCheck, robot: Dict) -> bool:
    title_text = f"{check.title} {check.metadata_title}".lower()
    if not title_text.strip():
        return False

    tokens = meaningful_tokens(robot.get("name"), robot.get("id"), robot.get("also_known_as"))
    return any(token in title_text for token in tokens)


def check_oembed(check: VideoCheck, timeout: int) -> None:
    if check.provider == "youtube":
        endpoint = (
            "https://www.youtube.com/oembed"
            f"?format=json&url={quote(check.canonical_url, safe='')}"
        )
    elif check.provider == "vimeo":
        endpoint = (
            "https://vimeo.com/api/oembed.json"
            f"?url={quote(check.canonical_url, safe='')}"
        )
    else:
        return

    try:
        response = requests.get(endpoint, timeout=timeout, headers=HEADERS)
    except requests.RequestException as exc:
        check.review_notes.append(f"oEmbed request failed: {exc}")
        return

    if response.status_code >= 400:
        check.issues.append(f"oEmbed returned HTTP {response.status_code}")
        return

    try:
        metadata = response.json()
    except ValueError:
        check.issues.append("oEmbed returned invalid JSON")
        return

    check.metadata_title = metadata.get("title") or ""
    check.metadata_author = metadata.get("author_name") or ""


def collect_video_checks(robots_data: List[Dict], timeout: int, no_network: bool) -> List[VideoCheck]:
    checks: List[VideoCheck] = []

    for robot in robots_data:
        robot_id = robot.get("id", "<missing id>")
        robot_name = robot.get("name", "<missing name>")
        videos = robot.get("videos")

        if videos is None:
            continue

        if not isinstance(videos, list):
            check = VideoCheck(robot_id, robot_name, -1, "")
            check.issues.append("videos is not an array")
            checks.append(check)
            continue

        if len(videos) > MAX_VIDEOS_PER_ROBOT:
            check = VideoCheck(robot_id, robot_name, -1, "")
            check.issues.append(f"videos has {len(videos)} items; maximum is {MAX_VIDEOS_PER_ROBOT}")
            checks.append(check)

        for index, video in enumerate(videos):
            if not isinstance(video, dict):
                check = VideoCheck(robot_id, robot_name, index, "")
                check.issues.append("video entry is not an object")
                checks.append(check)
                continue

            check = VideoCheck(
                robot_id=robot_id,
                robot_name=robot_name,
                index=index,
                url=video.get("url", ""),
                title=video.get("title", ""),
            )

            parsed_video, parse_error = parse_video_url(check.url)
            if parse_error:
                check.issues.append(parse_error)
            else:
                check.provider = parsed_video.provider
                check.video_id = parsed_video.video_id
                check.canonical_url = parsed_video.canonical_url

            if not check.title:
                check.review_notes.append("missing title")

            if parsed_video and not no_network:
                check_oembed(check, timeout)
                add_metadata_title_note(check)

            if parsed_video and not title_matches_robot(check, robot):
                check.review_notes.append("title does not clearly match robot name/id")

            checks.append(check)

    add_duplicate_notes(checks)
    return checks


def add_duplicate_notes(checks: List[VideoCheck]) -> None:
    by_key: Dict[str, List[VideoCheck]] = {}
    for check in checks:
        if check.index < 0:
            continue
        by_key.setdefault(check.duplicate_key, []).append(check)

    for duplicates in by_key.values():
        if len(duplicates) < 2:
            continue

        locations = [
            f"{duplicate.robot_id}[{duplicate.index}]"
            for duplicate in duplicates
        ]
        robot_ids = {duplicate.robot_id for duplicate in duplicates}
        note = f"duplicate video also appears at {', '.join(locations)}"

        for duplicate in duplicates:
            if len(robot_ids) == 1:
                duplicate.issues.append(note)
            else:
                duplicate.review_notes.append(note)


def apply_prefix_filter(robots_data: List[Dict], prefix: Optional[str]) -> List[Dict]:
    if not prefix:
        return robots_data

    prefix_lower = prefix.lower()
    return [
        robot for robot in robots_data
        if str(robot.get("id", "")).lower().startswith(prefix_lower)
    ]


def parse_provider_list(provider_arg: str) -> List[str]:
    providers = []
    for provider in provider_arg.split(","):
        normalized = provider.strip().lower()
        if not normalized:
            continue
        if normalized not in SEARCH_PROVIDER_CONFIG:
            valid = ", ".join(sorted(SEARCH_PROVIDER_CONFIG))
            logger.error(f"Unsupported search provider '{normalized}'. Valid providers: {valid}")
            sys.exit(2)
        if normalized not in providers:
            providers.append(normalized)

    if not providers:
        logger.error("At least one search provider is required")
        sys.exit(2)

    return providers


def existing_video_keys(robot: Dict) -> set:
    keys = set()
    videos = robot.get("videos") or []
    if not isinstance(videos, list):
        return keys

    for video in videos:
        if not isinstance(video, dict):
            continue

        url = video.get("url")
        if not url:
            continue

        parsed_video, parse_error = parse_video_url(url)
        if not parse_error and parsed_video:
            keys.add(f"{parsed_video.provider}:{parsed_video.video_id}")
            keys.add(parsed_video.canonical_url.strip().lower())
        keys.add(str(url).strip().lower())

    return keys


def rejected_video_keys(rejected_data: Dict[str, List[Dict]], robot_id: str) -> set:
    keys = set()
    for entry in rejected_data.get(robot_id, []):
        if not isinstance(entry, dict):
            continue

        url = entry.get("url")
        if not url:
            continue

        parsed_video, parse_error = parse_video_url(url)
        if not parse_error and parsed_video:
            keys.add(f"{parsed_video.provider}:{parsed_video.video_id}")
            keys.add(parsed_video.canonical_url.strip().lower())
        keys.add(str(url).strip().lower())

    return keys


def rejected_entry_key(entry: Dict) -> str:
    url = entry.get("url")
    if not url:
        return ""

    parsed_video, parse_error = parse_video_url(url)
    if not parse_error and parsed_video:
        return f"{parsed_video.provider}:{parsed_video.video_id}"

    return str(url).strip().lower()


def robot_search_phrases(robot: Dict) -> List[str]:
    phrases = []
    aliases = robot.get("also_known_as") or []
    if not isinstance(aliases, list):
        aliases = []

    for value in [robot.get("name"), *aliases]:
        if isinstance(value, str) and value.strip() and value.strip() not in phrases:
            phrases.append(value.strip())

    robot_id = robot.get("id")
    if isinstance(robot_id, str):
        readable_id = robot_id.replace("_", " ").replace("-", " ").replace("&", " ")
        readable_id = " ".join(readable_id.split())
        if readable_id and readable_id not in phrases:
            phrases.append(readable_id)

    return phrases


def quote_query_phrase(value: str) -> str:
    escaped = value.replace('"', "")
    return f'"{escaped}"'


def build_search_queries(robot: Dict, provider: str, query_limit: int) -> List[str]:
    site = SEARCH_PROVIDER_CONFIG[provider]["site"]
    phrases = robot_search_phrases(robot)
    queries = []

    for context in SEARCH_CONTEXT_TERMS:
        for phrase in phrases:
            query = f"site:{site} {quote_query_phrase(phrase)} {quote_query_phrase(context)}"
            if query not in queries:
                queries.append(query)
            if len(queries) >= query_limit:
                return queries

    return queries


def unwrap_search_result_url(href: str) -> str:
    if not href:
        return ""

    if href.startswith("//"):
        href = f"https:{href}"

    parsed = urlparse(href)
    if parsed.netloc.endswith("duckduckgo.com") or parsed.path.startswith("/l/"):
        query_values = parse_qs(parsed.query)
        if "uddg" in query_values and query_values["uddg"]:
            return unquote(query_values["uddg"][0])

    return href


def get_search_response(
    url: str,
    timeout: int,
    rate_limiter: SearchRateLimiter,
    backoff: float,
    retries: int,
    label: str,
) -> Optional[requests.Response]:
    attempts = max(0, retries) + 1
    for attempt in range(1, attempts + 1):
        rate_limiter.wait()
        try:
            response = requests.get(url, timeout=timeout, headers=HEADERS)
            rate_limiter.mark_request()
        except requests.RequestException as exc:
            rate_limiter.mark_request()
            logger.warning(f"{label} request failed: {exc}")
            return None

        if response.status_code not in {403, 429}:
            return response

        if attempt >= attempts:
            return response

        sleep_for = max(0.0, backoff)
        logger.warning(
            f"{label} returned HTTP {response.status_code}; "
            f"sleeping {sleep_for:.1f}s before retry {attempt + 1}/{attempts}"
        )
        if sleep_for > 0:
            time.sleep(sleep_for)

    return None


def search_duckduckgo(
    query: str,
    timeout: int,
    result_limit: int,
    rate_limiter: SearchRateLimiter,
    backoff: float,
    retries: int,
) -> List[Tuple[str, str]]:
    search_url = f"https://duckduckgo.com/html/?q={quote_plus(query)}"
    response = get_search_response(
        search_url,
        timeout,
        rate_limiter,
        backoff,
        retries,
        f"DuckDuckGo search for {query}",
    )
    if response is None:
        return []

    if response.status_code >= 400:
        logger.warning(f"Search request returned HTTP {response.status_code} for {query}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    anchors = soup.select("a.result__a")
    if not anchors:
        anchors = soup.find_all("a")

    seen_urls = set()
    for anchor in anchors:
        title = anchor.get_text(" ", strip=True)
        url = unwrap_search_result_url(anchor.get("href", ""))
        if not title or not url:
            continue

        normalized_url = url.strip().lower()
        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        results.append((title, url))
        if len(results) >= result_limit:
            break

    return results


def extract_json_object_after_marker(text: str, marker: str) -> Optional[Dict]:
    start = text.find(marker)
    if start < 0:
        return None

    brace_start = text.find("{", start + len(marker))
    if brace_start < 0:
        return None

    depth = 0
    in_string = False
    escaped = False

    for index in range(brace_start, len(text)):
        char = text[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(text[brace_start:index + 1])
                except json.JSONDecodeError:
                    return None

    return None


def walk_json(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_json(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_json(child)


def text_from_runs(value: Dict) -> str:
    if not isinstance(value, dict):
        return ""
    if isinstance(value.get("simpleText"), str):
        return value["simpleText"]
    runs = value.get("runs")
    if isinstance(runs, list):
        return "".join(
            run.get("text", "")
            for run in runs
            if isinstance(run, dict)
        ).strip()
    return ""


def search_youtube_direct(
    query: str,
    timeout: int,
    result_limit: int,
    rate_limiter: SearchRateLimiter,
    backoff: float,
    retries: int,
) -> List[Tuple[str, str]]:
    search_url = f"https://www.youtube.com/results?search_query={quote_plus(query)}"
    response = get_search_response(
        search_url,
        timeout,
        rate_limiter,
        backoff,
        retries,
        f"YouTube search for {query}",
    )
    if response is None:
        return []

    if response.status_code >= 400:
        logger.warning(f"YouTube search request returned HTTP {response.status_code} for {query}")
        return []

    initial_data = extract_json_object_after_marker(response.text, "var ytInitialData =")
    if not initial_data:
        initial_data = extract_json_object_after_marker(response.text, "ytInitialData =")
    if not initial_data:
        return []

    results = []
    seen_video_ids = set()
    for node in walk_json(initial_data):
        renderer = node.get("videoRenderer")
        if not isinstance(renderer, dict):
            continue

        video_id = renderer.get("videoId")
        if not isinstance(video_id, str) or not YOUTUBE_ID_RE.match(video_id):
            continue
        if video_id in seen_video_ids:
            continue

        title = text_from_runs(renderer.get("title", {}))
        if not title:
            title = f"YouTube video {video_id}"

        seen_video_ids.add(video_id)
        results.append((title, f"https://www.youtube.com/watch?v={video_id}"))
        if len(results) >= result_limit:
            break

    return results


def search_provider_results(
    provider: str,
    query: str,
    timeout: int,
    result_limit: int,
    rate_limiter: SearchRateLimiter,
    backoff: float,
    retries: int,
) -> List[Tuple[str, str]]:
    if provider == "youtube":
        youtube_query = re.sub(r"\bsite:\S+", "", query).strip()
        results = search_youtube_direct(
            youtube_query,
            timeout,
            result_limit,
            rate_limiter,
            backoff,
            retries,
        )
        if results:
            return results

    return search_duckduckgo(
        query,
        timeout,
        result_limit,
        rate_limiter,
        backoff,
        retries,
    )


def score_candidate(robot: Dict, title: str, url: str) -> Tuple[int, List[str]]:
    haystack = f"{title} {url}".lower()
    score = 0
    matched_terms = []

    def add_matched_term(term: str) -> None:
        if not any(existing.lower() == term.lower() for existing in matched_terms):
            matched_terms.append(term)

    robot_name = robot.get("name")
    if isinstance(robot_name, str) and robot_name.strip():
        normalized_name = robot_name.strip().lower()
        if normalized_name in haystack:
            score += 8
            add_matched_term(robot_name.strip())

    aliases = robot.get("also_known_as") or []
    if not isinstance(aliases, list):
        aliases = []

    for alias in aliases:
        if not isinstance(alias, str) or not alias.strip():
            continue
        normalized_alias = alias.strip().lower()
        if normalized_alias in haystack:
            score += 5
            add_matched_term(alias.strip())

    token_values = [
        robot.get("name"),
        aliases,
        str(robot.get("id", "")).replace("_", " "),
    ]
    for token in meaningful_tokens(*token_values):
        if token in haystack:
            score += 2
            add_matched_term(token)

    for context_token in ["surgical", "surgery", "robot", "robotic", "overview", "system"]:
        if context_token in haystack:
            score += 1

    return score, matched_terms


def search_video_candidates(
    robots_data: List[Dict],
    providers: List[str],
    timeout: int,
    candidate_limit: int,
    query_limit: int,
    result_limit: int,
    min_score: int,
    rejected_data: Dict[str, List[Dict]],
    search_delay: float,
    search_backoff: float,
    search_retries: int,
) -> List[VideoCandidate]:
    candidates: List[VideoCandidate] = []
    rate_limiter = SearchRateLimiter(search_delay)

    logger.info(
        f"Searching {len(robots_data)} robots across providers: "
        f"{', '.join(providers)}"
    )

    for robot_index, robot in enumerate(robots_data, start=1):
        robot_id = robot.get("id", "<missing id>")
        robot_name = robot.get("name", "<missing name>")
        existing_keys = existing_video_keys(robot)
        rejected_keys = rejected_video_keys(rejected_data, str(robot_id))
        robot_candidates: Dict[str, VideoCandidate] = {}

        logger.info(f"Search progress: {robot_index}/{len(robots_data)} {robot_id}")

        for provider in providers:
            queries = build_search_queries(robot, provider, query_limit)
            for query in queries:
                for title, url in search_provider_results(
                    provider,
                    query,
                    timeout,
                    result_limit,
                    rate_limiter,
                    search_backoff,
                    search_retries,
                ):
                    parsed_video = parse_search_candidate_url(url, provider)
                    if not parsed_video:
                        continue

                    candidate_key = f"{parsed_video.provider}:{parsed_video.video_id}"
                    if candidate_key in existing_keys:
                        continue
                    if parsed_video.canonical_url.strip().lower() in existing_keys:
                        continue
                    if candidate_key in rejected_keys:
                        continue
                    if parsed_video.canonical_url.strip().lower() in rejected_keys:
                        continue

                    score, matched_terms = score_candidate(robot, title, url)
                    if score < min_score:
                        continue

                    candidate = VideoCandidate(
                        robot_id=robot_id,
                        robot_name=robot_name,
                        provider=provider,
                        title=title,
                        url=url,
                        canonical_url=parsed_video.canonical_url,
                        query=query,
                        score=score,
                        matched_terms=matched_terms,
                    )

                    existing_candidate = robot_candidates.get(candidate_key)
                    if not existing_candidate or candidate.score > existing_candidate.score:
                        robot_candidates[candidate_key] = candidate

        ranked = sorted(
            robot_candidates.values(),
            key=lambda candidate: (-candidate.score, candidate.provider, candidate.title.lower()),
        )
        candidates.extend(ranked[:candidate_limit])

    return candidates


def print_search_results(candidates: List[VideoCandidate]) -> None:
    logger.info("\n=== Video Search Candidates ===")

    if not candidates:
        logger.info("No candidates found.")
        return

    current_robot_key = None
    for candidate in candidates:
        robot_key = (candidate.robot_id, candidate.robot_name)
        if robot_key != current_robot_key:
            current_robot_key = robot_key
            logger.info(f"\n{candidate.robot_id} - {candidate.robot_name}")

        provider_label = SEARCH_PROVIDER_CONFIG[candidate.provider]["label"]
        matched = ", ".join(candidate.matched_terms) if candidate.matched_terms else "none"
        logger.info(f"  [{provider_label}] score={candidate.score} matched={matched}")
        logger.info(f"    title: {candidate.title}")
        logger.info(f"    url: {candidate.canonical_url}")
        if candidate.canonical_url != candidate.url:
            logger.info(f"    found: {candidate.url}")
        logger.info(f"    query: {candidate.query}")


def robot_video_count(robot: Dict) -> int:
    videos = robot.get("videos") or []
    return len(videos) if isinstance(videos, list) else 0


def robot_video_capacity(robots_data: List[Dict]) -> Dict[str, int]:
    capacity = {}
    for robot in robots_data:
        robot_id = str(robot.get("id", ""))
        capacity[robot_id] = max(0, MAX_VIDEOS_PER_ROBOT - robot_video_count(robot))
    return capacity


def print_candidate_detail(candidate: VideoCandidate) -> None:
    provider_label = SEARCH_PROVIDER_CONFIG[candidate.provider]["label"]
    matched = ", ".join(candidate.matched_terms) if candidate.matched_terms else "none"

    logger.info(f"\n{candidate.robot_id} - {candidate.robot_name}")
    logger.info(f"  [{provider_label}] score={candidate.score} matched={matched}")
    logger.info(f"  title: {candidate.title}")
    logger.info(f"  url: {candidate.canonical_url}")
    if candidate.canonical_url != candidate.url:
        logger.info(f"  found: {candidate.url}")
    logger.info(f"  query: {candidate.query}")


def prompt_candidate_title(candidate: VideoCandidate) -> Optional[str]:
    try:
        raw = input(f"New title [{candidate.title}]: ").strip()
    except EOFError:
        logger.info("")
        return None

    return raw or candidate.title


def rejected_video_from_candidate(candidate: VideoCandidate, reason: str) -> RejectedVideo:
    return RejectedVideo(
        robot_id=candidate.robot_id,
        robot_name=candidate.robot_name,
        provider=candidate.provider,
        url=candidate.canonical_url,
        title=candidate.title,
        score=candidate.score,
        reason=reason,
        query=candidate.query,
    )


def collect_search_additions(
    candidates: List[VideoCandidate],
    robots_data: List[Dict],
    no_open: bool,
) -> SearchReviewActions:
    actions = SearchReviewActions()

    if not candidates:
        logger.info("\nNo search candidates to review.")
        return actions

    capacity = robot_video_capacity(robots_data)

    logger.info("\n=== Interactive Search Review ===")
    logger.info("Choices: (a)dd, (r)ename+add, (s)kip, (x)reject, or (q)uit")

    for candidate in candidates:
        print_candidate_detail(candidate)

        if candidate.provider not in SUPPORTED_ADD_PROVIDERS:
            logger.info(
                "  This provider is search-only for now; the app currently embeds YouTube/Vimeo."
            )
            choice = prompt_choice("Choice [(s)kip/(x)reject/(q)uit]: ", "sxq", "s")
            if choice == "x":
                actions.rejections.append(rejected_video_from_candidate(candidate, "unsupported provider"))
            if choice == "q":
                break
            continue

        remaining_slots = capacity.get(candidate.robot_id, 0)
        if remaining_slots <= 0:
            logger.info(
                f"  Cannot add: this robot already has {MAX_VIDEOS_PER_ROBOT} videos."
            )
            choice = prompt_choice("Choice [(s)kip/(x)reject/(q)uit]: ", "sxq", "s")
            if choice == "x":
                actions.rejections.append(rejected_video_from_candidate(candidate, "not relevant"))
            if choice == "q":
                break
            continue

        open_url_for_preview(candidate.canonical_url, no_open)
        choice = prompt_choice("Choice [(a)dd/(r)ename+add/(s)kip/(x)reject/(q)uit]: ", "arsxq", "s")

        if choice == "q":
            break
        if choice == "s":
            continue
        if choice == "x":
            actions.rejections.append(rejected_video_from_candidate(candidate, "not relevant"))
            continue

        title = candidate.title
        if choice == "r":
            new_title = prompt_candidate_title(candidate)
            if not new_title:
                logger.info("No title entered; skipping candidate.")
                continue
            title = new_title

        actions.additions.append(
            VideoAddition(
                robot_id=candidate.robot_id,
                robot_name=candidate.robot_name,
                provider=candidate.provider,
                url=candidate.canonical_url,
                title=title,
                score=candidate.score,
            )
        )
        capacity[candidate.robot_id] = remaining_slots - 1

    return actions


def print_addition_summary(additions: List[VideoAddition]) -> None:
    logger.info("\n=== Selected Additions ===")
    if not additions:
        logger.info("No videos selected for addition.")
        return

    for addition in additions:
        provider_label = SEARCH_PROVIDER_CONFIG[addition.provider]["label"]
        logger.info(f"Add: {addition.robot_id} - {provider_label} score={addition.score}")
        logger.info(f"  title: {addition.title}")
        logger.info(f"  url: {addition.url}")


def print_rejection_summary(rejections: List[RejectedVideo]) -> None:
    logger.info("\n=== Selected Rejections ===")
    if not rejections:
        logger.info("No videos selected for rejection.")
        return

    for rejection in rejections:
        provider_label = SEARCH_PROVIDER_CONFIG[rejection.provider]["label"]
        logger.info(f"Reject: {rejection.robot_id} - {provider_label} score={rejection.score}")
        logger.info(f"  title: {rejection.title}")
        logger.info(f"  url: {rejection.url}")
        logger.info(f"  reason: {rejection.reason}")


def apply_rejected_videos(
    rejected_data: Dict[str, List[Dict]],
    rejections: List[RejectedVideo],
) -> None:
    rejected_at = date.today().isoformat()

    for rejection in rejections:
        entries = rejected_data.setdefault(rejection.robot_id, [])
        existing_keys = {
            rejected_entry_key(entry)
            for entry in entries
            if isinstance(entry, dict)
        }

        entry = {
            "url": rejection.url,
            "title": rejection.title,
            "provider": rejection.provider,
            "reason": rejection.reason,
            "score": rejection.score,
            "query": rejection.query,
            "rejected_at": rejected_at,
        }
        entry_key = rejected_entry_key(entry)

        if entry_key in existing_keys:
            for existing_entry in entries:
                if rejected_entry_key(existing_entry) == entry_key:
                    existing_entry.update(entry)
                    break
            continue

        entries.append(entry)


def sort_robot_videos_by_relevance(robot: Dict) -> None:
    videos = robot.get("videos")
    if not isinstance(videos, list):
        return

    scored_videos = []
    for index, video in enumerate(videos):
        if not isinstance(video, dict):
            scored_videos.append((0, index, video))
            continue

        title = video.get("title") or ""
        url = video.get("url") or ""
        score, _ = score_candidate(robot, title, url)
        scored_videos.append((score, index, video))

    scored_videos.sort(key=lambda item: (-item[0], item[1]))
    robot["videos"] = [video for _, _, video in scored_videos]


def apply_search_additions(robots_data: List[Dict], additions: List[VideoAddition]) -> None:
    additions_by_robot: Dict[str, List[VideoAddition]] = {}
    for addition in additions:
        additions_by_robot.setdefault(addition.robot_id, []).append(addition)

    for robot in robots_data:
        robot_id = str(robot.get("id", ""))
        robot_additions = additions_by_robot.get(robot_id)
        if not robot_additions:
            continue

        videos = robot.get("videos")
        if not isinstance(videos, list):
            videos = []
            robot["videos"] = videos

        existing_keys = existing_video_keys(robot)
        sorted_additions = sorted(
            robot_additions,
            key=lambda addition: (-addition.score, addition.provider, addition.title.lower()),
        )

        for addition in sorted_additions:
            if len(videos) >= MAX_VIDEOS_PER_ROBOT:
                logger.warning(
                    f"Skipping {addition.robot_id}: maximum of {MAX_VIDEOS_PER_ROBOT} videos reached"
                )
                continue

            parsed_video, parse_error = parse_video_url(addition.url)
            candidate_key = ""
            if not parse_error and parsed_video:
                candidate_key = f"{parsed_video.provider}:{parsed_video.video_id}"

            if candidate_key and candidate_key in existing_keys:
                logger.warning(f"Skipping duplicate video for {addition.robot_id}: {addition.url}")
                continue

            videos.append({
                "url": addition.url,
                "title": addition.title,
            })
            if candidate_key:
                existing_keys.add(candidate_key)
            existing_keys.add(addition.url.strip().lower())

        sort_robot_videos_by_relevance(robot)


def run_search_interactive_mode(
    candidates: List[VideoCandidate],
    robots_data: List[Dict],
    rejected_data: Dict[str, List[Dict]],
    output_file: Path,
    rejected_file: Path,
    backup: bool,
    no_open: bool,
) -> Tuple[bool, bool]:
    actions = collect_search_additions(candidates, robots_data, no_open)
    print_addition_summary(actions.additions)
    print_rejection_summary(actions.rejections)

    if not actions.has_changes:
        return False, False

    targets = []
    if actions.additions:
        targets.append(str(output_file))
    if actions.rejections:
        targets.append(str(rejected_file))

    choice = prompt_choice(
        f"Write selected changes to {' and '.join(targets)}? [(y)es/(n)o]: ",
        "yn",
        "n",
    )
    if choice != "y":
        logger.info("No search changes written.")
        return False, False

    if actions.additions:
        apply_search_additions(robots_data, actions.additions)
        write_robots(output_file, robots_data, backup=backup)

    if actions.rejections:
        apply_rejected_videos(rejected_data, actions.rejections)
        write_rejected_videos(rejected_file, rejected_data)

    return True, bool(actions.additions)


def print_summary(checks: List[VideoCheck], show_passed: bool) -> None:
    pass_count = sum(1 for check in checks if check.status == STATUS_PASS)
    review_count = sum(1 for check in checks if check.status == STATUS_REVIEW)
    fail_count = sum(1 for check in checks if check.status == STATUS_FAIL)

    logger.info("\n=== Video Validation Summary ===")
    logger.info(f"PASS:   {pass_count}")
    logger.info(f"REVIEW: {review_count}")
    logger.info(f"FAIL:   {fail_count}")

    details = [
        check for check in checks
        if show_passed or check.status != STATUS_PASS
    ]

    if not details:
        return

    logger.info("\n=== Details ===")
    for check in details:
        location = f"{check.robot_id}[{check.index}]" if check.index >= 0 else check.robot_id
        title = check.title or "<missing title>"
        logger.info(f"{check.status} {location} {check.robot_name}")
        if check.url:
            logger.info(f"  url: {check.url}")
        if check.canonical_url and check.canonical_url != check.url:
            logger.info(f"  canonical: {check.canonical_url}")
        if check.provider:
            logger.info(f"  provider: {check.provider} ({check.video_id})")
        logger.info(f"  title: {title}")
        if check.metadata_title:
            logger.info(f"  oEmbed title: {check.metadata_title}")
        if check.metadata_author:
            logger.info(f"  oEmbed author: {check.metadata_author}")
        for issue in check.issues:
            logger.info(f"  fail: {issue}")
        for note in check.review_notes:
            logger.info(f"  review: {note}")


def print_check_detail(check: VideoCheck) -> None:
    location = f"{check.robot_id}[{check.index}]" if check.index >= 0 else check.robot_id
    title = check.title or "<missing title>"

    logger.info(f"\n{check.status} {location} {check.robot_name}")
    if check.url:
        logger.info(f"  url: {check.url}")
    if check.canonical_url and check.canonical_url != check.url:
        logger.info(f"  canonical: {check.canonical_url}")
    if check.provider:
        logger.info(f"  provider: {check.provider} ({check.video_id})")
    logger.info(f"  title: {title}")
    if check.metadata_title:
        logger.info(f"  oEmbed title: {check.metadata_title}")
    if check.metadata_author:
        logger.info(f"  oEmbed author: {check.metadata_author}")
    for issue in check.issues:
        logger.info(f"  fail: {issue}")
    for note in check.review_notes:
        logger.info(f"  review: {note}")


def prompt_choice(prompt: str, valid_choices: str, default: str) -> str:
    valid = {choice.lower() for choice in valid_choices}
    default = default.lower()

    while True:
        try:
            raw = input(prompt).strip().lower()
        except EOFError:
            logger.info("")
            return default

        if not raw:
            return default

        choice = raw[0]
        if choice in valid:
            return choice

        logger.info(f"Please enter one of: {', '.join(sorted(valid))}")


def prompt_title(check: VideoCheck) -> Optional[str]:
    suggested_title = check.metadata_title or check.title
    if suggested_title:
        prompt = f"New title [{suggested_title}]: "
    else:
        prompt = "New title: "

    try:
        raw = input(prompt).strip()
    except EOFError:
        logger.info("")
        return None

    if raw:
        return raw

    if suggested_title:
        return suggested_title

    logger.info("No title entered; keeping existing title.")
    return None


def open_url_for_preview(url: str, no_open: bool) -> None:
    if not url:
        return

    if no_open:
        logger.info(f"Preview disabled; URL: {url}")
        return

    logger.info(f"Opening in browser: {url}")
    opened = webbrowser.open(url, new=2)
    if not opened:
        logger.info("Browser open request was not accepted; paste the URL manually if needed.")


def open_video_for_review(check: VideoCheck, no_open: bool) -> None:
    open_url_for_preview(check.canonical_url or check.url, no_open)


def collect_interactive_actions(checks: List[VideoCheck], no_open: bool) -> InteractiveActions:
    actions = InteractiveActions()
    actionable_checks = [
        check for check in checks
        if check.status in {STATUS_FAIL, STATUS_REVIEW}
    ]

    if not actionable_checks:
        logger.info("\nNo FAIL or REVIEW video entries to process interactively.")
        return actions

    logger.info("\n=== Interactive Video Review ===")
    logger.info("FAIL choices: (k)eep or (d)elete")
    logger.info("REVIEW choices: (k)eep, (d)elete, or (r)ename")

    ordered_checks = [
        check for check in actionable_checks if check.status == STATUS_FAIL
    ] + [
        check for check in actionable_checks if check.status == STATUS_REVIEW
    ]

    for check in ordered_checks:
        print_check_detail(check)

        if check.index < 0:
            logger.info("  This is a structural issue; edit the JSON manually if needed.")
            continue

        key = (check.robot_id, check.index)

        if check.status == STATUS_FAIL:
            choice = prompt_choice("Choice [(k)eep/(d)elete]: ", "kd", "k")
            if choice == "d":
                actions.deletes.append(key)
            continue

        open_video_for_review(check, no_open)
        choice = prompt_choice("Choice [(k)eep/(d)elete/(r)ename]: ", "kdr", "k")
        if choice == "d":
            actions.deletes.append(key)
        elif choice == "r":
            new_title = prompt_title(check)
            if new_title:
                actions.renames[key] = new_title

    return actions


def apply_interactive_actions(robots_data: List[Dict], actions: InteractiveActions) -> None:
    deletes_by_robot: Dict[str, List[int]] = {}
    for robot_id, index in actions.deletes:
        deletes_by_robot.setdefault(robot_id, []).append(index)

    renames_by_robot: Dict[str, Dict[int, str]] = {}
    for (robot_id, index), title in actions.renames.items():
        renames_by_robot.setdefault(robot_id, {})[index] = title

    for robot in robots_data:
        robot_id = str(robot.get("id", ""))
        videos = robot.get("videos")
        if not isinstance(videos, list):
            continue

        delete_indexes = set(deletes_by_robot.get(robot_id, []))
        rename_map = renames_by_robot.get(robot_id, {})

        for index, title in sorted(rename_map.items()):
            if index in delete_indexes:
                continue
            if 0 <= index < len(videos) and isinstance(videos[index], dict):
                videos[index]["title"] = title

        for index in sorted(delete_indexes, reverse=True):
            if 0 <= index < len(videos):
                del videos[index]

        if not videos:
            del robot["videos"]


def print_action_summary(actions: InteractiveActions) -> None:
    logger.info("\n=== Selected Changes ===")
    if not actions.has_changes:
        logger.info("No changes selected.")
        return

    for robot_id, index in actions.deletes:
        logger.info(f"Delete: {robot_id}[{index}]")

    for (robot_id, index), title in actions.renames.items():
        logger.info(f"Rename: {robot_id}[{index}] -> {title}")


def create_backup(output_file: Path) -> None:
    if not output_file.exists():
        return

    if output_file.suffix:
        backup_file = output_file.with_suffix(f"{output_file.suffix}.bak")
    else:
        backup_file = output_file.with_name(f"{output_file.name}.bak")

    shutil.copy2(output_file, backup_file)
    logger.info(f"Backup created: {backup_file}")


def write_robots(output_file: Path, robots_data: List[Dict], backup: bool) -> None:
    if backup:
        create_backup(output_file)

    with open(output_file, "w", encoding="utf-8") as output:
        json.dump(robots_data, output, indent=2, ensure_ascii=False)
        output.write("\n")

    logger.info(f"Updated robots written to: {output_file}")


def run_interactive_mode(
    checks: List[VideoCheck],
    robots_data: List[Dict],
    output_file: Path,
    backup: bool,
    no_open: bool,
) -> bool:
    actions = collect_interactive_actions(checks, no_open)
    print_action_summary(actions)

    if not actions.has_changes:
        return False

    choice = prompt_choice(f"Write selected changes to {output_file}? [(y)es/(n)o]: ", "yn", "n")
    if choice != "y":
        logger.info("No changes written.")
        return False

    apply_interactive_actions(robots_data, actions)
    write_robots(output_file, robots_data, backup=backup)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate and interactively update video entries in robots.json"
    )
    parser.add_argument(
        "--source",
        type=Path,
        default=ROBOTS_FILE,
        help="Path to robots.json file (default: public/robots.json)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file for interactive changes (default: overwrites source)",
    )
    parser.add_argument(
        "--prefix",
        type=str,
        help="Process only robots whose IDs start with this prefix",
    )
    parser.add_argument(
        "--no-network",
        action="store_true",
        help="Skip YouTube/Vimeo oEmbed availability checks",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_TIMEOUT,
        help=f"Network timeout in seconds (default: {DEFAULT_TIMEOUT})",
    )
    parser.add_argument(
        "--show-passed",
        action="store_true",
        help="Print PASS entries as well as REVIEW/FAIL entries",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero for REVIEW results as well as FAIL results",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help=(
            "Prompt to update existing videos, or review/add candidates when "
            "combined with --search"
        ),
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open browser previews in interactive modes",
    )
    parser.add_argument(
        "--backup",
        action="store_true",
        help="Create a .bak file before writing interactive changes",
    )
    parser.add_argument(
        "--search",
        action="store_true",
        help="Search for candidate new robot videos without modifying robots.json",
    )
    parser.add_argument(
        "--providers",
        type=str,
        default=DEFAULT_SEARCH_PROVIDERS,
        help=(
            "Comma-separated providers for --search "
            f"(default: {DEFAULT_SEARCH_PROVIDERS}; valid: "
            f"{', '.join(sorted(SEARCH_PROVIDER_CONFIG))})"
        ),
    )
    parser.add_argument(
        "--search-limit",
        type=int,
        default=DEFAULT_SEARCH_LIMIT,
        help=f"Maximum candidates to show per robot (default: {DEFAULT_SEARCH_LIMIT})",
    )
    parser.add_argument(
        "--search-query-limit",
        type=int,
        default=3,
        help="Maximum search queries per provider/robot (default: 3)",
    )
    parser.add_argument(
        "--search-result-limit",
        type=int,
        default=8,
        help="Maximum search results to inspect per query (default: 8)",
    )
    parser.add_argument(
        "--search-min-score",
        type=int,
        default=4,
        help="Minimum heuristic score for a candidate (default: 4)",
    )
    parser.add_argument(
        "--search-delay",
        type=float,
        default=DEFAULT_SEARCH_DELAY,
        help=f"Seconds to sleep between search HTTP requests (default: {DEFAULT_SEARCH_DELAY})",
    )
    parser.add_argument(
        "--search-backoff",
        type=float,
        default=DEFAULT_SEARCH_BACKOFF,
        help=(
            "Seconds to sleep before retrying after HTTP 403/429 "
            f"(default: {DEFAULT_SEARCH_BACKOFF})"
        ),
    )
    parser.add_argument(
        "--search-retries",
        type=int,
        default=DEFAULT_SEARCH_RETRIES,
        help=f"Retries after HTTP 403/429 search responses (default: {DEFAULT_SEARCH_RETRIES})",
    )
    parser.add_argument(
        "--rejected-videos",
        type=Path,
        default=REJECTED_VIDEOS_FILE,
        help="Path to rejected video candidates (default: public/rejected-video.json)",
    )
    parser.add_argument(
        "--no-rejected-filter",
        action="store_true",
        help="Do not filter search candidates using rejected-video.json",
    )

    args = parser.parse_args()

    robots_data = load_robots(args.source)
    filtered_robots = apply_prefix_filter(robots_data, args.prefix)

    logger.info(f"Loaded {len(robots_data)} robots from {args.source}")
    if args.prefix:
        logger.info(f"Selected {len(filtered_robots)} robots with ID prefix '{args.prefix}'")

    if args.search:
        if args.no_network:
            logger.error("--search requires network access; remove --no-network")
            sys.exit(2)
        if args.output and not args.interactive:
            logger.warning("\n--output is only used with --interactive")
        if args.backup and not args.interactive:
            logger.warning("\n--backup is only used with --interactive")

        providers = parse_provider_list(args.providers)
        rejected_data = {} if args.no_rejected_filter else load_rejected_videos(args.rejected_videos)
        candidates = search_video_candidates(
            filtered_robots,
            providers=providers,
            timeout=args.timeout,
            candidate_limit=args.search_limit,
            query_limit=args.search_query_limit,
            result_limit=args.search_result_limit,
            min_score=args.search_min_score,
            rejected_data=rejected_data,
            search_delay=args.search_delay,
            search_backoff=args.search_backoff,
            search_retries=args.search_retries,
        )
        if args.interactive:
            output_file = args.output or args.source
            changed, added_videos = run_search_interactive_mode(
                candidates,
                robots_data,
                rejected_data,
                output_file=output_file,
                rejected_file=args.rejected_videos,
                backup=args.backup,
                no_open=args.no_open,
            )

            if changed and added_videos:
                filtered_robots = apply_prefix_filter(robots_data, args.prefix)
                checks = collect_video_checks(
                    filtered_robots,
                    timeout=args.timeout,
                    no_network=False,
                )
                logger.info("\nChecked video entries after adding search candidates")
                print_summary(checks, show_passed=args.show_passed)
                has_failures = any(check.status == STATUS_FAIL for check in checks)
                has_reviews = any(check.status == STATUS_REVIEW for check in checks)
                if has_failures or (args.strict and has_reviews):
                    sys.exit(1)
            sys.exit(0)

        print_search_results(candidates)
        sys.exit(0)

    checks = collect_video_checks(
        filtered_robots,
        timeout=args.timeout,
        no_network=args.no_network,
    )
    logger.info(f"Checked {len(checks)} video entries")
    print_summary(checks, show_passed=args.show_passed)

    if args.output and not args.interactive:
        logger.warning("\n--output is only used with --interactive")

    if args.backup and not args.interactive:
        logger.warning("\n--backup is only used with --interactive")

    if args.interactive:
        output_file = args.output or args.source
        changed = run_interactive_mode(
            checks,
            robots_data,
            output_file=output_file,
            backup=args.backup,
            no_open=args.no_open,
        )

        if changed:
            filtered_robots = apply_prefix_filter(robots_data, args.prefix)
            checks = collect_video_checks(
                filtered_robots,
                timeout=args.timeout,
                no_network=args.no_network,
            )
            logger.info("\nRe-checked video entries after interactive changes")
            print_summary(checks, show_passed=args.show_passed)

    has_failures = any(check.status == STATUS_FAIL for check in checks)
    has_reviews = any(check.status == STATUS_REVIEW for check in checks)

    if has_failures or (args.strict and has_reviews):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
