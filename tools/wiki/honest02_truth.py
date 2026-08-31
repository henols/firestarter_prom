#!/usr/bin/env python3
"""
tools/wiki/honest02_truth.py -- the standing truth gate for wiki content: for
every published page making a per-chip or per-protocol claim, assert a
database stamp is present, assert the claims inside a delimited region
resolve against the shipped chip database, and assert the stamp still
matches the database it was taken from.

After the model reversal there is no publishing-integrity check any more --
wiki edits produce no pull request, no diff and no review -- so this is the
only automated guard on wiki content. A green result has to mean something.

Exit-code contract:
  0 = every page matching the claim signature carries a stamp, every claim
      inside a delimited region resolves or is allowlisted, and every stamp
      matches the current database
  1 = a page matching the claim signature has no stamp, a delimited claim
      did not resolve and was not allowlisted, or a stamp's recorded hash no
      longer matches the current database
  2 = a precondition was not met: the database or allowlist path is missing
      or malformed, the database contains zero rows, the wiki directory
      contains zero pages, or an allowlist entry carries an empty reason

Three legs, three distinct outcome vocabularies, so a database disagreement
and a navigation-shaped problem never arrive as one indistinguishable red:

  MISSING STAMP  (leg 1) -- a page matching the claim signature has no
                  firestarter-claim-stamp comment at all.
  UNRESOLVED     (leg 2) -- a token inside a firestarter-claims-begin/end
                  region does not resolve against the database and is not in
                  the allowlist.
  STALE STAMP    (leg 3) -- a page's stamp carries a database hash that no
                  longer matches the current database. Stale is a distinct
                  outcome from wrong: it means nobody has re-verified the
                  page since the database changed, not that the page is
                  false.
  UNCHECKED (stamp only) -- not a failure. A stamped page with no delimited
                  region is named on its own line and is never folded into
                  the success line.

The claim signature (leg 1) is deliberately narrower than "any token shaped
like a part number or a hex byte." Measured against the real corpus, a
shape-only signature false-positives twice over: incidental cross-references
in navigation prose (Home.md's "AT28C04/AT28C16" naming what a linked page
covers) and board/MCU identifiers that are not chip claims at all
(Beta-Testing-Install.md's 328PB/ATmega328PB/uno328pb). The signature is
therefore defined as "the page carries at least one token that actually
resolves against the current database" -- a page that names no real,
checkable chip or algorithm needs no stamp. Home.md, How-To-Edit-This-Wiki.md,
_Sidebar.md and _Footer.md are wiki-mechanics/navigation pages, not chip or
protocol reference content (How-To-Edit-This-Wiki.md says so of itself), and
are excluded from all three legs before any signature is evaluated -- this
mirrors wiki.py's own NAV_EXCLUDED_PAGES precedent for _Sidebar.md/_Footer.md.

Part-number-shaped-token extraction excludes three syntactic shapes that are
never part numbers in this corpus -- a bare voltage ("5V", "12V"), a bare
capacity ("512K", "1M") and a bare pin count ("24PIN") -- because without
that exclusion nearly every claims region reports a wall of non-resolving
noise that has nothing to do with a part number being wrong.

Known trap, carried forward from the database's own shape: an `algorithm: 13`
(0x0D) row is a *promoted* row, and a promoted row's `programming.*`
sub-fields belong to a different algorithm. This checker only ever reads a
row's `programming.algorithm` value to build the set of valid algorithm
integers -- it never reads any other `programming.*` sub-field off any row,
promoted or otherwise, so the trap does not apply to anything computed here.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

NAV_PAGES = frozenset(
    {"Home.md", "How-To-Edit-This-Wiki.md", "_Sidebar.md", "_Footer.md"}
)
STAMP_HASH_LENGTH = 16

FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
WORD_RE = re.compile(r"[A-Za-z0-9]+")
HEX_TOKEN_RE = re.compile(r"\b0[xX][0-9A-Fa-f]+\b")
VOLTAGE_SHAPE_RE = re.compile(r"^\d+(\.\d+)?V$")
CAPACITY_SHAPE_RE = re.compile(r"^\d+[KM]$")
PIN_COUNT_SHAPE_RE = re.compile(r"^\d+PIN$")
STAMP_RE = re.compile(
    r"<!--\s*firestarter-claim-stamp:\s*db-sha256-16=([0-9a-f]{16})\s+"
    r"verified=(\d{4}-\d{2}-\d{2})\s*-->"
)
REGION_RE = re.compile(
    r"<!--\s*firestarter-claims-begin\s*-->(.*?)<!--\s*firestarter-claims-end\s*-->",
    re.DOTALL,
)


class PreconditionError(Exception):
    pass


def load_database(db_path: Path) -> tuple[set[str], set[int]]:
    try:
        with db_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PreconditionError(f"cannot load database {db_path}: {exc}") from exc

    part_numbers: set[str] = set()
    algorithms: set[int] = set()
    row_count = 0
    for vendor_rows in data.values():
        if not isinstance(vendor_rows, list):
            continue
        for row in vendor_rows:
            row_count += 1
            raw_part = row.get("part_number", "")
            for token in raw_part.split(","):
                token = token.strip().upper()
                if token:
                    part_numbers.add(token)
            programming = row.get("programming")
            if isinstance(programming, dict) and "algorithm" in programming:
                algorithms.add(int(programming["algorithm"]))

    if row_count == 0:
        raise PreconditionError(f"database {db_path} loaded but contains zero rows")

    return part_numbers, algorithms


def load_allowlist(allowlist_path: Path) -> tuple[set[str], set[int]]:
    try:
        with allowlist_path.open(encoding="utf-8") as handle:
            data = json.load(handle)
    except (OSError, json.JSONDecodeError) as exc:
        raise PreconditionError(
            f"cannot load allowlist {allowlist_path}: {exc}"
        ) from exc

    for key in ("schema_version", "part_tokens", "algorithm_tokens"):
        if key not in data:
            raise PreconditionError(f"allowlist is missing required key {key!r}")

    allow_parts: set[str] = set()
    for entry in data["part_tokens"]:
        token = entry.get("token", "")
        reason = entry.get("reason", "")
        if not token or not reason.strip():
            raise PreconditionError(
                f"allowlist part_tokens entry has an empty token or reason: {entry!r}"
            )
        allow_parts.add(token.upper())

    allow_algorithms: set[int] = set()
    for entry in data["algorithm_tokens"]:
        token = entry.get("token", "")
        reason = entry.get("reason", "")
        if not token or not reason.strip():
            raise PreconditionError(
                f"allowlist algorithm_tokens entry has an empty token or reason: {entry!r}"
            )
        allow_algorithms.add(int(token, 16))

    return allow_parts, allow_algorithms


def strip_fences(text: str) -> str:
    return FENCE_RE.sub(lambda match: "\n" * match.group(0).count("\n"), text)


def extract_part_tokens(text: str) -> set[str]:
    tokens: set[str] = set()
    for word in WORD_RE.findall(text):
        if len(word) < 2 or HEX_TOKEN_RE.fullmatch(word):
            continue
        upper = word.upper()
        if not (any(c.isdigit() for c in upper) and any(c.isalpha() for c in upper)):
            continue
        if (
            VOLTAGE_SHAPE_RE.match(upper)
            or CAPACITY_SHAPE_RE.match(upper)
            or PIN_COUNT_SHAPE_RE.match(upper)
        ):
            continue
        tokens.add(upper)
    return tokens


def extract_hex_tokens(text: str) -> set[str]:
    return set(HEX_TOKEN_RE.findall(text))


def find_stamp(text: str) -> tuple[str, str] | None:
    match = STAMP_RE.search(text)
    if match is None:
        return None
    return match.group(1), match.group(2)


def extract_claim_region(text: str) -> str | None:
    match = REGION_RE.search(text)
    if match is None:
        return None
    return match.group(1)


def page_matches_claim_signature(
    text: str, part_numbers: set[str], algorithms: set[int]
) -> bool:
    stripped = strip_fences(text)
    if extract_part_tokens(stripped) & part_numbers:
        return True
    for hex_token in extract_hex_tokens(stripped):
        if int(hex_token, 16) in algorithms:
            return True
    return False


def check_stamp_present(
    pages: dict[str, str], part_numbers: set[str], algorithms: set[int]
) -> tuple[list[str], int]:
    failures: list[str] = []
    matched = 0
    for name in sorted(pages):
        text = pages[name]
        if not page_matches_claim_signature(text, part_numbers, algorithms):
            continue
        matched += 1
        if find_stamp(text) is None:
            failures.append(
                f"MISSING STAMP: {name} matches the claim signature (names a "
                "part number or algorithm value that resolves in the "
                "database) but carries no firestarter-claim-stamp"
            )
    return failures, matched


def check_claims_resolve(
    pages: dict[str, str],
    part_numbers: set[str],
    algorithms: set[int],
    allow_parts: set[str],
    allow_algorithms: set[int],
) -> tuple[list[str], list[str], int, int]:
    failures: list[str] = []
    unchecked: list[str] = []
    regions_found = 0
    claims_checked = 0

    for name in sorted(pages):
        text = pages[name]
        region = extract_claim_region(text)
        if region is None:
            if find_stamp(text) is not None:
                unchecked.append(
                    f"UNCHECKED (stamp only): {name} carries a stamp but no "
                    "firestarter-claims-begin/end region -- its claims are "
                    "not resolved against the database"
                )
            continue

        regions_found += 1
        part_tokens = extract_part_tokens(region)
        hex_tokens = extract_hex_tokens(region)
        claims_checked += len(part_tokens) + len(hex_tokens)

        for token in sorted(part_tokens):
            if token in part_numbers or token in allow_parts:
                continue
            failures.append(
                f"UNRESOLVED: {name}: part token {token!r} does not resolve "
                "in the database and is not in the allowlist"
            )

        for token in sorted(hex_tokens):
            value = int(token, 16)
            if value in algorithms or value in allow_algorithms:
                continue
            failures.append(
                f"UNRESOLVED: {name}: algorithm token {token!r} does not "
                "resolve in the database and is not in the allowlist"
            )

    return failures, unchecked, regions_found, claims_checked


def check_stamp_freshness(
    pages: dict[str, str], current_hash: str
) -> tuple[list[str], int]:
    failures: list[str] = []
    checked = 0
    for name in sorted(pages):
        stamp = find_stamp(pages[name])
        if stamp is None:
            continue
        checked += 1
        recorded_hash, _verified_date = stamp
        if recorded_hash != current_hash:
            failures.append(
                f"STALE STAMP: {name}: recorded db-sha256-16={recorded_hash} "
                f"does not match the current db-sha256-16={current_hash} -- "
                "nobody has re-verified this page since the database changed"
            )
    return failures, checked


def compute_db_hash(db_path: Path) -> str:
    digest = hashlib.sha256(db_path.read_bytes()).hexdigest()
    return digest[:STAMP_HASH_LENGTH]


def load_pages(wiki_dir: Path) -> dict[str, str]:
    pages: dict[str, str] = {}
    for path in sorted(wiki_dir.glob("*.md")):
        if path.name in NAV_PAGES:
            continue
        pages[path.name] = path.read_text(encoding="utf-8")
    return pages


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="honest02_truth.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--wiki-dir", type=Path, required=True)
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--allowlist", type=Path, required=True)
    return parser


def main() -> int:
    args = _build_argparser().parse_args()

    if not args.db.is_file():
        print(f"ERROR: --db not found: {args.db}", file=sys.stderr)
        return 2
    if not args.allowlist.is_file():
        print(f"ERROR: --allowlist not found: {args.allowlist}", file=sys.stderr)
        return 2
    if not args.wiki_dir.is_dir():
        print(f"ERROR: --wiki-dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2

    try:
        part_numbers, algorithms = load_database(args.db)
    except PreconditionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    try:
        allow_parts, allow_algorithms = load_allowlist(args.allowlist)
    except PreconditionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    pages = load_pages(args.wiki_dir)
    if not pages:
        print(
            f"ERROR: {args.wiki_dir} contains zero content pages (excluding "
            f"navigation pages {sorted(NAV_PAGES)})",
            file=sys.stderr,
        )
        return 2

    current_hash = compute_db_hash(args.db)

    stamp_failures, pages_matched = check_stamp_present(pages, part_numbers, algorithms)
    resolve_failures, unchecked, regions_found, claims_checked = check_claims_resolve(
        pages, part_numbers, algorithms, allow_parts, allow_algorithms
    )
    freshness_failures, stamps_checked = check_stamp_freshness(pages, current_hash)

    print(
        f"LEG 1 -- stamp present: {len(pages)} pages scanned, {pages_matched} "
        f"matched the claim signature, {len(stamp_failures)} missing stamp"
    )
    for message in stamp_failures:
        print(f"ERROR: {message}", file=sys.stderr)

    print(
        f"LEG 2 -- claims resolve: {regions_found} regions found, "
        f"{claims_checked} claims checked, {len(unchecked)} pages stamp-only "
        "unchecked"
    )
    for message in unchecked:
        print(message)
    for message in resolve_failures:
        print(f"ERROR: {message}", file=sys.stderr)

    print(
        f"LEG 3 -- stamp freshness: {stamps_checked} stamps checked against "
        f"db-sha256-16={current_hash}, {len(freshness_failures)} stale"
    )
    for message in freshness_failures:
        print(f"ERROR: {message}", file=sys.stderr)

    if stamp_failures or resolve_failures or freshness_failures:
        return 1

    print(
        f"OK: leg1 stamp-present {pages_matched} matched/{len(stamp_failures)} "
        f"missing, leg2 claims-resolve {regions_found} regions/"
        f"{claims_checked} claims/{len(unchecked)} unchecked, leg3 "
        f"stamp-freshness {stamps_checked} checked/{len(freshness_failures)} "
        "stale."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
