#!/usr/bin/env python3
"""
Spider Cloud tier probe — finds cheapest Cloud tier that returns real content.

Tests T4-T7 in order. Stops at first success.
Spider Cloud returns chunked JSONL — must use stream=True + iter_lines(), NOT .json().

Usage:
    python probe_tiers.py <URL>
    python probe_tiers.py https://bbb.org/us/mi/detroit/category/pest-control
"""

import json
import os
import sys

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("SPIDER_API_KEY")
ENDPOINT = "https://api.spider.cloud/scrape"

TIERS = [
    {
        "id": "T4",
        "label": "Cloud basic (HTTP)",
        "cost": "~$0.001/page",
        "params": {"request": "http", "readability": True, "return_format": "markdown"},
    },
    {
        "id": "T5",
        "label": "Cloud chrome + readability",
        "cost": "~$0.005/page",
        "params": {"request": "chrome", "readability": True, "return_format": "markdown"},
    },
    {
        "id": "T6",
        "label": "Cloud proxy enabled",
        "cost": "~$0.0075/page",
        "params": {"request": "chrome", "readability": True, "return_format": "markdown", "proxy": "residential"},
    },
    {
        "id": "T7",
        "label": "Cloud unblocker",
        "cost": "~$0.01/page",
        "params": {"request": "smart", "readability": True, "return_format": "markdown"},
    },
]

MIN_CONTENT_BYTES = 500


def probe_tier(url: str, tier: dict) -> tuple[bool, str, int]:
    """Try one tier. Returns (success, content_preview, content_length)."""
    payload = {"url": url, **tier["params"]}
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    try:
        # Spider Cloud returns chunked JSONL — must stream, never call .json()
        resp = requests.post(ENDPOINT, json=payload, headers=headers, timeout=45, stream=True)

        if resp.status_code != 200:
            return False, f"HTTP {resp.status_code}", 0

        content = ""
        for line in resp.iter_lines():
            if not line:
                continue
            try:
                record = json.loads(line)
                if isinstance(record, list):
                    record = record[0]
                content = record.get("content", "")
                break
            except json.JSONDecodeError:
                continue

        if len(content) >= MIN_CONTENT_BYTES:
            return True, content[:200].replace("\n", " "), len(content)
        return False, f"too short ({len(content)} bytes)", len(content)

    except Exception as e:
        return False, str(e), 0


def main():
    if not API_KEY:
        print("ERROR: SPIDER_API_KEY not set in .env")
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: python probe_tiers.py <URL>")
        sys.exit(1)

    url = sys.argv[1]
    print(f"Probing: {url}\n")

    winner = None
    for tier in TIERS:
        print(f"  [{tier['id']}] {tier['label']} ({tier['cost']}) ... ", end="", flush=True)
        success, preview, length = probe_tier(url, tier)
        if success:
            print(f"OK — {length} bytes")
            print(f"         Preview: {preview[:120]}...")
            winner = tier
            break
        else:
            print(f"FAIL — {preview}")

    print()
    if winner:
        print(f"RESULT: Use {winner['id']} — {winner['label']} ({winner['cost']})")
    else:
        print("RESULT: All Cloud tiers blocked — fall back to SeleniumBase UC (T8)")


if __name__ == "__main__":
    main()
