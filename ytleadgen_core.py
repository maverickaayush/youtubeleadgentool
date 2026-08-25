#!/usr/bin/env python3
"""
YouTube LeadGen Tool - Core Logic
Handles YouTube API discovery and Selenium email scraping
"""

import os
import re
import csv
import time
import random
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Callable

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from selenium import webdriver
import selenium
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException

# Email regex pattern
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")


def extract_emails(text: str) -> List[str]:
    """Extract unique emails from text"""
    if not text:
        return []
    return list(dict.fromkeys([e.strip(".,;:") for e in EMAIL_RE.findall(text)]))


def human_sleep(a=2.5, b=6.5):
    """Random sleep to mimic human behavior"""
    time.sleep(random.uniform(a, b))


def yt_build(api_key: str):
    """Build YouTube API client"""
    return build("youtube", "v3", developerKey=api_key)


def search_channel_ids(yt, keyword: str, max_total: int, log_func: Optional[Callable] = None) -> List[str]:
    """Search for channel IDs using YouTube API"""
    ids, page_token = [], None

    while len(ids) < max_total:
        try:
            res = yt.search().list(
                q=keyword,
                type="channel",
                part="snippet",
                maxResults=50,
                pageToken=page_token
            ).execute()
        except HttpError as e:
            if log_func:
                log_func(f"Search error for '{keyword}': {e}")
            break

        ids.extend([it["snippet"]["channelId"] for it in res.get("items", [])])
        page_token = res.get("nextPageToken")

        if not page_token:
            break

        human_sleep(0.6, 1.3)

    return list(dict.fromkeys(ids))[:max_total]


def fetch_channel_details(yt, channel_ids: List[str], log_func: Optional[Callable] = None) -> List[Dict[str, Any]]:
    """Fetch detailed information for channels"""
    out = []

    for i in range(0, len(channel_ids), 50):
        try:
            res = yt.channels().list(
                part="snippet,statistics,brandingSettings",
                id=",".join(channel_ids[i:i+50])
            ).execute()
        except HttpError as e:
            if log_func:
                log_func(f"channels.list error: {e}")
            continue

        for item in res.get("items", []):
            snip = item.get("snippet", {})
            stats = item.get("statistics", {})
            brand = item.get("brandingSettings", {}).get("channel", {})

            subs = int(stats.get("subscriberCount")) if "subscriberCount" in stats else None

            out.append({
                "channel_id": item["id"],
                "title": snip.get("title"),
                "description": snip.get("description") or "",
                "country": brand.get("country"),
                "subs": subs,
                "about_url": f"https://www.youtube.com/channel/{item['id']}/about"
            })

        human_sleep(0.5, 1.2)

    return out


def apply_filters(channels, min_subs, max_subs, bio_key, country):
    """Filter channels by subscriber count, bio keyword, and country"""
    out = []
    key = bio_key.lower() if bio_key else None

    for c in channels:
        subs = c.get("subs")
        if subs is None or subs < min_subs or subs > max_subs:
            continue
        if key and key not in (c.get("description") or "").lower():
            continue
        if country and (c.get("country") or "").lower() != country.lower():
            continue
        out.append(c)

    return out


def _check_selenium_version():
    """Ensure Selenium 4+ is installed, raise helpful error otherwise."""
    ver = getattr(selenium, "__version__", "0")
    try:
        major = int(ver.split(".", 1)[0])
    except ValueError:
        major = 0
    if major < 4:
        raise RuntimeError(
            f"Selenium {ver} detected. This tool requires selenium>=4.\n"
            "Run: pip install --upgrade selenium"
        )


