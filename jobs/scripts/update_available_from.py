"""Set available_from to execution date + 14 days for selected companies in saved results.

Results may contain verified roles or manual-review entries for blocked companies.
"""

from __future__ import annotations

import argparse
from datetime import date, timedelta
import json
from pathlib import Path
import re

from role_finder_common import (
    JOBS_DIR, MANUAL_REVIEW_ROLE, atomic_json, company_error, company_key, opportunities,
    parse_date, read_json, sha256, valid_url,
)


def update_available_from(
    source: Path, roles_path: Path, selection_path: Path, *, today: date | None = None,
    dry_run: bool = False,
) -> dict:
    today = date.today() if today is None else today
    data, raw = read_json(source)
    entries = opportunities(data)
    manifest, _ = read_json(selection_path)
    roles, _ = read_json(roles_path)
    if not isinstance(manifest, dict) or set(manifest) != {"run_date", "input_sha256", "companies"}:
        raise ValueError("invalid selection manifest fields")
    run_date = parse_date(manifest["run_date"])
    if run_date != today:
        raise ValueError("selection must be from the execution date; regenerate it and refresh results")
    digest = manifest["input_sha256"]
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest) or digest != sha256(raw):
        raise ValueError("source changed since selection; regenerate the selection and review results")
    if not isinstance(manifest["companies"], list):
        raise ValueError("manifest companies must be an array")
    selected = {}
    seen_indices, seen_sources = set(), set()
    last_index = -1
    for company in manifest["companies"]:
        if not isinstance(company, dict) or set(company) != {"source_index", "name", "url", "available_from"}:
            raise ValueError("invalid company in selection manifest")
        index = company["source_index"]
        if type(index) is not int or not 0 <= index < len(entries) or index in seen_indices or index <= last_index:
            raise ValueError("invalid or unordered source_index in selection manifest")
        entry = entries[index]
        if company_error(entry, run_date) is not None:
            raise ValueError(f"selected source entry {index} was not eligible on the selection date")
        if any(company[key] != entry[key] for key in ("name", "url", "available_from")):
            raise ValueError(f"selected source entry {index} does not match the manifest")
        key = (entry["name"], entry["url"])
        if key in seen_sources:
            raise ValueError("duplicate company/URL in selection manifest")
        selected.setdefault(entry["name"], []).append(index)
        seen_indices.add(index)
        seen_sources.add(key)
        last_index = index
    if not isinstance(roles, list):
        raise ValueError("open_roles.json must be an array")
    matched = set()
    for role in roles:
        if not isinstance(role, dict) or set(role) != {"company_name", "role", "url"}:
            raise ValueError("each role must have exactly company_name, role, and url")
        if any(not isinstance(value, str) or not value.strip() for value in role.values()) or not valid_url(role["url"]):
            raise ValueError("result fields must be nonempty strings with an HTTP(S) application or careers URL")
        if role["company_name"] not in selected:
            raise ValueError(f"role company is not selected: {role['company_name']}")
        if len(selected[role["company_name"]]) != 1:
            raise ValueError(f"ambiguous company name in selection: {role['company_name']}")
        if role["role"] == MANUAL_REVIEW_ROLE:
            index = selected[role["company_name"]][0]
            if role["url"] != entries[index]["url"]:
                raise ValueError("manual-review URL must exactly match the selected company careers URL")
        matched.add(role["company_name"])
    for name in matched:
        index = selected[name][0]
        key = company_key(entries[index])
        duplicate_indices = [i for i, entry in enumerate(entries) if company_key(entry) == key]
        if len(duplicate_indices) > 1:
            raise ValueError(
                f"duplicate company/URL source entries for {name} at indices {duplicate_indices}; "
                "resolve duplicates before updating to avoid bypassing the cooldown"
            )
    target = (today + timedelta(days=14)).isoformat()
    changed = []
    for name, indices in selected.items():
        index = indices[0]
        if name in matched and entries[index]["available_from"] != target:
            changed.append(name)
            entries[index]["available_from"] = target
    if changed and not dry_run:
        if source.read_bytes() != raw:
            raise ValueError("source changed during update; no changes written")
        atomic_json(source, data, indent=4)
    return {"execution_date": today.isoformat(), "available_from": target, "companies": changed, "dry_run": dry_run}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=JOBS_DIR / "opportunities.json")
    parser.add_argument(
        "--roles", type=Path, default=JOBS_DIR / "open_roles.json",
        help="Saved results containing verified roles or manual-review entries for blocked companies",
    )
    parser.add_argument("--selection", type=Path, required=True, help="Unmodified manifest from select_companies.py")
    parser.add_argument("--dry-run", action="store_true", help="Validate and display changes without writing")
    args = parser.parse_args()
    try:
        result = update_available_from(args.source, args.roles, args.selection, dry_run=args.dry_run)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (OSError, ValueError) as error:
        parser.exit(1, f"error: {error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
