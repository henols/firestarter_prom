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

PHASE 159 HARDENING (REMAP-01/02/05) -- ADDITIONS OVER THE PHASE-154 ENGINE
----------------------------------------------------------------------------
The primitives above are unchanged. Everything below is ADDITIVE and is a
strict no-op unless its own flag is passed, so every Phase-154 behaviour and
every Phase-154 test remains byte-for-byte identical when none of the new
flags are used.

  * `stable_record_id()` -- a deterministic identity for a manifest record,
    used by every new surface below so an exception, an open-review count or a
    receipt line can name a record without depending on file order.

  * Multi-anchor historical maps. A record MAY carry its own `source_sha`
    (or, for a `retarget: true` row, `retarget_source_sha`) instead of the
    root-wide `--pre-sweep-sha` default, and the line-map cache is keyed by
    `(target_file_resolved, source_sha)` rather than path alone, so two
    records citing the same file at two different historical anchors get two
    independent maps. A record may instead carry a non-unique
    `source_sha_candidates` list, which stays BLOCKING (a violation) until an
    `--exceptions` ledger row supplies a `chosen_source_sha` contained in that
    list -- never guessed at.

  * `LocationResolver` -- reconciles a manifest's recorded `planning_file`
    against live topology when it no longer exists at that path: an approved
    `--corpus-overlay` row (bytes must equal one of its two declared hashes;
    a third state is rejected, never guessed at), or a tracked git rename
    detected between `--planning-base-sha` and the live worktree. An
    unresolved citing document remains the existing exit-1 BLOCK.

  * Fail-closed hardening is engaged by the mere PRESENCE of `--exceptions`
    (a reviewed ledger, JSONL, one row per stable record ID with
    `"status": "reviewed"` and either `chosen_target_line`/
    `chosen_current_text` (target/anchor review) or `chosen_source_sha`
    (anchor-candidate review)). Without `--exceptions` every Phase-154
    diagnostic behaviour is unchanged (dynamic retarget/unmatched rows are
    still notes, exit 0). With it, every actionable dynamic retarget,
    not-at-recorded-line and unmatched-in-document row not covered by a
    reviewed ledger entry becomes a violation (exit 1, nothing written); a
    reviewed entry is re-verified against its OWN `chosen_current_text`
    oracle before being treated as a fixed point or rewrite.

  * `BatchTransaction` -- an optional receipted apply (`--production-receipt`,
    `--recovery-bundle`). Preimages are captured before the first byte is
    written; each replacement is recorded as it happens; a caught failure
    restores every already-replaced path from the preimage bundle and marks
    the receipt `FAILED` / `rollback_status: COMPLETE`. A pre-existing receipt
    blocks a new apply. `recover_failed_receipt()` / `--recover-receipt`
    performs recovery ONLY -- it never resumes or replays an apply.
    `--inject-write-failure-after N` exists to prove this contract in
    disposable tests and refuses to run against the canonical `/workspaces`
    root.

  * `build_index_stage_plan()` / `--index-plan` -- describes, per affected
    document, a citation-only staging strategy: a clean tracked file's whole
    updated text is safe to stage; a DIRTY tracked file gets a
    `citation_only_blob` computed by re-applying the SAME citation edits to
    the committed INDEX content (never the live dirty bytes), via the same
    `remap_document()` used for the real apply; an untracked or renamed path
    reports `staging_strategy: requires_authorization` rather than silently
    staging a whole file.

  * `--report-json` -- a structured, deterministic report (`totals`,
    `actionable_counts`, `open_ids`, `affected_documents`,
    `corpus_fingerprint`, `topology_digest`, `range_proofs`) alongside the
    existing human-readable summary line.

None of the above is exercised against any real `.planning/` document by this
plan: it creates no manifest and performs no real-corpus apply.
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import uuid
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
#: Phase 159 addition: an actionable RETARGET/NOT_AT_RECORDED_LINE outcome
#: with no reviewed `--exceptions` ledger entry, once hardening is engaged.
UNREVIEWED_RETARGET = "unreviewed_retarget"

