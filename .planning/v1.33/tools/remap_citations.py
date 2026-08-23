#!/usr/bin/env python3
r"""
Citation remap tool for milestone v1.33 (SWEEP-11 -> REMAP-01..05).

WHAT IT DOES
------------
Reads the pre-sweep citation manifest produced by `build_citation_manifest.py`
(Phase 154 plan 04) and rewrites the line numbers of `path:N`, `path:N-M`,
`path:N,M`, `path#LN` and `path#LN-LM` citations inside `.planning/` documents
so that each citation still points at the line it described after the comment
sweep moved that line.

BUILT IN PHASE 154, APPLIED IN PHASE 159 -- NEVER BOTH (D-01 / D-10)
--------------------------------------------------------------------
The remap runs EXACTLY ONCE, in Phase 159, over the composite pre-154 ->
post-158 diff. D-10 records why the roadmap's sweep-last fallback was declined:
723 citations would otherwise be remapped twice, 41% of that rework caused by
four added `#include` lines, and composing four successive mappings would create
a range-shrinking hazard that one composite mapping avoids. Phase 154 therefore
BUILDS this tool and does not run it against any real `.planning/` document, so
`test_remap_citations.py` carries the whole proof burden.

Dry-run is the DEFAULT. `--apply` is required before a single byte is written.

THE LINE MAP
------------
`difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)` over line
lists. Stdlib only: no third-party dependency and no package manifest, matching
the `.planning/v1.16/ledger/tools/` precedent D-09 names. Two choices are
load-bearing:

  * `autojunk=False` is REQUIRED, not cosmetic. The default heuristic treats any
    element occurring in more than 1% of a sequence of at least 200 items as
    junk. Over a real ~900-line C++ file, ubiquitous lines like a lone closing
    brace, a lone `//` or a blank line are auto-junked and silently excluded
    from `equal` runs, which corrupts the map. MEASURED this session on
    `firestarter/src/proms/eeprom_28c.cpp` (920 lines) against a realistic
    provenance-stripping edit: 812 surviving lines with the flag off, 810 with
    it on -- old lines 412 and 413 map differently. Same shape on
    `firestarter_app/firestarter/cli_handlers.py` (2694 lines): 2537 vs 2535.
    A synthetic 500-line fixture built for the same purpose did NOT diverge,
    which is exactly research Pitfall 2's point: the bug hides on small
    fixtures and only shows on real files.

  * `replace` is treated as non-surviving, exactly like `delete`. A reflowed
    comment is a `replace`: its text changed, so the manifest's `source_text`
    can no longer match at the destination and the citation cannot round-trip.
    Such a record is flagged `retarget` and left for a human (D-08) instead of
    being assigned a positional number the oracle would then reject. Mapping
    `replace` positionally would manufacture false green.

THE PRE-SWEEP SIDE COMES FROM GIT, NOT FROM DISK
------------------------------------------------
By the time the remap runs in Phase 159 the pre-sweep content exists nowhere on
disk, so the "old" side is read with `git show <sha>:./<path>`. The `./` prefix
makes the path CWD-relative rather than repo-root-relative, so the same command
works whether a root is its own git repository (production: `firestarter` and
`firestarter_app` are separate repos) or a plain sub-directory of one enclosing
repository (the unit test's tmp fixture repo). `git diff -U0` is kept as an
INDEPENDENT CROSS-CHECK in the unit test only -- never as the production
mechanism, because it needs a subprocess per file and both endpoints resolvable
as git revisions, and it adds submodule/detached-HEAD failure modes for no gain.

RANGE ENDPOINTS ARE MAPPED INDEPENDENTLY (REMAP-03)
---------------------------------------------------
A range START clamps FORWARD to the next surviving line; a range END clamps
BACKWARD to the previous surviving line. The shrink property is not a special
case with its own branch -- it falls out automatically, because the accumulated
deletion offset differs at the two endpoints. On a 20-line fixture with 5 lines
deleted in two separated blocks, `map_range(m, 3, 18, 20)` returns
`(3, 13, False)`: old span 16 becomes new span 11, shrinking by exactly the 5
deleted lines. A constant-offset implementation returns `(-2, 13)` and is wrong.

`colon_list` elements (`path:N,M`) are handled as independent POINT citations
with forward clamping, never as a range. Research measured 194 occurrences of
the variant in the swept-targeting corpus (678 records) and the requirements do
not mention it, so the conservative reading is the one implemented.

IDEMPOTENCY == THE ORACLE == RESUMABILITY (one design, three requirements)
-------------------------------------------------------------------------
The REMAP-02 round-trip oracle IS the write predicate. Per record, in order:

  1. FIXED POINT. If the text at the citation's CURRENT line already equals the
     manifest's `source_text`, the record is already correct -> no-op. This
     alone makes run 2 a no-op.
  2. IDENTITY. Otherwise rewrite only when the number in the document equals the
     manifest's recorded PRE-sweep `target_line`. NEVER key a rewrite off "is
     this integer in the map's domain" -- that is the naive form research
     measured drifting `:15` -> `:10` -> `:8` -> `:6` on successive runs,
     because a map built from two separated deletion blocks contains a CHAIN
     (`map[15] = 10` and `map[10] = 8`).
  3. ORACLE. Assert the text at the destination equals `source_text` BEFORE
     writing. A mismatch means the map is wrong: fail loudly, write nothing.

A RECORD IS BOUND TO A CITATION POSITIONALLY, NEVER BY ITS LINE NUMBER
---------------------------------------------------------------------
The obvious binding -- find the integer in the text and look the record up by it
-- is wrong, and the chained fixture caught it during this plan's execution.
After run 1 the `colon_list` citation `chained_demo.cpp:15,20` reads `:10,15`.
That `15` is the ALREADY-REWRITTEN value of the record for old line 20, while a
DIFFERENT record was recorded for old line 15; a number-keyed lookup binds it to
the wrong record and rewrites it to `10`. MEASURED before the fix: `10,15` drifts
to `10,10` on run 2. A line number is not a unique identifier within a line.

Records are therefore bound POSITIONALLY within a `(cited path, variant)` group:
the generator appends records inside a `finditer` loop, so for one
`(planning_file, planning_line)` the manifest's record order for a group is the
document order of that group's citation spans. A length mismatch between the two
is never guessed at -- it is counted and the group is skipped. Every record of a
line takes part in the binding, including inert ones, because dropping an inert
row would misalign every later element of its group.

For the same reason the FIXED-POINT check is evaluated over the WHOLE match, not
per element: a `colon_list` whose elements have all been rewritten is a fixed
point as a whole even though no single element still sits at its recorded
pre-sweep number.

This single design gives SWEEP-11's idempotency, REMAP-02's oracle and
REMAP-05's resumability at once -- a partially-applied remap resumes correctly
because already-correct records are recognised as fixed points rather than
re-shifted. Breaking it breaks all three.

RETARGET RECORDS ARE NOT WRITTEN
--------------------------------
A `retarget` record's new target is HAND-CHOSEN. The clamp this tool computes is
a starting suggestion for the human, never the answer, so a retarget record is
reported and counted and its citation is left exactly as written (D-08). Phase
159's oracle skips these BY NAME instead of failing open on them. The same is
true of any record whose `text_status` is not `read`: an unresolved, ambiguous,
rejected or past-EOF row carries the `<UNREADABLE>` sentinel instead of a real
`source_text`, so it has no oracle and is skipped by name.

FAIL CLOSED, NEVER FAIL OPEN (D-09)
-----------------------------------
The repo root is a REQUIRED POSITIONAL ARGUMENT and nothing in this module
derives a root from its own location. Per
`reference_check_permitted_claims_here_resolves_wrong_phase_dir`, a checker
whose root is derived from its own file location scans nothing and exits 0 when
the file is moved -- the named house analog
`.planning/v1.16/ledger/tools/check_ledger.py` hard-codes four `..` segments
against its own location and is exactly the shape D-09 forbids. Also forbidden
is a DEFAULT for `--manifest`: an absent manifest is an error, not a derived
path. Silence is never success, so an empty input set exits non-zero.

The `firestarter` name-collision trap is why this module resolves NOTHING
itself: `firestarter_app/tests/scan_paths.py` documents that one `..` from a
`tools/` directory lands in the app's own Python package and two reach the
sibling firmware repo, and research F5 shows the same trap in citation form (99
citations to `firestarter.h` collide with the app's fake-firestarter fixture
copy). Path resolution is imported from `citation_paths` -- the SAME module
`build_citation_manifest.py` uses -- so a citation cannot resolve one way in the
generator and another way here. Every `target_file_resolved` this tool accepts is
additionally passed through that module's fixture guard, because a citation bound
to a planted fixture would round-trip GREEN against the wrong file (T-154-13).

PATH SAFETY (ASVS V5/V12)
-------------------------
Every path is repo-relative, carries no parent-traversal segment and is not
absolute; the resolved path must still lie inside the explicit repo root; a
symlinked document is refused rather than followed out of the tree; and writes
are atomic (temp file in the same directory, then `os.replace`).

Exit codes (house 0/1/2 convention):
  0 -- every applicable record processed and the oracle held. Counts printed:
       records examined, rewritten, already at their fixed point, and flagged
       `retarget`. A PASS naming zero records is visibly wrong, so it cannot
       happen -- see exit 2.
  1 -- a real violation. An oracle assertion failed (the text at the mapped
       destination is not the recorded `source_text`), or a record's
       `target_file_resolved` does not exist on disk, or a resolved target is
       fixture-shaped. Nothing is written when this happens: the whole run is
       planned before any byte is written, so a violation anywhere aborts
       everything.
  2 -- infrastructure. The manifest could not be loaded or parsed, the manifest
       parsed to ZERO records, the applicable input set is EMPTY, a required
       pre-sweep sha is missing, a root directory does not exist, or the
       pre-sweep blob could not be read from git. Kept distinct from 1 so a CI
       consumer cannot confuse a missing input with a real BLOCK.
"""