def _get_app_dir() -> str:
    """Return directory of script or frozen executable."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def _get_chromedriver_info(driver_path: Optional[str]) -> str:
    """Return chromedriver version string if possible (for nicer error messages)."""
    cmd = None
    if driver_path and os.path.exists(driver_path):
        cmd = [driver_path, "--version"]
    else:
        cmd = ["chromedriver", "--version"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def make_driver(headless: bool) -> webdriver.Chrome:
    """Create Chrome WebDriver with appropriate options and version checks."""
    _check_selenium_version()

    opts = ChromeOptions()
    opts.add_argument("--disable-blink-features=AutomationControlled")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")

    if headless:
        opts.add_argument("--headless")

    # Determine app dir and potential local chromedriver
    import sys
    if getattr(sys, 'frozen', False):
        app_dir = os.path.dirname(sys.executable)
    else:
        app_dir = os.path.dirname(os.path.abspath(__file__))

    local_driver = os.path.join(app_dir, "chromedriver.exe")
    driver_info = _get_chromedriver_info(local_driver if os.path.exists(local_driver) else None)

    try:
        if os.path.exists(local_driver):
            service = Service(local_driver)
            return webdriver.Chrome(service=service, options=opts)
        else:
            # Rely on PATH
            return webdriver.Chrome(options=opts)
    except SessionNotCreatedException as e:
        # Typical for Chrome/ChromeDriver version mismatch
        msg = str(e)
        raise RuntimeError(
            "ChromeDriver / Chrome version mismatch.\n"
            f"ChromeDriver info: {driver_info}\n"
            "Install a matching ChromeDriver for your Chrome version from:\n"
            "https://googlechromelabs.github.io/chrome-for-testing/"
        ) from e
    except Exception as e:
        # Bubble up other errors but keep them readable
        raise RuntimeError(f"Failed to start Chrome WebDriver: {e}") from e


def get_email_from_about(driver, about_url: str, wait_secs: int = 60, log_func: Optional[Callable] = None) -> List[str]:
    """Scrape email from YouTube About page"""
    try:
        driver.get(about_url)
        time.sleep(1.5)
    except Exception as e:
        if log_func:
            log_func(f"Failed to load {about_url}: {e}")
        return []

    # Try to click "View email address" button
    try:
        btn = driver.find_element(By.XPATH, "//button[contains(., 'View email address')]")
        btn.click()
        if log_func:
            log_func("Clicked 'View email address' - solve CAPTCHA if shown")
    except Exception:
        pass

    # Wait and check for emails
    t0 = time.time()
    while time.time() - t0 < wait_secs:
        found = extract_emails(driver.page_source or "")
        if found:
            return found
        human_sleep(1, 2)

    return []


def ensure_csv(path: Path, header: List[str]):
    """Create CSV file with header if it doesn't exist"""
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(header)


def append_csv(path: Path, rows: List[List]):
    """Append rows to CSV file"""
    with path.open("a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerows(rows)


def run_leadgen_core(
    api_key: str,
    keywords: str,
    min_subs: int,
    max_subs: int,
    bio_key: Optional[str],
    country: Optional[str],
    require_email: bool,
    out_file: str,
    test_mode: bool,
    headless: bool,
    gui_log_func: Optional[Callable[[str], None]] = None,
    gui_progress_func: Optional[Callable[[int, int], None]] = None,
) -> int:
    """
    Main workflow for YouTube lead generation
    Returns: number of rows saved
    """

    def log(msg: str):
        if gui_log_func:
            gui_log_func(msg)

    # Build YouTube API client
    log("Building YouTube API client...")
    yt = yt_build(api_key)

    # Discovery phase
    log("Starting channel discovery...")
    discovered = []

    if keywords:
        for kw in keywords.split(","):
            kw = kw.strip()
            if not kw:
                continue
            log(f"Searching for keyword: {kw}")
            ids = search_channel_ids(yt, kw, 50 if test_mode else 200, log)
            discovered.extend(ids)
            log(f"Found {len(ids)} channels for '{kw}'")

    discovered = list(dict.fromkeys(discovered))
    log(f"Total discovered: {len(discovered)} unique channels")

    if not discovered:
        log("No channels discovered. Exiting.")
        return 0

    # Fetch details
    log("Fetching channel details...")
    details = fetch_channel_details(yt, discovered, log)
    log(f"Retrieved details for {len(details)} channels")

    # Apply filters
    log("Applying filters...")
    filtered = apply_filters(details, min_subs, max_subs, bio_key, country)
    log(f"{len(filtered)} channels after filtering")

    if test_mode:
        filtered = filtered[:5]
        log("TEST MODE: Limited to 5 channels")

    if not filtered:
        log("No channels passed filters. Exiting.")
        return 0

    # Setup CSV
    out_path = Path(out_file)
    ensure_csv(out_path, ["channel_id", "title", "subs", "country", "emails"])

    # Create driver
    log(f"Starting Chrome driver (headless={headless})...")
    driver = make_driver(headless)

    saved_count = 0
    total = len(filtered)

    # Process each channel
    for idx, ch in enumerate(filtered, 1):
        log(f"Processing {idx}/{total}: {ch['title']}")

        if gui_progress_func:
            gui_progress_func(idx, total)

        # Get emails from About page
        emails_about = get_email_from_about(driver, ch["about_url"], 60, log)

        # Get emails from description
        emails_desc = extract_emails(ch["description"])

        # Combine and deduplicate
        all_emails = list(dict.fromkeys(emails_about + emails_desc))

        if require_email and not all_emails:
            log(f"No email found for {ch['title']}, skipping")
            continue

        # Save to CSV
        append_csv(out_path, [[
            ch["channel_id"],
            ch["title"],
            ch["subs"],
            ch.get("country", ""),
            ";".join(all_emails)
        ]])

        saved_count += 1
        log(f"Saved: {ch['title']} ({len(all_emails)} emails)")

        # Human-like delay
        human_sleep(3, 6)

    driver.quit()
    log(f"Done! Saved {saved_count} channels to {out_path}")

    return saved_count