OUTCOMES = (
    REWRITE,
    FIXED_POINT,
    RETARGET,
    NOT_AT_RECORDED_LINE,
    UNREADABLE_ROW,
    FLAGGED_RETARGET,
    NO_MATCH_IN_DOCUMENT,
    VIOLATION,
    UNREVIEWED_RETARGET,
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


def load_jsonl_rows(path: Path) -> list[dict]:
    """Generic JSONL row loader for `--exceptions` and `--corpus-overlay`.

    Deliberately schema-light: those two surfaces are Phase 159-02/03/04
    deliverables, and this plan only needs to prove the ENGINE reacts to a
    reviewed/approved row correctly, not to author the ledgers themselves.
    """
    rows: list[dict] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            _die(f"{path} line {lineno} is not valid JSON: {exc}", 2)
    return rows


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
# Stable record identity (Phase 159 -- REMAP-01/02)
# ---------------------------------------------------------------------------
def stable_record_id(record: dict) -> str:
    """Deterministic stable ID for a manifest record.

    A supplemental/late record MAY carry its own explicit `record_id` (Phase
    159's preparer is required to mint one); when present it is returned
    unchanged, so an external identity is never silently replaced. Otherwise
    an ID is DERIVED from the record's own positional identity -- planning
    location, citation shape and pre-sweep coordinates -- which is stable
    across a re-run because none of those fields change without a manifest
    edit. Hashing avoids ever writing an incrementing counter that would
    depend on record ORDER, which is not guaranteed stable across a JSONL
    reload.
    """
    explicit = record.get("record_id")
    if explicit:
        return str(explicit)
    basis = "\x1f".join(
        str(record.get(key, ""))
        for key in (
            "planning_file",
            "planning_line",
            "variant",
            "target_file_cited",
            "target_line",
            "target_line_end",
        )
    )
    digest = hashlib.sha256(basis.encode("utf-8")).hexdigest()[:16]
    return f"orig-{digest}"


# ---------------------------------------------------------------------------
# Planning-location reconciliation (Phase 159 -- REMAP-01/02)
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class LocationOutcome:
    status: str  # "found" | "overlay" | "renamed" | "missing"
    resolved_path: str | None
    reason: str


class LocationResolver:
    """Reconciles a manifest's recorded `planning_file` against live topology.

    Three sources are consulted, in order, and NONE of them guesses:

      1. the recorded path, if it still exists -- unchanged Phase-154 case.
      2. an approved `--corpus-overlay` row, whose current bytes must equal
         one of its two declared hashes (`preapply_sha256` or
         `expected_postapply_sha256`) -- a THIRD state (present but neither
         hash matches) is REJECTED outright, never accepted as a guess.
      3. a tracked git rename detected between `--planning-base-sha` and the
         live worktree, via `git diff --find-renames`.

    An unresolved path is reported `missing` and is the caller's exit-1 BLOCK,
    exactly like the existing "citing document does not exist" case.
    """

    def __init__(
        self,
        repo_root: Path,
        planning_base_sha: str | None = None,
        overlays: list[dict] | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.planning_base_sha = planning_base_sha
        self.overlays: dict[str, dict] = {
            row["path"]: row for row in (overlays or []) if row.get("path")
        }
        self._rename_cache: dict[str, str | None] = {}

    def resolve(self, planning_file: str) -> LocationOutcome:
        direct = self.repo_root / planning_file
        if direct.is_file() and not direct.is_symlink():
            return LocationOutcome("found", planning_file, "exists at its recorded path")

        overlay = self.overlays.get(planning_file)
        if overlay is not None:
            current = overlay.get("current_path")
            candidate = self.repo_root / current if current else None
            if candidate is not None and candidate.is_file() and not candidate.is_symlink():
                digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
                approved = {
                    overlay.get("preapply_sha256"),
                    overlay.get("expected_postapply_sha256"),
                } - {None}
                if digest in approved:
                    return LocationOutcome(
                        "overlay",
                        current,
                        "approved corpus overlay matches live path and bytes",
                    )
            return LocationOutcome(
                "missing",
                None,
                f"a corpus overlay is recorded for {planning_file!r} but its live "
                "path/bytes match neither approved hash -- rejected, not guessed at",
            )

        renamed = self._tracked_rename(planning_file)
        if renamed:
            return LocationOutcome(
                "renamed",
                renamed,
                "resolved via a tracked git rename from --planning-base-sha",
            )

        return LocationOutcome(
            "missing",
            None,
            "citing document does not exist and no approved overlay or tracked "
            "rename covers it",
        )

    def _tracked_rename(self, planning_file: str) -> str | None:
        if not self.planning_base_sha:
            return None
        if planning_file in self._rename_cache:
            return self._rename_cache[planning_file]
        target: str | None = None
        try:
            # No pathspec here, deliberately: restricting the diff to the OLD
            # path alone stops git's rename detection from ever pairing it
            # with a destination outside that pathspec (measured: the same
            # command WITH `-- planning_file` reports a plain delete). The
            # full diff is scanned instead for the specific rename row whose
            # source matches this planning_file.
            done = subprocess.run(
                [
                    "git", "-C", str(self.repo_root), "diff",
                    "--find-renames=50%", "--name-status",
                    self.planning_base_sha, "HEAD",
                ],
                capture_output=True, text=True, check=False,
            )
        except OSError:
            done = None
        if done is not None and done.returncode == 0:
            for line in done.stdout.splitlines():
                parts = line.split("\t")
                if len(parts) >= 3 and parts[0].startswith("R") and parts[1] == planning_file:
                    target = parts[2]
                    break
        self._rename_cache[planning_file] = target
        return target


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


def resolve_with_review(
    natural: Outcome,
    record: dict,
    record_id: str,
    exceptions: dict[str, dict] | None,
    lm: LineMap,
    strict: bool,
) -> Outcome:
    """Reconcile a RETARGET/NOT_AT_RECORDED_LINE outcome against the reviewed
    `--exceptions` ledger, or classify it as blocking once hardening is
    engaged and no review covers it (REMAP-02).

    `strict` is engaged by the mere PRESENCE of `--exceptions`: an operator
    who has not yet built a ledger gets the original Phase-154 diagnostic
    behaviour unchanged (a dry-run note, exit 0). Once a ledger exists, every
    actionable retarget/mislocation not explicitly reviewed becomes a
    contract violation, never a silent note -- and a reviewed row is
    re-verified against its OWN `chosen_current_text` oracle before being
    trusted, so a stale review cannot silently corrupt the corpus either.
    """
    if natural.outcome not in (RETARGET, NOT_AT_RECORDED_LINE):
        return natural

    entry = (exceptions or {}).get(record_id)
    if entry is not None and entry.get("status") == "reviewed":
        chosen_start = entry.get("chosen_target_line")
        chosen_end = entry.get("chosen_target_line_end")
        chosen_text = entry.get("chosen_current_text")
        chosen_text_end = entry.get("chosen_current_text_end")
        if chosen_start is None or chosen_text is None:
            return Outcome(
                UNREVIEWED_RETARGET,
                natural.start,
                natural.end,
                f"{record_id}'s reviewed ledger entry is missing "
                "chosen_target_line/chosen_current_text -- not a usable review",
            )
        if lm.text_at(chosen_start) != chosen_text or (
            chosen_end is not None and lm.text_at(chosen_end) != chosen_text_end
        ):
            return Outcome(
                VIOLATION,
                chosen_start,
                chosen_end,
                f"reviewed target for {record_id} failed its current-target-text "
                "oracle -- the chosen coordinate no longer reads the chosen text",
            )
        if (
            record.get("target_line") == chosen_start
            and record.get("target_line_end") == chosen_end
        ):
            return Outcome(
                FIXED_POINT, chosen_start, chosen_end, "reviewed target is already a fixed point"
            )
        return Outcome(REWRITE, chosen_start, chosen_end, "reviewed retarget applied")

    if not strict:
        return natural
    return Outcome(
        UNREVIEWED_RETARGET,
        natural.start,
        natural.end,
        f"{record_id} is an actionable {natural.outcome} outcome with no reviewed "
        "exceptions-ledger entry -- blocking under fail-closed hardening (REMAP-02)",
    )


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
    violations: list[str],
    strict: bool,
    open_ids: set[str] | None = None,
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
    rewritten. A length mismatch is not guessed at: it is counted and skipped
    -- and, once fail-closed hardening is engaged (`strict`), it is ALSO a
    blocking violation rather than a note-only outcome (REMAP-02).
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
            for rec in recs:
                rid = stable_record_id(rec)
                if open_ids is not None:
                    open_ids.add(rid)
                if strict:
                    violations.append(
                        f"{where} {key[0]} ({rid}) has no unambiguous matching "
                        "citation span in the document -- unmatched rows are "
                        "blocking under fail-closed hardening (REMAP-02)"
                    )
            continue
        for span, rec in zip(spans, recs):
            assigned[(span[0], span[1])] = rec
    return matches, assigned


def remap_document(
    doc_text: str,
    records_by_line: dict[int, list[dict]],
    maps: dict[tuple[str, str], LineMap],
    counts: Counter,
    notes: list[str],
    violations: list[str],
    planning_file: str,
    exceptions: dict[str, dict] | None = None,
    strict: bool = False,
    open_ids: set[str] | None = None,
    range_proofs: list[dict] | None = None,
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
            for rec in records:
                rid = stable_record_id(rec)
                if open_ids is not None:
                    open_ids.add(rid)
                if strict:
                    violations.append(
                        f"{where} ({rid}) is past EOF -- unmatched rows are "
                        "blocking under fail-closed hardening (REMAP-02)"
                    )
            continue

        line_text = lines[lineno - 1]
        matches, assigned = _associate(
            line_text, records, counts, notes, where, violations, strict, open_ids
        )
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
                lm = maps.get((rec["target_file_resolved"], rec.get("_effective_source_sha")))
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
                natural = decide(rec, start, end, lm)
                rid = stable_record_id(rec)
                out = resolve_with_review(natural, rec, rid, exceptions, lm, strict)
                counts[out.outcome] += 1
                target = f"{rec['target_file_resolved']}:{start}" + (
                    f"-{end}" if end is not None else ""
                )
                if out.outcome in (RETARGET, NOT_AT_RECORDED_LINE, UNREVIEWED_RETARGET):
                    if open_ids is not None:
                        open_ids.add(rid)
                if out.outcome in (VIOLATION, UNREVIEWED_RETARGET):
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
                    if range_proofs is not None:
                        range_proofs.append(
                            {
                                "record_id": rid,
                                "old_start": start,
                                "old_end": end,
                                "new_start": out.start,
                                "new_end": out.end,
                                "old_span": end - start + 1,
                                "new_span": (
                                    out.end - out.start + 1 if out.end is not None else None
                                ),
                            }
                        )
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


def write_json_report(path: Path, data: object) -> None:
    """Atomically write a structured JSON report/plan/receipt."""
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    atomic_write(path, json.dumps(data, indent=2, sort_keys=True, default=str) + "\n")


# ---------------------------------------------------------------------------
# Batch transaction: receipted, recoverable apply (Phase 159 -- REMAP-01/05)
# ---------------------------------------------------------------------------
def read_receipt(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class BatchTransaction:
    """A receipted, recoverable multi-document apply.

    `planned` is already fully computed text by the time this is constructed
    -- exactly as the legacy `--apply` loop always was. What is new is the
    receipt: preimages are captured before the first byte is written, every
    replaced path is recorded as it happens, and a caught failure restores
    every already-replaced path from the preimage bundle rather than leaving
    a half-applied corpus with no record of which half.

    The state machine is `PREPARED -> APPLYING -> APPLIED` on success, or
    `PREPARED -> APPLYING -> FAILED` (with `rollback_status: COMPLETE`) on any
    caught exception. There is no automatic retry: a `FAILED` receipt stops
    execution and `recover_failed_receipt()` / `--recover-receipt` is the only
    sanctioned path back, and it NEVER resumes or replays the apply itself.
    """

    def __init__(
        self,
        repo_root: Path,
        planned: dict[Path, str],
        receipt_path: Path,
        recovery_bundle_dir: Path,
        input_fingerprint: str,
        inject_failure_after: int | None = None,
    ) -> None:
        self.repo_root = repo_root
        self.planned = planned
        self.receipt_path = receipt_path
        self.recovery_bundle_dir = recovery_bundle_dir
        self.input_fingerprint = input_fingerprint
        self.inject_failure_after = inject_failure_after
        self.event_id = uuid.uuid4().hex

    def _rel(self, path: Path) -> str:
        try:
            return str(path.relative_to(self.repo_root)).replace(os.sep, "/")
        except ValueError:
            return str(path)

    def preflight(self) -> None:
        """A pre-existing receipt blocks a new apply (REMAP-01: one shot)."""
        if self.receipt_path.exists():
            existing = read_receipt(self.receipt_path)
            _die(
                f"a production receipt already exists at {self.receipt_path} "
                f"with status {existing.get('status')!r} -- a pre-existing "
                "receipt blocks a new apply; recover it with --recover-receipt "
                "or move it aside before retrying",
                1,
            )

    def _write_receipt(self, **fields) -> dict:
        receipt = {
            "status": None,
            "event_id": self.event_id,
            "production_apply_events": 0,
            "input_fingerprint": self.input_fingerprint,
            "planned_documents": sorted(self._rel(p) for p in self.planned),
            "replaced_documents": [],
            "preimage_hashes": {},
            "recovery_bundle_sha256": None,
            "rollback_status": None,
            "failure": None,
        }
        receipt.update(fields)
        write_json_report(self.receipt_path, receipt)
        return receipt

    def prepare(self) -> dict:
        """Render preimages + an exclusive recoverable bundle before any write."""
        self.recovery_bundle_dir.mkdir(parents=True, exist_ok=True)
        preimages: dict[str, str] = {}
        bundle_manifest: dict[str, str] = {}
        for path in self.planned:
            rel = self._rel(path)
            original = path.read_text(encoding="utf-8") if path.is_file() else ""
            preimages[rel] = hashlib.sha256(original.encode("utf-8")).hexdigest()
            fname = rel.replace("/", "__")
            (self.recovery_bundle_dir / fname).write_text(original, encoding="utf-8")
            bundle_manifest[rel] = fname
        write_json_report(self.recovery_bundle_dir / "_bundle_manifest.json", bundle_manifest)
        bundle_digest = hashlib.sha256(
            json.dumps(bundle_manifest, sort_keys=True).encode("utf-8")
        ).hexdigest()
        return self._write_receipt(
            status="PREPARED",
            preimage_hashes=preimages,
            recovery_bundle_sha256=bundle_digest,
        )

    def apply(self) -> dict:
        """Transition PREPARED -> APPLYING -> APPLIED|FAILED."""
        prepared = read_receipt(self.receipt_path)
        self._write_receipt(
            status="APPLYING",
            preimage_hashes=prepared["preimage_hashes"],
            recovery_bundle_sha256=prepared["recovery_bundle_sha256"],
        )
        replaced: list[str] = []
        try:
            for index, (path, text) in enumerate(sorted(self.planned.items(), key=lambda kv: self._rel(kv[0]))):
                if (
                    self.inject_failure_after is not None
                    and index >= self.inject_failure_after
                ):
                    raise RuntimeError(
                        "injected write failure for test purposes "
                        f"(after {self.inject_failure_after} replacement(s))"
                    )
                atomic_write(path, text)
                replaced.append(self._rel(path))
        except BaseException as exc:  # noqa: BLE001 -- must roll back on ANY failure
            self._rollback(replaced)
            return self._write_receipt(
                status="FAILED",
                preimage_hashes=prepared["preimage_hashes"],
                recovery_bundle_sha256=prepared["recovery_bundle_sha256"],
                replaced_documents=replaced,
                rollback_status="COMPLETE",
                failure={
                    "message": str(exc),
                    "after_document": replaced[-1] if replaced else None,
                },
            )
        return self._write_receipt(
            status="APPLIED",
            preimage_hashes=prepared["preimage_hashes"],
            recovery_bundle_sha256=prepared["recovery_bundle_sha256"],
            replaced_documents=replaced,
            production_apply_events=1,
        )

    def _rollback(self, replaced: list[str]) -> None:
        manifest = json.loads(
            (self.recovery_bundle_dir / "_bundle_manifest.json").read_text(encoding="utf-8")
        )
        for rel in replaced:
            fname = manifest[rel]
            original = (self.recovery_bundle_dir / fname).read_text(encoding="utf-8")
            atomic_write(self.repo_root / rel, original)


def recover_failed_receipt(receipt_path: Path, repo_root: Path, recovery_bundle_dir: Path) -> dict:
    """Recovery-only: restore bytes from the bundle and verify preimage hashes.

    Never resumes or replays an apply. A receipt already terminal
    (`APPLIED`, `RECOVERED`, or `FAILED` with `rollback_status == COMPLETE`)
    is left untouched and returned as-is: recovery of an already-settled
    receipt is a no-op, not a second event.
    """
    receipt = read_receipt(receipt_path)
    if receipt.get("status") == "APPLIED":
        return receipt
    if receipt.get("status") == "RECOVERED":
        return receipt
    if receipt.get("status") == "FAILED" and receipt.get("rollback_status") == "COMPLETE":
        return receipt

    manifest_path = recovery_bundle_dir / "_bundle_manifest.json"
    if not manifest_path.is_file():
        _die(f"no recovery bundle manifest at {manifest_path}", 2)
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    restored: list[str] = []
    for rel, fname in manifest.items():
        bundle_file = recovery_bundle_dir / fname
        if not bundle_file.is_file():
            continue
        original = bundle_file.read_text(encoding="utf-8")
        digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
        expected = receipt.get("preimage_hashes", {}).get(rel)
        if expected is not None and digest != expected:
            _die(
                f"recovery bundle preimage for {rel} does not match the "
                "receipt's recorded preimage hash -- refusing to restore from "
                "a corrupted bundle",
                1,
            )
        atomic_write(repo_root / rel, original)
        restored.append(rel)
    receipt["status"] = "RECOVERED"
    receipt["rollback_status"] = "COMPLETE"
    receipt["replaced_documents"] = sorted(set(receipt.get("replaced_documents", [])) | set(restored))
    write_json_report(receipt_path, receipt)
    return receipt


# ---------------------------------------------------------------------------
# Citation-only index staging plan (Phase 159 -- REMAP-01)
# ---------------------------------------------------------------------------
def build_index_stage_plan(
    repo_root: Path,
    planned: dict[Path, str],
    originals: dict[Path, str],
    by_doc: dict[str, dict[int, list[dict]]],
    maps: dict[tuple[str, str], LineMap],
) -> list[dict]:
    """Per-document staging plan for citation-only index objects.

    A tracked, DIRTY file must never be staged whole -- that would silently
    commit its unrelated edits alongside the citation remap. For a dirty
    tracked file this recomputes a `citation_only_blob` by re-applying the
    SAME citation edits (via the same `remap_document()` used for the real
    apply -- no second rewrite implementation) to the committed INDEX
    content, never to the live dirty bytes. An untracked or renamed path
    cannot be reasoned about this way and reports
    `staging_strategy: requires_authorization` instead of silently staging a
    whole file.
    """
    plans: list[dict] = []
    for path in sorted(planned, key=lambda p: str(p)):
        rel = str(path.relative_to(repo_root)).replace(os.sep, "/")
        original_text = originals.get(path, "")
        updated_text = planned[path]
        live_pre = hashlib.sha256(original_text.encode("utf-8")).hexdigest()
        live_post = hashlib.sha256(updated_text.encode("utf-8")).hexdigest()
        auth_id = stable_record_id(
            {
                "planning_file": rel,
                "planning_line": 0,
                "variant": "index_stage",
                "target_file_cited": rel,
                "target_line": 0,
                "target_line_end": None,
            }
        )

        tracked = subprocess.run(
            ["git", "-C", str(repo_root), "ls-files", "--error-unmatch", rel],
            capture_output=True, text=True, check=False,
        ).returncode == 0
        if not tracked:
            plans.append(
                {
                    "path": rel,
                    "index_mode": "untracked",
                    "base_index_blob": None,
                    "citation_only_blob": None,
                    "live_preimage_sha256": live_pre,
                    "live_postimage_sha256": live_post,
                    "staging_strategy": "requires_authorization",
                    "authorization_id": auth_id,
                }
            )
            continue

        base_rev = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", f"HEAD:{rel}"],
            capture_output=True, text=True, check=False,
        )
        base_index_blob = base_rev.stdout.strip() if base_rev.returncode == 0 else None
        show = subprocess.run(
            ["git", "-C", str(repo_root), "show", f":{rel}"],
            capture_output=True, text=True, check=False,
        )
        index_text = show.stdout if show.returncode == 0 else original_text

        if index_text == original_text:
            citation_only_text = updated_text
            strategy = "citation_only_index_object"
        else:
            scratch_counts: Counter = Counter()
            citation_only_text = remap_document(
                index_text, by_doc.get(rel, {}), maps, scratch_counts, [], [], rel
            )
            strategy = "citation_only_index_object"

        citation_only_blob = None
        if strategy == "citation_only_index_object":
            hashed = subprocess.run(
                # `-w` persists the blob into the ODB: an index-stage plan is
                # only useful if the caller can later `git update-index
                # --cacheinfo` the returned SHA, and a blob that was never
                # written cannot be staged.
                ["git", "-C", str(repo_root), "hash-object", "-w", "--stdin"],
                input=citation_only_text, capture_output=True, text=True, check=False,
            )
            citation_only_blob = hashed.stdout.strip() if hashed.returncode == 0 else None
            if not citation_only_blob:
                strategy = "requires_authorization"

        plans.append(
            {
                "path": rel,
                "index_mode": "tracked",
                "base_index_blob": base_index_blob,
                "citation_only_blob": citation_only_blob,
                "live_preimage_sha256": live_pre,
                "live_postimage_sha256": live_post,
                "staging_strategy": strategy,
                "authorization_id": (
                    None if strategy == "citation_only_index_object" else auth_id
                ),
            }
        )
    return plans


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

    This is the ROOT-WIDE default only. A record's own `source_sha` /
    `retarget_source_sha` (Phase 159) takes precedence over all three of these
    -- see `record_source_sha()`.
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


def record_source_sha(
    record: dict, shas: ShaResolver, exceptions: dict[str, dict] | None
) -> tuple[str | None, str | None]:
    """The historical SHA this record's map should be built at.

    Returns `(sha, error)`. Precedence:
      1. `retarget_source_sha` on a `retarget: true` row -- a Phase-154 hand
         choice advancing from its own post-154 anchor.
      2. an explicit per-record `source_sha` -- a late/supplemental row's own
         historical anchor.
      3. `source_sha_candidates` -- non-unique, stays BLOCKING until a
         reviewed `--exceptions` row supplies a `chosen_source_sha` contained
         in that candidate list.
      4. the root-wide `--pre-sweep-sha` / manifest-header default -- the
         homogeneous original-manifest case.
    """
    if record.get("retarget") and record.get("retarget_source_sha"):
        return record["retarget_source_sha"], None
    explicit = record.get("source_sha")
    if explicit:
        return explicit, None
    candidates = record.get("source_sha_candidates")
    if candidates:
        rid = stable_record_id(record)
        entry = (exceptions or {}).get(rid)
        chosen = entry.get("chosen_source_sha") if entry else None
        if chosen and chosen in candidates:
            return chosen, None
        return None, (
            f"{rid} carries {len(candidates)} non-unique historical source "
            "anchor candidate(s) with no reviewed chosen_source_sha -- blocking"
        )
    root_name = record["target_file_resolved"].split("/")[0]
    sha = shas.for_root(root_name)
    if not sha:
        return None, (
            f"no pre-sweep sha for root {root_name!r}: pass "
            f"--pre-sweep-sha {root_name}=<sha> or record it in the manifest header"
        )
    return sha, None


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
        action="append",
        required=True,
        help="pre-sweep citation manifest (JSONL). No default: an absent "
        "manifest is an error, never a derived path. Repeatable: multiple "
        "manifests (e.g. the original plus a late/supplemental manifest) are "
        "loaded and their records merged.",
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
        "--planning-base-sha",
        default=None,
        help="meta-repo commit at which recorded planning_file paths were "
        "valid; used to resolve a tracked rename via `git diff --find-renames`",
    )
    ap.add_argument(
        "--exceptions",
        default=None,
        help="reviewed exceptions ledger (JSONL, one row per stable record "
        "ID). Presence ENGAGES fail-closed hardening: an actionable dynamic "
        "retarget/not-at-recorded-line/unmatched row not covered by a "
        "reviewed row becomes a violation instead of a note.",
    )
    ap.add_argument(
        "--corpus-overlay",
        action="append",
        default=[],
        help="approved current-worktree location overlay (JSONL), repeatable",
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
    ap.add_argument(
        "--report-json",
        default=None,
        help="write a structured JSON report (totals, actionable_counts, "
        "open_ids, affected_documents, corpus_fingerprint, topology_digest, "
        "range_proofs)",
    )
    ap.add_argument(
        "--production-receipt",
        default=None,
        help="use a receipted BatchTransaction for --apply; a pre-existing "
        "receipt blocks a new apply",
    )
    ap.add_argument(
        "--recovery-bundle",
        default=None,
        help="preimage recovery bundle directory for --production-receipt / "
        "--recover-receipt",
    )
    ap.add_argument(
        "--recover-receipt",
        action="store_true",
        help="recovery-only: restore bytes from --recovery-bundle per "
        "--production-receipt's recorded preimages; never resumes an apply",
    )
    ap.add_argument(
        "--index-plan",
        default=None,
        help="write a citation-only index staging plan (JSON)",
    )
    ap.add_argument(
        "--inject-write-failure-after",
        type=int,
        default=None,
        help="TEST-ONLY: raise a synthetic write failure after N successful "
        "replacements inside a --production-receipt apply. Refuses to run "
        "against the canonical /workspaces root.",
    )
    args = ap.parse_args(argv)

    repo_root = Path(args.repo_root)
    if not repo_root.is_dir():
        _die(f"repo_root does not exist or is not a directory: {repo_root}", 2)
    repo_root = repo_root.resolve()

    if args.inject_write_failure_after is not None and repo_root == Path("/workspaces").resolve():
        _die(
            "--inject-write-failure-after refuses the canonical live root "
            "/workspaces -- it exists only to prove the batch-recovery "
            "contract in disposable tests",
            2,
        )

    if args.recover_receipt:
        if not args.production_receipt or not args.recovery_bundle:
            _die("--recover-receipt requires --production-receipt and --recovery-bundle", 2)
        receipt_path = Path(args.production_receipt)
        if not receipt_path.is_absolute():
            receipt_path = (Path.cwd() / receipt_path).resolve()
        bundle_dir = Path(args.recovery_bundle)
        if not bundle_dir.is_absolute():
            bundle_dir = (Path.cwd() / bundle_dir).resolve()
        if not receipt_path.is_file():
            _die(f"no receipt at {receipt_path} to recover", 2)
        receipt = recover_failed_receipt(receipt_path, repo_root, bundle_dir)
        print(
            f"RECOVERY: status={receipt['status']} "
            f"rollback_status={receipt.get('rollback_status')}"
        )
        sys.exit(0)

    manifest_paths: list[Path] = []
    for spec in args.manifest:
        mp = Path(spec)
        if not mp.is_absolute():
            mp = (Path.cwd() / mp).resolve()
        manifest_paths.append(mp)

    header: dict = {}
    records: list[dict] = []
    for mp in manifest_paths:
        h, recs = load_manifest(mp)
        if not header:
            header = h
        records.extend(recs)

    shas = ShaResolver(header, args.pre_sweep_sha)

    exceptions_by_id: dict[str, dict] = {}
    if args.exceptions:
        epath = Path(args.exceptions)
        if not epath.is_absolute():
            epath = (Path.cwd() / epath).resolve()
        if not epath.is_file():
            _die(f"cannot load exceptions ledger {epath}: no such file", 2)
        for row in load_jsonl_rows(epath):
            rid = row.get("record_id")
            if rid:
                exceptions_by_id[rid] = row
    strict = bool(args.exceptions)

    overlays: list[dict] = []
    for ov_spec in args.corpus_overlay:
        opath = Path(ov_spec)
        if not opath.is_absolute():
            opath = (Path.cwd() / opath).resolve()
        if not opath.is_file():
            _die(f"cannot load corpus overlay {opath}: no such file", 2)
        overlays.extend(load_jsonl_rows(opath))
    location_resolver = LocationResolver(repo_root, args.planning_base_sha, overlays)

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

    # ---- resolve each applicable record's historical anchor (multi-anchor) -
    sha_errors: list[str] = []
    for rec in applicable:
        sha, err = record_source_sha(rec, shas, exceptions_by_id)
        if err:
            sha_errors.append(
                f"{rec['planning_file']}:{rec['planning_line']} -- {err}"
            )
        rec["_effective_source_sha"] = sha
    if sha_errors:
        print(
            "FAIL: unresolved historical source anchor(s) -- nothing was "
            "written:\n",
            file=sys.stderr,
        )
        for e in sha_errors:
            print(f"  {e}", file=sys.stderr)
        print(f"\nTotal: {len(sha_errors)} violation(s). Exit 1 (BLOCK).", file=sys.stderr)
        sys.exit(1)

    # ---- build one line map per (target file, historical sha) pair --------
    targets = sorted(
        {(rec["target_file_resolved"], rec["_effective_source_sha"]) for rec in applicable}
    )
    root_names = sorted({safe_relative(t[0], "target_file_resolved").split("/")[0] for t in targets})
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
        index = citation_paths.CandidateIndex(roots, sorted({t[0] for t in targets}))
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

    maps: dict[tuple[str, str], LineMap] = {}
    missing_targets: list[str] = []
    for rel, sha in targets:
        name, _, subpath = rel.partition("/")
        disk = index.real_path(rel)
        if not disk.is_file():
            if rel not in missing_targets:
                missing_targets.append(rel)
            continue
        old_text = git_show(roots[name], sha, subpath)
        if old_text is None:
            _die(
                f"cannot read the pre-sweep blob {sha}:./{subpath} from "
                f"{roots[name]} -- the 'old' side of the map must come from "
                "git, because it exists nowhere on disk",
                2,
            )
        maps[(rel, sha)] = LineMap(
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
    originals: dict[Path, str] = {}
    open_ids: set[str] = set()
    range_proofs: list[dict] = []

    for rel in sorted(by_doc):
        doc_path = inside(repo_root, rel, "planning_file")
        if doc_path.is_symlink():
            _die(f"refusing to read the citing document through a symlink: {rel}", 1)
        if not doc_path.is_file():
            outcome = location_resolver.resolve(rel)
            if outcome.status == "missing":
                _die(f"citing document does not exist: {rel}", 1)
            resolved_rel = safe_relative(outcome.resolved_path, "planning_file (resolved)")
            doc_path = inside(repo_root, resolved_rel, "planning_file (resolved)")
            if doc_path.is_symlink() or not doc_path.is_file():
                _die(f"resolved citing document does not exist: {resolved_rel}", 1)
        original = doc_path.read_text(encoding="utf-8")
        originals[doc_path] = original
        updated = remap_document(
            original,
            by_doc[rel],
            maps,
            counts,
            notes,
            violations,
            rel,
            exceptions=exceptions_by_id,
            strict=strict,
            open_ids=open_ids,
            range_proofs=range_proofs,
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

    if args.index_plan:
        index_plan = build_index_stage_plan(repo_root, planned, originals, by_doc, maps)
        write_json_report(Path(args.index_plan), index_plan)

    if args.report_json:
        corpus_fingerprint = hashlib.sha256(
            json.dumps(sorted(f"{p}@{s}" for p, s in maps), sort_keys=True).encode("utf-8")
        ).hexdigest()
        topology_parts: dict[str, str | None] = {}
        for name, root_dir in roots.items():
            head = subprocess.run(
                ["git", "-C", str(root_dir), "rev-parse", "HEAD"],
                capture_output=True, text=True, check=False,
            )
            topology_parts[name] = head.stdout.strip() if head.returncode == 0 else None
        topology_digest = hashlib.sha256(
            json.dumps(topology_parts, sort_keys=True).encode("utf-8")
        ).hexdigest()
        report = {
            "totals": {"examined": counts["examined"], **{k: counts[k] for k in OUTCOMES}},
            "actionable_counts": {
                k: counts[k]
                for k in (RETARGET, NOT_AT_RECORDED_LINE, NO_MATCH_IN_DOCUMENT, UNREVIEWED_RETARGET, VIOLATION)
            },
            "open_ids": sorted(open_ids),
            "affected_documents": sorted(
                str(p.relative_to(repo_root)).replace(os.sep, "/") for p in planned
            ),
            "corpus_fingerprint": corpus_fingerprint,
            "topology_digest": topology_digest,
            "range_proofs": range_proofs,
        }
        write_json_report(Path(args.report_json), report)

    if args.apply:
        if args.production_receipt:
            receipt_path = Path(args.production_receipt)
            if not receipt_path.is_absolute():
                receipt_path = (Path.cwd() / receipt_path).resolve()
            if args.recovery_bundle:
                bundle_dir = Path(args.recovery_bundle)
            else:
                bundle_dir = receipt_path.parent / (receipt_path.stem + "-recovery-bundle")
            if not bundle_dir.is_absolute():
                bundle_dir = (Path.cwd() / bundle_dir).resolve()
            fingerprint = hashlib.sha256(
                json.dumps(
                    {
                        "targets": sorted(f"{p}@{s}" for p, s in maps),
                        "manifest_record_count": len(records),
                    },
                    sort_keys=True,
                ).encode("utf-8")
            ).hexdigest()
            txn = BatchTransaction(
                repo_root,
                planned,
                receipt_path,
                bundle_dir,
                fingerprint,
                inject_failure_after=args.inject_write_failure_after,
            )
            txn.preflight()
            txn.prepare()
            receipt = txn.apply()
            if receipt["status"] != "APPLIED":
                print(
                    f"FAIL: batch transaction ended in status "
                    f"{receipt['status']!r}; rollback_status="
                    f"{receipt.get('rollback_status')!r}. See {receipt_path} "
                    "for the full receipt. Exit 1 (BLOCK).",
                    file=sys.stderr,
                )
                sys.exit(1)
        else:
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