from __future__ import annotations

import argparse
import difflib
import json
import os
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import build_citation_manifest as bcm
import citation_paths

#: Reused from the generator rather than re-declared, so the remapper cannot
#: recognise a different citation grammar than the manifest was built from.
CITATION_RE = bcm._CITATION_RE
spans_from_match = bcm._spans_from_match

#: `text_status` values other than this one carry the `<UNREADABLE>` sentinel
#: instead of a real `source_text`, so they have no oracle and are skipped BY
#: NAME (never silently).
TEXT_STATUS_READ = bcm.TEXT_STATUS_READ

# Outcome labels. Exactly one is assigned to every span of every record, so the
# reported counts always sum to the number of records examined.
REWRITE = "rewrite"
FIXED_POINT = "fixed_point"
RETARGET = "retarget"
NOT_AT_RECORDED_LINE = "not_at_recorded_line"
UNREADABLE_ROW = "skipped_unreadable"
FLAGGED_RETARGET = "skipped_flagged_retarget"
NO_MATCH_IN_DOCUMENT = "no_match_in_document"
VIOLATION = "violation"

OUTCOMES = (
    REWRITE,
    FIXED_POINT,
    RETARGET,
    NOT_AT_RECORDED_LINE,
    UNREADABLE_ROW,
    FLAGGED_RETARGET,
    NO_MATCH_IN_DOCUMENT,
    VIOLATION,
)


