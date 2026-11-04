"""Select eligible companies deterministically without accessing their websites."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import sys

from role_finder_common import JOBS_DIR, atomic_json, company_error, company_key, opportunities, read_json, sha256


def select_companies(source: Path, *, today: date | None = None, limit: int | None = None) -> tuple[dict, list[str]]:
    """Skip duplicate source groups with conflicting dates rather than bypassing a cooldown."""
    today = date.today() if today is None else today
    if limit is not None and (isinstance(limit, bool) or not isinstance(limit, int) or limit < 0):
        raise ValueError("limit must be a nonnegative integer")
    data, raw = read_json(source)
    entries = opportunities(data)
    source_dates = {}
    conflicts = set()
    for entry in entries:
        key = company_key(entry)
        if key is not None:
            if key in source_dates and entry.get("available_from") != source_dates[key]:
                conflicts.add(key)
            source_dates[key] = entry.get("available_from")
    selected, diagnostics, seen = [], [], set()
    for index, entry in enumerate(entries):
        if company_key(entry) in conflicts:
            diagnostics.append(f"opportunities[{index}] skipped: conflicting available_from dates for duplicate company/URL")
            continue
        error = company_error(entry, today)
        if error:
            diagnostics.append(f"opportunities[{index}] skipped: {error}")
            continue
        key = (entry["name"], entry["url"])
        if key in seen:
            diagnostics.append(f"opportunities[{index}] skipped: duplicate company/URL")
            continue
        seen.add(key)
        selected.append({"source_index": index, **{key: entry[key] for key in ("name", "url", "available_from")}})
    if limit is not None:
        selected = selected[:limit]
    return {"run_date": today.isoformat(), "input_sha256": sha256(raw), "companies": selected}, diagnostics


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=JOBS_DIR / "opportunities.json")
    parser.add_argument("--limit", type=int, help="Maximum eligible companies, in source order (default: all)")
    parser.add_argument("--output", type=Path, help="Write manifest atomically here; otherwise print JSON to stdout")
    args = parser.parse_args()
    try:
        manifest, diagnostics = select_companies(args.source, limit=args.limit)
        if args.output is not None and args.output.resolve() == args.source.resolve():
            raise ValueError("output must not overwrite the source")
        for diagnostic in diagnostics:
            print(diagnostic, file=sys.stderr)
        if args.output is None:
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
        else:
            atomic_json(args.output, manifest)
            print(f"Selected {len(manifest['companies'])} companies: {args.output}", file=sys.stderr)
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
