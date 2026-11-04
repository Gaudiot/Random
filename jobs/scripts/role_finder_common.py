"""Shared JSON and validation helpers for the role-finder command-line tools."""

from __future__ import annotations

import hashlib
import ipaddress
import json
import os
from pathlib import Path
import re
import tempfile
from datetime import date
from urllib.parse import urlsplit


JOBS_DIR = Path(__file__).resolve().parents[1]
MANUAL_REVIEW_ROLE = "Revis\u00e3o manual \u2014 acesso bloqueado ou indispon\u00edvel"


def parse_date(value: object) -> date:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        raise ValueError("date must use YYYY-MM-DD")
    return date.fromisoformat(value)


def valid_url(value: object) -> bool:
    if not isinstance(value, str) or any(char.isspace() for char in value):
        return False
    try:
        parsed = urlsplit(value)
        hostname = parsed.hostname
        if parsed.scheme not in ("http", "https") or not hostname or parsed.port == 0:
            return False
        try:
            ipaddress.ip_address(hostname)
        except ValueError:
            labels = hostname.rstrip(".").encode("idna").decode("ascii").split(".")
            return len(hostname) <= 253 and all(
                re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?", label)
                for label in labels
            )
        return True
    except ValueError:
        return False


def read_json(path: Path) -> tuple[object, bytes]:
    raw = path.read_bytes()
    return json.loads(raw.decode("utf-8")), raw


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def opportunities(data: object) -> list:
    if not isinstance(data, dict) or not isinstance(data.get("opportunities"), list):
        raise ValueError("source must be an object containing an opportunities array")
    return data["opportunities"]


def company_key(entry: object) -> tuple[str, str] | None:
    """Identify a company source independently of its availability date."""
    if not isinstance(entry, dict):
        return None
    if not isinstance(entry.get("type"), str) or entry["type"].strip().casefold() != "company":
        return None
    if not isinstance(entry.get("name"), str) or not entry["name"].strip() or not valid_url(entry.get("url")):
        return None
    return entry["name"], entry["url"]


def company_error(entry: object, today: date) -> str | None:
    if not isinstance(entry, dict):
        return "entry is not an object"
    if not isinstance(entry.get("type"), str) or entry["type"].strip().casefold() != "company":
        return "type is not company"
    if not isinstance(entry.get("name"), str) or not entry["name"].strip():
        return "missing company name"
    if not valid_url(entry.get("url")):
        return "invalid HTTP(S) URL"
    try:
        available = parse_date(entry.get("available_from"))
    except ValueError as error:
        return f"invalid available_from: {error}"
    if available > today:
        return f"available_from is in the future ({available})"
    return None


def atomic_json(path: Path, data: object, *, indent: int = 2) -> None:
    """Replace only after a complete, parseable UTF-8 JSON document is written."""
    serialized = json.dumps(data, ensure_ascii=False, indent=indent) + "\n"
    json.loads(serialized)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            temporary = Path(handle.name)
            handle.write(serialized)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