# ---------------------------------------------------------------------------
# The line map. Prototyped in research §R1 and reproduced here unchanged, so a
# reader can diff the two.
# ---------------------------------------------------------------------------
def build_map(old_lines: list[str], new_lines: list[str]) -> dict[int, int | None]:
    """old 1-based line -> new 1-based line, or None if the line did not survive.

    `autojunk=False` is required -- see the module docstring for the measured
    corruption it prevents. `replace` is non-surviving exactly like `delete`.
    """
    sm = difflib.SequenceMatcher(None, old_lines, new_lines, autojunk=False)
    m: dict[int, int | None] = {}
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                m[i1 + k + 1] = j1 + k + 1
        elif tag in ("delete", "replace"):
            for k in range(i1, i2):
                m[k + 1] = None
    return m


def surviving(m: dict[int, int | None], n_old: int) -> list[int]:
    """Ascending old line numbers that survived verbatim."""
    return sorted(line for line in range(1, n_old + 1) if m.get(line) is not None)


def map_point(
    m: dict[int, int | None],
    line: int,
    n_old: int,
    direction: str,
    survivors: list[int] | None = None,
) -> tuple[int | None, bool]:
    """Map one point. Returns (new_line_or_None, retarget).

    `direction='fwd'` for a range START (clamp to the next survivor) and
    `'back'` for a range END (clamp to the previous survivor). A clamp always
    sets `retarget=True`: the returned number is a documented SUGGESTION for a
    human, never an answer the oracle may act on.
    """
    if m.get(line) is not None:
        return m[line], False
    surv = surviving(m, n_old) if survivors is None else survivors
    if direction == "fwd":
        later = [ln for ln in surv if ln > line]
        return (m[later[0]], True) if later else (None, True)
    earlier = [ln for ln in surv if ln < line]
    return (m[earlier[-1]], True) if earlier else (None, True)


def map_range(
    m: dict[int, int | None],
    a: int,
    b: int,
    n_old: int,
    survivors: list[int] | None = None,
) -> tuple[int | None, int | None, bool]:
    """Map both endpoints INDEPENDENTLY. The shrink property falls out of this."""
    a2, ra = map_point(m, a, n_old, "fwd", survivors)
    b2, rb = map_point(m, b, n_old, "back", survivors)
    return a2, b2, (ra or rb)


class LineMap:
    """One target file's old->new map plus its new text, with cached survivors."""

    def __init__(self, old_lines: list[str], new_lines: list[str]) -> None:
        self.old_lines = old_lines
        self.new_lines = new_lines
        self.n_old = len(old_lines)
        self.map = build_map(old_lines, new_lines)
        self._survivors: list[int] | None = None

    @property
    def survivors(self) -> list[int]:
        if self._survivors is None:
            self._survivors = surviving(self.map, self.n_old)
        return self._survivors

    def point(self, line: int, direction: str) -> tuple[int | None, bool]:
        return map_point(self.map, line, self.n_old, direction, self.survivors)

    def span(self, a: int, b: int) -> tuple[int | None, int | None, bool]:
        return map_range(self.map, a, b, self.n_old, self.survivors)

    def text_at(self, line: int | None) -> str | None:
        if line is None or line < 1 or line > len(self.new_lines):
            return None
        return self.new_lines[line - 1]


