#!/usr/bin/env python3
"""
tools/wiki/honest01_claims.py -- one-shot proof that migrating 12 doc/ files
onto the published GitHub wiki upgraded no claim.

Exit-code contract:
  0 = every claim token the source carried is present at least as often on
      the published page, for every resolvable row
  1 = a claim token was dropped, or a row's source or destination text could
      not be resolved and read
  2 = a precondition was not met (a required path missing, or the
      vocabulary file missing or malformed)

The comparison unit is a claim-token multiset (tools/wiki/claim-vocabulary.json),
never a text diff: the migration rewrote titles, rewrote links for a flat page
namespace, stripped GSD framing and added stamps, so a text or line diff is
guaranteed non-empty for reasons that have nothing to do with a claim being
softened.

The source side is read exclusively with `git -C <subrepo> show <sha>:<path>`
against the pre-deletion SHAs recorded in tools/wiki/MIGRATION-TABLE.md --
firestarter/doc/ and firestarter_app/doc/ are both deleted, and that git ref
is the only surviving oracle for the pre-migration text.

This checker is a one-shot proof, not a standing gate. It runs once during
the migration, is demonstrated failing on a deliberately weakened claim, and
its output is committed as evidence; then it retires. Once doc/ is gone its
source side is frozen at the recorded commits forever, and nothing after
this phase stops a later wiki edit from quietly softening a claim the
migrated documents made.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from wiki import strip_code_spans

TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$")
WHITESPACE_RE = re.compile(r"\s+")
NO_SHA_MARKER = "—"
REQUIRED_VOCAB_KEYS = ("schema_version", "families", "expected_zero")


class UnresolvedRow(Exception):
    def __init__(self, page: str, reason: str) -> None:
        super().__init__(reason)
        self.page = page
        self.reason = reason


def load_vocabulary(vocab_path: Path) -> dict:
    with vocab_path.open(encoding="utf-8") as handle:
        vocabulary = json.load(handle)
    for key in REQUIRED_VOCAB_KEYS:
        if key not in vocabulary:
            raise ValueError(f"vocabulary is missing required key {key!r}")
    for family_name, family in vocabulary["families"].items():
        if family.get("match") not in ("literal", "regex"):
            raise ValueError(f"family {family_name!r} has an unknown match mode")
        if not family.get("tokens"):
            raise ValueError(f"family {family_name!r} has no tokens")
    return vocabulary


def parse_migration_table(table_path: Path) -> list[dict[str, str]]:
    header: list[str] = []
    in_table = False
    rows: list[dict[str, str]] = []
    for line in table_path.read_text(encoding="utf-8").splitlines():
        match = TABLE_ROW_RE.match(line)
        if match is None:
            in_table = False
            continue
        cells = [cell.strip() for cell in match.group(1).split("|")]
        if not header:
            header = cells
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            in_table = True
            continue
        if not in_table:
            continue
        rows.append(dict(zip(header, cells)))
    return [row for row in rows if row.get("Pre-deletion SHA", NO_SHA_MARKER) != NO_SHA_MARKER]


def source_relative_path(source_repo: str, source_path: str) -> str:
    prefix = f"{source_repo}/"
    if source_path.startswith(prefix):
        return source_path[len(prefix) :]
    return source_path


def read_source_at_sha(repo_root: Path, source_repo: str, source_path: str, sha: str) -> str:
    subrepo_dir = repo_root / source_repo
    relative_path = source_relative_path(source_repo, source_path)
    result = subprocess.run(
        ["git", "-C", str(subrepo_dir), "show", f"{sha}:{relative_path}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise UnresolvedRow(
            source_path,
            f"git show {sha}:{relative_path} in {subrepo_dir} failed: "
            f"{result.stderr.strip()}",
        )
    if not result.stdout.strip():
        raise UnresolvedRow(source_path, f"git show {sha}:{relative_path} returned empty text")
    return result.stdout


def read_destination_page(wiki_dir: Path, wiki_page: str) -> str:
    page_path = wiki_dir / f"{wiki_page}.md"
    if not page_path.is_file():
        raise UnresolvedRow(wiki_page, f"{page_path} does not exist")
    text = page_path.read_text(encoding="utf-8")
    if not text.strip():
        raise UnresolvedRow(wiki_page, f"{page_path} is empty")
    return text


def normalize(text: str, lowercase: bool) -> str:
    collapsed = WHITESPACE_RE.sub(" ", strip_code_spans(text))
    return collapsed.lower() if lowercase else collapsed


def count_literal(text: str, token: str, case_sensitive: bool) -> int:
    haystack = text if case_sensitive else text.lower()
    needle = token if case_sensitive else token.lower()
    return haystack.count(needle)


def count_regex(text: str, pattern: str, case_sensitive: bool) -> int:
    flags = 0 if case_sensitive else re.IGNORECASE
    return len(re.findall(pattern, text, flags))


def count_tokens(text: str, vocabulary: dict) -> Counter:
    counts: Counter = Counter()
    for family in vocabulary["families"].values():
        case_sensitive = bool(family.get("case_sensitive", False))
        normalized = normalize(text, lowercase=not case_sensitive)
        for token in family["tokens"]:
            if family["match"] == "literal":
                counts[token] += count_literal(normalized, token, case_sensitive)
            else:
                counts[token] += count_regex(normalized, token, case_sensitive)
    known_tokens = {
        token for family in vocabulary["families"].values() for token in family["tokens"]
    }
    normalized_case_sensitive = normalize(text, lowercase=False)
    for token in vocabulary["expected_zero"]:
        if token in known_tokens:
            continue
        counts[token] += count_literal(normalized_case_sensitive, token, case_sensitive=True)
    return counts


def token_family(token: str, vocabulary: dict) -> str:
    for family_name, family in vocabulary["families"].items():
        if token in family["tokens"]:
            return family_name
    return "expected_zero"


def compare_multisets(
    page: str, source_counts: Counter, dest_counts: Counter, vocabulary: dict
) -> tuple[list[str], list[str]]:
    dropped: list[str] = []
    added: list[str] = []
    tokens = sorted(set(source_counts) | set(dest_counts))
    for token in tokens:
        source_count = source_counts[token]
        dest_count = dest_counts[token]
        family = token_family(token, vocabulary)
        if source_count > dest_count:
            dropped.append(
                f"{page}: token {token!r} (family={family}) source={source_count} "
                f"dest={dest_count}"
            )
        elif dest_count > source_count:
            added.append(
                f"{page}: token {token!r} (family={family}) source={source_count} "
                f"dest={dest_count}"
            )
    return dropped, added


def _build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="honest01_claims.py",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--table", type=Path, required=True, default=None)
    parser.add_argument("--wiki-dir", type=Path, required=True, default=None)
    parser.add_argument("--vocab", type=Path, required=True, default=None)
    parser.add_argument("--repo-root", type=Path, required=True, default=None)
    return parser


def main() -> int:
    args = _build_argparser().parse_args()

    if not args.table.is_file():
        print(f"ERROR: --table not found: {args.table}", file=sys.stderr)
        return 2
    if not args.wiki_dir.is_dir():
        print(f"ERROR: --wiki-dir not found: {args.wiki_dir}", file=sys.stderr)
        return 2
    if not args.repo_root.is_dir():
        print(f"ERROR: --repo-root not found: {args.repo_root}", file=sys.stderr)
        return 2
    if not args.vocab.is_file():
        print(f"ERROR: --vocab not found: {args.vocab}", file=sys.stderr)
        return 2

    try:
        vocabulary = load_vocabulary(args.vocab)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: could not load vocabulary {args.vocab}: {exc}", file=sys.stderr)
        return 2

    rows = parse_migration_table(args.table)
    if not rows:
        print(f"ERROR: {args.table} contains no rows with a Pre-deletion SHA", file=sys.stderr)
        return 2

    unresolved: list[str] = []
    all_dropped: list[str] = []
    all_added: list[str] = []
    total_source: Counter = Counter()
    total_dest: Counter = Counter()
    pages_compared = 0

    for row in rows:
        page = row["Wiki page"]
        try:
            source_text = read_source_at_sha(
                args.repo_root,
                row["Source repo"],
                row["Source path"],
                row["Pre-deletion SHA"],
            )
            dest_text = read_destination_page(args.wiki_dir, page)
        except UnresolvedRow as exc:
            unresolved.append(f"{exc.page}: {exc.reason}")
            continue

        source_counts = count_tokens(source_text, vocabulary)
        dest_counts = count_tokens(dest_text, vocabulary)
        total_source.update(source_counts)
        total_dest.update(dest_counts)
        pages_compared += 1

        dropped, added = compare_multisets(page, source_counts, dest_counts, vocabulary)
        all_dropped.extend(dropped)
        all_added.extend(added)

    vacuous: list[str] = []
    for token in vocabulary["expected_zero"]:
        if total_source[token] == 0 and total_dest[token] == 0:
            vacuous.append(f"{token!r}: 0 of 0 -- VACUOUS, not checked")

    tokens_compared = len({token for token in total_source} | {token for token in total_dest})

    if unresolved:
        print("UNRESOLVED:", file=sys.stderr)
        for message in unresolved:
            print(f"ERROR: unresolved row: {message}", file=sys.stderr)

    if all_dropped:
        print("DROPPED:", file=sys.stderr)
        for message in all_dropped:
            print(f"ERROR: dropped claim: {message}", file=sys.stderr)

    if all_added:
        print("ADDED:")
        for message in all_added:
            print(f"NOTE: added claim: {message}")

    if vacuous:
        print("VACUOUS (expected_zero, not folded into the pass line):")
        for message in vacuous:
            print(f"NOTE: {message}")

    if unresolved or all_dropped:
        return 1

    print(
        f"OK: {pages_compared} pages compared, {tokens_compared} tokens compared, "
        f"0 dropped, {len(all_added)} added, {len(vacuous)} vacuous."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
