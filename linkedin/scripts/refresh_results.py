#!/usr/bin/env python3
"""Refresh public engagement metrics in linkedin/result/*.result.json.

Only `reactions` and `comments` are recoverable from a logged-out LinkedIn page.
`impressions` and `shares` live behind author-only analytics, so they are never
touched here and stay whatever Victor last typed in by hand.

Usage:
    python3 linkedin/scripts/refresh_results.py            # stale files only
    python3 linkedin/scripts/refresh_results.py --dry-run  # report, write nothing
    python3 linkedin/scripts/refresh_results.py --all
    python3 linkedin/scripts/refresh_results.py dns_guide app_icon
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

RESULT_DIR = Path(__file__).resolve().parent.parent / "result"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
SETTLE_MONTHS = 3
SCRAPED_FIELDS = ("reactions", "comments")


def months_between(start: date, end: date) -> float:
    return (end.year - start.year) * 12 + (end.month - start.month) + (end.day - start.day) / 30.0


def fetch_html(url: str) -> str:
    result = subprocess.run(
        ["curl", "-sL", "--max-time", "30", "-A", USER_AGENT, url],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"curl exited {result.returncode}: {result.stderr.strip()}")
    return result.stdout


def scrape_metrics(url: str) -> dict[str, int]:
    """Return the public counts for the post the URL points at.

    The page also renders a feed of unrelated posts, so the block is narrowed to
    the span between the requested activity urn and the next one.
    """
    match = re.search(r"activity-(\d+)", url)
    if not match:
        raise ValueError(f"no activity id in url: {url}")
    activity_id = match.group(1)

    html = fetch_html(url)
    if "authwall" in html or len(html) < 5000:
        raise RuntimeError("LinkedIn served an auth wall instead of the post")

    urns = [(m.start(), m.group(1)) for m in re.finditer(r'data-activity-urn="urn:li:activity:(\d+)"', html)]
    start = next((pos for pos, urn in urns if urn == activity_id), None)
    if start is None:
        raise RuntimeError(f"activity {activity_id} not present in the response")
    end = next((pos for pos, urn in urns if pos > start), len(html))
    block = html[start:end]

    reactions = re.search(r'data-num-reactions="(\d+)"', block)
    comments = re.search(r'data-num-comments="(\d+)"', block)
    return {
        "reactions": int(reactions.group(1)) if reactions else 0,
        "comments": int(comments.group(1)) if comments else 0,
    }


def write_result(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=4, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("topics", nargs="*", help="slugs to refresh; defaults to every stale file")
    parser.add_argument("--all", action="store_true", help="refresh even already settled files")
    parser.add_argument("--dry-run", action="store_true", help="print the diff without writing")
    args = parser.parse_args()

    today = date.today()
    paths = sorted(RESULT_DIR.glob("*.result.json"))
    if args.topics:
        wanted = set(args.topics)
        paths = [p for p in paths if p.name.removesuffix(".result.json") in wanted]

    exit_code = 0
    for path in paths:
        slug = path.name.removesuffix(".result.json")
        data = json.loads(path.read_text(encoding="utf-8"))
        published = date.fromisoformat(data["published_at"])
        updated = date.fromisoformat(data["updated_at"])
        gap = months_between(published, updated)

        if not args.all and not args.topics and gap >= SETTLE_MONTHS:
            print(f"{slug}: settled ({gap:.1f}mo gap), skipped")
            continue

        try:
            scraped = scrape_metrics(data["url"])
        except Exception as error:  # noqa: BLE001 - one bad post must not stop the batch
            print(f"{slug}: FAILED, {error}", file=sys.stderr)
            exit_code = 1
            continue

        changes = [
            f"{field} {data.get(field)} -> {scraped[field]}"
            for field in SCRAPED_FIELDS
            if data.get(field) != scraped[field]
        ]
        data.update(scraped)
        data["updated_at"] = today.isoformat()

        if args.dry_run:
            print(f"{slug}: [dry-run] {', '.join(changes) if changes else 'no change'}")
            continue

        write_result(path, data)
        print(f"{slug}: {', '.join(changes) if changes else 'no change'}, updated_at -> {today}")

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
