"""Estimate text layout from word counts and explicit line breaks."""

import argparse
import json
import math
import sys
from pathlib import Path


def estimate_text_layout(text: str, *, words_per_line: float = 15.5,
                         lines_per_page: int = 52) -> dict:
    """Count wrapped lines, including blank lines, and estimate occupied pages.

    Each explicit line starts a new layout line. A terminal newline ends the
    last line; it does not itself add a blank line. Empty text occupies no lines.
    """
    if not math.isfinite(words_per_line) or words_per_line <= 0:
        raise ValueError("words_per_line must be a finite number greater than zero")
    if isinstance(lines_per_page, bool) or not isinstance(lines_per_page, int) or lines_per_page <= 0:
        raise ValueError("lines_per_page must be a positive integer")

    total_lines = 0
    word_count = 0
    for line in text.splitlines():
        words = len(line.split())
        word_count += words
        total_lines += max(1, math.ceil(words / words_per_line))

    return {
        "word_count": word_count,
        "total_lines": total_lines,
        "total_pages": (total_lines + lines_per_page - 1) // lines_per_page,
        "page_equivalent": round(total_lines / lines_per_page, 4),
        "words_per_line": words_per_line,
        "lines_per_page": lines_per_page,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    inputs = parser.add_mutually_exclusive_group()
    inputs.add_argument("--text", help="Text to estimate, including literal line breaks")
    inputs.add_argument("--file", type=Path, help="UTF-8 text file (not DOCX)")
    parser.add_argument("--words-per-line", type=float, default=15.5)
    parser.add_argument("--lines-per-page", type=int, default=52)
    args = parser.parse_args(argv)

    try:
        if args.text is not None:
            text = args.text
        elif args.file is not None:
            text = args.file.read_text(encoding="utf-8-sig")
        else:
            text = sys.stdin.read()
        result = estimate_text_layout(
            text, words_per_line=args.words_per_line,
            lines_per_page=args.lines_per_page,
        )
    except (OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
