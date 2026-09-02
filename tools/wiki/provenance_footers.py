#!/usr/bin/env python3
"""
tools/wiki/provenance_footers.py -- generate and verify the per-page
provenance footer on each migrated wiki page named in
tools/wiki/MIGRATION-TABLE.md, and confirm the table and the live wiki
agree on which pages exist.

Exit-code contract:
  0 = the asserted property holds
  1 = the asserted property is false
  2 = a precondition was not met (a required path missing, or the table
      not parsing to at least MIN_FOOTER_ROWS footer-eligible rows)

Two directions, two distinct failure vocabularies, so a table/page mismatch
and a footer content problem never arrive as one indistinguishable red:

  PAGE MISSING     -- a row names a wiki page the clone does not have.
  UNRECORDED PAGE   -- a live page has no row in the migration table.
  UNSAFE ROW        -- a row's Wiki page cell resolves outside --wiki-dir
                       and is never opened.
  FOOTER MISSING    -- a footer-eligible page's last non-empty line does
                       not match the generated footer form at all.
  FOOTER DRIFTED    -- a footer-eligible page's footer parses but
                       disagrees with the table's own fields.

The page/table accounting direction is checked first: a table that does
not correctly enumerate the live wiki cannot yet be trusted to name the
right footer text either, so footer content is only compared once table
and wiki agree on which pages exist.

The artifact this script writes and reads is an in-page trailing block,
never GitHub's reserved global _Footer.md page -- that page renders
identically everywhere and cannot carry a per-page source path or SHA.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
NO_VALUE_MARKER = "—"
NAV_EXCLUDED_PAGES = frozenset({"_Sidebar.md", "_Footer.md"})
MIN_FOOTER_ROWS = 6
MAIN_TABLE_KEY = "Wiki page"
RETIRED_TABLE_KEY = "Was published as"
REMOVED_TABLE_KEY = "What it was"
FOOTER_RULE = "---"
_FOOTER_LINE_BODY = (
    r"\*Relocated from `(?P<path>[^`]+)` in `(?P<repo>[^`]+)` "
    r"at `(?P<sha>[0-9a-f]{40})`"
    r"(?:\. Moved intact and not edited since; not re-verified against the code\.|"
    r", then (?P<edits>.+?) on the wiki; not re-verified against the code\.)\*"
)
FOOTER_RE = re.compile(r"^" + _FOOTER_LINE_BODY + r"$")
_TRAILING_FOOTER_BLOCK_RE = re.compile(
    r"\n*" + re.escape(FOOTER_RULE) + r"\n+" + _FOOTER_LINE_BODY + r"\n*\Z"
)


def parse_tables(table_path: Path) -> dict[str, list[dict[str, str]]]:
    tables: dict[str, list[dict[str, str]]] = {}
    header: list[str] = []
    key: str | None = None
    armed = False
    for line in table_path.read_text(encoding="utf-8").splitlines():
        match = TABLE_ROW_RE.match(line)
        if match is None:
            header = []
            key = None
            armed = False
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if not header:
            header = cells
            armed = False
            if MAIN_TABLE_KEY in header:
                key = "main"
            elif RETIRED_TABLE_KEY in header:
                key = "retired"
            elif REMOVED_TABLE_KEY in header:
                key = "removed"
            else:
                key = None
            if key is not None:
                tables.setdefault(key, [])
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            armed = True
            continue
        if not armed or key is None:
            continue
        tables[key].append(dict(zip(header, cells)))
    return tables


def footer_eligible_rows(main_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        row
        for row in main_rows
        if row.get("Source path", NO_VALUE_MARKER) != NO_VALUE_MARKER
        and row.get("Pre-deletion SHA", NO_VALUE_MARKER) != NO_VALUE_MARKER
    ]


def footer_line(row: dict[str, str]) -> str:
    source_path = row.get("Source path", NO_VALUE_MARKER)
    source_repo = row.get("Source repo", NO_VALUE_MARKER)
    sha = row.get("Pre-deletion SHA", NO_VALUE_MARKER)
    edits = row.get("Post-move edits", NO_VALUE_MARKER)
    prefix = f"*Relocated from `{source_path}` in `{source_repo}` at `{sha}`"
    if edits == NO_VALUE_MARKER:
        return prefix + ". Moved intact and not edited since; not re-verified against the code.*"
    return prefix + f", then {edits} on the wiki; not re-verified against the code.*"


def load_pages(wiki_dir: Path) -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(wiki_dir.glob("*.md")):
        if path.name in NAV_EXCLUDED_PAGES:
            continue
        pages[path.name] = path.read_text(encoding="utf-8")
    return pages


def _resolve_row_page(wiki_dir: Path, page: str) -> Path | None:
    base = wiki_dir.resolve()
    candidate = (wiki_dir / f"{page}.md").resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate


def check_footers(rows: list[dict[str, str]], wiki_dir: Path) -> list[str]:
    failures: list[str] = []
    for row in rows:
        page = row.get("Wiki page", "")
        candidate = _resolve_row_page(wiki_dir, page)
        if candidate is None:
            failures.append(f"UNSAFE ROW: {page} resolves outside the wiki directory")
            continue
        if not candidate.is_file():
            failures.append(
                f"PAGE MISSING: {page} — the table names it but the wiki clone does not have it"
            )
            continue
        text = candidate.read_text(encoding="utf-8")
        lines = [line for line in text.splitlines() if line.strip()]
        expected = footer_line(row)
        if not lines or FOOTER_RE.match(lines[-1].strip()) is None:
            failures.append(f"FOOTER MISSING: {page}")
            continue
        actual = lines[-1].strip()
        if actual != expected:
            failures.append(
                f"FOOTER DRIFTED: {page} — footer says {actual!r}, table says {expected!r}"
            )
    return failures


def check_page_accounting(main_rows: list[dict[str, str]], wiki_dir: Path) -> list[str]:
    failures: list[str] = []
    table_pages: set[str] = set()
    for row in main_rows:
        page = row.get("Wiki page", "")
        table_pages.add(page)
        candidate = _resolve_row_page(wiki_dir, page)
        if candidate is None:
            failures.append(f"UNSAFE ROW: {page} resolves outside the wiki directory")
            continue
        if not candidate.is_file():
            failures.append(
                f"PAGE MISSING: {page} — the table names it but the wiki clone does not have it"
            )
    live_pages = load_pages(wiki_dir)
    for name in sorted(live_pages):
        stem = name[:-3] if name.endswith(".md") else name
        if stem not in table_pages:
            failures.append(f"UNRECORDED PAGE: {stem} has no row in the migration table")
    return failures


def emit_footers(rows: list[dict[str, str]], wiki_dir: Path) -> int:
    written = 0
    for row in rows:
        page = row.get("Wiki page", "")
        candidate = _resolve_row_page(wiki_dir, page)
        if candidate is None or not candidate.is_file():
            continue
        text = candidate.read_text(encoding="utf-8")
        stripped = _TRAILING_FOOTER_BLOCK_RE.sub("", text)
        new_text = (
            stripped.rstrip("\n") + "\n\n" + FOOTER_RULE + "\n\n" + footer_line(row) + "\n"
        )
        candidate.write_text(new_text, encoding="utf-8")
        written += 1
    return written


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="provenance_footers.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--table", type=Path, required=True)
    parser.add_argument("--wiki-dir", type=Path, required=True)
    parser.add_argument("--emit", action="store_true")
    return parser


def main() -> int:
    args = _build_argparser().parse_args()

    if not args.table.is_file():
        print(f"ERROR: --table not found: {args.table}", file=sys.stderr)
        return 2
    if not args.wiki_dir.is_dir():
        print(f"ERROR: --wiki-dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2

    tables = parse_tables(args.table)
    main_rows = tables.get("main", [])
    if not main_rows:
        print(
            f"ERROR: main table not found by header identity in {args.table}",
            file=sys.stderr,
        )
        return 2

    eligible_rows = footer_eligible_rows(main_rows)
    if len(eligible_rows) < MIN_FOOTER_ROWS:
        print(
            f"ERROR: {len(eligible_rows)} footer-eligible row(s) parsed, fewer than "
            f"the required minimum of {MIN_FOOTER_ROWS}",
            file=sys.stderr,
        )
        return 2

    if args.emit:
        written = emit_footers(eligible_rows, args.wiki_dir)
        print(f"OK: {written} footers written.")
        return 0

    accounting_failures = check_page_accounting(main_rows, args.wiki_dir)
    if accounting_failures:
        for message in accounting_failures:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1

    footer_failures = check_footers(eligible_rows, args.wiki_dir)
    if footer_failures:
        for message in footer_failures:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1

    print(
        f"OK: {len(eligible_rows)} footers verified, {len(main_rows)} pages "
        "accounted for, 0 unrecorded."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