# ---------------------------------------------------------------------------
# Fail-closed loading
# ---------------------------------------------------------------------------
def _die(message: str, code: int) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(code)


def load_manifest(path: Path) -> tuple[dict, list[dict]]:
    """Load the JSONL manifest. Any load/parse problem is infrastructure (2)."""
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        _die(f"cannot load manifest {path}: {exc}", 2)
    header: dict = {}
    records: list[dict] = []
    for lineno, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError as exc:
            _die(f"manifest {path} line {lineno} is not valid JSON: {exc}", 2)
        if "_schema" in obj:
            header = obj["_schema"]
            continue
        missing = [k for k in bcm.RECORD_KEYS if k not in obj]
        if missing:
            _die(
                f"manifest {path} line {lineno} is missing required key(s) "
                f"{missing}; the manifest schema is the input contract",
                2,
            )
        records.append(obj)
    if not records:
        _die(
            f"manifest {path} parsed to ZERO records -- an empty input set is "
            "never a success (D-09)",
            2,
        )
    return header, records


def git_show(root_dir: Path, sha: str, subpath: str) -> str | None:
    """Pre-sweep blob text, or None if git cannot produce it.

    `<sha>:./<subpath>` is deliberate: the `./` prefix makes the path
    CWD-relative, so this works whether `root_dir` is its own repository or a
    sub-directory of an enclosing one.
    """
    try:
        done = subprocess.run(
            ["git", "-C", str(root_dir), "show", f"{sha}:./{subpath}"],
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if done.returncode != 0:
        return None
    return done.stdout


# ---------------------------------------------------------------------------
# Per-span decision -- the write predicate
# ---------------------------------------------------------------------------
@dataclass
class Outcome:
    outcome: str
    start: int | None
    end: int | None
    detail: str


def is_fixed_point(
    record: dict, cur_start: int, cur_end: int | None, lm: LineMap
) -> bool:
    """True when the number(s) the document ALREADY carries point at the
    recorded pre-sweep text in the POST-sweep file.

    This is check 1 of the three-check write predicate and it is what makes the
    tool idempotent and a partial run resumable (REMAP-05).
    """
    if lm.text_at(cur_start) != record["source_text"]:
        return False
    if cur_end is not None and lm.text_at(cur_end) != record["source_text_end"]:
        return False
    return True


def decide(record: dict, cur_start: int, cur_end: int | None, lm: LineMap) -> Outcome:
    """Checks 2 and 3 of the write predicate: IDENTITY, then MAP, then ORACLE.

    Check 1 (fixed point) is applied one level up, over the WHOLE match -- see
    `remap_document` for why the granularity matters.
    """
    src = record["source_text"]
    src_end = record["source_text_end"]

    # 2. IDENTITY -- only the recorded PRE-sweep number is ever rewritten.
    #    Never "is this integer a key of the map".
    if cur_start != record["target_line"] or cur_end != record["target_line_end"]:
        return Outcome(
            NOT_AT_RECORDED_LINE,
            cur_start,
            cur_end,
            f"document reads {cur_start}-{cur_end} but the manifest recorded "
            f"{record['target_line']}-{record['target_line_end']}",
        )

    # 3. MAP, then ORACLE.
    if cur_end is None:
        new_start, retarget = lm.point(cur_start, "fwd")
        new_end = None
    else:
        new_start, new_end, retarget = lm.span(cur_start, cur_end)

    if retarget or new_start is None or (cur_end is not None and new_end is None):
        return Outcome(
            RETARGET,
            new_start,
            new_end,
            "the cited line did not survive the sweep; the clamp "
            f"({new_start}-{new_end}) is a SUGGESTION for a human, not an "
            "answer (D-08)",
        )

    if lm.text_at(new_start) != src:
        return Outcome(
            VIOLATION,
            new_start,
            new_end,
            f"oracle violated at the mapped start line {new_start}: expected "
            f"{src!r}, found {lm.text_at(new_start)!r}",
        )
    if new_end is not None and lm.text_at(new_end) != src_end:
        return Outcome(
            VIOLATION,
            new_start,
            new_end,
            f"oracle violated at the mapped end line {new_end}: expected "
            f"{src_end!r}, found {lm.text_at(new_end)!r}",
        )
    return Outcome(REWRITE, new_start, new_end, "mapped and oracle-verified")


# ---------------------------------------------------------------------------
# Citation rendering -- the matched text is rebuilt in its own syntactic form
# ---------------------------------------------------------------------------
def render_citation(
    path: str, variant: str, numbers: list[int], anchor_end_keeps_l: bool
) -> str:
    if variant == bcm.VARIANT_ANCHOR:
        return f"{path}#L{numbers[0]}"
    if variant == bcm.VARIANT_ANCHOR_RANGE:
        sep = "-L" if anchor_end_keeps_l else "-"
        return f"{path}#L{numbers[0]}{sep}{numbers[1]}"
    if variant == bcm.VARIANT_COLON_RANGE:
        return f"{path}:{numbers[0]}-{numbers[1]}"
    if variant == bcm.VARIANT_COLON_LIST:
        return f"{path}:" + ",".join(str(n) for n in numbers)
    return f"{path}:{numbers[0]}"


def _anchor_end_keeps_l(matched: str) -> bool:
    """True when the matched anchor range was written `#LA-LB`, not `#LA-B`."""
    _head, _, tail = matched.partition("#L")
    return tail.count("-L") == 1


# ---------------------------------------------------------------------------
# Document remapping
# ---------------------------------------------------------------------------
def _associate(
    line_text: str,
    records: list[dict],
    counts: Counter,
    notes: list[str],
    where: str,
) -> tuple[list, dict[tuple[int, int], dict]]:
    """Bind manifest records to the citation spans actually present in a line.

    WHY POSITIONAL, NOT NUMBER-KEYED
    --------------------------------
    The obvious binding -- look the record up by the integer found in the text
    -- is WRONG, and the chained fixture caught it: after run 1 the
    `colon_list` citation `chained_demo.cpp:15,20` reads `:10,15`, and the `15`
    is now the ALREADY-REWRITTEN value of the record for old line 20 while a
    DIFFERENT record was recorded for old line 15. A number-keyed lookup binds
    that `15` to the wrong record and rewrites it to `10`, giving the measured
    drift `10,15` -> `10,10` on run 2. A line number is not a unique
    identifier within a line.

    The binding used instead is POSITIONAL within a `(cited path, variant)`
    group: the generator appends records inside a `finditer` loop, so for a
    given `(planning_file, planning_line)` the manifest's record order for a
    group IS the document order of that group's spans. Zipping the two is
    therefore exact, and it is immune to a number having already been
    rewritten. A length mismatch is not guessed at: it is counted and skipped.
    """
    matches = list(CITATION_RE.finditer(line_text))
    span_groups: dict[tuple[str, str], list[tuple[int, int, int, int | None]]] = (
        defaultdict(list)
    )
    for mi, mo in enumerate(matches):
        cited = mo.group("path")
        for si, (variant, start, end) in enumerate(spans_from_match(mo)):
            span_groups[(cited, variant)].append((mi, si, start, end))

    record_groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for rec in records:
        record_groups[(rec["target_file_cited"], rec["variant"])].append(rec)

    assigned: dict[tuple[int, int], dict] = {}
    for key, recs in record_groups.items():
        spans = span_groups.get(key, [])
        if len(spans) != len(recs):
            counts[NO_MATCH_IN_DOCUMENT] += len(recs)
            notes.append(
                f"{where} has {len(recs)} manifest record(s) for "
                f"{key[0]} ({key[1]}) but {len(spans)} matching citation "
                "span(s) in the document -- binding is ambiguous, so nothing "
                "is written for that group"
            )
            continue
        for span, rec in zip(spans, recs):
            assigned[(span[0], span[1])] = rec
    return matches, assigned


def remap_document(
    doc_text: str,
    records_by_line: dict[int, list[dict]],
    maps: dict[str, LineMap],
    counts: Counter,
    notes: list[str],
    violations: list[str],
    planning_file: str,
) -> str:
    lines = doc_text.split("\n")
    for lineno, records in sorted(records_by_line.items()):
        where = f"{planning_file}:{lineno}"
        if lineno < 1 or lineno > len(lines):
            counts[NO_MATCH_IN_DOCUMENT] += len(records)
            notes.append(
                f"{where} is past EOF ({len(lines)} lines); "
                f"{len(records)} record(s) matched no citation"
            )
            continue

        line_text = lines[lineno - 1]
        matches, assigned = _associate(line_text, records, counts, notes, where)
        if not assigned:
            continue

        replacements: dict[int, str] = {}
        for mi, mo in enumerate(matches):
            cited = mo.group("path")
            spans = spans_from_match(mo)
            variant = spans[0][0]
            pairs = [
                (si, spans[si], assigned[(mi, si)])
                for si in range(len(spans))
                if (mi, si) in assigned
            ]
            if not pairs:
                continue

            # ---- INERT rows are skipped BY NAME, never silently. They still
            # took part in the positional binding above -- that is deliberate:
            # dropping them from the binding would misalign every later element
            # of the same group. A `retarget: true` row's new target is
            # HAND-CHOSEN (D-08), and a row whose `text_status` is not `read`
            # carries the `<UNREADABLE>` sentinel instead of a real
            # `source_text`, so it has no oracle at all.
            actionable = []
            for si, sp, rec in pairs:
                counts["examined"] += 1
                target = f"{rec['target_file_cited']}:{sp[1]}"
                if rec["retarget"]:
                    counts[FLAGGED_RETARGET] += 1
                    notes.append(
                        f"{where} {target} is flagged retarget in the manifest "
                        "-- hand-chosen target, left exactly as written (D-08)"
                    )
                    continue
                if rec["text_status"] != TEXT_STATUS_READ or (
                    sp[2] is not None and rec["text_status_end"] != TEXT_STATUS_READ
                ):
                    counts[UNREADABLE_ROW] += 1
                    notes.append(
                        f"{where} {target} has text_status="
                        f"{rec['text_status']!r} / text_status_end="
                        f"{rec['text_status_end']!r} -- no recorded source text "
                        "on at least one endpoint, so no oracle; skipped by name"
                    )
                    continue
                lm = maps.get(rec["target_file_resolved"])
                if lm is None:
                    counts[UNREADABLE_ROW] += 1
                    notes.append(
                        f"{where} {target} resolves to "
                        f"{rec['target_file_resolved']} for which no line map "
                        "exists; skipped"
                    )
                    continue
                actionable.append((si, sp, rec, lm))
            if not actionable:
                continue

            # ---- CHECK 1, at MATCH granularity: is the whole citation already
            # a fixed point? Every actionable span's CURRENT number must point
            # at its own record's recorded text in the POST-sweep file.
            # Evaluating this per span would be too fine: a `colon_list` whose
            # elements have already been rewritten is a fixed point AS A WHOLE
            # even though no single element sits at its recorded pre-sweep
            # number any more.
            if all(
                is_fixed_point(rec, sp[1], sp[2], lm)
                for _si, sp, rec, lm in actionable
            ):
                counts[FIXED_POINT] += len(actionable)
                continue

            rendered = [sp[1] for sp in spans]
            touched = False
            for si, sp, rec, lm in actionable:
                start, end = sp[1], sp[2]
                out = decide(rec, start, end, lm)
                counts[out.outcome] += 1
                target = f"{rec['target_file_resolved']}:{start}" + (
                    f"-{end}" if end is not None else ""
                )
                if out.outcome == VIOLATION:
                    violations.append(f"{where} {target} -- {out.detail}")
                    continue
                if out.outcome in (RETARGET, NOT_AT_RECORDED_LINE):
                    notes.append(f"{where} {target} -- {out.detail}")
                    continue
                if out.outcome != REWRITE:
                    continue
                touched = True
                if end is None:
                    rendered[si] = out.start
                else:
                    rendered = [out.start, out.end]
            if touched:
                replacements[mi] = render_citation(
                    cited,
                    variant,
                    [int(n) for n in rendered],
                    _anchor_end_keeps_l(mo.group(0)),
                )

        if replacements:
            # Splice right-to-left so earlier match offsets stay valid.
            for mi in sorted(replacements, reverse=True):
                mo = matches[mi]
                line_text = (
                    line_text[: mo.start()] + replacements[mi] + line_text[mo.end() :]
                )
            lines[lineno - 1] = line_text
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Path safety
# ---------------------------------------------------------------------------
def safe_relative(rel: str, label: str) -> str:
    """Reject an absolute, `~`-rooted or `..`-carrying path outright (ASVS V5)."""
    norm = rel.replace("\\", "/").strip()
    if not norm:
        _die(f"{label} is empty", 1)
    if norm.startswith("/") or norm.startswith("~") or (
        len(norm) > 1 and norm[1] == ":"
    ):
        _die(f"{label} {rel!r} is not repo-relative", 1)
    if ".." in norm.split("/"):
        _die(f"{label} {rel!r} carries a parent-traversal segment", 1)
    return norm


def inside(repo_root: Path, rel: str, label: str) -> Path:
    target = (repo_root / rel).resolve()
    if target != repo_root and repo_root not in target.parents:
        _die(f"{label} {rel!r} resolves outside the repo root: {target}", 1)
    return target


def atomic_write(path: Path, text: str) -> None:
    if path.is_symlink():
        _die(f"refusing to write through the symlink {path}", 1)
    fd, tmp_name = tempfile.mkstemp(dir=str(path.parent), prefix=path.name + ".", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(text)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


# ---------------------------------------------------------------------------
# Pre-sweep sha resolution
# ---------------------------------------------------------------------------
class ShaResolver:
    """Pre-sweep revision per root name, argv winning over the manifest header.

    Precedence, highest first:
      1. `--pre-sweep-sha NAME=SHA`  -- an explicit per-root argument.
      2. `--pre-sweep-sha SHA`       -- a bare argument applying to every root.
      3. the manifest header's recorded `pre_sweep_shas`.

    The header is a legitimate LAST resort rather than a derived default: it is
    DATA inside the declared input file, not a path inferred from this module's
    own location. Argv must still win, because Phase 159 maps a COMPOSITE
    pre-154 -> post-158 diff whose old side is not the revision the manifest was
    generated at.
    """

    def __init__(self, header: dict, cli_shas: list[str]) -> None:
        self.header: dict[str, str] = {
            name: sha
            for name, sha in (header.get("pre_sweep_shas") or {}).items()
            if name != "note" and isinstance(sha, str) and sha
        }
        self.per_root: dict[str, str] = {}
        self.catch_all: str | None = None
        for spec in cli_shas:
            if "=" in spec:
                name, _, sha = spec.partition("=")
                self.per_root[name.strip()] = sha.strip()
            else:
                self.catch_all = spec.strip()

    def for_root(self, name: str) -> str | None:
        return self.per_root.get(name) or self.catch_all or self.header.get(name)


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------
def main(argv: list[str] | None = None) -> None:
    ap = argparse.ArgumentParser(
        description=(
            "Remap .planning/ citation line numbers across the comment sweep. "
            "Built in Phase 154, applied in Phase 159 (D-01/D-10). The repo "
            "root is an explicit argument and is never derived from this "
            "module's own location (D-09). Dry-run is the default."
        )
    )
    ap.add_argument(
        "repo_root",
        help="explicit meta-repo root; never derived from this module's location",
    )
    ap.add_argument(
        "--manifest",
        required=True,
        help="pre-sweep citation manifest (JSONL). No default: an absent "
        "manifest is an error, never a derived path.",
    )
    ap.add_argument(
        "--pre-sweep-sha",
        action="append",
        default=[],
        metavar="[NAME=]SHA",
        help="pre-sweep revision for a root (repeatable, e.g. "
        "firestarter=8695ee5); a bare SHA applies to every root. Overrides the "
        "manifest header's recorded pre_sweep_shas.",
    )
    ap.add_argument(
        "--apply",
        action="store_true",
        help="write the rewritten documents; the default is a dry run",
    )
    ap.add_argument(
        "--quiet-notes",
        action="store_true",
        help="suppress the per-record note list (counts are always printed)",
    )
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root)
    if not repo_root.is_dir():
        _die(f"repo_root does not exist or is not a directory: {repo_root}", 2)
    repo_root = repo_root.resolve()

    manifest_path = Path(args.manifest)
    if not manifest_path.is_absolute():
        manifest_path = (Path.cwd() / manifest_path).resolve()
    header, records = load_manifest(manifest_path)

    shas = ShaResolver(header, args.pre_sweep_sha)

    # ---- which records are actionable at all -------------------------------
    applicable = [
        rec
        for rec in records
        if not rec["retarget"]
        and rec["text_status"] == TEXT_STATUS_READ
        and rec["target_file_resolved"]
        and (
            rec["target_line_end"] is None
            or rec["text_status_end"] == TEXT_STATUS_READ
        )
    ]
    if not applicable:
        _die(
            f"the manifest holds {len(records)} record(s) but NONE is "
            "actionable (every row is retarget-flagged or carries no readable "
            "source text) -- an empty input set is never a success (D-09)",
            2,
        )

    # ---- build one line map per target file --------------------------------
    targets = sorted({rec["target_file_resolved"] for rec in applicable})
    root_names = sorted({safe_relative(t, "target_file_resolved").split("/")[0] for t in targets})
    roots: dict[str, Path] = {}
    for name in root_names:
        root_dir = repo_root / name
        if not root_dir.is_dir():
            _die(
                f"root {name!r} referenced by the manifest does not exist "
                f"under the explicit repo root: {root_dir}",
                2,
            )
        roots[name] = root_dir

    try:
        index = citation_paths.CandidateIndex(roots, targets)
    except (ValueError, NotADirectoryError) as exc:
        _die(f"the manifest's resolved target paths are not indexable: {exc}", 1)

    # ---- T-154-13: a citation must never be bound to a PLANTED COPY of a real
    # file. A fixture-shaped resolved path is NOT a violation by itself -- the
    # v1.33 manifest legitimately carries 6 such records, because some
    # `.planning/` documents cite a planted fixture BY NAME and that fixture is
    # the only candidate carrying the basename. Two declared shapes are
    # legitimate and everything else is a collision:
    #   (a) the citation as WRITTEN is itself fixture-shaped, so the author
    #       named the fixture deliberately (`exact` / `suffix` resolutions);
    #   (b) the record resolved through `citation_paths`' explicitly-labelled
    #       fixture-inclusive fallback, which runs only when NO non-fixture
    #       candidate carries the basename at all.
    # The fallback is recognised via the shared module's CONSTANT, not an inline
    # string: an inline copy would fail OPEN the day the reason is reworded.
    colliding: list[str] = []
    legitimate_fixture_rows = 0
    for rec in applicable:
        resolved = rec["target_file_resolved"]
        if not citation_paths.looks_like_fixture(resolved):
            continue
        if citation_paths.looks_like_fixture(rec["target_file_cited"]) or (
            rec["resolution_reason"]
            == citation_paths.FIXTURE_INCLUSIVE_FALLBACK_REASON
        ):
            legitimate_fixture_rows += 1
            continue
        colliding.append(
            f"{rec['planning_file']}:{rec['planning_line']} cites "
            f"{rec['target_file_cited']!r} which bound to {resolved} "
            f"({rec['resolution']}: {rec['resolution_reason']})"
        )
    if colliding:
        print(
            "FAIL: citation(s) bound to a PLANTED COPY of a real file, which "
            "would round-trip GREEN against the wrong file (T-154-13):",
            file=sys.stderr,
        )
        for row in colliding:
            print(f"  {row}", file=sys.stderr)
        print(
            f"Total: {len(colliding)} violation(s). Exit 1 (BLOCK).",
            file=sys.stderr,
        )
        sys.exit(1)

    maps: dict[str, LineMap] = {}
    missing_targets: list[str] = []
    for rel in targets:
        name, _, subpath = rel.partition("/")
        disk = index.real_path(rel)
        if not disk.is_file():
            missing_targets.append(rel)
            continue
        sha = shas.for_root(name)
        if not sha:
            _die(
                f"no pre-sweep sha for root {name!r}: pass "
                f"--pre-sweep-sha {name}=<sha> or record it in the manifest "
                "header",
                2,
            )
        old_text = git_show(roots[name], sha, subpath)
        if old_text is None:
            _die(
                f"cannot read the pre-sweep blob {sha}:./{subpath} from "
                f"{roots[name]} -- the 'old' side of the map must come from "
                "git, because it exists nowhere on disk",
                2,
            )
        maps[rel] = LineMap(
            old_text.splitlines(),
            disk.read_text(encoding="utf-8", errors="replace").splitlines(),
        )

    if missing_targets:
        print(
            "FAIL: record(s) name a target_file_resolved that does not exist "
            "on disk:",
            file=sys.stderr,
        )
        for rel in missing_targets:
            print(f"  {rel}", file=sys.stderr)
        print(
            f"Total: {len(missing_targets)} violation(s). Exit 1 (BLOCK).",
            file=sys.stderr,
        )
        sys.exit(1)

    # ---- plan every document before writing anything -----------------------
    # EVERY record is grouped, not only the actionable ones: the record-to-span
    # binding inside a `(cited path, variant)` group is POSITIONAL, so dropping
    # an inert row here would misalign every later element of its group. Inert
    # rows are recognised and skipped by name inside `remap_document`.
    by_doc: dict[str, dict[int, list[dict]]] = defaultdict(lambda: defaultdict(list))
    for rec in records:
        rel = safe_relative(rec["planning_file"], "planning_file")
        by_doc[rel][rec["planning_line"]].append(rec)

    counts: Counter = Counter()
    notes: list[str] = []
    violations: list[str] = []
    planned: dict[Path, str] = {}

    for rel in sorted(by_doc):
        doc_path = inside(repo_root, rel, "planning_file")
        if doc_path.is_symlink():
            _die(f"refusing to read the citing document through a symlink: {rel}", 1)
        if not doc_path.is_file():
            _die(f"citing document does not exist: {rel}", 1)
        original = doc_path.read_text(encoding="utf-8")
        updated = remap_document(
            original, by_doc[rel], maps, counts, notes, violations, rel
        )
        if updated != original:
            planned[doc_path] = updated

    if violations:
        print("FAIL: the round-trip oracle was violated -- nothing was written:\n", file=sys.stderr)
        for v in violations:
            print(f"  {v}", file=sys.stderr)
        print(
            f"\nTotal: {len(violations)} violation(s). Exit 1 (BLOCK).",
            file=sys.stderr,
        )
        sys.exit(1)

    if notes and not args.quiet_notes:
        print(f"notes ({len(notes)}):")
        for note in notes:
            print(f"  {note}")
        print()

    if args.apply:
        for path, text in planned.items():
            atomic_write(path, text)

    mode = "APPLIED" if args.apply else "DRY RUN (no bytes written; pass --apply)"
    print(
        f"PASS [{mode}]: {counts['examined']} record(s) examined across "
        f"{len(by_doc)} document(s) and {len(maps)} target file(s); "
        f"{counts[REWRITE]} rewritten, {counts[FIXED_POINT]} already at their "
        f"fixed point, {counts[RETARGET] + counts[FLAGGED_RETARGET]} flagged "
        f"retarget, {counts[NOT_AT_RECORDED_LINE]} not at their recorded line, "
        f"{counts[UNREADABLE_ROW]} skipped as unreadable, "
        f"{counts[NO_MATCH_IN_DOCUMENT]} unmatched in their document; "
        f"{legitimate_fixture_rows} record(s) legitimately cite a planted "
        "fixture by name; "
        f"{len(planned)} document(s) "
        + ("changed." if args.apply else "would change.")
    )
    sys.exit(0)


if __name__ == "__main__":
    main()
