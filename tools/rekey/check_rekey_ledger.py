#!/usr/bin/env python3
"""
Cross-tree checker binding the app-side re-key ledger to
`.planning/MILESTONES.md` (Phase 174, GATE-06, D-13).

Reads BOTH trees from the meta side, the only side that can see both: the
app-side ledger `firestarter_app/tests/fixtures/rekey_ledger.py` is
AUTHORITATIVE and machine-readable (D-09/D-13); `.planning/MILESTONES.md`
narrates it for a human. Every declared (`after_hash is not None`) ledger
row must have a matching `MILESTONES.md` row, and every `RK-174-`
`MILESTONES.md` row must have a matching ledger row -- both directions, so a
row cannot be declared on one side and silently never appear on the other.
An undeclared ledger row (`after_hash is None`) may have no `MILESTONES.md`
row at all, but if one exists for that `ledger_id` a duplicated
`MILESTONES.md` row for the same `ledger_id` is rejected rather than
merged, and the existing row's `shape_id` and `before` cell must match the
ledger's own values while its `after` cell must be the exact literal
`(undeclared)` -- not merely fail a loose hash-shaped regex, so an
off-by-one-character truncation or an uppercase hash is rejected too. A
`MILESTONES.md` carrying zero `RK-174-` rows while the ledger declares any
is also rejected, closing the route of deleting the whole table to escape
every per-row comparison at once.

The ledger is parsed with `ast.parse` plus `ast.literal_eval` on the
`LEDGER` assignment's value -- NEVER imported. A cross-tree import would
also violate the standing "skills must own their scripts" rule, and the
ledger's row shape (plain tuples of `str`/`None`) is authored specifically
so no evaluable expression can reach this parser (D-13).

Both input paths resolve from an explicit `--repo-root`, defaulting to the
current working directory, NEVER from `__file__`'s parent -- this project
has a recorded checker whose directory-relative resolution made it scan
nothing and exit 0.

Exit codes:
  0 -- every declared row has a matching MILESTONES.md row and vice versa
  1 -- a mismatch was found (printed as one ERROR: line per mismatch)
  2 -- an input path is missing, the LEDGER assignment could not be found
       or evaluated, or MILESTONES.md could not be parsed (including a
       duplicated ledger_id row, which is a parse failure rather than a
       mismatch)
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

_LEDGER_DEFAULT = Path("firestarter_app/tests/fixtures/rekey_ledger.py")
_MILESTONES_DEFAULT = Path(".planning/MILESTONES.md")

_ROW_RE = re.compile(
    r"^\|\s*(RK-174-[^\s|]+)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|"
    r"\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*([^|]*?)\s*\|\s*$"
)

_UNDECLARED = "(undeclared)"

LedgerRow = tuple[str, str, "str | None", str]


class LedgerParseError(Exception):
    pass


def parse_ledger(path: Path) -> list[LedgerRow]:
    """Parse `path`'s `LEDGER` module-level assignment with
    `ast.literal_eval`. Raises `LedgerParseError` when the file cannot be
    read, cannot be parsed as Python, or carries no `LEDGER` assignment."""
    if not path.is_file():
        raise LedgerParseError(f"ledger not found: {path}")
    source = path.read_text(encoding="utf-8")
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        raise LedgerParseError(f"ledger is not valid Python: {path}: {exc}") from exc
    for node in ast.walk(tree):
        value = None
        if isinstance(node, ast.Assign) and any(
            getattr(target, "id", "") == "LEDGER" for target in node.targets
        ):
            value = node.value
        elif (
            isinstance(node, ast.AnnAssign)
            and getattr(node.target, "id", "") == "LEDGER"
            and node.value is not None
        ):
            value = node.value
        if value is not None:
            try:
                rows = ast.literal_eval(value)
            except (ValueError, SyntaxError) as exc:
                raise LedgerParseError(
                    f"LEDGER assignment in {path} is not literal_eval-able: {exc}"
                ) from exc
            return list(rows)
    raise LedgerParseError(f"no LEDGER assignment found in {path}")


def parse_milestones_rows(path: Path) -> dict[str, tuple[str, str, str]]:
    """Parse the `### v1.36 Re-Key Ledger` table's `RK-174-` rows out of
    `path`, keyed by `ledger_id`, each value `(shape_id, before, after)`.
    Only pipe-delimited rows whose `ledger_id` cell starts with `RK-174-`
    are collected -- the header and separator rows never match `_ROW_RE`."""
    if not path.is_file():
        raise LedgerParseError(f"milestones file not found: {path}")
    rows: dict[str, tuple[str, str, str]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _ROW_RE.match(line.strip())
        if m:
            ledger_id, shape_id, _change, _owner, before, after, _declared = m.groups()
            if ledger_id in rows:
                raise LedgerParseError(
                    f"duplicate MILESTONES.md row for ledger_id {ledger_id!r}"
                )
            rows[ledger_id] = (shape_id, before, after)
    return rows


def check(
    ledger_rows: list[LedgerRow], milestones_rows: dict[str, tuple[str, str, str]]
) -> list[str]:
    """Both-directions comparison. Returns a list of `ERROR:` message
    strings; an empty list means the two trees agree."""
    errors: list[str] = []
    ledger_by_id = {row[3]: row for row in ledger_rows}

    if ledger_rows and not milestones_rows:
        errors.append(
            f"ERROR: MILESTONES.md carries 0 RK-174- row(s) while the "
            f"ledger declares {len(ledger_rows)} row(s)"
        )

    for row in ledger_rows:
        shape_id, before_hash, after_hash, ledger_id = row
        m_row = milestones_rows.get(ledger_id)
        if after_hash is not None:
            if m_row is None:
                errors.append(
                    f"ERROR: declared ledger row {ledger_id!r} "
                    f"(after_hash={after_hash!r}) has no MILESTONES.md row"
                )
                continue
            if m_row != (shape_id, before_hash, after_hash):
                errors.append(
                    f"ERROR: {ledger_id!r} MILESTONES.md row {m_row!r} does "
                    f"not match ledger row {(shape_id, before_hash, after_hash)!r}"
                )
        else:
            if m_row is not None:
                if (m_row[0], m_row[1]) != (shape_id, before_hash):
                    errors.append(
                        f"ERROR: {ledger_id!r} MILESTONES.md row "
                        f"(shape_id, before)={(m_row[0], m_row[1])!r} does not "
                        f"match ledger row (shape_id, before_hash)="
                        f"{(shape_id, before_hash)!r}"
                    )
                if m_row[2] != _UNDECLARED:
                    errors.append(
                        f"ERROR: {ledger_id!r} is undeclared in the ledger "
                        f"but MILESTONES.md's after cell {m_row[2]!r} is "
                        f"not the exact literal {_UNDECLARED!r}"
                    )

    for ledger_id in milestones_rows:
        if ledger_id not in ledger_by_id:
            errors.append(
                f"ERROR: MILESTONES.md row {ledger_id!r} has no matching ledger row"
            )

    return errors


def _build_argparser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="check_rekey_ledger.py",
        description=(
            "Bind the app-side re-key ledger to .planning/MILESTONES.md "
            "(GATE-06, D-13)."
        ),
    )
    p.add_argument("--repo-root", type=Path, default=Path.cwd())
    p.add_argument("--ledger", type=Path, default=None)
    p.add_argument("--milestones", type=Path, default=None)
    return p


def main() -> int:
    args = _build_argparser().parse_args()
    ledger_path = (
        args.ledger if args.ledger is not None else args.repo_root / _LEDGER_DEFAULT
    )
    milestones_path = (
        args.milestones
        if args.milestones is not None
        else args.repo_root / _MILESTONES_DEFAULT
    )

    try:
        ledger_rows = parse_ledger(ledger_path)
        milestones_rows = parse_milestones_rows(milestones_path)
    except LedgerParseError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors = check(ledger_rows, milestones_rows)
    if errors:
        for err in errors:
            print(err)
        return 1

    print(
        f"OK: {len(ledger_rows)} ledger row(s), {len(milestones_rows)} "
        "MILESTONES.md row(s) bound"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
