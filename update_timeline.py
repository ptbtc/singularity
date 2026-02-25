#!/usr/bin/env python3
"""
Fetch latest @alexwg Substack posts and append to data.json.
Designed to run as an OpenClaw isolated cron job.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

DATA_PATH = Path(__file__).parent / "data.json"
SUBSTACK_API = "https://theinnermostloop.substack.com/api/v1/archive?sort=new&limit=5"
SUBSTACK_POST = "https://theinnermostloop.substack.com/p/{slug}"


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())


def fetch_post_body(slug):
    """Fetch full post HTML and extract text."""
    url = f"https://theinnermostloop.substack.com/api/v1/posts/{slug}"
    try:
        data = fetch_json(url)
        body = data.get("body_html", "") or ""
        # Strip HTML tags for plain text
        text = re.sub(r'<[^>]+>', ' ', body)
        text = re.sub(r'\s+', ' ', text).strip()
        return text, data.get("canonical_url", f"https://theinnermostloop.substack.com/p/{slug}")
    except Exception:
        return "", f"https://theinnermostloop.substack.com/p/{slug}"


def parse_date_from_title(title):
    """Extract date from 'Welcome to February 24, 2026' style titles."""
    m = re.search(r'(\w+ \d{1,2},? \d{4})', title)
    if m:
        return m.group(1)
    return None


def existing_dates(data):
    """Get set of all dates already in data.json."""
    return {entry["date"] for entry in data}


def main():
    # Load existing data
    with open(DATA_PATH) as f:
        data = json.load(f)

    known = existing_dates(data)
    print(f"Loaded {len(data)} existing entries")

    # Fetch latest posts from Substack API
    posts = fetch_json(SUBSTACK_API)
    new_entries = []

    for post in posts:
        title = post.get("title", "")
        if "welcome to" not in title.lower():
            continue

        date_str = parse_date_from_title(title)
        if not date_str or date_str in known:
            continue

        slug = post["slug"]
        print(f"New post found: {date_str} ({slug})")

        body_text, canonical_url = fetch_post_body(slug)
        truncated = post.get("truncated_body_text", "")
        description = post.get("description", "")

        # Output the raw content for the cron job's AI session to process
        entry = {
            "date": date_str,
            "slug": slug,
            "url": canonical_url,
            "description": description,
            "truncated_text": truncated,
            "full_text": body_text[:8000],  # Cap for AI processing
        }
        new_entries.append(entry)

    if not new_entries:
        print("No new posts to add.")
        return

    # Write raw entries to a staging file for the AI cron to enrich
    staging = Path(__file__).parent / "staging.json"
    with open(staging, "w") as f:
        json.dump(new_entries, f, indent=2)
    print(f"Staged {len(new_entries)} new entries to staging.json")

    # Print for cron job AI to pick up
    for e in new_entries:
        print(f"\n=== NEW ENTRY: {e['date']} ===")
        print(f"URL: {e['url']}")
        print(f"Description: {e['description']}")
        print(f"Text preview: {e['full_text'][:2000]}")


if __name__ == "__main__":
    main()
