#!/usr/bin/env python3
r"""
Provenance-comment corpus survey — the SWEEP-03 post-sweep oracle and the
SWEEP-06 hit-count oracle for Phase 154 (dual-repo provenance comment sweep).

Given the two sub-repo roots as explicit positional arguments (`fw_root` for
`firestarter`, `app_root` for `firestarter_app` — NEVER derived from
`__file__`, per D-09 / reference_check_permitted_claims_here_resolves_wrong_phase_dir),
this tool counts every comment/preprocessor line across both repos that opens
with a GSD provenance token, grouped into seven named corpus groups, and
reports the counts on demand so every hit-count criterion in this phase
resolves to one committed command instead of an assertion.

THE REGEX (research's reconstruction, stated verbatim so a future reader can
see exactly what "a hit" means):

    (//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)

Two of the eleven alternations, `P\d{3}` and `REQ-`, match **nothing** on
`beta` (research measured 0 each) — their presence is historical and no
triage effort is budgeted for them.

CORPUS DEFINITION — what is NOT a hit
--------------------------------------
The regex requires the provenance token to sit **immediately after** a
comment opener (`//`, `/*`, a `*`-continuation line, or `#`). Consequences:

  (a) Python **docstrings** are outside the corpus entirely — a docstring
      line does not open with `#`, so no docstring line can ever match,
      regardless of how dense its prose is with provenance tokens.
  (b) A token sitting deeper inside a comment line (not immediately after
      the opener) is not itself a hit on that occurrence.

Measured consequence: `firestarter_app/tests/scan_paths.py` carries **zero**
regex hits even though its module docstring is dense with `D-11` / `A-7` /
`C-8` / `BASE-02` / `Phase 123 Plan 08` labels — a token-anywhere scan over
the app's `.py` files finds about 2,657 further token lines across ~173
files. Extending the sweep there is deliberately NOT done: no measurement
backs a corpus that size, D-03 retains exactly those IDs in test files where
they are the case's traceability key, and several gates assert docstring
content. Consequence for D-04's named keep-in-full case:
`scan_paths.py` is kept in full by **not being edited at all** — recorded
here rather than silently skipped.

GROUPS
------
  fw-src      firestarter/src
  fw-include  firestarter/include
  fw-test     firestarter/test
  fw-lib      firestarter/lib            (measured: 0 files / 0 hits)
  app-pkg     firestarter_app/firestarter
  app-tests   firestarter_app/tests
  app-tools   firestarter_app/tools

Source extensions scanned: .cpp .c .h .hpp .ino .py

EXIT CODES (house 0/1/2 convention)
------------------------------------
  0 — measured and reported (or, under --assert-tokens-zero, no violation).
  1 — a real violation: --assert-tokens-zero found at least one hit line for
      the given token class still present in the selected scope.
  2 — infrastructure: a root argument does not exist / is not a directory;
      an EXPLICITLY selected --group's directory carries zero candidate
      source files (a legitimately empty group like fw-lib is only "0" when
      it is scanned as part of the full, unfiltered corpus — requesting it
      BY NAME and finding nothing is an infrastructure problem, not a
      measurement); or the corpus scanned this run produced zero hit lines
      in total. Silence is never success.

PATH SAFETY (ASVS V5)
----------------------
`--group` only accepts one of the seven fixed group names above (enforced by
argparse `choices`), so no filesystem path, `..` segment, or absolute path
can ever reach this tool through that argument. Every candidate file found
under a group's directory is independently resolved and asserted to still
live under its repo root before being counted, so a symlink cannot walk the
scan outside the two explicit root arguments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Fixed group -> (which root, relative subdirectory) map. Deliberately a
# closed set: --group's argparse `choices` is drawn from this dict's keys,
# so no path-shaped value can ever be accepted here.
# ---------------------------------------------------------------------------
_GROUPS: dict[str, tuple[str, str]] = {
    "fw-src": ("fw", "src"),
    "fw-include": ("fw", "include"),
    "fw-test": ("fw", "test"),
    "fw-lib": ("fw", "lib"),
    "app-pkg": ("app", "firestarter"),
    "app-tests": ("app", "tests"),
    "app-tools": ("app", "tools"),
}

_EXTENSIONS = {".cpp", ".c", ".h", ".hpp", ".ino", ".py"}

# The corpus regex, verbatim per research's reconstruction (see module
# docstring). re.MULTILINE is irrelevant here since matching is done
# per-line, but ^ is kept anchored to line start via per-line application.
_REGEX = re.compile(
    r"(//|/\*|^\s*\*|#)\s*(Task|Phase|Plan|P\d{3}|Req|REQ-|CAP-0|D-\d|WR-\d|LOOP-\d|\d{3}-CONTEXT)"
)

# Named token classes for --assert-tokens-zero, each mapped to the single
# alternation it represents (same comment-opener prefix as _REGEX).
_TOKEN_CLASSES: dict[str, str] = {
    "Task": r"Task",
    "Phase": r"Phase",
    "Plan": r"Plan",
    "P###": r"P\d{3}",
    "Req": r"Req",
    "REQ-": r"REQ-",
    "CAP-0": r"CAP-0",
    "D-#": r"D-\d",
    "WR-#": r"WR-\d",
    "LOOP-#": r"LOOP-\d",
    "###-CONTEXT": r"\d{3}-CONTEXT",
}


def _token_regex(label: str) -> re.Pattern[str]:
    fragment = _TOKEN_CLASSES[label]
    return re.compile(rf"(//|/\*|^\s*\*|#)\s*({fragment})")


def _scan_candidate_files(base: Path, repo_root: Path) -> list[Path]:
    """Every file under `base` with a scanned extension, resolved and
    asserted to still live under `repo_root` (ASVS V5 path-safety check).
    Returns an empty list if `base` does not exist -- that is a legitimate
    zero for an unfiltered run and an infrastructure error for an explicit
    one; the caller decides which."""
    if not base.is_dir():
        return []
    files: list[Path] = []
    for candidate in sorted(base.rglob("*")):
        if not candidate.is_file() or candidate.suffix not in _EXTENSIONS:
            continue
        resolved = candidate.resolve()
        try:
            resolved.relative_to(repo_root)
        except ValueError:
            print(
                f"ERROR: candidate path escapes its repo root, refusing: "
                f"{candidate} -> {resolved} (not under {repo_root})",
                file=sys.stderr,
            )
            sys.exit(2)
        files.append(candidate)
    return files


def _scan_hits(files: list[Path], repo_root: Path) -> dict:
    """Per-file hit-line counts (and the raw (lineno, text) pairs, kept only
    in-process for --assert-tokens-zero -- never serialized to JSON)."""
    file_hits: dict[str, int] = {}
    file_hit_lines: dict[str, list[tuple[int, str]]] = {}
    total_hits = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"ERROR: cannot read {f}: {e}", file=sys.stderr)
            sys.exit(2)
        hits: list[tuple[int, str]] = []
        for lineno, line in enumerate(text.splitlines(), start=1):
            if _REGEX.search(line):
                hits.append((lineno, line))
        if hits:
            rel = str(f.resolve().relative_to(repo_root))
            file_hits[rel] = len(hits)
            file_hit_lines[rel] = hits
            total_hits += len(hits)
    return {
        "candidate_files": len(files),
        "files": len(file_hits),
        "hits": total_hits,
        "file_hits": file_hits,
        "file_hit_lines": file_hit_lines,
    }


def _root_for(kind: str, fw_root: Path, app_root: Path) -> Path:
    return fw_root if kind == "fw" else app_root


def _print_group_table(per_group: dict[str, dict]) -> None:
    print(f"{'group':<12} {'candidate_files':>15} {'files_with_hits':>16} {'hits':>8}")
    for name in sorted(per_group):
        g = per_group[name]
        print(f"{name:<12} {g['candidate_files']:>15} {g['files']:>16} {g['hits']:>8}")


def _print_file_table(per_group: dict[str, dict]) -> None:
    print()
    print(f"{'group':<12} {'hits':>6}  file")
    for name in sorted(per_group):
        for rel, count in sorted(per_group[name]["file_hits"].items()):
            print(f"{name:<12} {count:>6}  {rel}")


def _json_group(g: dict) -> dict:
    return {
        "candidate_files": g["candidate_files"],
        "files": g["files"],
        "hits": g["hits"],
        "file_hits": g["file_hits"],
    }


def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument(
        "fw_root",
        help="firestarter (firmware) repo root -- explicit argument, NEVER derived from __file__",
    )
    ap.add_argument(
        "app_root",
        help="firestarter_app (host) repo root -- explicit argument, NEVER derived from __file__",
    )
    ap.add_argument(
        "--group",
        action="append",
        choices=sorted(_GROUPS),
        default=None,
        help="restrict to one or more named groups (repeatable); default is all seven groups",
    )
    ap.add_argument("--json", action="store_true", help="emit machine-readable per-group/per-file JSON")
    ap.add_argument(
        "--file-table", action="store_true", help="also print a per-file hit-count table"
    )
    ap.add_argument(
        "--assert-tokens-zero",
        metavar="TOKENCLASS",
        choices=sorted(_TOKEN_CLASSES),
        help="exit 1 if any hit line in the selected scope matches this token class, else 0",
    )
    args = ap.parse_args(argv)

    fw_root_arg = Path(args.fw_root)
    app_root_arg = Path(args.app_root)
    for label, root in (("fw_root", fw_root_arg), ("app_root", app_root_arg)):
        if not root.is_dir():
            print(
                f"ERROR: {label} does not exist or is not a directory: {root}",
                file=sys.stderr,
            )
            sys.exit(2)
    fw_root = fw_root_arg.resolve()
    app_root = app_root_arg.resolve()

    explicit_groups = args.group is not None and len(args.group) > 0
    selected = args.group if explicit_groups else sorted(_GROUPS)

    per_group: dict[str, dict] = {}
    for name in selected:
        kind, rel_subdir = _GROUPS[name]
        repo_root = _root_for(kind, fw_root, app_root)
        base = repo_root / rel_subdir
        candidates = _scan_candidate_files(base, repo_root)
        if explicit_groups and len(candidates) == 0:
            print(
                f"ERROR: group {name!r} matched 0 candidate source files under {base} "
                f"(explicit --group selection; an empty group found BY NAME is an "
                f"infrastructure problem, not a measurement).",
                file=sys.stderr,
            )
            sys.exit(2)
        per_group[name] = _scan_hits(candidates, repo_root)

    total_files = sum(g["candidate_files"] for g in per_group.values())
    total_hits = sum(g["hits"] for g in per_group.values())

    if total_hits == 0:
        print(
            "ERROR: the scanned corpus produced zero hit lines across all selected "
            "groups -- silence is never success.",
            file=sys.stderr,
        )
        sys.exit(2)

    if args.assert_tokens_zero:
        token_re = _token_regex(args.assert_tokens_zero)
        violations: list[tuple[str, str, int, str]] = []
        for name in selected:
            for rel, lines in per_group[name]["file_hit_lines"].items():
                for lineno, text in lines:
                    if token_re.search(text):
                        violations.append((name, rel, lineno, text))
        if violations:
            print(
                f"FAIL: --assert-tokens-zero {args.assert_tokens_zero!r} found "
                f"{len(violations)} hit line(s) in scope {selected}:",
                file=sys.stderr,
            )
            for name, rel, lineno, text in violations[:20]:
                print(f"  {name}:{rel}:{lineno}: {text.strip()}", file=sys.stderr)
            if len(violations) > 20:
                print(f"  ... and {len(violations) - 20} more", file=sys.stderr)
            print(f"Total: {len(violations)} violation(s). Exit 1 (BLOCK).", file=sys.stderr)
            sys.exit(1)
        print(
            f"PASS: --assert-tokens-zero {args.assert_tokens_zero!r} -- 0 hit lines in "
            f"scope {selected} ({total_files} candidate files, {total_hits} total corpus "
            f"hit lines examined)."
        )
        sys.exit(0)

    if args.json:
        out = {name: _json_group(g) for name, g in per_group.items()}
        out["summary"] = {
            "candidate_files": total_files,
            "hits": total_hits,
            "groups_selected": selected,
        }
        print(json.dumps(out, indent=2, sort_keys=True))
        sys.exit(0)

    _print_group_table(per_group)
    if args.file_table:
        _print_file_table(per_group)
    print()
    print(
        f"PASS: measured {total_files} candidate files, {total_hits} hit lines "
        f"across {len(selected)} group(s)."
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
